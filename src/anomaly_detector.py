#!/usr/bin/env python3
"""
Anomaly detection for medical devices using Machine Learning.

Uses ML to detect atypical devices based on: security score, vulnerability count,
encryption type, protocol, and other security features.

Algorithms: Isolation Forest, LOF, One-Class SVM, Autoencoder (DL), Random Forest,
KMeans/DBSCAN. Features: real-time streaming detection, vulnerability prediction,
clustering by security similarity, SIEM integration (CEF, syslog, callbacks).
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

try:
    import os
    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
    os.environ['TF_FORCE_GPU_ALLOW_GROWTH'] = 'true'
    os.environ['CUDA_VISIBLE_DEVICES'] = ''
    import tensorflow as tf
    try:
        tf.config.set_visible_devices([], 'GPU')
        tf.config.threading.set_inter_op_parallelism_threads(1)
        tf.config.threading.set_intra_op_parallelism_threads(1)
    except Exception:
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
    """ML-based anomaly detection for medical devices (unusual security score, vulnerability count, encryption, protocol)."""
    
    def __init__(self, contamination: float = 0.1):
        """Initialize detector. contamination: expected fraction of anomalies (0.0-0.5)."""
        if not SKLEARN_AVAILABLE:
            raise ImportError("scikit-learn is not installed. Install: pip install scikit-learn")
        
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
        
        self.trained = False
        self.model_dir = Path(__file__).parent.parent / "data" / "models"
        self.model_dir.mkdir(parents=True, exist_ok=True)
        
        self.streaming_buffer = deque(maxlen=100)
        self.streaming_lock = threading.Lock()
        
        self.autoencoder = None
        self.use_deep_learning = False
        
        self.vulnerability_predictor = None
        self.vulnerability_trained = False
        
        self.clusterer = None
        self.clusters_trained = False
        
        # SIEM integration
        self.siem_enabled = False
        self.siem_callbacks: List[Callable] = []
    
    def extract_features(self, devices: List[Device]) -> np.ndarray:
        """Extract numeric feature vector from devices (security score, vuln count, encryption, protocol, device type, RSSI, open ports, enc strength). Returns (n_samples, n_features)."""
        features = []
        
        for device in devices:
            feature_vector = []
            
            # 1. Security score
            feature_vector.append(device.security_score)
            
            feature_vector.append(len(device.vulnerabilities))
            feature_vector.append(1 if device.has_encryption else 0)
            
            feature_vector.append(1 if device.requires_pairing else 0)
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
            
            if device.rssi is not None:
                normalized_rssi = (device.rssi + 100) / 100
                feature_vector.append(max(0, min(1, normalized_rssi)))
            else:
                feature_vector.append(0.5)
            open_ports = device.metadata.get('open_ports', [])
            feature_vector.append(len(open_ports))
            
            enc_analysis = device.metadata.get('encryption_analysis', {})
            if enc_analysis:
                feature_vector.append(enc_analysis.get('score', 0))
            else:
                feature_vector.append(50 if device.has_encryption else 0)
            
            features.append(feature_vector)
        
        return np.array(features)
    
    def train(self, devices: List[Device]) -> Dict:
        """Train ML models on historical device data. Returns dict with training stats."""
        if len(devices) < 2:
            return {
                'trained': False,
                'reason': 'Insufficient data (minimum 2 devices)',
                'devices_count': len(devices)
            }
        X = self.extract_features(devices)
        X_scaled = self.scaler.fit_transform(X)
        n_neighbors_lof = max(1, min(20, len(devices) - 1))
        self.lof.set_params(n_neighbors=n_neighbors_lof)
        
        self.isolation_forest.fit(X_scaled)
        self.lof.fit(X_scaled)
        self.one_class_svm.fit(X_scaled)
        
        self.trained = True
        
        self.save_model()
        
        return {
            'trained': True,
            'devices_count': len(devices),
            'features_count': X.shape[1],
            'contamination': self.contamination
        }
    
    def detect_anomalies(self, devices: List[Device], use_ensemble: bool = True) -> List[Dict]:
        """Detect anomalies. Returns list of dicts: device, is_anomaly, anomaly_score, method, reason."""
        if not devices:
            return []
        if not self.trained:
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
        X = self.extract_features(devices)
        X_scaled = self.scaler.transform(X)
        if_anomalies = self.isolation_forest.predict(X_scaled)
        if_scores = -self.isolation_forest.score_samples(X_scaled)
        
        lof_anomalies = self.lof.predict(X_scaled)
        lof_scores = -self.lof.score_samples(X_scaled)
        
        svm_anomalies = self.one_class_svm.predict(X_scaled)
        svm_scores = -self.one_class_svm.score_samples(X_scaled)
        
        results = []
        for i, device in enumerate(devices):
            if_anomaly = if_anomalies[i] == -1
            lof_anomaly = lof_anomalies[i] == -1
            svm_anomaly = svm_anomalies[i] == -1
            if use_ensemble:
                is_anomaly = sum([if_anomaly, lof_anomaly, svm_anomaly]) >= 2
                method = 'ensemble'
                anomaly_score = np.mean([if_scores[i], lof_scores[i], svm_scores[i]])
                reasons = []
                if if_anomaly:
                    reasons.append("Isolation Forest")
                if lof_anomaly:
                    reasons.append("LOF")
                if svm_anomaly:
                    reasons.append("One-Class SVM")
                reason = f"Detected by: {', '.join(reasons)}" if reasons else "Normal"
            else:
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
        """Save trained model to file."""
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
            print(f"Error saving model: {e}")
    
    def load_model(self) -> bool:
        """Load trained model from file. Returns True if loaded, False otherwise."""
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
            print(f"Error loading model: {e}")
            return False
    
    def get_anomaly_statistics(self, results: List[Dict]) -> Dict:
        """Compute statistics for detected anomalies (from detect_anomalies() results)."""
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
        """Detect anomalies in real time for a single device (streaming). Returns dict: device, is_anomaly, anomaly_score, method, reason, timestamp."""
        if not self.trained:
            is_anomaly = device.security_score < 30 or len(device.vulnerabilities) > 5
            return {
                'device': device,
                'is_anomaly': is_anomaly,
                'anomaly_score': 1.0 - (device.security_score / 100),
                'method': 'heuristic',
                'reason': 'Low security score or many vulnerabilities' if is_anomaly else 'Normal',
                'timestamp': datetime.now().isoformat()
            }
        X = self.extract_features([device])
        X_scaled = self.scaler.transform(X)
        if_anomaly = self.isolation_forest.predict(X_scaled)[0] == -1
        if_score = -self.isolation_forest.score_samples(X_scaled)[0]
        
        lof_anomaly = self.lof.predict(X_scaled)[0] == -1
        lof_score = -self.lof.score_samples(X_scaled)[0]
        
        svm_anomaly = self.one_class_svm.predict(X_scaled)[0] == -1
        svm_score = -self.one_class_svm.score_samples(X_scaled)[0]
        
        # Ensemble voting
        is_anomaly = sum([if_anomaly, lof_anomaly, svm_anomaly]) >= 2
        anomaly_score = np.mean([if_score, lof_score, svm_score])
        
        if self.use_deep_learning and self.autoencoder is not None:
            try:
                reconstruction_error = self.autoencoder.predict(X_scaled, verbose=0)
                mse = np.mean(np.power(X_scaled - reconstruction_error, 2))
                if mse > 0.5:
                    is_anomaly = True
                    anomaly_score = max(anomaly_score, mse)
            except Exception:
                pass
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
        
        if is_anomaly and self.siem_enabled:
            self._send_to_siem(result)
        
        return result
    
    def train_deep_learning(self, devices: List[Device], epochs: int = 50) -> Dict:
        """Train Autoencoder (Deep Learning) for anomaly detection. Returns training stats dict."""
        if not TENSORFLOW_AVAILABLE:
            return {
                'trained': False,
                'reason': 'TensorFlow is not installed. Install: pip install tensorflow'
            }
        if len(devices) < 2:
            return {
                'trained': False,
                'reason': 'Insufficient data (minimum 2 devices for DL)',
                'devices_count': len(devices)
            }
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
        
        batch_size = min(32, max(1, len(devices)))
        validation_split = min(0.2, 0.5 - 0.5 / max(1, len(devices))) if len(devices) > 1 else 0.0
        
        history = self.autoencoder.fit(
            X_scaled, X_scaled,
            epochs=epochs,
            batch_size=batch_size,
            validation_split=validation_split,
            verbose=0
        )
        
        self.use_deep_learning = True
        try:
            autoencoder_path = self.model_dir / "autoencoder.h5"
            self.autoencoder.save(str(autoencoder_path))
        except Exception as e:
            print(f"Error saving autoencoder: {e}")
        
        return {
            'trained': True,
            'devices_count': len(devices),
            'epochs': epochs,
            'final_loss': float(history.history['loss'][-1])
        }
    
    def load_deep_learning(self) -> bool:
        """Load trained Autoencoder from disk."""
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
            print(f"Error loading autoencoder: {e}")
            return False
    
    def train_vulnerability_predictor(self, devices: List[Device]) -> Dict:
        """Train model to predict future vulnerabilities from current security features. Returns training stats dict."""
        if len(devices) < 2:
            return {
                'trained': False,
                'reason': 'Insufficient data (minimum 2 devices)',
                'devices_count': len(devices)
            }
        X = self.extract_features(devices)
        X_scaled = self.scaler.fit_transform(X)
        y = np.array([1 if len(d.vulnerabilities) > 0 else 0 for d in devices])
        self.vulnerability_predictor = RandomForestClassifier(
            n_estimators=100,
            random_state=42,
            max_depth=10
        )
        self.vulnerability_predictor.fit(X_scaled, y)
        
        self.vulnerability_trained = True
        try:
            predictor_path = self.model_dir / "vulnerability_predictor.pkl"
            with open(predictor_path, 'wb') as f:
                pickle.dump(self.vulnerability_predictor, f)
        except Exception as e:
            print(f"Error saving predictor: {e}")
        
        accuracy = self.vulnerability_predictor.score(X_scaled, y)
        
        return {
            'trained': True,
            'devices_count': len(devices),
            'accuracy': float(accuracy)
        }
    
    def predict_vulnerability(self, device: Device) -> Dict:
        """Predict probability of future vulnerabilities. Returns dict: probability, risk_level, recommendations."""
        if not self.vulnerability_trained:
            return {
                'probability': 0.5,
                'risk_level': 'unknown',
                'recommendations': ['Model is not trained']
            }
        
        X = self.extract_features([device])
        X_scaled = self.scaler.transform(X)
        
        probability = self.vulnerability_predictor.predict_proba(X_scaled)[0][1]
        
        if probability < 0.3:
            risk_level = 'low'
            recommendations = [
                'Device has low vulnerability risk',
                'Continue regular scanning'
            ]
        elif probability < 0.7:
            risk_level = 'medium'
            recommendations = [
                'Device has medium vulnerability risk',
                'Increase scan frequency',
                'Consider software update'
            ]
        else:
            risk_level = 'high'
            recommendations = [
                'Device has high vulnerability risk',
                'Immediate update required',
                'Consider disconnecting from network until fixed',
                'Scan daily'
            ]
        
        return {
            'probability': float(probability),
            'risk_level': risk_level,
            'recommendations': recommendations
        }
    
    def cluster_devices(self, devices: List[Device], n_clusters: int = 5, method: str = 'kmeans') -> List[Dict]:
        """Cluster devices by security similarity. Returns list of dicts: device, cluster, cluster_name."""
        if len(devices) < 1:
            return []
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
        """Enable or disable SIEM integration."""
        self.siem_enabled = enabled
    
    def add_siem_callback(self, callback: Callable[[Dict], None]):
        """Add callback to send alerts to SIEM (function receives alert dict)."""
        self.siem_callbacks.append(callback)
    
    def export_to_cef(self, anomaly_result: Dict) -> str:
        """Export anomaly result to CEF (Common Event Format). Returns CEF string."""
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
        """Send alert to syslog server (host, port)."""
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
            print(f"Error sending to syslog: {e}")
    
    def _send_to_siem(self, anomaly_result: Dict):
        """Send alert to all registered SIEM callbacks and optionally to syslog."""
        cef_message = self.export_to_cef(anomaly_result)
        for callback in self.siem_callbacks:
            try:
                callback(anomaly_result)
            except Exception as e:
                print(f"Error in SIEM callback: {e}")
        if self.siem_enabled:
            self.export_to_syslog(anomaly_result)
