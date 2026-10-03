from __future__ import annotations

from typing import Any

from .models import Course, Student, TimeSlot


def build_demo_courses() -> list[Course]:
    return [
        Course(
            course_id="CS101",
            name="Python 程式設計",
            credits=3,
            required=True,
            teacher="林老師",
            capacity=30,
            classroom="A101",
            time_slots=[TimeSlot(1, "3"), TimeSlot(1, "4")],
        ),
        Course(
            course_id="CS102",
            name="資料結構",
            credits=3,
            required=True,
            teacher="王老師",
            capacity=25,
            classroom="B201",
            time_slots=[TimeSlot(2, "5"), TimeSlot(2, "6")],
        ),
        Course(
            course_id="MA101",
            name="微積分",
            credits=4,
            required=True,
            teacher="張老師",
            capacity=35,
            classroom="C305",
            time_slots=[TimeSlot(3, "1"), TimeSlot(3, "2")],
        ),
    ]


def build_demo_students() -> list[Student]:
    return [
        Student("S001", "王小明", "資工系", ["CS101"], 24),
        Student("S002", "李小華", "資工系", ["MA101"], 22),
        Student("S003", "陳大同", "資訊工程", [], 20),
    ]


def build_demo_school_data() -> dict[str, Any]:
    return {
        "courses": build_demo_courses(),
        "students": build_demo_students(),
        "classrooms": [
            {"room_id": "A101", "capacity": 50, "equipment": ["投影機"], "building": "資訊大樓"},
            {"room_id": "B201", "capacity": 40, "equipment": ["白板"], "building": "工程大樓"},
            {"room_id": "C305", "capacity": 45, "equipment": ["投影機", "白板"], "building": "理工大樓"},
        ],
        "activities": [],
    }


def student_activity_summary(student: Student, courses: dict[str, Course]) -> dict[str, Any]:
    current_credits = sum(courses[cid].credits for cid in student.enrolled_courses if cid in courses)
    return {
        "student_id": student.student_id,
        "name": student.name,
        "enrolled_courses": list(student.enrolled_courses),
        "current_credits": current_credits,
        "credit_limit": student.credit_limit,
    }
