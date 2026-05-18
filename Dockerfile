FROM python:3.11-slim

# Metadane
LABEL maintainer="LANDaNuM"
LABEL description="Medical Device Security Scanner"

# Zmienne środowiskowe
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/src

WORKDIR /app

# Zależności systemowe (nmap, libusb dla USB)
RUN apt-get update && apt-get install -y --no-install-recommends \
    nmap \
    libusb-1.0-0 \
    libnfc-dev \
    bluetooth \
    bluez \
    && rm -rf /var/lib/apt/lists/*

# Najpierw tylko requirements (cache warstw)
COPY requirements.txt .

# Instaluj bez tensorflow (za duży na podstawowy obraz)
RUN pip install --no-cache-dir -r requirements.txt \
    --ignore-requires-python \
    || pip install --no-cache-dir \
    python-dotenv bleak scapy python-nmap \
    pyusb pyserial pandas numpy scikit-learn \
    streamlit plotly flask flask-cors gunicorn \
    sqlalchemy reportlab matplotlib pydantic \
    rich requests mac-vendor-lookup APScheduler schedule

# Kopiuj kod
COPY src/ ./src/
COPY scripts/ ./scripts/
COPY tests/ ./tests/

# Foldery na dane
RUN mkdir -p data/cache exports reports

# Port dla Flask API i Streamlit
EXPOSE 5000 8501

# Domyślne uruchomienie
CMD ["python", "src/scanner.py", "--help"]
