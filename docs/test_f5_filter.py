from __future__ import annotations

import pytest

from campus_planner.course_filter import FilterCriteria, filter_courses, format_filter_result
from campus_planner.data_manager import SchoolCatalog, add_course, add_student
from campus_planner.models import Course, Student, TimeSlot


def course(course_id: str, slots: list[tuple[int, str]], credits: int = 3, capacity: int = 30) -> Course:
    return Course(course_id, f"課程{course_id}", credits, True, "林老師", capacity, "A101",
                  [TimeSlot(day, period) for day, period in slots])


@pytest.fixture
def catalog() -> SchoolCatalog:
    c = SchoolCatalog()
    add_course(c, course("REQ1", [(1, "1"), (1, "2")]))                 # 必修
    add_course(c, course("REQ2", [(2, "1"), (2, "2")], credits=4))      # 必修
    add_course(c, course("CS201", [(1, "2"), (1, "3")]))                # 與 REQ1 衝堂
    add_course(c, course("CS202", [(3, "1")], credits=2))               # 星期三
    add_course(c, course("CS203", [(4, "6"), (5, "6")]))                # 星期四、五
    add_course(c, course("CS204", [(1, "9")], credits=1, capacity=1))   # 額滿
    add_course(c, course("CS205", [(5, "a")], credits=2))               # 星期五晚上
    add_student(c, Student("S001", "王小明", "資工系", ["CS204"], 24))
    return c


def ids(result) -> list[str]:
    return [c.course.course_id for c in result.candidates]


# ---------- 正常案例 ----------

def test_basic_filter(catalog: SchoolCatalog) -> None:
    result = filter_courses(catalog, FilterCriteria(required=["REQ1", "REQ2"], min_credits=9, max_credits=20))
    assert result.feasible
    assert ids(result) == ["CS202", "CS203", "CS205"]
    assert set(result.rejected) == {"CS201", "CS204"}


def test_preferred_days_ranked_first(catalog: SchoolCatalog) -> None:
    result = filter_courses(catalog, FilterCriteria(preferred_days=[4, 5]))
    assert ids(result)[:2] == ["CS203", "CS205"]
    assert [c.preferred for c in result.candidates][:2] == [True, True]


def test_wanted_list_limits_pool(catalog: SchoolCatalog) -> None:
    result = filter_courses(catalog, FilterCriteria(wanted=["CS202", "CS205"]))
    assert ids(result) == ["CS202", "CS205"]


def test_unavailable_slot_excludes_course(catalog: SchoolCatalog) -> None:
    result = filter_courses(catalog, FilterCriteria(unavailable=[TimeSlot(5, "a")]))
    assert result.rejected["CS205"] == ["位於不可上課時段：星期五第 a 節"]


def test_output_format(catalog: SchoolCatalog) -> None:
    text = format_filter_result(filter_courses(catalog, FilterCriteria(preferred_days=[3])))
    assert "可行性：可行" in text and "★ CS202" in text


# ---------- 邊界案例 ----------

def test_min_equals_max(catalog: SchoolCatalog) -> None:
    assert filter_courses(catalog, FilterCriteria(required=["REQ1"], min_credits=3, max_credits=3)).feasible


def test_adjacent_unavailable_period_not_excluded(catalog: SchoolCatalog) -> None:
    result = filter_courses(catalog, FilterCriteria(unavailable=[TimeSlot(3, "2")]))
    assert "CS202" in ids(result)


def test_reachable_credits_exactly_minimum(catalog: SchoolCatalog) -> None:
    # 必修 7 學分＋候選 CS202(2)、CS203(3)、CS205(2) = 14
    assert filter_courses(catalog, FilterCriteria(required=["REQ1", "REQ2"], min_credits=14)).feasible


def test_no_preferred_days_marks_nothing(catalog: SchoolCatalog) -> None:
    assert not any(c.preferred for c in filter_courses(catalog, FilterCriteria()).candidates)


def test_required_credits_exactly_maximum(catalog: SchoolCatalog) -> None:
    assert filter_courses(catalog, FilterCriteria(required=["REQ1", "REQ2"], max_credits=7)).feasible


# ---------- 錯誤與衝突案例（F5 驗收：至少五種限制情境） ----------

def test_contradiction_min_greater_than_max(catalog: SchoolCatalog) -> None:
    result = filter_courses(catalog, FilterCriteria(min_credits=20, max_credits=10))
    assert "條件矛盾：最低學分 20 大於最高學分 10" in result.problems


def test_required_courses_conflict_with_each_other(catalog: SchoolCatalog) -> None:
    result = filter_courses(catalog, FilterCriteria(required=["REQ1", "CS201"]))
    assert "必修 CS201 課程CS201：與必修 REQ1 衝堂：星期一第 2 節" in result.problems


def test_required_course_in_unavailable_slot(catalog: SchoolCatalog) -> None:
    result = filter_courses(catalog, FilterCriteria(required=["REQ1"], unavailable=[TimeSlot(1, "1")]))
    assert "必修 REQ1 課程REQ1：位於不可上課時段：星期一第 1 節" in result.problems


def test_full_course(catalog: SchoolCatalog) -> None:
    result = filter_courses(catalog, FilterCriteria(required=["CS204"]))
    assert "必修 CS204 課程CS204：課程已額滿" in result.problems
    assert filter_courses(catalog, FilterCriteria()).rejected["CS204"] == ["課程已額滿"]


def test_cannot_reach_minimum_credits(catalog: SchoolCatalog) -> None:
    result = filter_courses(catalog, FilterCriteria(required=["REQ1", "REQ2"], min_credits=15))
    assert result.problems == ["無法滿足最低學分：必修 7 學分加上所有候選課程最多 14 學分，低於最低學分 15"]


def test_required_credits_exceed_maximum(catalog: SchoolCatalog) -> None:
    result = filter_courses(catalog, FilterCriteria(required=["REQ1", "REQ2"], max_credits=6))
    assert "必修學分 7 已超過最高學分 6" in result.problems


def test_unknown_course_and_bad_day(catalog: SchoolCatalog) -> None:
    result = filter_courses(catalog, FilterCriteria(required=["XX999"], preferred_days=[8]))
    assert result.problems == ["偏好星期不合法: 8", "課程 XX999 不存在"]


def test_candidate_conflicting_with_required_rejected(catalog: SchoolCatalog) -> None:
    result = filter_courses(catalog, FilterCriteria(required=["REQ1"]))
    assert result.rejected["CS201"] == ["與必修 REQ1 衝堂：星期一第 2 節"]
