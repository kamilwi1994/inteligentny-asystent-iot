# --- PLIK: silnik_rag.py ---
import os
import pandas as pd
from sqlalchemy import create_engine, text
from datetime import datetime, timedelta
import json
import requests
import warnings
from requests.packages.urllib3.exceptions import InsecureRequestWarning

# --- FIX SSL ---
warnings.simplefilter('ignore', InsecureRequestWarning)
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
os.environ['CURL_CA_BUNDLE'] = ''
os.environ['PYTHONHTTPSVERIFY'] = '0'
old_request = requests.Session.request
def new_request(self, method, url, *args, **kwargs):
    kwargs['verify'] = False
    return old_request(self, method, url, *args, **kwargs)
requests.Session.request = new_request
# ----------------

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

    try:
        engine = create_engine(cfg.SCIEZKA_DO_BAZY_DANYCH_HA, json_serializer=lambda obj: obj, json_deserializer=lambda x: x)
    except Exception as e:
        print(f"Błąd inicjalizacji silnika DB: {e}")
        return False
    
    # Pobieramy 30 dni
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    
    wszystkie_encje = list(cfg.CZUJNIKI_TEMPERATURY.keys()) + list(cfg.CZUJNIKI_ENERGII.keys())
    if not wszystkie_encje: return False

    placeholders = ', '.join([f"'{e}'" for e in wszystkie_encje])

    query = text(f"""
        SELECT 
            sm.entity_id, 
            s.state, 
            s.last_updated_ts
        FROM states s
        JOIN states_meta sm ON s.metadata_id = sm.metadata_id
        WHERE 
            sm.entity_id IN ({placeholders})
            AND s.last_updated_ts BETWEEN {start_date.timestamp()} AND {end_date.timestamp()}
            AND s.state IS NOT NULL
    """)

    try:
        with engine.connect() as connection:
            df = pd.read_sql(query, connection)
    except Exception as e:
        print(f"Błąd DB: {e}")
        return False

    if df.empty: return False
        
    df['last_updated'] = pd.to_datetime(df['last_updated_ts'], unit='s')
    df['date'] = df['last_updated'].dt.date

    # Przetwarzanie
    df_temp = df[df['entity_id'].isin(cfg.CZUJNIKI_TEMPERATURY.keys())].copy()
    df_temp["temperature"] = pd.to_numeric(df_temp["state"], errors='coerce')
    df_temp.dropna(subset=["temperature"], inplace=True)

    df_energy = df[df['entity_id'].isin(cfg.CZUJNIKI_ENERGII.keys())].copy()
    df_energy['state'] = pd.to_numeric(df_energy['state'], errors='coerce')

    unique_dates = pd.to_datetime(df['date'].unique()).sort_values()
    print(f"Generuję raporty dla {len(unique_dates)} dni...")

    for date in unique_dates:
        raport_date = date.date()
        file_path = os.path.join(DATA_DIR, f"raport_{raport_date.strftime('%Y-%m-%d')}.txt")
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(f"Raport dzienny: {raport_date}\n\n")
            
            # 1. TEMPERATURY 
            f.write("=== TEMPERATURY (Co godzinę) ===\n")
            temp_group = df_temp[df_temp['date'] == raport_date]
            
            if not temp_group.empty:
                for entity_id, group in temp_group.groupby('entity_id'):
                    nazwa = cfg.CZUJNIKI_TEMPERATURY.get(entity_id, entity_id)
                    f.write(f"\n[Pokój: {nazwa}]\n")
                    logs = group.sort_values('last_updated')
                    for _, row in logs.iterrows():
                        godzina = row['last_updated'].strftime('%H:%M')
                        temp = row['temperature']
                        f.write(f" - {godzina}: {temp:.1f}°C\n")

            # 2. ENERGIA 
            f.write("\n=== ZUŻYCIE ENERGII ===\n")
            energy_group = df_energy[df_energy['date'] == raport_date]
            total_today = 0
            
            if not energy_group.empty:
                for entity_id, group in energy_group.groupby('entity_id'):
                    nazwa = cfg.CZUJNIKI_ENERGII.get(entity_id, entity_id)
                    f.write(f"\n[Licznik: {nazwa}]\n")
                    
                    logs = group.sort_values('last_updated')
                    logs['consumption'] = logs['state'].diff()
                    
                    for _, row in logs.iterrows():
                        if pd.isna(row['consumption']): continue
                        if row['consumption'] > 0.001:
                            godzina = row['last_updated'].strftime('%H:%M')
                            kwh = row['consumption']
                            f.write(f" - {godzina}: {kwh:.2f} kWh\n")
                            total_today += kwh
            
            f.write(f"\nCAŁKOWITE ZUŻYCIE DNIA: {total_today:.2f} kWh\n")
    
    return True

def stworz_i_zapisz_baze_wektorowa():
    print("Indeksowanie danych...")
    docs = []
    if os.path.exists('baza_wiedzy/'):
        docs.extend(DirectoryLoader('baza_wiedzy/', glob="**/*.txt", loader_cls=TextLoader, loader_kwargs={'encoding': 'utf-8'}).load())
    docs.extend(DirectoryLoader(DATA_DIR, glob="**/*.txt", loader_cls=TextLoader, loader_kwargs={'encoding': 'utf-8'}).load())
    
    if not docs: return None

    splits = RecursiveCharacterTextSplitter(chunk_size=4000, chunk_overlap=200).split_documents(docs)
    
    embedding_model = GoogleGenerativeAIEmbeddings(
        model="models/embedding-001", 
        google_api_key=cfg.GOOGLE_API_KEY,
        transport="rest",
        client_options={"api_endpoint": "generativelanguage.googleapis.com"}
    )
    return Chroma.from_documents(documents=splits, embedding=embedding_model, persist_directory=DB_DIR)

def get_rag_chain():
    if os.path.exists(DB_DIR):
        import shutil
        try: shutil.rmtree(DB_DIR)
        except: pass

    przygotuj_dane_z_ha()
    stworz_i_zapisz_baze_wektorowa()

    embedding_model = GoogleGenerativeAIEmbeddings(
        model="models/embedding-001", 
        google_api_key=cfg.GOOGLE_API_KEY,
        transport="rest",
        client_options={"api_endpoint": "generativelanguage.googleapis.com"}
    )
    vectorstore = Chroma(persist_directory=DB_DIR, embedding_function=embedding_model)
    
    # Pobieramy 40 dokumentów (dni)
    retriever = vectorstore.as_retriever(search_kwargs={"k": 40}) 

    
    template = """Jesteś ekspertem analizy danych.
Masz dostęp do raportów z wielu dni (każdy dokument to jeden dzień).
Jeśli pytam o średnią, zsumuj wartości z dostępnych dni i podziel przez liczbę dni.

Kontekst:
{context}

Pytanie: {question}
"""
    prompt = ChatPromptTemplate.from_template(template)
    
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash-001", 
        temperature=0, 
        google_api_key=cfg.GOOGLE_API_KEY,
        transport="rest",
        client_options={"api_endpoint": "generativelanguage.googleapis.com"}
    )

    return ({"context": retriever | (lambda docs: "\n\n".join(d.page_content for d in docs)), "question": RunnablePassthrough()} | prompt | llm | StrOutputParser())