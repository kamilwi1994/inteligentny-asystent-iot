# Inteligentny Asystent IoT (Local LLM + RAG)

Projekt zrealizowany w ramach przedmiotu "Internet Rzeczy". System integruje dane z inteligentnego domu z lokalnym modelem językowym (Ollama) przy użyciu architektury RAG.

Projekt jest w pełni konfigurowalny poprzez plik `.env`.

---

## 📋 Spis treści
1. [Wymagania](#wymagania)
2. [Szybki start](#szybki-start)
3. [Konfiguracja (.env)](#konfiguracja-env)
4. [Architektura Sieciowa](#architektura-sieciowa)

---

## 🛠 Wymagania
*   Docker & Docker Compose

---

## 🚀 Szybki start

### Krok 1: Pobierz projekt
```bash
git clone https://github.com/kamilwi1994/inteligentny-asystent-iot.git
cd inteligentny-asystent-iot
```

### Krok 2: Konfiguracja
W głównym katalogu znajduje się plik `.env`. Otwórz go i dostosuj do swojego środowiska (domyślne wartości są gotowe do użycia).

**Przykładowa zawartość .env:**
```ini
AI_NETWORK_NAME=ai_network
OLLAMA_BASE_URL=http://ollama:11434
```

### Krok 3: Przygotuj sieć Docker
Ponieważ aplikacja łączy się z zewnętrznym kontenerem AI, utwórz sieć o nazwie zdefiniowanej w `.env`:

```bash
docker network create ai_network
```

### Krok 4: Uruchom Ollamę (Silnik AI)
Jeśli jeszcze nie masz uruchomionej Ollamy, uruchom ją w tej samej sieci:

```bash
docker run -d --name ollama --network ai_network -p 11434:11434 -v ollama_data:/root/.ollama ollama/ollama:latest
```

### Krok 5: Uruchom Aplikację
```bash
docker compose up --build
```
Aplikacja automatycznie wykryje brakujące modele AI i je pobierze.

Dostęp: **http://localhost:8501**

---

## ⚙️ Konfiguracja (.env)

Plik `.env` pozwala na pełną kontrolę nad aplikacją bez zmiany kodu:

| Zmienna | Domyślnie | Opis |
| :--- | :--- | :--- |
| `AI_NETWORK_NAME` | `ai_network` | Nazwa zewnętrznej sieci Docker, w której działa Ollama. |
| `OLLAMA_BASE_URL` | `http://ollama:11434` | Adres URL kontenera Ollama (zazwyczaj `http://nazwa_kontenera:port`). |
| `OLLAMA_MODEL_CHAT` | `llama3.2` | Model używany do generowania odpowiedzi. |
| `HISTORY_DAYS` | `30` | Zakres dni generowanych w bazie demo i analizowanych przez RAG. |
| `RAG_K_RETRIEVAL` | `3` | Liczba dni pobierana do kontekstu (im mniej, tym szybciej działa na CPU). |

---

## 🌐 Architektura Sieciowa

Aplikacja zakłada, że Ollama działa jako osobny serwis (mikroserwis).
Dzięki zmiennej `AI_NETWORK_NAME` w pliku `.env`, możesz łatwo podpiąć asystenta do dowolnej istniejącej infrastruktury Dockerowej, wpisując po prostu nazwę sieci, w której działa Twój LLM.
```