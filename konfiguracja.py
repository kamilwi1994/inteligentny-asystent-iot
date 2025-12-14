# --- PLIK: konfiguracja.py ---
import os
from urllib.parse import quote_plus

# Pobieramy klucz z systemu (Docker) lub używamy domyślnego (lokalnie)
# UWAGA: Profesor wpisze swój klucz w docker-compose lub pliku .env,
# ale zostawiamy pusty string jako fallback.
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "TU_WPISZ_SWOJ_KLUCZ_JESLI_URUCHAMIASZ_LOKALNIE")

# Konfiguracja bazy danych
# W Dockerze host to nazwa serwisu z docker-compose, czyli "db"
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")
DB_HOST = os.getenv("DB_HOST", "localhost") # Domyślnie localhost, w dockerze nadpiszemy na 'db'
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "home_assistant_local")

encoded_password = quote_plus(DB_PASSWORD)
SCIEZKA_DO_BAZY_DANYCH_HA = f"postgresql+psycopg2://{DB_USER}:{encoded_password}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Słowniki mapujące techniczne ID na ludzkie nazwy
# Te ID muszą się zgadzać z tym, co wygenerujemy w skrypcie demo
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