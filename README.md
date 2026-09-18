# sylla-study-stats

> Componente pianificato dell'ecosistema **[Sylla](https://github.com/mariyadyshkant/sylla-ai-driven-pj)**, l'app desktop per il tracciamento delle lezioni dei corsi seguiti. Sylla stessa è ancora in fase di progettazione (modello dati e architettura definiti, sviluppo non iniziato); questo microservizio è il componente più avanzato lato implementazione, ma prende pieno senso solo una volta che l'app principale esiste ed espone i dati da cui leggere le statistiche.

Microservizio indipendente e containerizzato che ingerisce il file `study-stats.json`
esportato dall'app desktop [Sylla](../sylla-project) (corsi + lezioni segnate come
svolte) e serve statistiche "quanto ho studiato" via API REST + dashboard interna.

Vedi [ADR.md](ADR.md) per le decisioni architetturali e [BRIEF.md](BRIEF.md) per il flow.

Sylla espone in locale (bind `127.0.0.1:4174`, non raggiungibile dalla rete) un
endpoint `GET /api/v1/study-stats` sempre aggiornato: questo microservizio lo
interroga automaticamente, a intervalli regolari, senza alcuna azione manuale
dell'utente né export da parte di Sylla.

## Setup locale (senza Docker)

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

## Ingestione

Automatica: all'avvio dell'app FastAPI parte un ciclo in background che chiama
`STUDY_STATS_SOURCE_URL` ogni `INGEST_INTERVAL_SECONDS` (default 300s) e fa upsert
su `courses` / `study_sessions`. Nessun comando da lanciare a mano.

Per un'esecuzione singola manuale (debug, o sorgente file invece di API live):

```bash
# da API live (default)
STUDY_STATS_SOURCE_URL=http://127.0.0.1:4174/api/v1/study-stats .venv/bin/python ingest.py

# da uno snapshot esportato a mano da Sylla (Impostazioni -> Backup e dati)
STUDY_STATS_EXPORT_PATH=./data/study-stats.json .venv/bin/python ingest.py
```

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

Sia l'endpoint `GET /api/v1/study-stats` di Sylla sia il file `study-stats.json`
esportato manualmente restituiscono lo stesso formato:

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

## Autrice
 
Mariya Dyshkant
[Portfolio](https://mariyadyshkant.com) · [LinkedIn](https://linkedin.com/in/mariya-dyshkant-45bb411ba)
