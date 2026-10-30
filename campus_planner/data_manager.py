"""F1 課程、學生與教室資料管理。

所有函式都接收 SchoolCatalog 作為參數，不使用全域變數，也不呼叫 input()。
新增與修改回傳錯誤清單（空清單代表成功）；失敗時 catalog 內容保持不變。
選課人數以學生的 enrolled_courses 為唯一來源，不另外維護一份計數。
"""
from __future__ import annotations

from dataclasses import dataclass, field, fields, replace
from pathlib import Path
from typing import Any

from .data_store import load_school_data, save_school_data
from .models import Activity, Classroom, Course, Student, TimeSlot
from .validation import validate_activity, validate_classroom, validate_course, validate_student


@dataclass
class SchoolCatalog:
    courses: dict[str, Course] = field(default_factory=dict)
    students: dict[str, Student] = field(default_factory=dict)
    classrooms: dict[str, Classroom] = field(default_factory=dict)
    activities: dict[str, Activity] = field(default_factory=dict)


# ---------- 選課人數 ----------

def enrolled_count(catalog: SchoolCatalog, course_id: str) -> int:
    return sum(1 for student in catalog.students.values() if course_id in student.enrolled_courses)


def remaining_seats(catalog: SchoolCatalog, course_id: str) -> int:
    course = catalog.courses[course_id]
    return course.capacity - enrolled_count(catalog, course_id)


# ---------- 課程 ----------

def add_course(catalog: SchoolCatalog, course: Course) -> list[str]:
    errors = validate_course(course)
    if course.course_id in catalog.courses:
        errors.insert(0, "課程代號不得重複")
    if not errors:
        catalog.courses[course.course_id] = course
    return errors


def update_course(catalog: SchoolCatalog, course_id: str, /, **changes: Any) -> list[str]:
    if course_id not in catalog.courses:
        return [f"課程 {course_id} 不存在"]

    allowed = {f.name for f in fields(Course)} - {"course_id"}
    unknown = sorted(set(changes) - allowed)
    if unknown:
        return [f"不可修改的欄位: {', '.join(unknown)}"]

    updated = replace(catalog.courses[course_id], **changes)
    errors = validate_course(updated)
    count = enrolled_count(catalog, course_id)
    if isinstance(updated.capacity, int) and updated.capacity < count:
        errors.append(f"人數上限 {updated.capacity} 小於目前選課人數 {count}")
    if not errors:
        catalog.courses[course_id] = updated
    return errors


def delete_course(catalog: SchoolCatalog, course_id: str) -> bool:
    """刪除課程；不存在或仍有學生選修時回傳 False，資料不變。"""
    if course_id not in catalog.courses or enrolled_count(catalog, course_id) > 0:
        return False
    del catalog.courses[course_id]
    return True


def cancel_course(catalog: SchoolCatalog, course_id: str) -> list[str]:
    """課程取消程序：先替所有選修學生退選，再刪除課程。回傳受影響學號。"""
    if course_id not in catalog.courses:
        return []
    affected: list[str] = []
    for student in catalog.students.values():
        if course_id in student.enrolled_courses:
            student.enrolled_courses.remove(course_id)
            affected.append(student.student_id)
    del catalog.courses[course_id]
    return sorted(affected)


def find_courses(
    catalog: SchoolCatalog,
    course_id: str | None = None,
    teacher: str | None = None,
    day: int | None = None,
    required: bool | None = None,
    min_remaining: int | None = None,
) -> list[Course]:
    """多條件查詢；未給的條件不篩選。course_id 以前綴比對（例如 "CS"）。結果依代號排序。"""
    results: list[Course] = []
    for course in catalog.courses.values():
        if course_id is not None and not course.course_id.startswith(course_id):
            continue
        if teacher is not None and course.teacher != teacher:
            continue
        if day is not None and all(slot.day != day for slot in course.time_slots):
            continue
        if required is not None and course.required != required:
            continue
        if min_remaining is not None and remaining_seats(catalog, course.course_id) < min_remaining:
            continue
        results.append(course)
    return sorted(results, key=lambda c: c.course_id)


# ---------- 學生 ----------

def _student_course_errors(catalog: SchoolCatalog, student: Student) -> list[str]:
    return [f"已選課程 {cid} 不存在" for cid in student.enrolled_courses if cid not in catalog.courses]


def add_student(catalog: SchoolCatalog, student: Student) -> list[str]:
    errors = validate_student(student) + _student_course_errors(catalog, student)
    if student.student_id in catalog.students:
        errors.insert(0, "學號不得重複")
    if not errors:
        catalog.students[student.student_id] = student
    return errors


