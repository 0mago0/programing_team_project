from __future__ import annotations

from pathlib import Path

import pytest

from campus_planner.activities import (
    assign_room,
    cancel_activity,
    check_registration,
    create_activity,
    find_activities,
    find_available_rooms,
    register_activity,
    time_range_to_slots,
    unregister_activity,
    update_activity,
)
from campus_planner.data_manager import SchoolCatalog, add_classroom, add_course, add_student, load_catalog
from campus_planner.models import Activity, Classroom, Course, Student, TimeSlot

SAMPLE = Path(__file__).resolve().parents[1] / "data" / "sample_school_data.json"


@pytest.fixture
def catalog() -> SchoolCatalog:
    c = SchoolCatalog()
    add_classroom(c, Classroom("R10", 10, ["投影機"], "資訊大樓"))
    add_classroom(c, Classroom("R30", 30, ["投影機", "電腦"], "資訊大樓"))
    add_classroom(c, Classroom("R60", 60, ["白板"], "工程大樓"))
    add_course(c, Course("CS101", "程式設計", 3, True, "林老師", 30, "R30", [TimeSlot(1, "3"), TimeSlot(1, "4")]))
    for i in range(1, 13):
        add_student(c, Student(f"S{i:03d}", f"學生{i}", "資工系", [], 24))
    c.students["S001"].enrolled_courses.append("CS101")
    return c


def activity(activity_id: str, slots: list[tuple[int, str]], expected: int = 10, room: str = "",
             equipment: list[str] | None = None, kind: str = "講座") -> Activity:
    return Activity(activity_id, f"活動{activity_id}", [TimeSlot(d, p) for d, p in slots], expected, kind,
                    room, equipment or [])


# ---------- 正常案例 ----------

def test_time_range_converts_to_periods() -> None:
    assert time_range_to_slots("2026-11-05", "10:10", "12:00") == [TimeSlot(4, "3"), TimeSlot(4, "4")]


def test_find_available_rooms_sorted_by_capacity(catalog: SchoolCatalog) -> None:
    result = find_available_rooms(catalog, [TimeSlot(2, "1")], 8)
    assert [r.room_id for r in result.available] == ["R10", "R30", "R60"]


def test_create_activity_with_room(catalog: SchoolCatalog) -> None:
    assert create_activity(catalog, activity("A1", [(2, "5")], 20, "R30", ["電腦"])) == []
    assert catalog.activities["A1"].classroom == "R30"


def test_assign_room(catalog: SchoolCatalog) -> None:
    create_activity(catalog, activity("A1", [(2, "5")], 25))
    assert assign_room(catalog, "A1", "R30") == []
    assert catalog.activities["A1"].classroom == "R30"


def test_update_activity(catalog: SchoolCatalog) -> None:
    create_activity(catalog, activity("A1", [(2, "5")], 10, "R30"))
    assert update_activity(catalog, "A1", name="改名", time_slots=[TimeSlot(3, "5")]) == []
    assert catalog.activities["A1"].name == "改名"


def test_multiple_registrations(catalog: SchoolCatalog) -> None:
    create_activity(catalog, activity("A1", [(2, "5")], 10, "R30"))
    for sid in ("S002", "S003", "S004"):
        assert register_activity(catalog, sid, "A1").ok
    assert catalog.activities["A1"].participants == ["S002", "S003", "S004"]


def test_cancel_activity_returns_participants(catalog: SchoolCatalog) -> None:
    create_activity(catalog, activity("A1", [(2, "5")], 10))
    register_activity(catalog, "S003", "A1")
    register_activity(catalog, "S002", "A1")
    assert cancel_activity(catalog, "A1") == ["S002", "S003"]
    assert "A1" not in catalog.activities


def test_find_activities_by_conditions(catalog: SchoolCatalog) -> None:
    create_activity(catalog, activity("A1", [(2, "5")], 10, "R30", kind="講座"))
    create_activity(catalog, activity("A2", [(3, "5")], 10, "R60", kind="社團"))
    register_activity(catalog, "S002", "A2")
    assert [a.activity_id for a in find_activities(catalog, activity_type="社團")] == ["A2"]
    assert [a.activity_id for a in find_activities(catalog, day=2)] == ["A1"]
    assert [a.activity_id for a in find_activities(catalog, classroom="R30")] == ["A1"]
    assert [a.activity_id for a in find_activities(catalog, student_id="S002")] == ["A2"]


# ---------- 邊界案例 ----------

def test_time_range_exactly_one_period() -> None:
    assert time_range_to_slots("2026-11-08", "10:10", "11:00") == [TimeSlot(7, "3")]


def test_evening_periods() -> None:
    assert [s.period for s in time_range_to_slots("2026-11-02", "18:30", "21:10")] == ["a", "b", "c"]


def test_room_capacity_exactly_equal(catalog: SchoolCatalog) -> None:
    assert create_activity(catalog, activity("A1", [(2, "5")], 10, "R10")) == []


def test_registration_up_to_room_capacity(catalog: SchoolCatalog) -> None:
    create_activity(catalog, activity("A1", [(2, "5")], 10, "R10"))
    for i in range(2, 12):
        assert register_activity(catalog, f"S{i:03d}", "A1").ok
    result = check_registration(catalog, "S012", "A1")
    assert "活動報名已額滿（10/10）" in result.errors
    assert "教室 R10 容量已滿（10/10）" in result.errors


