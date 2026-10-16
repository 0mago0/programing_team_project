from __future__ import annotations

import json
from pathlib import Path

import pytest

from campus_planner.data_manager import (
    SchoolCatalog,
    add_classroom,
    add_course,
    add_student,
    cancel_course,
    delete_classroom,
    delete_course,
    delete_student,
    enrolled_count,
    find_classrooms,
    find_courses,
    find_students,
    load_catalog,
    remaining_seats,
    save_catalog,
    update_classroom,
    update_course,
    update_student,
)
from campus_planner.models import Classroom, Course, Student, TimeSlot

SAMPLE = Path(__file__).resolve().parents[1] / "data" / "sample_school_data.json"


def make_course(course_id: str = "CS101", **overrides) -> Course:
    values = dict(
        course_id=course_id,
        name="Python 程式設計",
        credits=3,
        required=True,
        teacher="林老師",
        capacity=30,
        classroom="A101",
        time_slots=[TimeSlot(1, "3"), TimeSlot(1, "4")],
    )
    values.update(overrides)
    return Course(**values)


@pytest.fixture
def catalog() -> SchoolCatalog:
    c = SchoolCatalog()
    add_classroom(c, Classroom("A101", 50, ["投影機"], "資訊大樓"))
    add_course(c, make_course("CS101"))
    add_course(c, make_course("MA101", name="微積分", teacher="張老師", required=False,
                              capacity=2, time_slots=[TimeSlot(3, "1")]))
    add_student(c, Student("S001", "王小明", "資工系", ["CS101"], 24))
    add_student(c, Student("S002", "李小華", "電機系", ["CS101", "MA101"], 24))
    return c


# ---------- 正常案例 ----------

def test_sample_data_meets_week6_acceptance() -> None:
    catalog, errors = load_catalog(SAMPLE)
    assert errors == []
    assert len(catalog.courses) >= 20
    assert len(catalog.students) >= 15
    assert len(catalog.classrooms) >= 5


def test_enrolled_count_and_remaining_seats(catalog: SchoolCatalog) -> None:
    assert enrolled_count(catalog, "CS101") == 2
    assert remaining_seats(catalog, "CS101") == 28
    assert remaining_seats(catalog, "MA101") == 1


def test_find_courses_by_each_condition(catalog: SchoolCatalog) -> None:
    assert [c.course_id for c in find_courses(catalog, course_id="CS")] == ["CS101"]
    assert [c.course_id for c in find_courses(catalog, teacher="張老師")] == ["MA101"]
    assert [c.course_id for c in find_courses(catalog, day=3)] == ["MA101"]
    assert [c.course_id for c in find_courses(catalog, required=False)] == ["MA101"]
    assert [c.course_id for c in find_courses(catalog, min_remaining=2)] == ["CS101"]
    assert [c.course_id for c in find_courses(catalog)] == ["CS101", "MA101"]


def test_find_courses_combines_conditions(catalog: SchoolCatalog) -> None:
    assert find_courses(catalog, teacher="林老師", day=3) == []


def test_update_course_success(catalog: SchoolCatalog) -> None:
    assert update_course(catalog, "CS101", teacher="王老師", capacity=40) == []
    assert catalog.courses["CS101"].teacher == "王老師"
    assert catalog.courses["CS101"].capacity == 40


def test_delete_course_without_students(catalog: SchoolCatalog) -> None:
    add_course(catalog, make_course("CS999", time_slots=[TimeSlot(5, "1")]))
    assert delete_course(catalog, "CS999") is True
    assert "CS999" not in catalog.courses


def test_cancel_course_drops_students_then_deletes(catalog: SchoolCatalog) -> None:
    assert cancel_course(catalog, "CS101") == ["S001", "S002"]
    assert "CS101" not in catalog.courses
    assert catalog.students["S001"].enrolled_courses == []
    assert catalog.students["S002"].enrolled_courses == ["MA101"]


def test_find_students_by_course_and_department(catalog: SchoolCatalog) -> None:
    assert [s.student_id for s in find_students(catalog, course_id="MA101")] == ["S002"]
    assert [s.student_id for s in find_students(catalog, department="資工系")] == ["S001"]


def test_update_and_delete_student(catalog: SchoolCatalog) -> None:
    assert update_student(catalog, "S001", credit_limit=20) == []
    assert catalog.students["S001"].credit_limit == 20
    assert delete_student(catalog, "S001") is True
    assert "S001" not in catalog.students


def test_classroom_management(catalog: SchoolCatalog) -> None:
    assert add_classroom(catalog, Classroom("B201", 40, ["白板"], "工程大樓")) == []
    assert [r.room_id for r in find_classrooms(catalog, min_capacity=45)] == ["A101"]
    assert [r.room_id for r in find_classrooms(catalog, equipment=["白板"])] == ["B201"]
    assert update_classroom(catalog, "B201", capacity=80) == []
    assert catalog.classrooms["B201"].capacity == 80
    assert delete_classroom(catalog, "B201") is True


def test_save_and_load_catalog_round_trip(catalog: SchoolCatalog, tmp_path: Path) -> None:
    path = tmp_path / "school.json"
    save_catalog(path, catalog)
    loaded, errors = load_catalog(path)
    assert errors == []
    assert loaded == catalog


# ---------- 邊界案例 ----------

def test_capacity_one_is_allowed() -> None:
    assert add_course(SchoolCatalog(), make_course(capacity=1)) == []


def test_day_seven_and_period_c_are_valid() -> None:
    assert add_course(SchoolCatalog(), make_course(time_slots=[TimeSlot(7, "c")])) == []


