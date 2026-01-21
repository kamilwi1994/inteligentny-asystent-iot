import os
from urllib.parse import quote_plus

# --- USTAWIENIALLM ---
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://ollama:11434")
MODEL_CHAT = os.getenv("OLLAMA_MODEL", "llama3.2")
MODEL_EMBED = os.getenv("OLLAMA_EMBED_MODEL", "nomic-embed-text")

# --- USTAWIENIA RAG ---
# Domyślnie 30 dni historii i k=3 dla wydajności CPU
HISTORY_DAYS = int(os.getenv("HISTORY_DAYS", 30))
RAG_K_RETRIEVAL = int(os.getenv("RAG_K_RETRIEVAL", 3))

# --- USTAWIENIA BAZY DANYCH ---
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "home_assistant_local")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "password123")

encoded_password = quote_plus(DB_PASSWORD)
SCIEZKA_DO_BAZY_DANYCH_HA = f"postgresql+psycopg2://{DB_USER}:{encoded_password}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# --- MAPOWANIE CZUJNIKÓW ---
CZUJNIKI_TEMPERATURY = {
    "sensor.salon_termostat_salon_70": "Salon",
    "sensor.sypialnia_termostat_sypialnia_65": "Sypialnia",
    "sensor.dzieciecy_termostat_dzieciecy_77": "Pokój dziecięcy",
}

CZUJNIKI_ENERGII = {
    "sensor.faza_1_suma_dostarczonej_energii": "Faza 1",
    "sensor.faza_2_suma_dostarczonej_energii": "Faza 2",
    "sensor.faza_3_suma_dostarczonej_energii": "Faza 3",
}