def test_adjacent_period_in_same_room_allowed(catalog: SchoolCatalog) -> None:
    assert create_activity(catalog, activity("A1", [(1, "5")], 10, "R30")) == []


# ---------- 錯誤與衝突案例 ----------

@pytest.mark.parametrize("date, start, end, message", [
    ("2026/11/05", "10:10", "11:00", "日期格式錯誤"),
    ("2026-11-05", "10點", "11:00", "時間格式錯誤"),
    ("2026-11-05", "12:00", "10:00", "開始時間必須早於結束時間"),
    ("2026-11-05", "12:05", "12:10", "沒有對應的節次"),
])
def test_time_range_errors(date: str, start: str, end: str, message: str) -> None:
    with pytest.raises(ValueError, match=message):
        time_range_to_slots(date, start, end)


def test_venue_conflict_with_course(catalog: SchoolCatalog) -> None:
    errors = create_activity(catalog, activity("A1", [(1, "4")], 10, "R30"))
    assert errors == ["時段已被使用：星期一第 4 節 CS101 程式設計"]
    assert "A1" not in catalog.activities


def test_venue_conflict_with_other_activity(catalog: SchoolCatalog) -> None:
    create_activity(catalog, activity("A1", [(2, "5")], 10, "R60"))
    assert assign_room(catalog, "A1", "R60") == []
    create_activity(catalog, activity("A2", [(2, "5")], 10))
    assert assign_room(catalog, "A2", "R60") == ["時段已被使用：星期二第 5 節 A1 活動A1"]
    assert catalog.activities["A2"].classroom == ""


def test_no_suitable_room_lists_unmet_conditions(catalog: SchoolCatalog) -> None:
    result = find_available_rooms(catalog, [TimeSlot(1, "3")], 40, ["投影機"])
    assert result.available == []
    assert result.unmet == {
        "R10": ["容量 10 小於需求人數 40"],
        "R30": ["容量 30 小於需求人數 40", "時段已被使用：星期一第 3 節 CS101 程式設計"],
        "R60": ["缺少設備：投影機"],
    }


def test_room_full_rejected(catalog: SchoolCatalog) -> None:
    assert create_activity(catalog, activity("A1", [(2, "5")], 11, "R10")) == ["容量 10 小於需求人數 11"]


def test_failed_update_keeps_original(catalog: SchoolCatalog) -> None:
    create_activity(catalog, activity("A1", [(2, "5")], 10, "R30"))
    assert update_activity(catalog, "A1", time_slots=[TimeSlot(1, "3")]) == ["時段已被使用：星期一第 3 節 CS101 程式設計"]
    assert catalog.activities["A1"].time_slots == [TimeSlot(2, "5")]


def test_update_rejects_id_and_participants(catalog: SchoolCatalog) -> None:
    create_activity(catalog, activity("A1", [(2, "5")], 10))
    assert update_activity(catalog, "A1", participants=["S002"]) == ["不可修改的欄位: participants"]
    assert update_activity(catalog, "NOPE", name="x") == ["活動 NOPE 不存在"]


def test_registration_conflicts_with_course(catalog: SchoolCatalog) -> None:
    create_activity(catalog, activity("A1", [(1, "3")], 10))
    result = register_activity(catalog, "S001", "A1")
    assert [c.other_id for c in result.conflicts] == ["CS101"]
    assert catalog.activities["A1"].participants == []


def test_unregister_errors(catalog: SchoolCatalog) -> None:
    create_activity(catalog, activity("A1", [(2, "5")], 10))
    assert unregister_activity(catalog, "S002", "A1") == ["學生 S002 沒有報名 A1"]
    assert unregister_activity(catalog, "S002", "NOPE") == ["活動 NOPE 不存在"]


def test_ten_activities_acceptance_scenario() -> None:
    """F4 驗收：以範例資料模擬 10 項活動，含多人報名、活動取消、教室額滿與場地衝突。"""
    catalog, errors = load_catalog(SAMPLE)
    assert errors == [] and len(catalog.activities) == 4
    new = [
        activity("A005", [(2, "a")], 30, "L102", kind="讀書會"),
        activity("A006", [(3, "9")], 40, "A205", kind="講座"),
        activity("A007", [(6, "1"), (6, "2")], 60, "C305", kind="社團"),
        activity("A008", [(7, "1")], 20, "B201", kind="系學會"),
        activity("A009", [(4, "c")], 2, "L102", kind="讀書會"),
        activity("A010", [(2, "b")], 45, "B201", kind="講座"),
    ]
    for item in new:
        assert create_activity(catalog, item) == []
    assert len(catalog.activities) == 10

    for sid in ("S014", "S015", "S009"):                                      # 多人報名
        assert register_activity(catalog, sid, "A005").ok
    assert register_activity(catalog, "S014", "A009").ok and register_activity(catalog, "S015", "A009").ok
    assert "活動報名已額滿（2/2）" in check_registration(catalog, "S009", "A009").errors   # 額滿
    assert cancel_activity(catalog, "A010") == []                              # 活動取消
    conflict = create_activity(catalog, activity("A011", [(1, "3")], 10, "A101"))  # 場地衝突（CS101）
    assert conflict == ["時段已被使用：星期一第 3 節 CS101 計算機程式設計"]
    too_big = create_activity(catalog, activity("A012", [(7, "2")], 100, "C305"))  # 教室容量不足
    assert too_big == ["容量 80 小於需求人數 100"]
    assert len(catalog.activities) == 9
