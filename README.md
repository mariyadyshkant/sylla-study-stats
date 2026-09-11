# sylla-study-stats

Microservizio indipendente e containerizzato che ingerisce il file `study-stats.json`
esportato dall'app desktop [Sylla](../sylla-project) (corsi + lezioni segnate come
svolte) e serve statistiche "quanto ho studiato" via API REST + dashboard interna.

Vedi [ADR.md](ADR.md) per le decisioni architetturali e [BRIEF.md](BRIEF.md) per il flow.

Nessuna connessione diretta con il processo Electron: l'unico punto di contatto è il
file JSON di export, montato in sola lettura nel container.

## Setup locale (senza Docker)

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

## Ingestione (manuale)

```bash
STUDY_STATS_EXPORT_PATH=./data/study-stats.json .venv/bin/python ingest.py
```

Legge il file JSON esportato da Sylla (Impostazioni → Backup e dati → "Esporta dati
per study-stats") e fa upsert su `courses` / `study_sessions`. Ri-eseguendolo
sincronizza gli aggiornamenti.

## API

```bash
.venv/bin/uvicorn app.main:app --reload
```

| Metodo | Path | Descrizione |
|--------|------|-------------|
| GET | `/api/v1/courses` | Elenco corsi con minuti studiati totali |
| GET | `/api/v1/stats/weekly?course_id=` | Minuti studiati per settimana (opzionalmente per corso) |
| GET | `/api/v1/health` | Stato servizio + conteggio sessioni |
| GET | `/` | Dashboard interna |

## Docker

```bash
cp .env.example .env
# In docker-compose.yml, monta il file di export di Sylla in ./data/study-stats.json
docker compose up --build
docker compose exec study-stats python ingest.py
```

## Contratto dati (sorgente)

Il file `study-stats.json` prodotto da Sylla ha il formato:

```json
{
  "generated_at": "2026-09-11T10:00:00Z",
  "courses": [
    {
      "id": 1,
      "name": "...",
      "teacher": "...",
      "total_hours": 40,
      "status": "active",
      "lessons": [
        { "date": "2026-09-08", "start_time": "09:00", "end_time": "11:00", "status": "svolta", "studied_minutes": 120 }
      ]
    }
  ]
}
```

## Struttura

```
app/          modello, schema, database, API FastAPI
static/       dashboard (HTML/CSS/JS, nessun framework)
ingest.py     pipeline di ingestione da study-stats.json
data/         study-stats.json (montato da Sylla) + DB SQLite generato
```
