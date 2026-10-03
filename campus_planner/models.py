from __future__ import annotations

from dataclasses import dataclass, field
from typing import List


VALID_DAYS = set(range(1, 8))
VALID_PERIODS = {"1", "2", "3", "4", "5", "6", "7", "8", "9", "a", "b", "c"}


@dataclass(frozen=True)
class TimeSlot:
    day: int
    period: str


@dataclass
class Course:
    course_id: str
    name: str
    credits: int
    required: bool
    teacher: str
    capacity: int
    classroom: str
    time_slots: List[TimeSlot] = field(default_factory=list)


@dataclass
class Student:
    student_id: str
    name: str
    department: str
    enrolled_courses: List[str] = field(default_factory=list)
    credit_limit: int = 24


@dataclass
class Classroom:
    room_id: str
    capacity: int
    equipment: List[str] = field(default_factory=list)
    building: str = "校本部"


@dataclass
class Activity:
    activity_id: str
    name: str
    date: str
    start_time: str
    end_time: str
    expected_participants: int
    activity_type: str
    venue_requirements: List[str] = field(default_factory=list)
