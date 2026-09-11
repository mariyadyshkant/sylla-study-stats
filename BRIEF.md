# Brief Overview

Sorgente: `study-stats.json` (export prodotto dall'app desktop Sylla — corsi + lezioni svolte)
Risorse: `courses`, `study_sessions`
Campi canonici course: `id, name, teacher, total_hours, status`
Campi canonici study_session: `id, course_id, date, start_time, end_time, studied_minutes`
Storage: SQLite (`courses`, `study_sessions`)
Consumer: dashboard interna "quanto ho studiato"

## Flow

1. L'app desktop Sylla esporta periodicamente `study-stats.json` (corsi + lezioni con `status = 'svolta'`).
2. Il file viene montato come volume in sola lettura nel container di questo microservizio.
3. Lo script di ingestione (`ingest.py`) legge il file, fa upsert su `courses` (chiave logica: `id` del corso in Sylla) e su `study_sessions` (chiave logica: `course_id + date + start_time`).
4. L'API REST espone statistiche aggregate (minuti/ore studiate per corso, per settimana).
5. La dashboard interna consuma l'API per mostrare "quanto ho studiato".
6. Ri-eseguendo l'ingest si sincronizzano gli aggiornamenti (nuove lezioni svolte, corsi modificati).

## Requirements

Step 1: Definire modello e schema per `courses` e `study_sessions`.
Step 2: Implementare la pipeline di ingestione da `study-stats.json`.
Step 3: Sviluppare l'API REST per statistiche aggregate (`/api/v1/stats/weekly`, `/api/v1/courses`).
Step 4: Costruire la dashboard interna "quanto ho studiato".
Step 5: Containerizzare con Docker, montando il file di export come volume in sola lettura.

## Stack

- Database: SQLite
- Backend: FastAPI
- Frontend: dashboard interna (plain HTML/CSS/JS)
- Ingestione: script Python, legge il file JSON montato come volume
- Deploy: Docker + docker-compose, nessuna rete verso il processo Electron
