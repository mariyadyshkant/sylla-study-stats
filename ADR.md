# Architecture Decision Record

**Progetto:** Sylla study-stats — microservizio di aggregazione statistiche di studio
**Data:** 2026-09-11
**Autore:**

## Decisione

È stato costruito un microservizio indipendente, containerizzato con Docker, che
ingerisce il file `study-stats.json` esportato manualmente dall'app desktop Sylla
(corsi + lezioni segnate come "svolta"), lo normalizza in due risorse SQLite
(`courses`, `study_sessions`) e lo espone tramite un'API REST (FastAPI) e una
dashboard interna statica per rispondere alla domanda "quanto ho studiato".

## Contesto

Sylla è un'app Electron locale, single-user, senza rete né server esposto (vedi ADR
del progetto principale). Questo microservizio non comunica mai direttamente con il
processo Electron: l'unico punto di contatto è il file JSON di export, prodotto da
Sylla su richiesta dell'utente e montato in sola lettura nel container.

## Piattaforme scelte

- Backend: Python + FastAPI (endpoint di sola lettura/statistiche)
- Database: SQLite
- Ingestione: script Python standalone (`ingest.py`), lanciato manualmente o via cron
  dell'host, legge il file JSON montato come volume
- Frontend: dashboard interna, plain HTML/CSS/JS servita staticamente da FastAPI
- Deploy: Docker + docker-compose

## Componenti principali

- **Modello dati `Course` / `StudySession`**: ORM SQLAlchemy, chiave logica su
  `course.id` (proveniente da Sylla) e su `(course_id, date, start_time)` per le sessioni.
- **Pipeline di ingestione (`ingest.py`)**: legge `study-stats.json`, fa upsert di
  corsi e sessioni di studio.
- **API REST (FastAPI)**: `/api/v1/courses`, `/api/v1/stats/weekly`, `/api/v1/health`.
- **Dashboard interna**: pagina statica che mostra ore studiate per corso/settimana.

## Decisioni architetturali

- **Nessuna rete diretta con Electron**: il disaccoppiamento tramite file JSON
  esportato manualmente evita di introdurre un server nell'app desktop, rispettando
  il vincolo "no cloud, no rete" dell'ADR di Sylla.
- **Database**: SQLite scelto per lo stesso motivo dell'esercitazione di riferimento
  (microservice-week-6) — volume ridotto, zero infrastruttura.
- **Ingestione manuale/cron dell'host**: nessuna coda o scheduler nel container in
  questa fase; la sincronizzazione avviene rieseguendo `ingest.py` (upsert).
- **Containerizzazione**: Docker + docker-compose come standard di deploy, stesso
  pattern dell'esercitazione di riferimento (immagine `python:3.12-slim`, volume per
  il file di export in sola lettura, health check su `/api/v1/health`).

## Vincoli

- Il file `study-stats.json` è l'unica fonte dati: nessun accesso diretto al DB SQLite
  di Sylla.
- Nessuna autenticazione (uso interno/locale, single-user, come Sylla).
- L'ingestione non è automatica in questa fase: va lanciata a mano o via cron host.

## Cosa NON è in scope

- Connessione diretta o di rete al processo Electron di Sylla.
- Autenticazione / autorizzazione.
- Scheduling automatico dell'ingestione all'interno del container.
- Multi-utente / multi-installazione Sylla simultanea.

## Feature future pianificate

- Scheduling dell'ingestione (cron nel container o trigger da Sylla via file watcher).
- Statistiche più granulari (streak di studio, confronto tra corsi, obiettivi settimanali).