def update_student(catalog: SchoolCatalog, student_id: str, /, **changes: Any) -> list[str]:
    if student_id not in catalog.students:
        return [f"學生 {student_id} 不存在"]

    allowed = {f.name for f in fields(Student)} - {"student_id"}
    unknown = sorted(set(changes) - allowed)
    if unknown:
        return [f"不可修改的欄位: {', '.join(unknown)}"]

    original = catalog.students[student_id]
    updated = replace(original, **changes)
    if "enrolled_courses" not in changes:
        updated.enrolled_courses = list(original.enrolled_courses)
    errors = validate_student(updated) + _student_course_errors(catalog, updated)
    if not errors:
        catalog.students[student_id] = updated
    return errors


def delete_student(catalog: SchoolCatalog, student_id: str) -> bool:
    if student_id not in catalog.students:
        return False
    del catalog.students[student_id]
    return True


def find_students(
    catalog: SchoolCatalog,
    student_id: str | None = None,
    department: str | None = None,
    course_id: str | None = None,
) -> list[Student]:
    """依學號前綴、系級、已選課程查詢學生。結果依學號排序。"""
    results: list[Student] = []
    for student in catalog.students.values():
        if student_id is not None and not student.student_id.startswith(student_id):
            continue
        if department is not None and student.department != department:
            continue
        if course_id is not None and course_id not in student.enrolled_courses:
            continue
        results.append(student)
    return sorted(results, key=lambda s: s.student_id)


# ---------- 教室 ----------

def add_classroom(catalog: SchoolCatalog, classroom: Classroom) -> list[str]:
    errors = validate_classroom(classroom)
    if classroom.room_id in catalog.classrooms:
        errors.insert(0, "教室代號不得重複")
    if not errors:
        catalog.classrooms[classroom.room_id] = classroom
    return errors


def update_classroom(catalog: SchoolCatalog, room_id: str, /, **changes: Any) -> list[str]:
    if room_id not in catalog.classrooms:
        return [f"教室 {room_id} 不存在"]

    allowed = {f.name for f in fields(Classroom)} - {"room_id"}
    unknown = sorted(set(changes) - allowed)
    if unknown:
        return [f"不可修改的欄位: {', '.join(unknown)}"]

    updated = replace(catalog.classrooms[room_id], **changes)
    errors = validate_classroom(updated)
    if not errors:
        catalog.classrooms[room_id] = updated
    return errors


def delete_classroom(catalog: SchoolCatalog, room_id: str) -> bool:
    """刪除教室；不存在或仍有課程使用時回傳 False。"""
    if room_id not in catalog.classrooms:
        return False
    if any(course.classroom == room_id for course in catalog.courses.values()):
        return False
    del catalog.classrooms[room_id]
    return True


def find_classrooms(
    catalog: SchoolCatalog,
    building: str | None = None,
    min_capacity: int | None = None,
    equipment: list[str] | None = None,
) -> list[Classroom]:
    results: list[Classroom] = []
    for room in catalog.classrooms.values():
        if building is not None and room.building != building:
            continue
        if min_capacity is not None and room.capacity < min_capacity:
            continue
        if equipment and not set(equipment) <= set(room.equipment):
            continue
        results.append(room)
    return sorted(results, key=lambda r: r.room_id)


# ---------- 活動（F4 完整功能於第 8 週擴充） ----------

def add_activity(catalog: SchoolCatalog, activity: Activity) -> list[str]:
    errors = validate_activity(activity)
    if activity.activity_id in catalog.activities:
        errors.insert(0, "活動代號不得重複")
    if activity.classroom and activity.classroom not in catalog.classrooms:
        errors.append(f"教室 {activity.classroom} 不存在")
    errors += [f"報名學生 {sid} 不存在" for sid in activity.participants if sid not in catalog.students]
    if not errors:
        catalog.activities[activity.activity_id] = activity
    return errors


def activities_of_student(catalog: SchoolCatalog, student_id: str) -> list[Activity]:
    """學生參加的活動；參加名單以活動的 participants 為唯一來源。結果依代號排序。"""
    found = [a for a in catalog.activities.values() if student_id in a.participants]
    return sorted(found, key=lambda a: a.activity_id)


# ---------- JSON 轉換與存取 ----------

def course_from_dict(data: dict[str, Any]) -> Course:
    try:
        slots = [TimeSlot(slot["day"], str(slot["period"])) for slot in data.get("time_slots", [])]
        return Course(
            course_id=data["course_id"],
            name=data["name"],
            credits=data["credits"],
            required=data["required"],
            teacher=data["teacher"],
            capacity=data["capacity"],
            classroom=data["classroom"],
            time_slots=slots,
        )
    except (KeyError, TypeError) as exc:
        raise ValueError(f"課程資料缺少欄位或格式錯誤: {exc}") from exc


