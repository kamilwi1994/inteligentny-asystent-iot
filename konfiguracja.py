from urllib.parse import quote_plus


GOOGLE_API_KEY = "" 


DB_USER = "postgres"  
DB_PASSWORD = "" 
DB_HOST = "localhost" 
DB_PORT = "5432"      
DB_NAME = "home_assistant_local" 


encoded_password = quote_plus(DB_PASSWORD)
SCIEZKA_DO_BAZY_DANYCH_HA = f"postgresql+psycopg2://{DB_USER}:{encoded_password}@{DB_HOST}:{DB_PORT}/{DB_NAME}"


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