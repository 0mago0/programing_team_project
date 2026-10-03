from __future__ import annotations

from typing import Any

from .models import Course, TimeSlot

PERIOD_ORDER = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "a", "b", "c"]


def build_weekly_matrix() -> list[list[str | None]]:
    return [[None for _ in range(len(PERIOD_ORDER))] for _ in range(7)]


def slot_to_index(period: str) -> int:
    if period not in PERIOD_ORDER:
        raise ValueError(f"節次不合法: {period}")
    return PERIOD_ORDER.index(period)


def place_course_in_timetable(matrix: list[list[str | None]], course: Course) -> list[list[str | None]]:
    for slot in course.time_slots:
        row = slot.day - 1
        col = slot_to_index(slot.period)
        matrix[row][col] = f"{course.course_id} - {course.name}"
    return matrix


def find_available_slots(matrix: list[list[str | None]], day: int, start: int, duration: int) -> list[tuple[int, int]]:
    if day not in range(1, 8):
        raise ValueError("星期範圍必須為 1~7")

    row = day - 1
    results: list[tuple[int, int]] = []
    for idx in range(start, min(len(PERIOD_ORDER), start + duration)):
        if matrix[row][idx] is None:
            results.append((row, idx))
        else:
            return []
    return results


def summarise_timetable(matrix: list[list[str | None]]) -> dict[str, Any]:
    occupied = 0
    for row in matrix:
        occupied += sum(1 for cell in row if cell is not None)

    return {
        "days": 7,
        "periods": len(PERIOD_ORDER),
        "occupied_slots": occupied,
        "empty_slots": (7 * len(PERIOD_ORDER)) - occupied,
    }
