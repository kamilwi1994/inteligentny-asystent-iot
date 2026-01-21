import pandas as pd
from sqlalchemy import create_engine, text
import konfiguracja as cfg
import random
from datetime import datetime, timedelta
import time
import math

def stworz_strukture_tabel(engine):
    with engine.connect() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS states_meta (
                metadata_id SERIAL PRIMARY KEY,
                entity_id VARCHAR(255) UNIQUE
            );
        """))
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS states (
                state_id SERIAL PRIMARY KEY,
                metadata_id INTEGER REFERENCES states_meta(metadata_id),
                state VARCHAR(255),
                attributes JSONB,
                event_id SMALLINT,
                last_changed_ts FLOAT,
                last_updated_ts FLOAT,
                old_state_id INTEGER
            );
        """))
        conn.commit()
    print(" Struktura tabel gotowa.")

def generuj_dane():
    print("Generowanie SZCZEGÓŁOWYCH danych godzinowych (30 DNI)...")
    
    max_retries = 10
    for i in range(max_retries):
        try:
            engine = create_engine(cfg.SCIEZKA_DO_BAZY_DANYCH_HA)
            stworz_strukture_tabel(engine)
            break
        except Exception as e:
            print(f"Oczekiwanie na bazę ({i+1}/{max_retries})...")
            time.sleep(3)
    else:
        print("Nie udało się połączyć z bazą.")
        return

    # Metadata
    wszystkie_czujniki = {**cfg.CZUJNIKI_TEMPERATURY, **cfg.CZUJNIKI_ENERGII}
    meta_map = {}

    with engine.connect() as conn:
        for entity_id in wszystkie_czujniki.keys():
            res = conn.execute(text("SELECT metadata_id FROM states_meta WHERE entity_id = :eid"), {"eid": entity_id}).fetchone()
            if res:
                meta_map[entity_id] = res[0]
            else:
                res = conn.execute(text("INSERT INTO states_meta (entity_id) VALUES (:eid) RETURNING metadata_id"), {"eid": entity_id}).fetchone()
                meta_map[entity_id] = res[0]
                conn.commit()
    
    # Generujemy dane z 30 dni 
    end_date = datetime.now()
    start_date = end_date - timedelta(days=cfg.HISTORY_DAYS) 
    
    records = []
    energy_counters = {k: random.uniform(1000, 5000) for k in cfg.CZUJNIKI_ENERGII}

    current_date = start_date
    while current_date <= end_date:
        timestamp = current_date.timestamp()
        hour = current_date.hour
        
        # Temp
        for entity_id in cfg.CZUJNIKI_TEMPERATURY:
            if 6 <= hour < 23: target_temp = 21.5
            else: target_temp = 18.0
            
            temp = target_temp + random.uniform(-0.3, 0.3)
            variation = math.sin((hour / 24) * 2 * math.pi) * 0.5
            temp += variation

            records.append({
                "metadata_id": meta_map[entity_id],
                "state": f"{temp:.2f}",
                "attributes": '{"unit_of_measurement": "°C"}',
                "last_updated_ts": timestamp
            })

        # Energia
        for entity_id in cfg.CZUJNIKI_ENERGII:
            increment = random.uniform(0.1, 0.3)
            if 17 <= hour <= 22: increment *= 3 
            if 0 <= hour <= 5: increment *= 0.1
            
            energy_counters[entity_id] += increment
            records.append({
                "metadata_id": meta_map[entity_id],
                "state": f"{energy_counters[entity_id]:.2f}",
                "attributes": '{"unit_of_measurement": "kWh"}',
                "last_updated_ts": timestamp
            })

        current_date += timedelta(hours=1)

    if records:
        with engine.connect() as conn:
            conn.execute(text("TRUNCATE TABLE states"))
            conn.commit()
            
        df = pd.DataFrame(records)
        df.to_sql("states", engine, if_exists="append", index=False)
        print(f"Wygenerowano {len(records)} rekordów (30 dni).")
    else:
        print("Błąd generowania.")

if __name__ == "__main__":
    generuj_dane()