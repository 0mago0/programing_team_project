from __future__ import annotations

from typing import Iterable

from .models import VALID_DAYS, VALID_PERIODS, Activity, Classroom, Course, Student, TimeSlot


def _is_blank(value: object) -> bool:
    return not isinstance(value, str) or not value.strip()


def _is_positive_int(value: object) -> bool:
    # bool 是 int 的子類別，True 不應被當成 1 學分
    return isinstance(value, int) and not isinstance(value, bool) and value > 0


def validate_time_slot(slot: object) -> list[str]:
    if not isinstance(slot, TimeSlot):
        return [f"時段資料格式錯誤: {slot!r}"]

    errors: list[str] = []
    if isinstance(slot.day, bool) or slot.day not in VALID_DAYS:
        errors.append(f"星期不合法: {slot.day}")
    if slot.period not in VALID_PERIODS:
        errors.append(f"節次不合法: {slot.period}")
    return errors


def validate_course(course: Course) -> list[str]:
    errors: list[str] = []

    if _is_blank(course.course_id):
        errors.append("課程代號不可空白")
    if _is_blank(course.name):
        errors.append("課程名稱不可空白")
    if not _is_positive_int(course.credits):
        errors.append("學分必須為正整數")
    if not isinstance(course.required, bool):
        errors.append("必選修必須為 true 或 false")
    if not _is_positive_int(course.capacity):
        errors.append("人數上限不得小於 1")
    if _is_blank(course.teacher):
        errors.append("授課教師不可空白")
    if _is_blank(course.classroom):
        errors.append("教室不可空白")

    seen: set[TimeSlot] = set()
    for slot in course.time_slots:
        slot_errors = validate_time_slot(slot)
        errors.extend(slot_errors)
        if not slot_errors:
            if slot in seen:
                errors.append(f"時段重複: 星期{slot.day} 第{slot.period}節")
            seen.add(slot)

    return errors


def validate_student(student: Student) -> list[str]:
    errors: list[str] = []

    if _is_blank(student.student_id):
        errors.append("學號不可空白")
    if _is_blank(student.name):
        errors.append("姓名不可空白")
    if _is_blank(student.department):
        errors.append("系級不可空白")
    if not _is_positive_int(student.credit_limit):
        errors.append("學分上限必須大於 0")
    if len(set(student.enrolled_courses)) != len(student.enrolled_courses):
        errors.append("已選課程不得重複")

    return errors


def validate_classroom(classroom: Classroom) -> list[str]:
    errors: list[str] = []

    if _is_blank(classroom.room_id):
        errors.append("教室代號不可空白")
    if not _is_positive_int(classroom.capacity):
        errors.append("教室容量必須為正整數")
    if _is_blank(classroom.building):
        errors.append("建築物不可空白")

    return errors


def validate_activity(activity: Activity) -> list[str]:
    errors: list[str] = []

    if _is_blank(activity.activity_id):
        errors.append("活動代號不可空白")
    if _is_blank(activity.name):
        errors.append("活動名稱不可空白")
    if not activity.time_slots:
        errors.append("活動至少要有一個時段")
    if not _is_positive_int(activity.expected_participants):
        errors.append("預計人數必須為正整數")
    elif len(activity.participants) > activity.expected_participants:
        errors.append(f"報名人數 {len(activity.participants)} 超過預計人數 {activity.expected_participants}")
    if len(set(activity.participants)) != len(activity.participants):
        errors.append("報名學生不得重複")

    seen: set[TimeSlot] = set()
    for slot in activity.time_slots:
        slot_errors = validate_time_slot(slot)
        errors.extend(slot_errors)
        if not slot_errors:
            if slot in seen:
                errors.append(f"時段重複: 星期{slot.day} 第{slot.period}節")
            seen.add(slot)

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
