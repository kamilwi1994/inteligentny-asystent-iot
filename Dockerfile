# Używamy lekkiego obrazu Pythona
FROM python:3.9-slim

# Ustawiamy katalog roboczy
WORKDIR /app

# Instalujemy zależności systemowe potrzebne dla psycopg2
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Kopiujemy plik wymagań
COPY requirements.txt .

# Instalujemy biblioteki Pythona
RUN pip install --no-cache-dir --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org -r requirements.txt

# Kopiujemy resztę kodu aplikacji
COPY . .

# Odkrywamy port, na którym działa Streamlit
EXPOSE 8501

# Komenda startowa:
# 1. Generuje dane testowe (dla pewności, że baza nie jest pusta)
# 2. Uruchamia aplikację
CMD python generuj_dane_demo.py && streamlit run app.py --server.address=0.0.0.0