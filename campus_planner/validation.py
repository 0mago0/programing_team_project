from __future__ import annotations

from typing import Iterable

from .models import Course, Student, TimeSlot

VALID_PERIODS = {"1", "2", "3", "4", "5", "6", "7", "8", "9", "a", "b", "c"}


def validate_course(course: Course) -> list[str]:
    errors: list[str] = []

    if not course.course_id:
        errors.append("課程代號不可空白")
    if not course.name:
        errors.append("課程名稱不可空白")
    if course.credits <= 0:
        errors.append("學分必須為正整數")
    if course.capacity < 1:
        errors.append("人數上限不得小於 1")
    if not course.teacher:
        errors.append("授課教師不可空白")
    if not course.classroom:
        errors.append("教室不可空白")

    for slot in course.time_slots:
        if not isinstance(slot, TimeSlot):
            errors.append(f"時段資料格式錯誤: {slot!r}")
            continue
        if slot.day not in range(1, 8):
            errors.append(f"星期不合法: {slot.day}")
        if slot.period not in VALID_PERIODS:
            errors.append(f"節次不合法: {slot.period}")

    return errors


def validate_student(student: Student) -> list[str]:
    errors: list[str] = []

    if not student.student_id:
        errors.append("學號不可空白")
    if not student.name:
        errors.append("姓名不可空白")
    if not student.department:
        errors.append("系級不可空白")
    if student.credit_limit <= 0:
        errors.append("學分上限必須大於 0")

    return errors


def check_time_conflict(slot_a: TimeSlot, slot_b: TimeSlot) -> bool:
    return slot_a.day == slot_b.day and slot_a.period == slot_b.period


def check_slot_list_conflict(slot_list_a: Iterable[TimeSlot], slot_list_b: Iterable[TimeSlot]) -> list[TimeSlot]:
    conflicts: list[TimeSlot] = []
    slot_array_a = list(slot_list_a)
    slot_array_b = list(slot_list_b)

    for slot_a in slot_array_a:
        for slot_b in slot_array_b:
            if check_time_conflict(slot_a, slot_b):
                conflicts.append(slot_a)
                break

    return conflicts


def evaluate_enrollment(student: Student, course: Course, course_catalog: dict[str, Course]) -> list[str]:
    errors: list[str] = []

    if student.student_id not in {"", None} and course.course_id in student.enrolled_courses:
        errors.append(f"學生 {student.student_id} 已選修 {course.course_id}")

    if course.course_id not in course_catalog:
        errors.append(f"課程 {course.course_id} 不存在")
        return errors

    current_credits = sum(course_catalog[cid].credits for cid in student.enrolled_courses if cid in course_catalog)
    projected_credits = current_credits + course.credits
    if projected_credits > student.credit_limit:
        errors.append(
            f"加選後學分 {projected_credits} 超過上限 {student.credit_limit}"
        )

    if len(student.enrolled_courses) >= course.capacity:
        errors.append(f"課程 {course.course_id} 已額滿")

    return errors
