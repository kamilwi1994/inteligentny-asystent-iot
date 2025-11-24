from urllib.parse import quote_plus

# Wpisz tutaj swój klucz API z Google AI Studio
GOOGLE_API_KEY = "" 

# Dane dostępowe do bazy PostgreSQL (Home Assistant)
DB_USER = "postgres"  
DB_PASSWORD = "" 
DB_HOST = "localhost" 
DB_PORT = "5432"      
DB_NAME = "home_assistant_local" 


encoded_password = quote_plus(DB_PASSWORD)
SCIEZKA_DO_BAZY_DANYCH_HA = f"postgresql+psycopg2://{DB_USER}:{encoded_password}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Słownik mapujący entity_id z Home Assistant na nazwę pomieszczenia.
# Klucz: entity_id (z Home Assistant)
# Wartość: Czytelna nazwa dla Asystenta
CZUJNIKI_TEMPERATURY = {
    # Przykład: "sensor.nazwa_techniczna": "Nazwa Czytelna",
    "sensor.salon_termostat_salon_70": "Salon",
    "sensor.sypialnia_termostat_sypialnia_65": "Sypialnia",
    "sensor.dzieciecy_termostat_dzieciecy_77": "Pokój dziecięcy",
}

CZUJNIKI_ENERGII = {
    "sensor.faza_1_suma_dostarczonej_energii": "Faza 1",
    "sensor.faza_2_suma_dostarczonej_energii": "Faza 2",
    "sensor.faza_3_suma_dostarczonej_energii": "Faza 3",

}
