"""F5 多條件課程篩選與可行性檢查。

學生提供希望修習的課程、必修清單、最低與最高學分、不可上課時段及偏好星期，
系統篩選出符合基本條件的候選課程，並列出每門被排除課程的原因。
另外檢查條件本身是否矛盾、是否可能湊到最低學分；結果只做篩選，不修改資料。
"""
from __future__ import annotations

from dataclasses import dataclass, field

from .data_manager import SchoolCatalog, remaining_seats
from .models import PERIOD_ORDER, Course, TimeSlot

DAY_NAMES = "一二三四五六日"


@dataclass
class FilterCriteria:
    wanted: list[str] = field(default_factory=list)          # 希望修習的課程；空清單代表全部課程
    required: list[str] = field(default_factory=list)        # 必修清單
    min_credits: int = 0
    max_credits: int = 25
    unavailable: list[TimeSlot] = field(default_factory=list)
    preferred_days: list[int] = field(default_factory=list)


@dataclass
class Candidate:
    course: Course
    preferred: bool          # 所有上課時段都在偏好星期內


@dataclass
class FilterResult:
    candidates: list[Candidate] = field(default_factory=list)
    rejected: dict[str, list[str]] = field(default_factory=dict)
    problems: list[str] = field(default_factory=list)        # 條件矛盾或無法滿足的原因

    @property
    def feasible(self) -> bool:
        return not self.problems


def _when(slots: list[TimeSlot]) -> str:
    ordered = sorted(slots, key=lambda s: (s.day, PERIOD_ORDER.index(s.period)))
    return "、".join(f"星期{DAY_NAMES[s.day - 1]}第 {s.period} 節" for s in ordered)


def _course_reasons(catalog: SchoolCatalog, course: Course, criteria: FilterCriteria,
                    taken: list[Course]) -> list[str]:
    reasons: list[str] = []
    if remaining_seats(catalog, course.course_id) <= 0:
        reasons.append("課程已額滿")
    blocked = [slot for slot in course.time_slots if slot in set(criteria.unavailable)]
    if blocked:
        reasons.append(f"位於不可上課時段：{_when(blocked)}")
    for other in taken:
        overlap = [slot for slot in course.time_slots if slot in set(other.time_slots)]
        if overlap:
            reasons.append(f"與必修 {other.course_id} 衝堂：{_when(overlap)}")
    return reasons


def filter_courses(catalog: SchoolCatalog, criteria: FilterCriteria) -> FilterResult:
    """依條件篩選候選課程，並做可行性檢查。必修課本身也會列入候選並標示問題。"""
    result = FilterResult()
    if criteria.min_credits > criteria.max_credits:
        result.problems.append(f"條件矛盾：最低學分 {criteria.min_credits} 大於最高學分 {criteria.max_credits}")
    for day in criteria.preferred_days:
        if day not in range(1, 8):
            result.problems.append(f"偏好星期不合法: {day}")

    unknown = [cid for cid in [*criteria.required, *criteria.wanted] if cid not in catalog.courses]
    for cid in dict.fromkeys(unknown):
        result.problems.append(f"課程 {cid} 不存在")
    required = [catalog.courses[cid] for cid in dict.fromkeys(criteria.required) if cid in catalog.courses]

    # 必修課之間與必修課本身的問題
    for index, course in enumerate(required):
        reasons = _course_reasons(catalog, course, criteria, required[:index])
        for reason in reasons:
            result.problems.append(f"必修 {course.course_id} {course.name}：{reason}")
    required_credits = sum(c.credits for c in required)
    if required_credits > criteria.max_credits:
        result.problems.append(f"必修學分 {required_credits} 已超過最高學分 {criteria.max_credits}")

    # 其他課程
    pool = criteria.wanted or sorted(catalog.courses)
    preferred = set(criteria.preferred_days)
    for cid in pool:
        course = catalog.courses.get(cid)
        if course is None or cid in criteria.required:
            continue
        reasons = _course_reasons(catalog, course, criteria, required)
        if reasons:
            result.rejected[cid] = reasons
        else:
            in_pref = bool(preferred) and all(slot.day in preferred for slot in course.time_slots)
            result.candidates.append(Candidate(course, in_pref))
    result.candidates.sort(key=lambda c: (not c.preferred, c.course.course_id))

    # 最低學分：必修加上所有候選課程仍不足時，必定無法滿足
    reachable = required_credits + sum(c.course.credits for c in result.candidates)
    if reachable < criteria.min_credits:
        result.problems.append(f"無法滿足最低學分：必修 {required_credits} 學分加上所有候選課程最多 {reachable} 學分，"
                               f"低於最低學分 {criteria.min_credits}")
    return result


def format_filter_result(result: FilterResult) -> str:
    lines = [f"可行性：{'可行' if result.feasible else '不可行'}"]
    lines += [f"問題：{p}" for p in result.problems]
    lines.append(f"候選課程 {len(result.candidates)} 門：")
    for cand in result.candidates:
        mark = "★" if cand.preferred else " "
        lines.append(f" {mark} {cand.course.course_id} {cand.course.name}｜{cand.course.credits} 學分｜{_when(cand.course.time_slots)}")
    if result.rejected:
        lines.append(f"排除 {len(result.rejected)} 門：")
        lines += [f"   {cid}：{'；'.join(reasons)}" for cid, reasons in result.rejected.items()]
    return "\n".join(lines)
