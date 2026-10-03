from __future__ import annotations

from campus_planner.data_store import load_school_data, save_school_data
from campus_planner.models import Course, Student, TimeSlot
from campus_planner.timetable import build_weekly_matrix, place_course_in_timetable, summarise_timetable
from campus_planner.validation import check_time_conflict, validate_course, validate_student


def test_valid_course_passes() -> None:
    course = Course(
        course_id="CS101",
        name="Python 程式設計",
        credits=3,
        required=True,
        teacher="林老師",
        capacity=30,
        classroom="A101",
        time_slots=[TimeSlot(1, "3"), TimeSlot(1, "4")],
    )
    assert validate_course(course) == []


def test_invalid_course_diagnostics() -> None:
    course = Course(
        course_id="",
        name="",
        credits=0,
        required=True,
        teacher="",
        capacity=0,
        classroom="",
        time_slots=[TimeSlot(8, "x")],
    )
    errors = validate_course(course)
    assert "課程代號不可空白" in errors
    assert "學分必須為正整數" in errors
    assert "人數上限不得小於 1" in errors
    assert "節次不合法: x" in errors


def test_student_and_conflict_checks() -> None:
    student = Student("S001", "王小明", "資工系", ["CS101"], 24)
    assert validate_student(student) == []

    s1 = TimeSlot(2, "3")
    s2 = TimeSlot(2, "3")
    assert check_time_conflict(s1, s2) is True


def test_timetable_generation_and_json_round_trip(tmp_path) -> None:
    course = Course(
        course_id="CS102",
        name="資料結構",
        credits=3,
        required=False,
        teacher="王老師",
        capacity=20,
        classroom="B201",
        time_slots=[TimeSlot(3, "5"), TimeSlot(3, "6")],
    )

    matrix = build_weekly_matrix()
    matrix = place_course_in_timetable(matrix, course)
    summary = summarise_timetable(matrix)

    assert matrix[2][4] == "CS102 - 資料結構"
    assert summary["days"] == 7
    assert summary["periods"] == 12

    payload = {
        "courses": [{"course_id": course.course_id, "name": course.name}],
        "students": [{"student_id": "S001", "name": "王小明"}],
    }
    file_path = tmp_path / "school.json"
    save_school_data(file_path, payload)
    loaded = load_school_data(file_path)
    assert loaded == payload
