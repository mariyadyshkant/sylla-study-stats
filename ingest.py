"""Legge study-stats.json (esportato da Sylla) e fa upsert su courses/study_sessions."""

import json
import os
import sys

from app.database import SessionLocal, init_db
from app.models import Course, StudySession

EXPORT_PATH = os.environ.get("STUDY_STATS_EXPORT_PATH", "data/study-stats.json")


def upsert_course(db, entry: dict) -> Course:
    course = db.get(Course, entry["id"])
    if course is None:
        course = Course(id=entry["id"])
        db.add(course)
    course.name = entry["name"]
    course.teacher = entry.get("teacher") or ""
    course.total_hours = entry.get("total_hours")
    course.status = entry.get("status", "active")
    return course


def upsert_session(db, course_id: int, entry: dict) -> str:
    existing = (
        db.query(StudySession)
        .filter_by(course_id=course_id, date=entry["date"], start_time=entry.get("start_time"))
        .one_or_none()
    )
    if existing is None:
        db.add(
            StudySession(
                course_id=course_id,
                date=entry["date"],
                start_time=entry.get("start_time"),
                end_time=entry.get("end_time"),
                studied_minutes=entry.get("studied_minutes", 0),
            )
        )
        return "created"

    changed = existing.end_time != entry.get("end_time") or existing.studied_minutes != entry.get(
        "studied_minutes", 0
    )
    existing.end_time = entry.get("end_time")
    existing.studied_minutes = entry.get("studied_minutes", 0)
    return "updated" if changed else "unchanged"


def run(export_path: str = EXPORT_PATH) -> None:
    init_db()
    with open(export_path, "r", encoding="utf-8") as f:
        payload = json.load(f)

    db = SessionLocal()
    counters = {"created": 0, "updated": 0, "unchanged": 0}
    try:
        for course_entry in payload.get("courses", []):
            course = upsert_course(db, course_entry)
            db.flush()
            for session_entry in course_entry.get("lessons", []):
                outcome = upsert_session(db, course.id, session_entry)
                counters[outcome] += 1
        db.commit()
    finally:
        db.close()

    print(f"Ingest completato da {export_path}: {counters}")


if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else EXPORT_PATH
    run(path)
