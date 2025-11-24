
import os
import pandas as pd
from sqlalchemy import create_engine, text
from datetime import datetime, timedelta
import json

from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

import konfiguracja as cfg

DB_DIR = "wektorowa_baza_danych"
DATA_DIR = "dane_z_ha"

def przygotuj_dane_z_ha():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

    engine = create_engine(cfg.SCIEZKA_DO_BAZY_DANYCH_HA, json_serializer=lambda obj: obj, json_deserializer=lambda x: x)
    
    end_date = datetime.now()

    start_date = end_date - timedelta(days=365)
    
    wszystkie_encje = list(cfg.CZUJNIKI_TEMPERATURY.keys()) + list(cfg.CZUJNIKI_ENERGII.keys())
    placeholders = ', '.join([f"'{e}'" for e in wszystkie_encje])


    query = text(f"""
        SELECT 
            sm.entity_id, 
            s.state, 
            s.attributes,
            s.last_updated_ts
        FROM states s
        JOIN states_meta sm ON s.metadata_id = sm.metadata_id
        WHERE 
            sm.entity_id IN ({placeholders})
            AND s.last_updated_ts BETWEEN {start_date.timestamp()} AND {end_date.timestamp()}
            AND s.state IS NOT NULL AND s.state NOT IN ('unknown', 'unavailable')
    """)

    try:
        with engine.connect() as connection:
            df = pd.read_sql(query, connection)
    except Exception as e:
        print(f"Błąd podczas połączenia z bazą danych: {e}")
        return False

    if df.empty:
        print("Nie znaleziono danych dla podanych encji w zadanym okresie.")
        return False
        
    df['last_updated'] = pd.to_datetime(df['last_updated_ts'], unit='s')
    df['date'] = df['last_updated'].dt.date

    df_temp = df[df['entity_id'].isin(cfg.CZUJNIKI_TEMPERATURY.keys())].copy()
    
    def extract_temperature(row):
        try:
            return float(row["state"])
        except:
            pass

        attr = row["attributes"]
        try:
            if isinstance(attr, str):
                attr = json.loads(attr)
            if isinstance(attr, dict):
                if "current_temperature" in attr:
                    return float(attr["current_temperature"])
                if "temperature" in attr:
                    return float(attr["temperature"])
        except:
            pass

        return None

    df_temp["temperature"] = df_temp.apply(extract_temperature, axis=1)
    df_temp.dropna(subset=["temperature"], inplace=True)
    df_temp["temperature"] = pd.to_numeric(df_temp["temperature"])

    df_energy = df[df['entity_id'].isin(cfg.CZUJNIKI_ENERGII.keys())].copy()
    df_energy['state'] = pd.to_numeric(df_energy['state'], errors='coerce')
    df_energy.dropna(subset=['state'], inplace=True)

    for date in pd.to_datetime(df['date'].unique()).sort_values():
        raport_date = date.date()
        file_path = os.path.join(DATA_DIR, f"raport_{raport_date.strftime('%Y-%m-%d')}.txt")
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(f"Raport dzienny dla daty: {raport_date.strftime('%Y-%m-%d')}\n\n")
            
            f.write("Podsumowanie temperatur:\n")
            temp_group = df_temp[df_temp['date'] == raport_date]
            if not temp_group.empty:
                for entity_id, group in temp_group.groupby('entity_id'):
                    nazwa_pokoju = cfg.CZUJNIKI_TEMPERATURY.get(entity_id, "Nieznany pokój")
                    f.write(f"- {nazwa_pokoju}: Średnia {group['temperature'].mean():.1f}°C, Min {group['temperature'].min():.1f}°C, Max {group['temperature'].max():.1f}°C\n")
            else:
                f.write("- Brak danych o temperaturze dla tego dnia.\n")

            f.write("\nPodsumowanie zużycia energii:\n")
            total_energy_today = 0
            for entity_id in cfg.CZUJNIKI_ENERGII.keys():
                energy_entity_data = df_energy[df_energy['entity_id'] == entity_id].sort_values('last_updated')
                today_data = energy_entity_data[energy_entity_data['date'] == raport_date]
                prev_day_data = energy_entity_data[energy_entity_data['date'] == (raport_date - timedelta(days=1))]

                if not today_data.empty:
                    last_reading_today = today_data['state'].iloc[-1]
                    last_reading_prev_day = 0
                    if not prev_day_data.empty: last_reading_prev_day = prev_day_data['state'].iloc[-1]
                    daily_consumption = last_reading_today - last_reading_prev_day
                    if daily_consumption < 0: daily_consumption = last_reading_today
                    
                    nazwa_fazy = cfg.CZUJNIKI_ENERGII.get(entity_id, "Nieznana faza")
                    f.write(f"- {nazwa_fazy}: {daily_consumption:.2f} kWh\n")
                    total_energy_today += daily_consumption
            
            if total_energy_today > 0:
                f.write(f"\nCałkowite zużycie energii w tym dniu: {total_energy_today:.2f} kWh\n")
            else:
                f.write("- Brak danych o zużyciu energii dla tego dnia.\n")
    
    print(f"Pomyślnie przetworzono i zapisano dane z HA w folderze '{DATA_DIR}'.")
    return True

def stworz_i_zapisz_baze_wektorowa():
    print("Tworzenie bazy wektorowej...")
    docs = DirectoryLoader('baza_wiedzy/', glob="**/*.txt", loader_cls=TextLoader, loader_kwargs={'encoding': 'utf-8'}).load()
    docs.extend(DirectoryLoader(DATA_DIR, glob="**/*.txt", loader_cls=TextLoader, loader_kwargs={'encoding': 'utf-8'}).load())
    splits = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200).split_documents(docs)
    embedding_model = GoogleGenerativeAIEmbeddings(model="models/embedding-001", google_api_key=cfg.GOOGLE_API_KEY)
    vectorstore = Chroma.from_documents(documents=splits, embedding=embedding_model, persist_directory=DB_DIR)
    print(f"Baza wektorowa została pomyślnie utworzona i zapisana w folderze '{DB_DIR}'.")
    return vectorstore

def get_rag_chain():
    if os.path.exists(DB_DIR):
        import shutil
        shutil.rmtree(DB_DIR)
        print("Usunięto starą bazę wektorową.")

    if not przygotuj_dane_z_ha():
        print("Nie udało się przygotować danych z HA. Baza wektorowa nie zostanie utworzona.")
        return None
    stworz_i_zapisz_baze_wektorowa()

    embedding_model = GoogleGenerativeAIEmbeddings(model="models/embedding-001", google_api_key=cfg.GOOGLE_API_KEY)
    vectorstore = Chroma(persist_directory=DB_DIR, embedding_function=embedding_model)
    retriever = vectorstore.as_retriever(search_kwargs={"k": 20})
    
    template = """Jesteś inteligentnym asystentem domu. Twoim zadaniem jest odpowiadać na pytania użytkownika na podstawie dostarczonych danych z systemu smart home.
Odpowiadaj rzeczowo, uprzejmie i po polsku. Analizuj dane, porównuj je i wyciągaj wnioski.

Kontekst:
{context}

Pytanie: {question}
"""
    prompt = ChatPromptTemplate.from_template(template)
    llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash-001", temperature=0, google_api_key=cfg.GOOGLE_API_KEY)

    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)

    rag_chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )
    
    return rag_chain