#!/usr/bin/env python3
"""
Moduł wykrywania anomalii w urządzeniach medycznych używając Machine Learning.

Używa algorytmów ML do wykrywania nietypowych urządzeń na podstawie:
- Security score
- Liczby podatności
- Typu szyfrowania
- Protokołu komunikacji
- Innych cech bezpieczeństwa

Algorytmy:
- Isolation Forest: Szybki i skuteczny dla wysokowymiarowych danych
- Local Outlier Factor (LOF): Wykrywa lokalne anomalie
- One-Class SVM: Wykrywa odstające urządzenia od normalnego wzorca
- Autoencoder (Deep Learning): Wykrywa złożone wzorce anomalii
- Random Forest: Predykcja przyszłych podatności
- KMeans/DBSCAN: Klasteryzacja urządzeń według podobieństwa

Funkcjonalności:
- Wykrywanie anomalii w czasie rzeczywistym (streaming)
- Deep Learning (Autoencoder) dla złożonych wzorców
- Predykcja przyszłych podatności
- Klasteryzacja urządzeń według podobieństwa bezpieczeństwa
- Integracja z systemami SIEM (CEF, syslog, custom callbacks)
"""

import numpy as np
import pandas as pd
from typing import List, Dict, Optional, Tuple, Callable
from pathlib import Path
import json
from datetime import datetime
import pickle
import threading
from collections import deque
import socket
# syslog - używany tylko w export_to_syslog, nie wymaga importu modułu syslog

try:
    from sklearn.ensemble import IsolationForest
    from sklearn.neighbors import LocalOutlierFactor
    from sklearn.svm import OneClassSVM
    from sklearn.preprocessing import StandardScaler
    from sklearn.decomposition import PCA
    from sklearn.cluster import KMeans, DBSCAN
    from sklearn.linear_model import LogisticRegression
    from sklearn.ensemble import RandomForestClassifier
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    IsolationForest = None
    LocalOutlierFactor = None
    OneClassSVM = None
    StandardScaler = None
    PCA = None
    KMeans = None
    DBSCAN = None
    LogisticRegression = None
    RandomForestClassifier = None

# Deep Learning - opcjonalne
try:
    # Wycisz WSZYSTKIE komunikaty TensorFlow o CUDA/GPU przed importem
    import os
    # TF_CPP_MIN_LOG_LEVEL:
    # 0 = wszystkie komunikaty (domyślnie)
    # 1 = wycisz INFO
    # 2 = wycisz INFO i WARNING
    # 3 = wycisz wszystko oprócz ERROR (w tym błędy CUDA)
    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  # Wycisz wszystko oprócz krytycznych błędów
    os.environ['TF_FORCE_GPU_ALLOW_GROWTH'] = 'true'
    
    # Całkowicie wyłącz próby użycia GPU (wymusza CPU)
    os.environ['CUDA_VISIBLE_DEVICES'] = ''  # Wyłącz CUDA - wymusza użycie tylko CPU
    
    # Wyłącz GPU jeśli nie jest dostępne (zapobiega komunikatom o CUDA)
    import tensorflow as tf
    # Ustaw tylko CPU - całkowicie wyłącz GPU
    try:
        # Wyłącz wszystkie GPU przed inicjalizacją
        tf.config.set_visible_devices([], 'GPU')
        # Wymuś użycie CPU
        tf.config.threading.set_inter_op_parallelism_threads(1)
        tf.config.threading.set_intra_op_parallelism_threads(1)
    except Exception:
        # Ignoruj błędy konfiguracji GPU
        pass
    
    from tensorflow import keras
    from tensorflow.keras import layers
    TENSORFLOW_AVAILABLE = True
except ImportError:
    TENSORFLOW_AVAILABLE = False
    tf = None
    keras = None

from device import Device, Protocol, DeviceType


