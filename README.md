# Inteligentny Asystent IoT (RAG + Home Assistant)

Projekt realizowany w ramach przedmiotu "Internet Rzeczy". System integruje dane z inteligentnego domu (Home Assistant) z modelem językowym (LLM) przy użyciu architektury **RAG (Retrieval-Augmented Generation)**. Aplikacja pozwala na rozmowę z asystentem o temperaturze i zużyciu energii w domu, analizując historyczne dane.

---

## 📋 Spis treści

1. [Wymagania](#wymagania)
2. [Szybki start (Docker) - Zalecane](#szybki-start-docker)
3. [Jak to działa? (Symulacja Danych)](#jak-to-działa-symulacja-danych)
4. [Konfiguracja i Mapowanie Urządzeń](#konfiguracja-i-mapowanie-urządzeń)
5. [Przełączenie na tryb Produkcyjny](#przełączenie-na-tryb-produkcyjny)
6. [Rozwiązywanie problemów](#rozwiązywanie-problemów-technicznych)

---

## 🛠 Wymagania

*   **Docker** oraz **Docker Compose** (do uruchomienia skonteneryzowanego środowiska).
*   **Klucz API Google (Gemini)** – darmowy klucz można wygenerować w [Google AI Studio](https://aistudio.google.com/).

> **Uwaga:** Projekt nie wymaga posiadania własnej instalacji Home Assistant. System automatycznie stawia kontener z bazą danych i generuje dane demonstracyjne.

---

## 🚀 Szybki start (Docker)

To zalecana metoda uruchomienia, nie wymaga instalowania Pythona ani bazy PostgreSQL lokalnie na komputerze.

### Krok 1: Pobierz projekt
```bash
git clone https://github.com/kamilwi1994/inteligentny-asystent-iot.git
cd inteligentny-asystent-iot
```
### Krok 2: Ustaw Klucz API
Musisz przekazać swój klucz API Google do kontenera. Najbezpieczniej zrobić to poprzez zmienną środowiskową w terminalu przed uruchomieniem.
Linux / macOS:

```Bash
export GOOGLE_API_KEY="TWOJ_KLUCZ_TUTAJ"
```
Windows (PowerShell):

```Powershell
$env:GOOGLE_API_KEY="TWOJ_KLUCZ_TUTAJ"
```
(Alternatywnie możesz wpisać klucz na sztywno w pliku docker-compose.yml w sekcji environment, ale pamiętaj, by nie commitować go do repozytorium).

### Krok 3: Uruchom kontenery
Wpisz w terminalu:

```Bash
docker-compose up --build
```
System wykona następujące czynności:
Pobierze obraz bazy danych PostgreSQL.
Zbuduje obraz aplikacji (instalując biblioteki).
Uruchomi skrypt generuj_dane_demo.py, który wypełni bazę danymi z ostatnich 30 dni (symulując zmiany temperatur dzień/noc oraz zużycie energii).
Uruchomi aplikację Streamlit.

### Krok 4: Otwórz aplikację
Wejdź w przeglądarce na adres:

👉 http://localhost:8501

🧠 Jak to działa? (Symulacja Danych)
Aby umożliwić sprawdzenie projektu bez dostępu do fizycznego domu studenta, zaimplementowano mechanizm symulacji (generuj_dane_demo.py).

Symulacja Bazy HA: Przy starcie kontenera tworzona jest struktura tabel identyczna jak w Home Assistant (states, states_meta).

Generowanie Danych: Skrypt generuje historyczne odczyty dla ostatnich 30 dni:

Temperatury: Symuluje cykl dobowy (cieplej w dzień, chłodniej w nocy) oraz bezwładność cieplną.

Energia: Symuluje przyrosty licznika ze szczytami zużycia w godzinach wieczornych (18:00 - 22:00).

Silnik RAG (silnik_rag.py): Pobiera dane z SQL. Agreguje je do szczegółowych raportów tekstowych (z dokładnością co godzinę).

Tworzy wektorową bazę wiedzy, którą przeszukuje model AI (Gemini) w celu udzielenia odpowiedzi.
⚙️ Konfiguracja i Mapowanie Urządzeń
W pliku konfiguracja.py znajdują się słowniki mapujące techniczne identyfikatory sensorów na nazwy zrozumiałe dla człowieka.
Po co to edytujemy?
Home Assistant używa ID typu sensor.salon_t1_v2. Asystent AI musi wiedzieć, że to po prostu "Salon".

Python

## Przykład z pliku konfiguracja.py
```
CZUJNIKI_TEMPERATURY = {
    "sensor.salon_termostat_salon_70": "Salon",       # <-- Klucz: ID z bazy
    "sensor.sypialnia_termostat_sypialnia_65": "Sypialnia", # <-- Wartość: Nazwa dla AI
}
```
W trybie demo (Docker) te ID są już skonfigurowane i zgodne z generatorem danych.

## 🏭 Przełączenie na tryb Produkcyjny

Aby podłączyć aplikację do prawdziwej instalacji Home Assistant:

Otwórz docker-compose.yml.

Zmień dane logowania do bazy danych (DB_HOST, DB_USER, DB_PASSWORD) na adres Twojego prawdziwego serwera PostgreSQL (gdzie Home Assistant trzyma historię).

Edytuj konfiguracja.py:

Wpisz prawdziwe entity_id swoich czujników w słownikach CZUJNIKI_TEMPERATURY i CZUJNIKI_ENERGII.

Uruchom aplikację. Skrypt wykryje, że baza istnieje i pominie generowanie danych demo, a zamiast tego przeanalizuje Twoje prawdziwe dane.

🔧 Rozwiązywanie problemów technicznych
"SSL: CERTIFICATE_VERIFY_FAILED"
Projekt zawiera specjalny mechanizm ("Monkey Patch") w pliku silnik_rag.py, który pozwala na działanie w specyficznych środowiskach sieciowych (np. sieci uczelniane Eduroam, korporacyjne VPN, silne antywirusy z inspekcją SSL).
Jeśli widzisz ostrzeżenia InsecureRequestWarning w logach – jest to celowe działanie wymuszające połączenie z API Google pomimo restrykcji sieciowych. Aplikacja przełącza się również na tryb REST zamiast gRPC, aby uniknąć blokad portów.
Instalacja lokalna (bez Dockera)

## Jeśli wolisz uruchomić projekt klasycznie (Python + venv):
Utwórz środowisko wirtualne:

```Bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```
Zainstaluj zależności:

```Bash
pip install -r requirements.txt
```
Upewnij się, że masz lokalnie uruchomioną bazę PostgreSQL i wpisz jej dane w konfiguracja.py.
Wygeneruj dane:

```Bash
python generuj_dane_demo.py
```
Uruchom:

```Bash
streamlit run app.py
