# Architecture Decision Record

**Progetto:** Sylla study-stats — microservizio di aggregazione statistiche di studio
**Data:** 2026-09-11
**Autore:**

## Decisione

È stato costruito un microservizio indipendente, containerizzato con Docker, che
sincronizza automaticamente (in background, a intervalli regolari) i dati di
corsi e lezioni svolte esposti dall'app desktop Sylla, li normalizza in due
risorse SQLite (`courses`, `study_sessions`) e li espone tramite un'API REST
(FastAPI) e una dashboard interna statica per rispondere alla domanda "quanto ho
studiato". Nessuna azione manuale è richiesta né lato Sylla né lato microservizio.

## Contesto

Sylla è un'app Electron locale, single-user (vedi ADR del progetto principale).
Espone un piccolo server HTTP in ascolto solo su `127.0.0.1:4174`
(`GET /api/v1/study-stats`), non raggiungibile dalla rete esterna alla macchina —
compatibile coi vincoli "nessuna autenticazione / nessuna esposizione
multi-utente" perché il traffico non lascia mai l'host. Questo microservizio,
girando in un container Docker Desktop sulla stessa macchina, raggiunge quella
porta tramite `host.docker.internal` (routing verso servizi in ascolto su
loopback dell'host, funzionalità nativa di Docker Desktop). In alternativa resta
supportato il flusso a file (`study-stats.json`) esportato manualmente da Sylla,
per debug o uso offline.

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
- **Pipeline di ingestione (`ingest.py`)**: legge dall'endpoint HTTP di Sylla (o, in
  fallback, da un file `study-stats.json`), fa upsert di corsi e sessioni di studio.
- **Scheduler in-process (`app/main.py`)**: task asyncio avviato allo startup di
  FastAPI che richiama l'ingest ogni `INGEST_INTERVAL_SECONDS` (default 300s).
- **API REST (FastAPI)**: `/api/v1/courses`, `/api/v1/stats/weekly`, `/api/v1/health`.
- **Dashboard interna**: pagina statica che mostra ore studiate per corso/settimana.

## Decisioni architetturali

- **Pull via HTTP locale invece di file di export**: Sylla espone un endpoint
  read-only in ascolto solo su loopback; il microservizio lo interroga
  periodicamente. Questo elimina la necessità di un'azione manuale (click di
  export) e mantiene i dati sempre aggiornati, restando comunque "locale":
  il traffico non lascia mai la macchina dell'utente (nessun cloud, nessuna
  esposizione di rete).
- **Scheduler interno invece di cron esterno**: la sincronizzazione periodica vive
  dentro il processo FastAPI (asyncio task), così containerizzare il servizio è
  sufficiente per avere ingest automatico, senza dipendenze da cron dell'host.
- **Database**: SQLite scelto per lo stesso motivo dell'esercitazione di riferimento
  (microservice-week-6) — volume ridotto, zero infrastruttura.
- **Containerizzazione**: Docker + docker-compose come standard di deploy;
  `host.docker.internal` (con `extra_hosts: host-gateway` per compatibilità Linux)
  per raggiungere l'endpoint di Sylla sull'host, health check su `/api/v1/health`.

## Vincoli

- L'endpoint `GET /api/v1/study-stats` di Sylla è la fonte primaria; il file
  `study-stats.json` resta supportato solo come fallback manuale/offline.
- Nessuna autenticazione: entrambi i lati (Sylla e il microservizio) restano
  raggiungibili solo dalla macchina locale (uso interno/single-user, come Sylla).
- Il microservizio deve girare sulla stessa macchina di Sylla (nessun deploy remoto).

## Cosa NON è in scope

- Esposizione dell'endpoint di Sylla oltre `127.0.0.1` (nessun bind su `0.0.0.0`,
  nessuna raggiungibilità da altre macchine della LAN).
- Autenticazione / autorizzazione.
- Multi-utente / multi-installazione Sylla simultanea.

## Feature future pianificate

- Notifica push da Sylla al microservizio sugli eventi di modifica (invece di
  polling a intervalli fissi), se il polling risultasse troppo lento per l'uso reale.
- Statistiche più granulari (streak di studio, confronto tra corsi, obiettivi settimanali).