class AnomalyDetector:
    """
    Klasa do wykrywania anomalii w urządzeniach medycznych używając ML.
    
    Wykrywa nietypowe urządzenia na podstawie ich cech bezpieczeństwa:
    - Urządzenia z nietypowo niskim security score
    - Urządzenia z nietypową liczbą podatności
    - Urządzenia z nietypowym typem szyfrowania
    - Urządzenia z nietypowym protokołem dla danego typu
    """
    
    def __init__(self, contamination: float = 0.1):
        """
        Inicjalizacja detektora anomalii.
        
        Args:
            contamination: Oczekiwany procent anomalii w danych (0.0-0.5)
        """
        if not SKLEARN_AVAILABLE:
            raise ImportError("scikit-learn nie jest zainstalowany. Zainstaluj: pip install scikit-learn")
        
        self.contamination = contamination
        self.scaler = StandardScaler()
        self.isolation_forest = IsolationForest(
            contamination=contamination,
            random_state=42,
            n_estimators=100
        )
        self.lof = LocalOutlierFactor(
            contamination=contamination,
            novelty=True,
            n_neighbors=20
        )
        self.one_class_svm = OneClassSVM(
            nu=contamination,
            kernel='rbf',
            gamma='scale'
        )
        
        # Model historyczny do uczenia
        self.trained = False
        self.model_dir = Path(__file__).parent.parent / "data" / "models"
        self.model_dir.mkdir(parents=True, exist_ok=True)
        
        # Streaming detection - bufor dla urządzeń w czasie rzeczywistym
        self.streaming_buffer = deque(maxlen=100)  # Ostatnie 100 urządzeń
        self.streaming_lock = threading.Lock()
        
        # Deep Learning - Autoencoder (opcjonalny)
        self.autoencoder = None
        self.use_deep_learning = False
        
        # Predykcja podatności
        self.vulnerability_predictor = None
        self.vulnerability_trained = False
        
        # Klasteryzacja
        self.clusterer = None
        self.clusters_trained = False
        
        # SIEM integration
        self.siem_enabled = False
        self.siem_callbacks: List[Callable] = []
    
    def extract_features(self, devices: List[Device]) -> np.ndarray:
        """
        Ekstrahuje cechy z urządzeń do wektora numerycznego.
        
        Cechy:
        1. Security score (0-100)
        2. Liczba podatności
        3. Czy ma szyfrowanie (0/1)
        4. Czy wymaga parowania (0/1)
        5. Typ protokołu (one-hot encoded: BLE=0, WiFi=1, USB=2, NFC=3)
        6. Typ urządzenia (one-hot encoded)
        7. RSSI (jeśli dostępne, normalizowane)
        8. Liczba otwartych portów (jeśli dostępne)
        9. Encryption strength score (jeśli dostępne)
        
        Args:
            devices: Lista urządzeń
            
        Returns:
            Macierz cech (n_samples, n_features)
        """
        features = []
        
        for device in devices:
            feature_vector = []
            
            # 1. Security score
            feature_vector.append(device.security_score)
            
            # 2. Liczba podatności
            feature_vector.append(len(device.vulnerabilities))
            
            # 3. Czy ma szyfrowanie (0/1)
            feature_vector.append(1 if device.has_encryption else 0)
            
            # 4. Czy wymaga parowania (0/1)
            feature_vector.append(1 if device.requires_pairing else 0)
            
            # 5. Typ protokołu (one-hot encoded)
            protocol_map = {
                Protocol.BLE: 0,
                Protocol.WIFI: 1,
                Protocol.USB: 2,
                Protocol.NFC: 3
            }
            protocol_encoded = [0, 0, 0, 0]
            protocol_idx = protocol_map.get(device.protocol, 0)
            protocol_encoded[protocol_idx] = 1
            feature_vector.extend(protocol_encoded)
            
            # 6. Typ urządzenia (one-hot encoded)
            device_type_map = {
                DeviceType.GLUCOSE_METER: 0,
                DeviceType.INSULIN_PUMP: 1,
                DeviceType.BLOOD_PRESSURE: 2,
                DeviceType.PULSE_OXIMETER: 3,
                DeviceType.FITNESS_TRACKER: 4,
                DeviceType.SMARTWATCH: 5,
                DeviceType.UNKNOWN: 6
            }
            device_type_encoded = [0] * 7
            device_type_idx = device_type_map.get(device.device_type, 6)
            device_type_encoded[device_type_idx] = 1
            feature_vector.extend(device_type_encoded)
            
            # 7. RSSI (normalizowane, jeśli dostępne)
            if device.rssi is not None:
                # Normalizuj RSSI do zakresu 0-1 (zakładamy zakres -100 do 0 dBm)
                normalized_rssi = (device.rssi + 100) / 100
                feature_vector.append(max(0, min(1, normalized_rssi)))
            else:
                feature_vector.append(0.5)  # Wartość domyślna
            
            # 8. Liczba otwartych portów (jeśli dostępne)
            open_ports = device.metadata.get('open_ports', [])
            feature_vector.append(len(open_ports))
            
            # 9. Encryption strength score (jeśli dostępne)
            enc_analysis = device.metadata.get('encryption_analysis', {})
            if enc_analysis:
                enc_score = enc_analysis.get('score', 0)
                feature_vector.append(enc_score)
            else:
                # Jeśli brak analizy, użyj heurystyki
                if device.has_encryption:
                    feature_vector.append(50)  # Średnia siła
                else:
                    feature_vector.append(0)  # Brak szyfrowania
            
            features.append(feature_vector)
        
        return np.array(features)
    
    def train(self, devices: List[Device]) -> Dict:
        """
        Trenuje modele ML na podstawie historycznych danych.
        
        Args:
            devices: Lista urządzeń do treningu
            
        Returns:
            Słownik ze statystykami treningu
        """
        if len(devices) < 2:
            # Potrzebne co najmniej 2 urządzenia do treningu (LOF wymaga n_neighbors < n_samples)
            return {
                'trained': False,
                'reason': 'Za mało danych (minimum 2 urządzenia)',
                'devices_count': len(devices)
            }
        
        # Ekstrahuj cechy
        X = self.extract_features(devices)
        
        # Normalizuj cechy
        X_scaled = self.scaler.fit_transform(X)
        
        # LOF: n_neighbors musi być mniejsze niż liczba próbek – dostosuj do dostępnej liczby urządzeń
        n_neighbors_lof = max(1, min(20, len(devices) - 1))
        self.lof.set_params(n_neighbors=n_neighbors_lof)
        
        # Trenuj modele
        self.isolation_forest.fit(X_scaled)
        self.lof.fit(X_scaled)
        self.one_class_svm.fit(X_scaled)
        
        self.trained = True
        
        # Zapisz model
        self.save_model()
        
        return {
            'trained': True,
            'devices_count': len(devices),
            'features_count': X.shape[1],
            'contamination': self.contamination
        }
    
    def detect_anomalies(self, devices: List[Device], use_ensemble: bool = True) -> List[Dict]:
        """
        Wykrywa anomalie w urządzeniach.
        
        Args:
            devices: Lista urządzeń do analizy
            use_ensemble: Czy użyć ensemble (głosowanie większościowe)
        
        Returns:
            Lista słowników z wynikami dla każdego urządzenia:
            {
                'device': Device,
                'is_anomaly': bool,
                'anomaly_score': float,
                'method': str,
                'reason': str
            }
        """
        if not devices:
            return []
        
        # Jeśli model nie jest wytrenowany, użyj domyślnych wartości
        if not self.trained:
            # Prosta heurystyka: urządzenia z bardzo niskim security score
            results = []
            for device in devices:
                is_anomaly = device.security_score < 30 or len(device.vulnerabilities) > 5
                results.append({
                    'device': device,
                    'is_anomaly': is_anomaly,
                    'anomaly_score': 1.0 - (device.security_score / 100),
                    'method': 'heuristic',
                    'reason': 'Low security score or many vulnerabilities' if is_anomaly else 'Normal'
                })
            return results
        
        # Ekstrahuj cechy
        X = self.extract_features(devices)
        X_scaled = self.scaler.transform(X)
        
        # Wykryj anomalie używając różnych metod
        if_anomalies = self.isolation_forest.predict(X_scaled)
        if_scores = -self.isolation_forest.score_samples(X_scaled)  # Neguj, bo -1 = anomalia
        
        lof_anomalies = self.lof.predict(X_scaled)
        lof_scores = -self.lof.score_samples(X_scaled)
        
        svm_anomalies = self.one_class_svm.predict(X_scaled)
        svm_scores = -self.one_class_svm.score_samples(X_scaled)
        
        # Ensemble: głosowanie większościowe
        results = []
        for i, device in enumerate(devices):
            if_anomaly = if_anomalies[i] == -1
            lof_anomaly = lof_anomalies[i] == -1
            svm_anomaly = svm_anomalies[i] == -1
            
            if use_ensemble:
                # Głosowanie większościowe: anomalia jeśli 2 z 3 metod wykryły
                is_anomaly = sum([if_anomaly, lof_anomaly, svm_anomaly]) >= 2
                method = 'ensemble'
                anomaly_score = np.mean([if_scores[i], lof_scores[i], svm_scores[i]])
                
                # Określ przyczynę
                reasons = []
                if if_anomaly:
                    reasons.append("Isolation Forest")
                if lof_anomaly:
                    reasons.append("LOF")
                if svm_anomaly:
                    reasons.append("One-Class SVM")
                reason = f"Detected by: {', '.join(reasons)}" if reasons else "Normal"
            else:
                # Użyj tylko Isolation Forest (najszybszy)
                is_anomaly = if_anomaly
                method = 'isolation_forest'
                anomaly_score = if_scores[i]
                reason = "Anomaly detected by Isolation Forest" if is_anomaly else "Normal"
            
            results.append({
                'device': device,
                'is_anomaly': is_anomaly,
                'anomaly_score': float(anomaly_score),
                'method': method,
                'reason': reason,
                'scores': {
                    'isolation_forest': float(if_scores[i]),
                    'lof': float(lof_scores[i]),
                    'svm': float(svm_scores[i])
                }
            })
        
        return results
    
    def save_model(self):
        """Zapisuje wytrenowany model do pliku."""
        if not self.trained:
            return
        
        model_data = {
            'scaler': self.scaler,
            'isolation_forest': self.isolation_forest,
            'lof': self.lof,
            'one_class_svm': self.one_class_svm,
            'trained': True,
            'timestamp': datetime.now().isoformat()
        }
        
        model_path = self.model_dir / "anomaly_detector.pkl"
        try:
            with open(model_path, 'wb') as f:
                pickle.dump(model_data, f)
        except Exception as e:
            print(f"Błąd zapisywania modelu: {e}")
    
    def load_model(self) -> bool:
        """
        Wczytuje wytrenowany model z pliku.
        
        Returns:
            True jeśli model został wczytany, False w przeciwnym razie
        """
        model_path = self.model_dir / "anomaly_detector.pkl"
        if not model_path.exists():
            return False
        
        try:
            with open(model_path, 'rb') as f:
                model_data = pickle.load(f)
            
            self.scaler = model_data['scaler']
            self.isolation_forest = model_data['isolation_forest']
            self.lof = model_data['lof']
            self.one_class_svm = model_data['one_class_svm']
            self.trained = model_data.get('trained', False)
            
            return True
        except Exception as e:
            print(f"Błąd wczytywania modelu: {e}")
            return False
    
    def get_anomaly_statistics(self, results: List[Dict]) -> Dict:
        """
        Oblicza statystyki dotyczące wykrytych anomalii.
        
        Args:
            results: Wyniki z detect_anomalies()
        
        Returns:
            Słownik ze statystykami
        """
        if not results:
            return {
                'total_devices': 0,
                'anomalies_count': 0,
                'anomalies_percentage': 0,
                'avg_anomaly_score': 0,
                'max_anomaly_score': 0
            }
        
        anomalies = [r for r in results if r['is_anomaly']]
        anomaly_scores = [r['anomaly_score'] for r in results]
        
        return {
            'total_devices': len(results),
            'anomalies_count': len(anomalies),
            'anomalies_percentage': (len(anomalies) / len(results)) * 100,
            'avg_anomaly_score': np.mean(anomaly_scores),
            'max_anomaly_score': np.max(anomaly_scores),
            'min_anomaly_score': np.min(anomaly_scores)
        }
    
    def detect_anomaly_streaming(self, device: Device) -> Dict:
        """
        Wykrywa anomalie w czasie rzeczywistym dla pojedynczego urządzenia (streaming).
        
        Args:
            device: Pojedyncze urządzenie do analizy
        
        Returns:
            Słownik z wynikiem:
            {
                'device': Device,
                'is_anomaly': bool,
                'anomaly_score': float,
                'method': str,
                'reason': str,
                'timestamp': str
            }
        """
        if not self.trained:
            # Prosta heurystyka jeśli model nie jest wytrenowany
            is_anomaly = device.security_score < 30 or len(device.vulnerabilities) > 5
            return {
                'device': device,
                'is_anomaly': is_anomaly,
                'anomaly_score': 1.0 - (device.security_score / 100),
                'method': 'heuristic',
                'reason': 'Low security score or many vulnerabilities' if is_anomaly else 'Normal',
                'timestamp': datetime.now().isoformat()
            }
        
        # Ekstrahuj cechy dla pojedynczego urządzenia
        X = self.extract_features([device])
        X_scaled = self.scaler.transform(X)
        
        # Wykryj anomalie
        if_anomaly = self.isolation_forest.predict(X_scaled)[0] == -1
        if_score = -self.isolation_forest.score_samples(X_scaled)[0]
        
        lof_anomaly = self.lof.predict(X_scaled)[0] == -1
        lof_score = -self.lof.score_samples(X_scaled)[0]
        
        svm_anomaly = self.one_class_svm.predict(X_scaled)[0] == -1
        svm_score = -self.one_class_svm.score_samples(X_scaled)[0]
        
        # Ensemble voting
        is_anomaly = sum([if_anomaly, lof_anomaly, svm_anomaly]) >= 2
        anomaly_score = np.mean([if_score, lof_score, svm_score])
        
        # Deep Learning check (jeśli dostępny)
        if self.use_deep_learning and self.autoencoder is not None:
            try:
                reconstruction_error = self.autoencoder.predict(X_scaled, verbose=0)
                mse = np.mean(np.power(X_scaled - reconstruction_error, 2))
                if mse > 0.5:  # Próg dla anomalii
                    is_anomaly = True
                    anomaly_score = max(anomaly_score, mse)
            except Exception:
                pass  # Ignoruj błędy DL
        
        # Dodaj do bufora streamingowego
        with self.streaming_lock:
            self.streaming_buffer.append({
                'device': device,
                'timestamp': datetime.now(),
                'anomaly_score': float(anomaly_score),
                'is_anomaly': is_anomaly
            })
        
        reasons = []
        if if_anomaly:
            reasons.append("Isolation Forest")
        if lof_anomaly:
            reasons.append("LOF")
        if svm_anomaly:
            reasons.append("One-Class SVM")
        
        result = {
            'device': device,
            'is_anomaly': is_anomaly,
            'anomaly_score': float(anomaly_score),
            'method': 'streaming_ensemble',
            'reason': f"Detected by: {', '.join(reasons)}" if reasons else "Normal",
            'timestamp': datetime.now().isoformat()
        }
        
        # Wywołaj callbacki SIEM jeśli anomalia wykryta
        if is_anomaly and self.siem_enabled:
            self._send_to_siem(result)
        
        return result
    
    def train_deep_learning(self, devices: List[Device], epochs: int = 50) -> Dict:
        """
        Trenuje Autoencoder (Deep Learning) dla wykrywania anomalii.
        
        Args:
            devices: Lista urządzeń do treningu
            epochs: Liczba epok treningu
        
        Returns:
            Słownik ze statystykami treningu
        """
        if not TENSORFLOW_AVAILABLE:
            return {
                'trained': False,
                'reason': 'TensorFlow nie jest zainstalowany. Zainstaluj: pip install tensorflow'
            }
        
        if len(devices) < 2:
            return {
                'trained': False,
                'reason': 'Za mało danych (minimum 2 urządzenia dla DL)',
                'devices_count': len(devices)
            }
        
        # Ekstrahuj cechy
        X = self.extract_features(devices)
        X_scaled = self.scaler.fit_transform(X)
        
        input_dim = X_scaled.shape[1]
        
        # Buduj Autoencoder
        input_layer = keras.Input(shape=(input_dim,))
        encoded = layers.Dense(input_dim // 2, activation='relu')(input_layer)
        encoded = layers.Dense(input_dim // 4, activation='relu')(encoded)
        decoded = layers.Dense(input_dim // 2, activation='relu')(encoded)
        decoded = layers.Dense(input_dim, activation='sigmoid')(decoded)
        
        self.autoencoder = keras.Model(input_layer, decoded)
        self.autoencoder.compile(optimizer='adam', loss='mse')
        
        # batch_size dopasowany do liczby urządzeń (TensorFlow wymaga batch_size <= n_samples)
        batch_size = min(32, max(1, len(devices)))
        validation_split = min(0.2, 0.5 - 0.5 / max(1, len(devices))) if len(devices) > 1 else 0.0
        
        # Trenuj
        history = self.autoencoder.fit(
            X_scaled, X_scaled,
            epochs=epochs,
            batch_size=batch_size,
            validation_split=validation_split,
            verbose=0
        )
        
        self.use_deep_learning = True
        
        # Zapisz model
        try:
            autoencoder_path = self.model_dir / "autoencoder.h5"
            self.autoencoder.save(str(autoencoder_path))
        except Exception as e:
            print(f"Błąd zapisywania autoencodera: {e}")
        
        return {
            'trained': True,
            'devices_count': len(devices),
            'epochs': epochs,
            'final_loss': float(history.history['loss'][-1])
        }
    
    def load_deep_learning(self) -> bool:
        """Wczytuje wytrenowany Autoencoder."""
        if not TENSORFLOW_AVAILABLE:
            return False
        
        autoencoder_path = self.model_dir / "autoencoder.h5"
        if not autoencoder_path.exists():
            return False
        
        try:
            self.autoencoder = keras.models.load_model(str(autoencoder_path))
            self.use_deep_learning = True
            return True
        except Exception as e:
            print(f"Błąd wczytywania autoencodera: {e}")
            return False
    
    def train_vulnerability_predictor(self, devices: List[Device]) -> Dict:
        """
        Trenuje model do predykcji przyszłych podatności.
        
        Przewiduje prawdopodobieństwo wystąpienia podatności w przyszłości
        na podstawie obecnych cech bezpieczeństwa.
        
        Args:
            devices: Lista urządzeń z historią podatności
        
        Returns:
            Słownik ze statystykami treningu
        """
        if len(devices) < 2:
            return {
                'trained': False,
                'reason': 'Za mało danych (minimum 2 urządzenia)',
                'devices_count': len(devices)
            }
        
        # Ekstrahuj cechy
        X = self.extract_features(devices)
        X_scaled = self.scaler.fit_transform(X)
        
        # Cel: czy urządzenie będzie miało podatności w przyszłości?
        # Używamy obecnej liczby podatności jako proxy
        y = np.array([1 if len(d.vulnerabilities) > 0 else 0 for d in devices])
        
        # Trenuj Random Forest
        self.vulnerability_predictor = RandomForestClassifier(
            n_estimators=100,
            random_state=42,
            max_depth=10
        )
        self.vulnerability_predictor.fit(X_scaled, y)
        
        self.vulnerability_trained = True
        
        # Zapisz model
        try:
            predictor_path = self.model_dir / "vulnerability_predictor.pkl"
            with open(predictor_path, 'wb') as f:
                pickle.dump(self.vulnerability_predictor, f)
        except Exception as e:
            print(f"Błąd zapisywania predyktora: {e}")
        
        accuracy = self.vulnerability_predictor.score(X_scaled, y)
        
        return {
            'trained': True,
            'devices_count': len(devices),
            'accuracy': float(accuracy)
        }
    
    def predict_vulnerability(self, device: Device) -> Dict:
        """
        Przewiduje prawdopodobieństwo wystąpienia podatności w przyszłości.
        
        Args:
            device: Urządzenie do analizy
        
        Returns:
            Słownik z predykcją:
            {
                'probability': float,  # 0-1
                'risk_level': str,    # 'low', 'medium', 'high'
                'recommendations': List[str]
            }
        """
        if not self.vulnerability_trained:
            return {
                'probability': 0.5,
                'risk_level': 'unknown',
                'recommendations': ['Model nie jest wytrenowany']
            }
        
        X = self.extract_features([device])
        X_scaled = self.scaler.transform(X)
        
        probability = self.vulnerability_predictor.predict_proba(X_scaled)[0][1]
        
        if probability < 0.3:
            risk_level = 'low'
            recommendations = [
                'Urządzenie ma niskie ryzyko podatności',
                'Kontynuuj regularne skanowania'
            ]
        elif probability < 0.7:
            risk_level = 'medium'
            recommendations = [
                'Urządzenie ma średnie ryzyko podatności',
                'Zwiększ częstotliwość skanowań',
                'Rozważ aktualizację oprogramowania'
            ]
        else:
            risk_level = 'high'
            recommendations = [
                'Urządzenie ma wysokie ryzyko podatności',
                'Wymagana natychmiastowa aktualizacja',
                'Rozważ wyłączenie z sieci do czasu naprawy',
                'Skanuj codziennie'
            ]
        
        return {
            'probability': float(probability),
            'risk_level': risk_level,
            'recommendations': recommendations
        }
    
    def cluster_devices(self, devices: List[Device], n_clusters: int = 5, method: str = 'kmeans') -> List[Dict]:
        """
        Klasteryzuje urządzenia według podobieństwa bezpieczeństwa.
        
        Args:
            devices: Lista urządzeń
            n_clusters: Liczba klastrów (dla KMeans)
            method: 'kmeans' lub 'dbscan'
        
        Returns:
            Lista słowników z przypisaniami klastrów:
            {
                'device': Device,
                'cluster': int,
                'cluster_name': str
            }
        """
        if len(devices) < 1:
            return []
        
        # Liczba klastrów nie może przekraczać liczby urządzeń
        n_clusters_actual = min(n_clusters, max(1, len(devices)))
        
        X = self.extract_features(devices)
        X_scaled = self.scaler.fit_transform(X)
        
        if method == 'kmeans':
            self.clusterer = KMeans(n_clusters=n_clusters_actual, random_state=42, n_init=10)
            labels = self.clusterer.fit_predict(X_scaled)
        else:  # dbscan
            min_samples = min(3, len(devices))
            self.clusterer = DBSCAN(eps=0.5, min_samples=min_samples)
            labels = self.clusterer.fit_predict(X_scaled)
        
        # Nazwy klastrów na podstawie średniego security score
        cluster_stats = {}
        for cluster_id in set(labels):
            if cluster_id == -1:  # DBSCAN noise
                continue
            cluster_devices = [devices[i] for i, label in enumerate(labels) if label == cluster_id]
            avg_score = np.mean([d.security_score for d in cluster_devices])
            cluster_stats[cluster_id] = {
                'avg_score': avg_score,
                'count': len(cluster_devices)
            }
        
        results = []
        for i, device in enumerate(devices):
            cluster_id = int(labels[i])
            if cluster_id == -1:
                cluster_name = "Noise/Outliers"
            else:
                score = cluster_stats.get(cluster_id, {}).get('avg_score', 50)
                if score >= 80:
                    cluster_name = f"Cluster {cluster_id}: High Security"
                elif score >= 60:
                    cluster_name = f"Cluster {cluster_id}: Medium Security"
                else:
                    cluster_name = f"Cluster {cluster_id}: Low Security"
            
            results.append({
                'device': device,
                'cluster': cluster_id,
                'cluster_name': cluster_name
            })
        
        self.clusters_trained = True
        return results
    
    def enable_siem_integration(self, enabled: bool = True):
        """Włącza/wyłącza integrację z SIEM."""
        self.siem_enabled = enabled
    
    def add_siem_callback(self, callback: Callable[[Dict], None]):
        """
        Dodaje callback do wysyłania alertów do SIEM.
        
        Args:
            callback: Funkcja przyjmująca słownik z alertem i wysyłająca do SIEM
        """
        self.siem_callbacks.append(callback)
    
    def export_to_cef(self, anomaly_result: Dict) -> str:
        """
        Eksportuje wynik anomalii do formatu CEF (Common Event Format).
        
        Args:
            anomaly_result: Wynik z detect_anomaly_streaming()
        
        Returns:
            String w formacie CEF
        """
        device = anomaly_result['device']
        timestamp = datetime.now().strftime('%b %d %H:%M:%S')
        
        # CEF format: CEF:Version|Device Vendor|Device Product|Device Version|Signature ID|Name|Severity|Extension
        cef = (
            f"CEF:0|MedicalDeviceScanner|AnomalyDetector|1.0|"
            f"ANOMALY_DETECTED|Device Anomaly Detected|"
            f"{int(anomaly_result['anomaly_score'] * 10)}|"
            f"src={device.mac_address} "
            f"dhost={device.name} "
            f"cs1={device.protocol.value} "
            f"cs2={device.security_score} "
            f"cs3={len(device.vulnerabilities)} "
            f"msg={anomaly_result['reason']}"
        )
        return cef
    
    def export_to_syslog(self, anomaly_result: Dict, host: str = 'localhost', port: int = 514):
        """
        Wysyła alert do syslog.
        
        Args:
            anomaly_result: Wynik z detect_anomaly_streaming()
            host: Adres serwera syslog
            port: Port serwera syslog
        """
        device = anomaly_result['device']
        message = (
            f"MEDICAL_DEVICE_ANOMALY: device={device.name} "
            f"mac={device.mac_address} "
            f"score={anomaly_result['anomaly_score']:.2f} "
            f"reason={anomaly_result['reason']}"
        )
        
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.sendto(message.encode('utf-8'), (host, port))
            sock.close()
        except Exception as e:
            print(f"Błąd wysyłania do syslog: {e}")
    
    def _send_to_siem(self, anomaly_result: Dict):
        """Wysyła alert do wszystkich zarejestrowanych callbacków SIEM."""
        # Eksport do CEF
        cef_message = self.export_to_cef(anomaly_result)
        
        # Wywołaj wszystkie callbacki
        for callback in self.siem_callbacks:
            try:
                callback(anomaly_result)
            except Exception as e:
                print(f"Błąd w callbacku SIEM: {e}")
        
        # Opcjonalnie wyślij do syslog
        if self.siem_enabled:
            self.export_to_syslog(anomaly_result)
