from __future__ import annotations

from pathlib import Path

import pytest

from campus_planner.data_manager import SchoolCatalog, add_activity, add_classroom, add_course, add_student, load_catalog
from campus_planner.enrollment import (
    check_activity_join,
    check_enrollment,
    drop_course,
    enroll_course,
    format_check_result,
    join_activity,
    room_conflicts,
)
from campus_planner.models import Activity, Classroom, Course, Student, TimeSlot

SAMPLE = Path(__file__).resolve().parents[1] / "data" / "sample_school_data.json"


def course(course_id: str, slots: list[tuple[int, str]], credits: int = 3, capacity: int = 30, room: str = "A101") -> Course:
    return Course(course_id, f"課程{course_id}", credits, True, "林老師", capacity, room,
                  [TimeSlot(day, period) for day, period in slots])


@pytest.fixture
def catalog() -> SchoolCatalog:
    c = SchoolCatalog()
    for room in ("A101", "B201", "C305"):
        add_classroom(c, Classroom(room, 50, [], "資訊大樓"))
    add_course(c, course("MA101", [(2, "3"), (2, "4")], credits=4, room="B201"))
    add_course(c, course("CS101", [(1, "3"), (1, "4")], room="A101"))
    add_course(c, course("EN101", [(3, "1")], credits=2, room="C305"))
    add_student(c, Student("S001", "王小明", "資工系", ["MA101"], 24))
    add_activity(c, Activity("A001", "程式設計讀書會", [TimeSlot(4, "5")], 10, classroom="C305", participants=["S001"]))
    return c


# ---------- 正常案例 ----------

def test_enroll_without_conflict_succeeds(catalog: SchoolCatalog) -> None:
    result = enroll_course(catalog, "S001", "CS101")
    assert result.ok
    assert catalog.students["S001"].enrolled_courses == ["MA101", "CS101"]
    assert (result.current_credits, result.projected_credits, result.credit_limit) == (4, 7, 24)


def test_check_does_not_change_data(catalog: SchoolCatalog) -> None:
    assert check_enrollment(catalog, "S001", "CS101").ok
    assert catalog.students["S001"].enrolled_courses == ["MA101"]


def test_drop_course(catalog: SchoolCatalog) -> None:
    assert drop_course(catalog, "S001", "MA101") == []
    assert catalog.students["S001"].enrolled_courses == []


def test_join_activity_without_conflict(catalog: SchoolCatalog) -> None:
    add_activity(catalog, Activity("A002", "社團博覽會", [TimeSlot(6, "5")], 10))
    assert join_activity(catalog, "S001", "A002").ok
    assert "S001" in catalog.activities["A002"].participants


def test_success_output_format(catalog: SchoolCatalog) -> None:
    text = format_check_result(check_enrollment(catalog, "S001", "CS101"))
    assert "選課結果：成功" in text
    assert "加選後學分：7" in text


# ---------- 邊界案例 ----------

def test_credits_exactly_at_limit_allowed(catalog: SchoolCatalog) -> None:
    catalog.students["S001"].credit_limit = 7
    assert enroll_course(catalog, "S001", "CS101").ok


def test_last_seat_can_be_taken(catalog: SchoolCatalog) -> None:
    add_course(catalog, course("PE101", [(6, "3")], credits=1, capacity=2, room="C305"))
    add_student(catalog, Student("S002", "李小華", "資工系", ["PE101"], 24))
    assert enroll_course(catalog, "S001", "PE101").ok
    add_student(catalog, Student("S003", "陳大同", "資工系", [], 24))
    assert "課程已額滿（2/2）" in check_enrollment(catalog, "S003", "PE101").errors


def test_adjacent_periods_do_not_conflict(catalog: SchoolCatalog) -> None:
    add_course(catalog, course("CS201", [(2, "5"), (2, "6")], room="A101"))
    assert check_enrollment(catalog, "S001", "CS201").ok


def test_same_period_on_another_day_does_not_conflict(catalog: SchoolCatalog) -> None:
    add_course(catalog, course("CS202", [(3, "3"), (3, "4")], room="A101"))
    assert check_enrollment(catalog, "S001", "CS202").ok


def test_capacity_counts_real_enrollment_not_student_course_count(catalog: SchoolCatalog) -> None:
    """缺陷 D1 回歸測試：學生已選很多門課，不代表欲加選的課已額滿。"""
    add_course(catalog, course("CS301", [(5, "1")], credits=1, capacity=2, room="A101"))
    catalog.students["S001"].enrolled_courses = ["MA101", "EN101"]
    assert check_enrollment(catalog, "S001", "CS301").ok


# ---------- 錯誤與衝突案例 ----------

def test_student_time_conflict(catalog: SchoolCatalog) -> None:
    add_course(catalog, course("CS102", [(2, "4"), (2, "5")], room="A101"))
    result = check_enrollment(catalog, "S001", "CS102")
    assert [c.describe() for c in result.conflicts] == ["星期二第 4 節｜已選課程：MA101 課程MA101"]


