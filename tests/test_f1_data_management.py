from __future__ import annotations

from campus_planner.data_manager import SchoolCatalog, add_course, add_student, delete_course, find_courses, find_students
from campus_planner.models import Course, Student, TimeSlot


def test_add_and_find_courses() -> None:
    catalog = SchoolCatalog()
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

    assert add_course(catalog, course) == []
    assert catalog.courses["CS101"].name == "Python 程式設計"
    assert find_courses(catalog, teacher="林老師")[0].course_id == "CS101"
    assert find_courses(catalog, day=1)[0].course_id == "CS101"


def test_reject_duplicate_and_invalid_course_data() -> None:
    catalog = SchoolCatalog()
    valid = Course("CS101", "Python", 3, True, "林老師", 10, "A101", [TimeSlot(2, "3")])
    assert add_course(catalog, valid) == []

    duplicate = Course("CS101", "重複", 2, False, "王老師", 5, "B101", [TimeSlot(2, "4")])
    assert "課程代號不得重複" in add_course(catalog, duplicate)

    bad = Course("CS999", "Bad", 0, False, "老師", 0, "A101", [TimeSlot(8, "x")])
    errors = add_course(catalog, bad)
    assert "學分必須為正整數" in errors
    assert "人數上限不得小於 1" in errors
    assert "星期不合法: 8" in errors or "節次不合法: x" in errors


def test_delete_course_protected_when_students_enrolled() -> None:
    catalog = SchoolCatalog()
    course = Course("CS201", "網路概論", 3, False, "張老師", 20, "A201", [TimeSlot(3, "1")])
    add_course(catalog, course)

    student = Student("S001", "王小明", "資工系", ["CS201"], 24)
    add_student(catalog, student)

    result = delete_course(catalog, "CS201")
    assert result is False
    assert "CS201" in catalog.courses


def test_student_management_and_queries() -> None:
    catalog = SchoolCatalog()
    student = Student("S001", "王小明", "資工系", [], 24)
    assert add_student(catalog, student) == []
    assert catalog.students["S001"].name == "王小明"
    assert find_students(catalog, department="資工系")[0].student_id == "S001"
