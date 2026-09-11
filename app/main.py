import asyncio
import os
from datetime import date, timedelta

from fastapi import Depends, FastAPI
from fastapi.staticfiles import StaticFiles
from sqlalchemy import func
from sqlalchemy.orm import Session

import ingest
from .database import get_db, init_db
from .models import Course, StudySession
from .schemas import CourseOut, WeeklyStatOut

app = FastAPI(title="Sylla study-stats")

INGEST_INTERVAL_SECONDS = int(os.environ.get("INGEST_INTERVAL_SECONDS", "300"))
_ingest_task: asyncio.Task | None = None


async def ingest_loop():
    while True:
        try:
            result = await asyncio.to_thread(ingest.run)
            print(f"[ingest] sync automatica: {result}")
        except Exception as exc:  # sorgente irraggiungibile: riprova al prossimo giro
            print(f"[ingest] fallita ({exc}), riprovo tra {INGEST_INTERVAL_SECONDS}s")
        await asyncio.sleep(INGEST_INTERVAL_SECONDS)


@app.on_event("startup")
def on_startup():
    global _ingest_task
    init_db()
    _ingest_task = asyncio.create_task(ingest_loop())


@app.on_event("shutdown")
def on_shutdown():
    if _ingest_task:
        _ingest_task.cancel()


def week_start(iso_date: str) -> str:
    d = date.fromisoformat(iso_date)
    return (d - timedelta(days=d.weekday())).isoformat()


@app.get("/api/v1/health")
def health(db: Session = Depends(get_db)):
    count = db.query(func.count(StudySession.id)).scalar()
    return {"status": "ok", "study_sessions": count}


@app.get("/api/v1/courses", response_model=list[CourseOut])
def list_courses(db: Session = Depends(get_db)):
    courses = db.query(Course).order_by(Course.name).all()
    out = []
    for c in courses:
        total = sum(s.studied_minutes for s in c.sessions)
        out.append(
            CourseOut(
                id=c.id,
                name=c.name,
                teacher=c.teacher or "",
                total_hours=c.total_hours,
                status=c.status,
                studied_minutes_total=total,
            )
        )
    return out


@app.get("/api/v1/stats/weekly", response_model=list[WeeklyStatOut])
def weekly_stats(course_id: int | None = None, db: Session = Depends(get_db)):
    query = db.query(StudySession).join(Course)
    if course_id is not None:
        query = query.filter(StudySession.course_id == course_id)

    buckets: dict[tuple[str, int], int] = {}
    names: dict[int, str] = {}
    for session in query.all():
        key = (week_start(session.date), session.course_id)
        buckets[key] = buckets.get(key, 0) + session.studied_minutes
        names[session.course_id] = session.course.name

    return [
        WeeklyStatOut(
            week_start=week,
            course_id=cid,
            course_name=names[cid],
            studied_minutes=minutes,
        )
        for (week, cid), minutes in sorted(buckets.items())
    ]


app.mount("/", StaticFiles(directory="static", html=True), name="static")
