from __future__ import annotations

import pytest

from campus_planner.data_manager import SchoolCatalog, add_activity, add_course, add_student
from campus_planner.models import Activity, Course, Student, TimeSlot
from campus_planner.timetable import (
    build_student_timetable,
    build_weekly_matrix,
    conflicts_in,
    entries_at,
    entries_on_day,
    find_available_slots,
    find_free_blocks,
    place_course_in_timetable,
    render_timetable,
    slots_of,
    timetable_stats,
)


def course(course_id: str, slots: list[tuple[int, str]], credits: int = 3) -> Course:
    return Course(course_id, f"課程{course_id}", credits, True, "林老師", 30, "A101",
                  [TimeSlot(day, period) for day, period in slots])


@pytest.fixture
def catalog() -> SchoolCatalog:
    c = SchoolCatalog()
    add_course(c, course("CS101", [(1, "1"), (1, "2"), (3, "2")]))      # 一週上兩天
    add_course(c, course("MA101", [(1, "6"), (1, "7")], credits=4))      # 與 CS101 同一天
    add_course(c, course("EN101", [(7, "c")], credits=2))                 # 星期日第 c 節
    add_student(c, Student("S001", "王小明", "資工系", ["CS101", "MA101", "EN101"], 24))
    add_activity(c, Activity("A001", "讀書會", [TimeSlot(2, "5")], 10, participants=["S001"]))
    return c


# ---------- 正常案例 ----------

def test_timetable_is_7_by_12(catalog: SchoolCatalog) -> None:
    table = build_student_timetable(catalog, "S001")
    assert len(table) == 7
    assert all(len(row) == 12 for row in table)


def test_course_with_multiple_weekly_slots_shown_everywhere(catalog: SchoolCatalog) -> None:
    table = build_student_timetable(catalog, "S001")
    assert slots_of(table, "CS101") == [TimeSlot(1, "1"), TimeSlot(1, "2"), TimeSlot(3, "2")]


def test_activity_shown_in_timetable(catalog: SchoolCatalog) -> None:
    entry = entries_at(build_student_timetable(catalog, "S001"), 2, "5")[0]
    assert (entry.kind, entry.item_id) == ("活動", "A001")


def test_query_by_day_lists_multiple_courses_in_order(catalog: SchoolCatalog) -> None:
    day = entries_on_day(build_student_timetable(catalog, "S001"), 1)
    assert [(period, entry.item_id) for period, entry in day] == [
        ("1", "CS101"), ("2", "CS101"), ("6", "MA101"), ("7", "MA101")]


def test_stats(catalog: SchoolCatalog) -> None:
    stats = timetable_stats(catalog, "S001")
    assert stats["daily_periods"][1] == 4
    assert stats["daily_periods"][2] == 0          # 活動不計入上課節數
    assert stats["total_credits"] == 9
    assert stats["daily_gaps"][1] == 3             # 星期一第 3、4、5 節為空堂
    assert stats["total_gaps"] == 3


def test_render_contains_course_ids(catalog: SchoolCatalog) -> None:
    text = render_timetable(build_student_timetable(catalog, "S001"))
    assert "CS101" in text and "A001" in text


# ---------- 邊界案例 ----------

def test_three_consecutive_free_periods(catalog: SchoolCatalog) -> None:
    table = build_student_timetable(catalog, "S001")
    blocks = find_free_blocks(table, TimeSlot(1, "1"), TimeSlot(1, "c"), min_length=3)
    assert [(b.start, b.end, b.length) for b in blocks] == [("3", "5", 3), ("8", "c", 5)]


def test_cross_day_query_does_not_merge_days(catalog: SchoolCatalog) -> None:
    table = build_student_timetable(catalog, "S001")
    blocks = find_free_blocks(table, TimeSlot(1, "8"), TimeSlot(2, "3"))
    assert [(b.day, b.start, b.end) for b in blocks] == [(1, "8", "c"), (2, "1", "3")]


def test_day_seven_period_c(catalog: SchoolCatalog) -> None:
    table = build_student_timetable(catalog, "S001")
    assert entries_at(table, 7, "c")[0].item_id == "EN101"
    assert find_free_blocks(table, TimeSlot(7, "a"), TimeSlot(7, "c"))[0].end == "b"


def test_whole_free_day(catalog: SchoolCatalog) -> None:
    blocks = find_free_blocks(build_student_timetable(catalog, "S001"), TimeSlot(6, "1"), TimeSlot(6, "c"), 12)
    assert [(b.start, b.end, b.length) for b in blocks] == [("1", "c", 12)]


def test_overlapping_items_kept_in_same_cell(catalog: SchoolCatalog) -> None:
    add_activity(catalog, Activity("A002", "迎新", [TimeSlot(1, "1")], 10, participants=["S001"]))
    table = build_student_timetable(catalog, "S001")
    assert [e.item_id for e in entries_at(table, 1, "1")] == ["CS101", "A002"]
    assert len(conflicts_in(table)) == 1


# ---------- 錯誤案例 ----------

@pytest.mark.parametrize("day, period", [(0, "1"), (8, "1"), (1, "d")])
def test_invalid_query_raises(catalog: SchoolCatalog, day: int, period: str) -> None:
    with pytest.raises(ValueError):
        entries_at(build_student_timetable(catalog, "S001"), day, period)


def test_free_block_range_reversed(catalog: SchoolCatalog) -> None:
    with pytest.raises(ValueError, match="開始時段不可晚於結束時段"):
        find_free_blocks(build_student_timetable(catalog, "S001"), TimeSlot(2, "1"), TimeSlot(1, "1"))


def test_unknown_student() -> None:
    with pytest.raises(ValueError, match="學生 S999 不存在"):
        build_student_timetable(SchoolCatalog(), "S999")


def test_place_course_rejects_day_zero() -> None:
    """缺陷 D2 回歸測試：星期 0 不可被寫到星期日。"""
    with pytest.raises(ValueError, match="星期不合法: 0"):
        place_course_in_timetable(build_weekly_matrix(), course("X", [(0, "1")]))


def test_place_course_rejects_overwrite() -> None:
    """缺陷 D2 回歸測試：同一格已有課程時不可覆蓋。"""
    matrix = place_course_in_timetable(build_weekly_matrix(), course("A", [(1, "1")]))
    with pytest.raises(ValueError, match="時段衝突"):
        place_course_in_timetable(matrix, course("B", [(1, "1")]))
    assert matrix[0][0] == "A - 課程A"


def test_find_available_slots_out_of_range() -> None:
    """缺陷 D3 回歸測試：從第 b 節查 3 節超出範圍，不可靜默截斷。"""
    with pytest.raises(ValueError, match="查詢範圍超出節次"):
        find_available_slots(build_weekly_matrix(), 1, 10, 3)


def test_float_day_rejected_instead_of_crashing() -> None:
    """星期 1.0 會通過 F1 驗證（Code Review 第 4 項），F3 產生課表時須回報錯誤而不是 TypeError。"""
    c = SchoolCatalog()
    add_course(c, Course("X", "x", 3, True, "林老師", 10, "A101", [TimeSlot(1.0, "1")]))
    add_student(c, Student("S1", "王小明", "資工系", ["X"], 24))
    with pytest.raises(ValueError, match="星期不合法: 1.0"):
        build_student_timetable(c, "S1")