def test_activity_conflict(catalog: SchoolCatalog) -> None:
    add_course(catalog, course("CS103", [(4, "5")], room="A101"))
    result = check_enrollment(catalog, "S001", "CS103")
    assert [c.kind for c in result.conflicts] == ["已參加活動"]


def test_room_conflict(catalog: SchoolCatalog) -> None:
    add_course(catalog, course("CS104", [(1, "4"), (6, "1")], room="A101"))
    result = check_enrollment(catalog, "S001", "CS104")
    assert [(c.kind, c.other_id, c.periods) for c in result.conflicts] == [("教室衝堂", "CS101", ("4",))]


def test_room_conflicts_include_activities(catalog: SchoolCatalog) -> None:
    found = room_conflicts(catalog, "C305", [TimeSlot(4, "5"), TimeSlot(3, "1")])
    assert [c.other_id for c in found] == ["EN101", "A001"]


def test_all_conflicts_listed_and_sorted_by_day_and_period(catalog: SchoolCatalog) -> None:
    """F2 驗收：一次列出所有衝突，依星期及節次排序，且不因某項通過就忽略其他限制。"""
    add_course(catalog, course("CS120", [(4, "5"), (2, "4"), (2, "3"), (1, "3")], credits=21, capacity=1, room="A101"))
    add_student(catalog, Student("S002", "李小華", "資工系", ["CS120"], 24))
    result = check_enrollment(catalog, "S001", "CS120")
    assert [c.describe() for c in result.conflicts] == [
        "星期一第 3 節｜教室衝堂：CS101 課程CS101",
        "星期二第 3、4 節｜已選課程：MA101 課程MA101",
        "星期四第 5 節｜已參加活動：A001 程式設計讀書會",
    ]
    assert result.errors == ["加選後學分 25 超過上限 24", "課程已額滿（1/1）"]


def test_failed_enrollment_keeps_data(catalog: SchoolCatalog) -> None:
    add_course(catalog, course("CS102", [(2, "3")], room="A101"))
    assert not enroll_course(catalog, "S001", "CS102").ok
    assert catalog.students["S001"].enrolled_courses == ["MA101"]


def test_credit_limit_exceeded(catalog: SchoolCatalog) -> None:
    catalog.students["S001"].credit_limit = 6
    assert check_enrollment(catalog, "S001", "CS101").errors == ["加選後學分 7 超過上限 6"]


def test_unknown_student_and_course() -> None:
    assert check_enrollment(SchoolCatalog(), "S999", "XX999").errors == ["學生 S999 不存在", "課程 XX999 不存在"]


def test_already_enrolled(catalog: SchoolCatalog) -> None:
    assert "已選修 MA101，不可重複加選" in check_enrollment(catalog, "S001", "MA101").errors


def test_drop_course_not_enrolled(catalog: SchoolCatalog) -> None:
    assert drop_course(catalog, "S001", "CS101") == ["學生 S001 沒有選修 CS101"]


def test_activity_join_conflicts_with_course_and_activity(catalog: SchoolCatalog) -> None:
    add_activity(catalog, Activity("A003", "迎新", [TimeSlot(2, "4"), TimeSlot(4, "5")], 10))
    result = check_activity_join(catalog, "S001", "A003")
    assert [(c.kind, c.other_id) for c in result.conflicts] == [("已選課程", "MA101"), ("已參加活動", "A001")]
    assert not join_activity(catalog, "S001", "A003").ok
    assert catalog.activities["A003"].participants == []


def test_activity_full(catalog: SchoolCatalog) -> None:
    add_student(catalog, Student("S002", "李小華", "資工系", [], 24))
    add_activity(catalog, Activity("A004", "講座", [TimeSlot(6, "1")], 1, participants=["S002"]))
    assert "活動報名已額滿（1/1）" in check_activity_join(catalog, "S001", "A004").errors


def test_failure_output_format(catalog: SchoolCatalog) -> None:
    add_course(catalog, course("CS102", [(2, "3"), (2, "4")], room="A101"))
    text = format_check_result(check_enrollment(catalog, "S001", "CS102"))
    assert "選課結果：失敗" in text
    assert "衝突 1：星期二第 3、4 節｜已選課程：MA101 課程MA101" in text


def test_sample_data_has_full_course() -> None:
    catalog, errors = load_catalog(SAMPLE)
    assert errors == []
    assert "課程已額滿（2/2）" in check_enrollment(catalog, "S015", "PE101").errors


def test_activities_saved_and_loaded(catalog: SchoolCatalog, tmp_path: Path) -> None:
    """缺陷 D4 回歸測試：儲存再載入後，活動資料與報名名單仍保留。"""
    from campus_planner.data_manager import save_catalog

    path = tmp_path / "school.json"
    save_catalog(path, catalog)
    loaded, errors = load_catalog(path)
    assert errors == []
    assert loaded.activities == catalog.activities