def student_from_dict(data: dict[str, Any]) -> Student:
    try:
        return Student(
            student_id=data["student_id"],
            name=data["name"],
            department=data["department"],
            enrolled_courses=list(data.get("enrolled_courses", [])),
            credit_limit=data.get("credit_limit", 24),
        )
    except (KeyError, TypeError) as exc:
        raise ValueError(f"學生資料缺少欄位或格式錯誤: {exc}") from exc


def classroom_from_dict(data: dict[str, Any]) -> Classroom:
    try:
        return Classroom(
            room_id=data["room_id"],
            capacity=data["capacity"],
            equipment=list(data.get("equipment", [])),
            building=data.get("building", "校本部"),
        )
    except (KeyError, TypeError) as exc:
        raise ValueError(f"教室資料缺少欄位或格式錯誤: {exc}") from exc


def activity_from_dict(data: dict[str, Any]) -> Activity:
    try:
        slots = [TimeSlot(slot["day"], str(slot["period"])) for slot in data.get("time_slots", [])]
        return Activity(
            activity_id=data["activity_id"],
            name=data["name"],
            time_slots=slots,
            expected_participants=data["expected_participants"],
            activity_type=data.get("activity_type", "一般"),
            classroom=data.get("classroom", ""),
            venue_requirements=list(data.get("venue_requirements", [])),
            participants=list(data.get("participants", [])),
        )
    except (KeyError, TypeError) as exc:
        raise ValueError(f"活動資料缺少欄位或格式錯誤: {exc}") from exc


def catalog_from_dict(data: dict[str, Any]) -> tuple[SchoolCatalog, list[str]]:
    """把 JSON 物件轉成 SchoolCatalog。

    單筆資料錯誤只會略過該筆並記錄原因，不會讓整批載入失敗。
    依教室 → 課程 → 學生 → 活動的順序載入，讓學生的已選課程與活動的報名學生可以檢查是否存在。
    """
    catalog = SchoolCatalog()
    errors: list[str] = []
    sections = [
        ("classrooms", "教室", classroom_from_dict, add_classroom, "room_id"),
        ("courses", "課程", course_from_dict, add_course, "course_id"),
        ("students", "學生", student_from_dict, add_student, "student_id"),
        ("activities", "活動", activity_from_dict, add_activity, "activity_id"),
    ]
    for key, label, convert, add, id_field in sections:
        records = data.get(key)
        if records is None:
            records = []
        elif not isinstance(records, list):
            errors.append(f"{label}資料（{key}）格式錯誤：應為清單，實際為 {type(records).__name__}，已略過")
            continue
        for index, record in enumerate(records):
            name = record.get(id_field, f"#{index + 1}") if isinstance(record, dict) else f"#{index + 1}"
            try:
                item = convert(record)
            except (ValueError, AttributeError) as exc:
                errors.append(f"{label} {name}: {exc}")
                continue
            for message in add(catalog, item):
                errors.append(f"{label} {name}: {message}")
    return catalog, errors


def catalog_to_dict(catalog: SchoolCatalog) -> dict[str, Any]:
    def slot_list(item: Course | Activity) -> list[dict[str, Any]]:
        return [{"day": slot.day, "period": slot.period} for slot in item.time_slots]

    return {
        "courses": [
            {
                "course_id": c.course_id,
                "name": c.name,
                "credits": c.credits,
                "required": c.required,
                "teacher": c.teacher,
                "capacity": c.capacity,
                "classroom": c.classroom,
                "time_slots": slot_list(c),
            }
            for c in catalog.courses.values()
        ],
        "students": [
            {
                "student_id": s.student_id,
                "name": s.name,
                "department": s.department,
                "enrolled_courses": list(s.enrolled_courses),
                "credit_limit": s.credit_limit,
            }
            for s in catalog.students.values()
        ],
        "classrooms": [
            {
                "room_id": r.room_id,
                "capacity": r.capacity,
                "equipment": list(r.equipment),
                "building": r.building,
            }
            for r in catalog.classrooms.values()
        ],
        "activities": [
            {
                "activity_id": a.activity_id,
                "name": a.name,
                "time_slots": slot_list(a),
                "expected_participants": a.expected_participants,
                "activity_type": a.activity_type,
                "classroom": a.classroom,
                "venue_requirements": list(a.venue_requirements),
                "participants": list(a.participants),
            }
            for a in catalog.activities.values()
        ],
    }


def load_catalog(path: str | Path) -> tuple[SchoolCatalog, list[str]]:
    if not Path(path).exists():
        return SchoolCatalog(), [f"找不到資料檔：{path}"]
    try:
        data = load_school_data(path)
    except ValueError as exc:
        return SchoolCatalog(), [str(exc)]
    return catalog_from_dict(data)


def save_catalog(path: str | Path, catalog: SchoolCatalog) -> Path:
    return save_school_data(path, catalog_to_dict(catalog))
