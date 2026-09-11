from pydantic import BaseModel, ConfigDict


class StudySessionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    date: str
    start_time: str | None = None
    end_time: str | None = None
    studied_minutes: int


class CourseOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    teacher: str = ""
    total_hours: float | None = None
    status: str
    studied_minutes_total: int = 0


class WeeklyStatOut(BaseModel):
    week_start: str
    course_id: int
    course_name: str
    studied_minutes: int