def test_day_one_and_period_one_are_valid() -> None:
    assert add_course(SchoolCatalog(), make_course(time_slots=[TimeSlot(1, "1")])) == []


def test_full_course_has_zero_remaining(catalog: SchoolCatalog) -> None:
    add_student(catalog, Student("S003", "陳大同", "資工系", ["MA101"], 24))
    assert remaining_seats(catalog, "MA101") == 0
    assert find_courses(catalog, min_remaining=1, course_id="MA") == []


def test_capacity_can_shrink_to_current_enrollment(catalog: SchoolCatalog) -> None:
    assert update_course(catalog, "CS101", capacity=2) == []


def test_course_with_multiple_weekly_slots_found_on_each_day() -> None:
    catalog = SchoolCatalog()
    add_course(catalog, make_course(time_slots=[TimeSlot(1, "2"), TimeSlot(4, "2")]))
    assert len(find_courses(catalog, day=1)) == 1
    assert len(find_courses(catalog, day=4)) == 1
    assert find_courses(catalog, day=2) == []


# ---------- 錯誤案例 ----------

@pytest.mark.parametrize("credits", [0, -3, 3.5, True, "3"])
def test_reject_invalid_credits(credits) -> None:
    assert "學分必須為正整數" in add_course(SchoolCatalog(), make_course(credits=credits))


@pytest.mark.parametrize("period", ["d", "0", "10", ""])
def test_reject_invalid_period(period: str) -> None:
    errors = add_course(SchoolCatalog(), make_course(time_slots=[TimeSlot(1, period)]))
    assert f"節次不合法: {period}" in errors


@pytest.mark.parametrize("day", [0, 8])
def test_reject_invalid_day(day: int) -> None:
    errors = add_course(SchoolCatalog(), make_course(time_slots=[TimeSlot(day, "1")]))
    assert f"星期不合法: {day}" in errors


def test_reject_duplicate_slot_in_same_course() -> None:
    errors = add_course(SchoolCatalog(), make_course(time_slots=[TimeSlot(1, "3"), TimeSlot(1, "3")]))
    assert "時段重複: 星期1 第3節" in errors


def test_reject_duplicate_student_id(catalog: SchoolCatalog) -> None:
    assert "學號不得重複" in add_student(catalog, Student("S001", "另一人", "資工系", [], 24))
    assert catalog.students["S001"].name == "王小明"


def test_reject_student_enrolled_in_unknown_course(catalog: SchoolCatalog) -> None:
    assert "已選課程 XX999 不存在" in add_student(catalog, Student("S009", "測試", "資工系", ["XX999"], 24))
    assert "S009" not in catalog.students


def test_failed_course_update_keeps_original(catalog: SchoolCatalog) -> None:
    before = catalog.courses["CS101"]
    errors = update_course(catalog, "CS101", credits=0, time_slots=[TimeSlot(1, "d")])
    assert "學分必須為正整數" in errors
    assert catalog.courses["CS101"] is before
    assert catalog.courses["CS101"].credits == 3


def test_reject_capacity_below_enrollment(catalog: SchoolCatalog) -> None:
    assert "人數上限 1 小於目前選課人數 2" in update_course(catalog, "CS101", capacity=1)
    assert catalog.courses["CS101"].capacity == 30


def test_course_id_cannot_be_changed(catalog: SchoolCatalog) -> None:
    assert update_course(catalog, "CS101", course_id="CS999") == ["不可修改的欄位: course_id"]


def test_update_unknown_records() -> None:
    catalog = SchoolCatalog()
    assert update_course(catalog, "NOPE", name="x") == ["課程 NOPE 不存在"]
    assert update_student(catalog, "NOPE", name="x") == ["學生 NOPE 不存在"]
    assert update_classroom(catalog, "NOPE", capacity=1) == ["教室 NOPE 不存在"]


def test_delete_unknown_course_returns_false() -> None:
    assert delete_course(SchoolCatalog(), "NOPE") is False


def test_classroom_in_use_cannot_be_deleted(catalog: SchoolCatalog) -> None:
    assert delete_classroom(catalog, "A101") is False
    assert "A101" in catalog.classrooms


def test_reject_invalid_and_duplicate_classroom(catalog: SchoolCatalog) -> None:
    assert "教室代號不得重複" in add_classroom(catalog, Classroom("A101", 10, [], "資訊大樓"))
    assert "教室容量必須為正整數" in add_classroom(catalog, Classroom("Z001", 0, [], "資訊大樓"))


def test_bad_record_does_not_stop_loading(tmp_path: Path) -> None:
    data = json.loads(SAMPLE.read_text(encoding="utf-8"))
    data["courses"].append({"course_id": "BAD1", "name": "缺欄位"})
    data["courses"].append({**data["courses"][0], "course_id": "BAD2", "credits": 0})
    path = tmp_path / "broken.json"
    path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")

    catalog, errors = load_catalog(path)
    assert len(catalog.courses) == 20
    assert any(e.startswith("課程 BAD1:") for e in errors)
    assert "課程 BAD2: 學分必須為正整數" in errors


def test_broken_json_file_returns_error(tmp_path: Path) -> None:
    path = tmp_path / "broken.json"
    path.write_text("{not json", encoding="utf-8")
    catalog, errors = load_catalog(path)
    assert catalog == SchoolCatalog()
    assert errors and errors[0].startswith("JSON 格式錯誤")


def test_student_id_and_room_id_cannot_be_changed(catalog: SchoolCatalog) -> None:
    assert update_student(catalog, "S001", student_id="S999") == ["不可修改的欄位: student_id"]
    assert update_classroom(catalog, "A101", room_id="Z999") == ["不可修改的欄位: room_id"]
