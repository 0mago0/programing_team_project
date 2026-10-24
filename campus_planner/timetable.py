"""F3 個人課表產生與空閒時段查詢。

課表為 7 天 × 12 節（星期一～日 × 節次 1～9、a、b、c）的二維矩陣，每一格是該時段的
項目清單（課程或活動），因此同一格有兩個以上項目時可以看出衝突，而不是被覆蓋。
空閒時段只在同一天內連續計算，跨日查詢時每天各自成為獨立的區段。
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .data_manager import SchoolCatalog, activities_of_student
from .models import PERIOD_ORDER, VALID_DAYS, Course, TimeSlot

DAY_NAMES = "一二三四五六日"


@dataclass(frozen=True)
class Entry:
    """課表中的一個項目。kind 為「課程」或「活動」。"""

    kind: str
    item_id: str
    name: str
    classroom: str

    def label(self) -> str:
        return f"{self.item_id} {self.name}"


@dataclass(frozen=True)
class FreeBlock:
    """一段連續的空閒時段。"""

    day: int
    start: str
    end: str
    length: int

    def describe(self) -> str:
        span = self.start if self.start == self.end else f"{self.start}～{self.end}"
        return f"星期{DAY_NAMES[self.day - 1]}第 {span} 節（連續 {self.length} 節）"


Timetable = list[list[list[Entry]]]


# ---------- 輸入檢查 ----------

def slot_to_index(period: str) -> int:
    if period not in PERIOD_ORDER:
        raise ValueError(f"節次不合法: {period}")
    return PERIOD_ORDER.index(period)


def _check_day(day: int) -> None:
    if not isinstance(day, int) or isinstance(day, bool) or day not in VALID_DAYS:
        raise ValueError(f"星期不合法: {day}")


# ---------- 個人課表 ----------

def empty_timetable() -> Timetable:
    return [[[] for _ in PERIOD_ORDER] for _ in VALID_DAYS]


def build_student_timetable(catalog: SchoolCatalog, student_id: str) -> Timetable:
    """把學生已選課程與已參加活動放進 7×12 課表；同一門課每週多次上課會出現在所有對應時段。"""
    if student_id not in catalog.students:
        raise ValueError(f"學生 {student_id} 不存在")
    table = empty_timetable()
    student = catalog.students[student_id]
    items: list[tuple[Entry, list[TimeSlot]]] = []
    for course_id in student.enrolled_courses:
        course = catalog.courses.get(course_id)
        if course is not None:
            items.append((Entry("課程", course.course_id, course.name, course.classroom), course.time_slots))
    for activity in activities_of_student(catalog, student_id):
        items.append((Entry("活動", activity.activity_id, activity.name, activity.classroom), activity.time_slots))
    for entry, slots in items:
        for slot in slots:
            _check_day(slot.day)
            table[slot.day - 1][slot_to_index(slot.period)].append(entry)
    return table


def entries_at(table: Timetable, day: int, period: str) -> list[Entry]:
    """查詢某星期某節次的項目。"""
    _check_day(day)
    return list(table[day - 1][slot_to_index(period)])


def entries_on_day(table: Timetable, day: int) -> list[tuple[str, Entry]]:
    """查詢某一天所有項目，依節次排序。"""
    _check_day(day)
    return [(period, entry) for period, cell in zip(PERIOD_ORDER, table[day - 1]) for entry in cell]


def slots_of(table: Timetable, item_id: str) -> list[TimeSlot]:
    """查詢某課程（或活動）代號在課表中的所有時段。"""
    return [
        TimeSlot(day_index + 1, period)
        for day_index, row in enumerate(table)
        for period, cell in zip(PERIOD_ORDER, row)
        if any(entry.item_id == item_id for entry in cell)
    ]


def conflicts_in(table: Timetable) -> list[tuple[TimeSlot, list[Entry]]]:
    """同一格有兩個以上項目的時段。"""
    return [
        (TimeSlot(day_index + 1, period), list(cell))
        for day_index, row in enumerate(table)
        for period, cell in zip(PERIOD_ORDER, row)
        if len(cell) > 1
    ]


# ---------- 空閒時段 ----------

def find_free_blocks(table: Timetable, start: TimeSlot, end: TimeSlot, min_length: int = 1) -> list[FreeBlock]:
    """查詢 start 到 end（含）之間、長度至少 min_length 的連續空閒時段。

    範圍可以跨日；每一天的空閒時段各自計算，不會把前一天最後一節與隔天第一節合併。
    """
    for slot in (start, end):
        _check_day(slot.day)
        slot_to_index(slot.period)
    if not isinstance(min_length, int) or isinstance(min_length, bool) or min_length < 1:
        raise ValueError("最少連續節數必須為正整數")
    if (start.day, slot_to_index(start.period)) > (end.day, slot_to_index(end.period)):
        raise ValueError("開始時段不可晚於結束時段")

    blocks: list[FreeBlock] = []
    for day in range(start.day, end.day + 1):
        first = slot_to_index(start.period) if day == start.day else 0
        last = slot_to_index(end.period) if day == end.day else len(PERIOD_ORDER) - 1
        run: list[int] = []
        for index in range(first, last + 2):
            if index <= last and not table[day - 1][index]:
                run.append(index)
                continue
            if len(run) >= min_length:
                blocks.append(FreeBlock(day, PERIOD_ORDER[run[0]], PERIOD_ORDER[run[-1]], len(run)))
            run = []
    return blocks


# ---------- 統計 ----------

def timetable_stats(catalog: SchoolCatalog, student_id: str) -> dict[str, Any]:
    """每日上課節數、每週總學分與空堂數。

    上課節數只計課程，活動不算。空堂數為同一天第一節課與最後一節課之間沒有課的節數。
    """
    table = build_student_timetable(catalog, student_id)
    daily_periods: dict[int, int] = {}
    daily_gaps: dict[int, int] = {}
    for day_index, row in enumerate(table):
        busy = [i for i, cell in enumerate(row) if any(entry.kind == "課程" for entry in cell)]
        daily_periods[day_index + 1] = len(busy)
        daily_gaps[day_index + 1] = (busy[-1] - busy[0] + 1 - len(busy)) if busy else 0
    student = catalog.students[student_id]
    credits = sum(catalog.courses[cid].credits for cid in student.enrolled_courses if cid in catalog.courses)
    return {
        "daily_periods": daily_periods,
        "total_periods": sum(daily_periods.values()),
        "total_credits": credits,
        "daily_gaps": daily_gaps,
        "total_gaps": sum(daily_gaps.values()),
        "conflicts": len(conflicts_in(table)),
    }


# ---------- 輸出 ----------

def render_timetable(table: Timetable, width: int = 10) -> str:
    """以文字表格顯示課表；同一格多個項目時以「/」分隔，方便看出衝突。"""
    def cell_text(cell: list[Entry]) -> str:
        text = "/".join(entry.item_id for entry in cell) or "."
        return text[:width].ljust(width)

    header = "節次 " + "".join(f"週{name}".ljust(width - 1) for name in DAY_NAMES)
    lines = [header]
    for index, period in enumerate(PERIOD_ORDER):
        lines.append(f" {period}   " + "".join(cell_text(table[day][index]) for day in range(7)))
    return "\n".join(lines)


# ---------- 第 5 週骨架介面（保留相容） ----------

def build_weekly_matrix() -> list[list[str | None]]:
    return [[None for _ in PERIOD_ORDER] for _ in VALID_DAYS]


def place_course_in_timetable(matrix: list[list[str | None]], course: Course) -> list[list[str | None]]:
    """把課程放進字串矩陣。星期不合法或該格已有其他課程時丟出 ValueError，不會覆蓋。"""
    for slot in course.time_slots:
        _check_day(slot.day)
        row, col = slot.day - 1, slot_to_index(slot.period)
        label = f"{course.course_id} - {course.name}"
        if matrix[row][col] not in (None, label):
            raise ValueError(f"時段衝突: 星期{slot.day} 第{slot.period}節已有 {matrix[row][col]}")
        matrix[row][col] = label
    return matrix


def find_available_slots(matrix: list[list[str | None]], day: int, start: int, duration: int) -> list[tuple[int, int]]:
    """從第 start 個節次（0 起算）起連續 duration 節都空著時，回傳這些格子；超出範圍時丟出 ValueError。"""
    _check_day(day)
    if start < 0 or duration < 1 or start + duration > len(PERIOD_ORDER):
        raise ValueError(f"查詢範圍超出節次：start={start}, duration={duration}")
    row = day - 1
    results: list[tuple[int, int]] = []
    for idx in range(start, start + duration):
        if matrix[row][idx] is not None:
            return []
        results.append((row, idx))
    return results


def summarise_timetable(matrix: list[list[str | None]]) -> dict[str, Any]:
    occupied = sum(1 for row in matrix for cell in row if cell is not None)
    return {
        "days": 7,
        "periods": len(PERIOD_ORDER),
        "occupied_slots": occupied,
        "empty_slots": (7 * len(PERIOD_ORDER)) - occupied,
    }
