"""F1～F6 整合測試：多個模組串在一起，確認共用同一份 SchoolCatalog 時結果一致。"""
from __future__ import annotations

from pathlib import Path

import pytest

from campus_planner.activities import create_activity, find_available_rooms, register_activity
from campus_planner.course_filter import FilterCriteria, filter_courses
from campus_planner.data_manager import SchoolCatalog, add_course, cancel_course, load_catalog
from campus_planner.enrollment import check_enrollment, drop_course, enroll_course
from campus_planner.models import Activity, Course, TimeSlot
from campus_planner.storage import load_data, save_data
from campus_planner.timetable import build_student_timetable, entries_at, timetable_stats

SAMPLE = Path(__file__).resolve().parents[1] / "data" / "sample_school_data.json"


@pytest.fixture
def catalog() -> SchoolCatalog:
    catalog, errors = load_catalog(SAMPLE)
    assert errors == []
    return catalog


# ---------- 正常案例 ----------

def test_enroll_then_timetable_shows_course(catalog: SchoolCatalog) -> None:
    assert enroll_course(catalog, "S015", "CS109").ok                       # F2
    table = build_student_timetable(catalog, "S015")                       # F3
    assert [e.item_id for e in entries_at(table, 1, "6")] == ["CS109"]
    assert timetable_stats(catalog, "S015")["total_credits"] == 3


@pytest.mark.parametrize("target", ["school.json", "csv_folder"])
def test_changes_survive_save_and_reload(catalog: SchoolCatalog, tmp_path: Path, target: str) -> None:
    """F6：加選、活動報名後儲存，重新載入（模擬重新啟動）後資料完全相同。"""
    enroll_course(catalog, "S015", "CS109")
    register_activity(catalog, "S015", "A002")
    save_data(tmp_path / target, catalog)
    reloaded, errors = load_data(tmp_path / target)
    assert errors == []
    assert reloaded == catalog
    assert build_student_timetable(reloaded, "S015") == build_student_timetable(catalog, "S015")


def test_filter_candidates_can_actually_be_enrolled(catalog: SchoolCatalog) -> None:
    """F5 篩出的候選課程，交給 F2 檢查時對沒有選課的學生都能加選。"""
    result = filter_courses(catalog, FilterCriteria(max_credits=22))
    assert result.candidates
    for cand in result.candidates:
        assert check_enrollment(catalog, "S015", cand.course.course_id).ok, cand.course.course_id


# ---------- 邊界案例 ----------

def test_drop_then_enroll_last_seat(catalog: SchoolCatalog) -> None:
    assert not check_enrollment(catalog, "S015", "PE101").ok               # 額滿 2/2
    assert drop_course(catalog, "S004", "PE101") == []
    assert enroll_course(catalog, "S015", "PE101").ok                      # 退選後剛好空出一位


def test_room_freed_after_course_cancelled(catalog: SchoolCatalog) -> None:
    slots = [TimeSlot(1, "3")]
    assert "A101" not in [r.room_id for r in find_available_rooms(catalog, slots, 10).available]
    cancel_course(catalog, "CS101")                                        # F1 課程取消程序
    assert "A101" in [r.room_id for r in find_available_rooms(catalog, slots, 10).available]


# ---------- 錯誤與衝突案例 ----------

def test_activity_and_course_share_conflict_check(catalog: SchoolCatalog) -> None:
    """F4 配置教室與 F2 加選使用同一套時段衝突檢查。"""
    assert create_activity(catalog, Activity("A100", "講座", [TimeSlot(2, "1")], 20, classroom="L102")) == []
    add_course(catalog, Course("CS300", "示範", 1, False, "林老師", 30, "L102", [TimeSlot(2, "1")]))
    result = check_enrollment(catalog, "S015", "CS300")
    assert [(c.kind, c.other_id) for c in result.conflicts] == [("教室衝堂", "A100")]


def test_filter_and_enrollment_agree_on_full_course(catalog: SchoolCatalog) -> None:
    assert "課程已額滿" in filter_courses(catalog, FilterCriteria()).rejected["PE101"]
    assert "課程已額滿（2/2）" in check_enrollment(catalog, "S015", "PE101").errors


def test_bad_participant_row_only_skips_that_row(catalog: SchoolCatalog, tmp_path: Path) -> None:
    save_data(tmp_path / "csv", catalog)
    with (tmp_path / "csv" / "activity_participants.csv").open("a", encoding="utf-8") as file:
        file.write("A001,S999\n")
    reloaded, errors = load_data(tmp_path / "csv")
    assert len(errors) == 1 and errors[0].endswith("學生 S999 不存在，已略過")
    assert reloaded.activities["A001"].participants == catalog.activities["A001"].participants
