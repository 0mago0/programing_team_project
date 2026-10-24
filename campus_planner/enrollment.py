"""F2 多層次衝堂與選課檢查。

一次檢查所有限制，不在第一個錯誤就停止：
- 學生衝堂：與已選課程的時段重疊
- 活動衝突：與學生已參加活動的時段重疊
- 教室衝堂：欲加選課程的教室，同一時段已被其他課程或活動使用
- 學分限制：加選後總學分不得超過學分上限
- 人數限制：課程已額滿時拒絕

時段衝突依星期、節次排序；同一門課（或活動）在同一天的連續衝突合併成一筆，
例如「星期二第 3、4 節」。所有函式都以 SchoolCatalog 為參數，不使用全域變數。
"""
from __future__ import annotations

from dataclasses import dataclass, field

from .data_manager import SchoolCatalog, activities_of_student, enrolled_count
from .models import PERIOD_ORDER, Activity, Course, TimeSlot

DAY_NAMES = "一二三四五六日"


@dataclass(frozen=True)
class Conflict:
    """一筆時段衝突：kind 為「已選課程」「已參加活動」「教室衝堂」之一。"""

    kind: str
    day: int
    periods: tuple[str, ...]
    other_id: str
    other_name: str

    def sort_key(self) -> tuple[int, int, str]:
        return self.day, PERIOD_ORDER.index(self.periods[0]), self.other_id

    def describe(self) -> str:
        when = f"星期{DAY_NAMES[self.day - 1]}第 {'、'.join(self.periods)} 節"
        return f"{when}｜{self.kind}：{self.other_id} {self.other_name}"


@dataclass
class CheckResult:
    """加選（或參加活動）的檢查結果。ok 為 True 代表沒有任何衝突與錯誤。"""

    student_id: str
    target_id: str
    target_name: str = ""
    conflicts: list[Conflict] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    current_credits: int = 0
    projected_credits: int = 0
    credit_limit: int = 0

    @property
    def ok(self) -> bool:
        return not self.conflicts and not self.errors


# ---------- 共用的時段衝突檢查（F4 教室配置也使用） ----------

def _group_overlaps(kind: str, mine: list[TimeSlot], other_id: str, other_name: str,
                    others: list[TimeSlot]) -> list[Conflict]:
    overlap = set(mine) & set(others)
    by_day: dict[int, list[str]] = {}
    for slot in overlap:
        by_day.setdefault(slot.day, []).append(slot.period)
    return [
        Conflict(kind, day, tuple(sorted(periods, key=PERIOD_ORDER.index)), other_id, other_name)
        for day, periods in by_day.items()
    ]


def room_conflicts(catalog: SchoolCatalog, room_id: str, time_slots: list[TimeSlot],
                   ignore_id: str = "") -> list[Conflict]:
    """同一教室在相同時段被其他課程或活動使用的情況。ignore_id 為自己的代號。"""
    found: list[Conflict] = []
    users: list[Course | Activity] = [*catalog.courses.values(), *catalog.activities.values()]
    for item in users:
        item_id = item.course_id if isinstance(item, Course) else item.activity_id
        if item_id == ignore_id or item.classroom != room_id:
            continue
        found += _group_overlaps("教室衝堂", time_slots, item_id, item.name, item.time_slots)
    return sorted(found, key=Conflict.sort_key)


def schedule_conflicts(catalog: SchoolCatalog, student_id: str, time_slots: list[TimeSlot],
                       ignore_id: str = "") -> list[Conflict]:
    """時段與學生已選課程、已參加活動的重疊情況。"""
    student = catalog.students[student_id]
    found: list[Conflict] = []
    for course_id in student.enrolled_courses:
        course = catalog.courses.get(course_id)
        if course is None or course_id == ignore_id:
            continue
        found += _group_overlaps("已選課程", time_slots, course_id, course.name, course.time_slots)
    for activity in activities_of_student(catalog, student_id):
        if activity.activity_id == ignore_id:
            continue
        found += _group_overlaps("已參加活動", time_slots, activity.activity_id, activity.name,
                                 activity.time_slots)
    return sorted(found, key=Conflict.sort_key)


def current_credits(catalog: SchoolCatalog, student_id: str) -> int:
    student = catalog.students[student_id]
    return sum(catalog.courses[cid].credits for cid in student.enrolled_courses if cid in catalog.courses)


