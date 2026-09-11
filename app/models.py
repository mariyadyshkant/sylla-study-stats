from sqlalchemy import Column, Integer, String, Float, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship

from .database import Base


class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True)  # stesso id del corso in Sylla
    name = Column(String, nullable=False)
    teacher = Column(String, default="")
    total_hours = Column(Float, nullable=True)
    status = Column(String, nullable=False, default="active")

    sessions = relationship(
        "StudySession", back_populates="course", cascade="all, delete-orphan"
    )


class StudySession(Base):
    __tablename__ = "study_sessions"
    __table_args__ = (
        UniqueConstraint("course_id", "date", "start_time", name="uq_session_slot"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    course_id = Column(Integer, ForeignKey("courses.id", ondelete="CASCADE"), nullable=False)
    date = Column(String, nullable=False)
    start_time = Column(String, nullable=True)
    end_time = Column(String, nullable=True)
    studied_minutes = Column(Integer, nullable=False, default=0)

    course = relationship("Course", back_populates="sessions")
