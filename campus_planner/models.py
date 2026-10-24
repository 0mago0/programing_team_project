from __future__ import annotations

from dataclasses import dataclass, field
from typing import List


VALID_DAYS = set(range(1, 8))
# 節次的唯一定義：順序即課表矩陣的欄位順序
PERIOD_ORDER = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "a", "b", "c"]
VALID_PERIODS = set(PERIOD_ORDER)


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
    """校園活動。時間與課程一樣以 TimeSlot（星期＋節次）表示，共用同一套衝突檢查。"""

    activity_id: str
    name: str
    time_slots: List[TimeSlot] = field(default_factory=list)
    expected_participants: int = 1
    activity_type: str = "一般"
    classroom: str = ""
    venue_requirements: List[str] = field(default_factory=list)
    participants: List[str] = field(default_factory=list)