# ---------- 選課 ----------

def check_enrollment(catalog: SchoolCatalog, student_id: str, course_id: str) -> CheckResult:
    """檢查學生能否加選課程，回傳所有衝突與錯誤；不修改資料。"""
    result = CheckResult(student_id, course_id)
    if student_id not in catalog.students:
        result.errors.append(f"學生 {student_id} 不存在")
    if course_id not in catalog.courses:
        result.errors.append(f"課程 {course_id} 不存在")
    if result.errors:
        return result

    student = catalog.students[student_id]
    course = catalog.courses[course_id]
    result.target_name = course.name
    if course_id in student.enrolled_courses:
        result.errors.append(f"已選修 {course_id}，不可重複加選")

    result.conflicts = sorted(
        schedule_conflicts(catalog, student_id, course.time_slots, ignore_id=course_id)
        + room_conflicts(catalog, course.classroom, course.time_slots, ignore_id=course_id),
        key=Conflict.sort_key,
    )

    result.current_credits = current_credits(catalog, student_id)
    result.projected_credits = result.current_credits + course.credits
    result.credit_limit = student.credit_limit
    if result.projected_credits > student.credit_limit:
        result.errors.append(f"加選後學分 {result.projected_credits} 超過上限 {student.credit_limit}")

    count = enrolled_count(catalog, course_id)
    if count >= course.capacity:
        result.errors.append(f"課程已額滿（{count}/{course.capacity}）")
    return result


def enroll_course(catalog: SchoolCatalog, student_id: str, course_id: str) -> CheckResult:
    """檢查通過才加選；失敗時資料完全不變。"""
    result = check_enrollment(catalog, student_id, course_id)
    if result.ok:
        catalog.students[student_id].enrolled_courses.append(course_id)
    return result


def drop_course(catalog: SchoolCatalog, student_id: str, course_id: str) -> list[str]:
    """退選；回傳錯誤清單，空清單代表成功。"""
    if student_id not in catalog.students:
        return [f"學生 {student_id} 不存在"]
    student = catalog.students[student_id]
    if course_id not in student.enrolled_courses:
        return [f"學生 {student_id} 沒有選修 {course_id}"]
    student.enrolled_courses.remove(course_id)
    return []


# ---------- 參加活動 ----------

def check_activity_join(catalog: SchoolCatalog, student_id: str, activity_id: str) -> CheckResult:
    """檢查學生能否參加活動：與已選課程或其他已參加活動是否重疊，以及報名人數。"""
    result = CheckResult(student_id, activity_id)
    if student_id not in catalog.students:
        result.errors.append(f"學生 {student_id} 不存在")
    if activity_id not in catalog.activities:
        result.errors.append(f"活動 {activity_id} 不存在")
    if result.errors:
        return result

    activity = catalog.activities[activity_id]
    result.target_name = activity.name
    if student_id in activity.participants:
        result.errors.append(f"已報名 {activity_id}，不可重複報名")
    result.conflicts = schedule_conflicts(catalog, student_id, activity.time_slots, ignore_id=activity_id)
    if len(activity.participants) >= activity.expected_participants:
        result.errors.append(f"活動報名已額滿（{len(activity.participants)}/{activity.expected_participants}）")
    return result


def join_activity(catalog: SchoolCatalog, student_id: str, activity_id: str) -> CheckResult:
    result = check_activity_join(catalog, student_id, activity_id)
    if result.ok:
        catalog.activities[activity_id].participants.append(student_id)
    return result


# ---------- 輸出 ----------

def format_check_result(result: CheckResult) -> str:
    """依作業 F2 範例的格式輸出選課結果。"""
    lines = [
        f"學生：{result.student_id}",
        f"欲加選：{result.target_id} {result.target_name}".rstrip(),
        f"選課結果：{'成功' if result.ok else '失敗'}",
    ]
    for index, conflict in enumerate(result.conflicts, 1):
        lines.append(f"衝突 {index}：{conflict.describe()}")
    for message in result.errors:
        lines.append(f"限制：{message}")
    if result.credit_limit:
        lines += [
            f"目前學分：{result.current_credits}",
            f"加選後學分：{result.projected_credits}",
            f"學分上限：{result.credit_limit}",
        ]
    return "\n".join(lines)
