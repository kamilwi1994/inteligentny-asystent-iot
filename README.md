# inteligentny-asystent-iot
Projekt zrealizowany w ramach przedmiotu "Internet Rzeczy". System integruje dane z inteligentnego domu (Home Assistant) z modelem językowym (LLM) przy użyciu architektury RAG (Retrieval-Augmented Generation).
# Wymagania 

*   Python 3.9+
*   Dostęp do bazy danych Home Assistant (PostgreSQL)
*   Klucz API Google (Gemini)

# Instalacja 

1.  **Sklonuj repozytorium:**

    git clone https://github.com/kamilwi1994/inteligentny-asystent-iot.git
    cd inteligentny-asystent-iot

2.  **Zainstaluj wymagane biblioteki:**
    Zalecane jest użycie środowiska wirtualnego.

    pip install -r requirements.txt

3.  **Konfiguracja:**
    Otwórz plik `konfiguracja.py`. Jest to główny plik ustawień projektu. Musisz uzupełnić go o dane swojego środowiska:

    *   **Poświadczenia:**
        *   `GOOGLE_API_KEY`: Twój klucz API z Google AI Studio (potrzebny do modelu Gemini).
        *   `DB_...`: Dane logowania do bazy PostgreSQL, w której Home Assistant zapisuje historię (host, użytkownik, hasło).

    *   **Mapowanie urządzeń (Słowniki):**
        System musi wiedzieć, które encje w Home Assistant odpowiadają za temperaturę i energię. Edytuj słowniki `CZUJNIKI_TEMPERATURY` i `CZUJNIKI_ENERGII`:
        *   **Klucz (lewa strona):** To dokładne `entity_id` z Home Assistanta (np. `sensor.salon_temperature`).
        *   **Wartość (prawa strona):** To przyjazna nazwa, której Asystent będzie używał w rozmowie (np. `"Salon"`, `"Sypialnia rodziców"`).

    Przykład konfiguracji:

    CZUJNIKI_TEMPERATURY = {
        "sensor.termostat_salon_actual_temperature": "Salon",
        "sensor.sypialnia_temp": "Sypialnia",
    }
    
# Uruchomienie

1.  **Uruchom aplikację komendą:**

    streamlit run app.py


2.  Aplikacja automatycznie:
    *   Połączy się z bazą danych.
    *   Pobierze i przetworzy dane historyczne.
    *   Utworzy/zaktualizuje wektorową bazę wiedzy (folder `wektorowa_baza_danych`).
    *   Uruchomi interfejs w przeglądarce (domyślnie `http://localhost:8501`).
