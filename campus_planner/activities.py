"""F4 校園活動與教室配置。

- 活動的新增（含教室檢查）、修改、取消與查詢
- 依教室容量、可用時段及設備需求篩選場地；沒有合適教室時列出每間教室未滿足的條件
- 同一教室同一時段不得重複配置：與課程共用 enrollment.room_conflicts 的時段衝突檢查
- 報名人數不得超過活動預計人數，也不得超過教室容量
- 日期與起訖時間依節次時間表換算成星期＋節次
"""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass, field, fields, replace
from typing import Any

from .data_manager import SchoolCatalog, add_activity
from .enrollment import CheckResult, check_activity_join, room_conflicts
from .models import PERIOD_ORDER, Activity, Classroom, TimeSlot
from .validation import validate_activity

# 節次時間表（每節 50 分鐘）；日期與時間換算節次時使用
PERIOD_TIMES: dict[str, tuple[str, str]] = {
    "1": ("08:10", "09:00"), "2": ("09:10", "10:00"), "3": ("10:10", "11:00"), "4": ("11:10", "12:00"),
    "5": ("13:10", "14:00"), "6": ("14:10", "15:00"), "7": ("15:10", "16:00"), "8": ("16:10", "17:00"),
    "9": ("17:10", "18:00"), "a": ("18:30", "19:20"), "b": ("19:25", "20:15"), "c": ("20:20", "21:10"),
}


@dataclass
class RoomSearch:
    """教室篩選結果：available 為所有條件都滿足的教室，unmet 為其餘教室各自未滿足的條件。"""

    available: list[Classroom] = field(default_factory=list)
    unmet: dict[str, list[str]] = field(default_factory=dict)


# ---------- 時間換算 ----------

def _parse_time(text: str) -> dt.time:
    try:
        return dt.datetime.strptime(text.strip(), "%H:%M").time()
    except (AttributeError, ValueError):
        raise ValueError(f"時間格式錯誤: {text!r}（應為 HH:MM）") from None


def time_range_to_slots(date: str, start: str, end: str) -> list[TimeSlot]:
    """把日期與起訖時間換算成星期＋節次；與時間範圍有重疊的節次都算在內。"""
    try:
        day = dt.date.fromisoformat(date.strip()).isoweekday()
    except (AttributeError, ValueError):
        raise ValueError(f"日期格式錯誤: {date!r}（應為 YYYY-MM-DD）") from None
    begin, finish = _parse_time(start), _parse_time(end)
    if begin >= finish:
        raise ValueError("開始時間必須早於結束時間")
    slots = [
        TimeSlot(day, period)
        for period in PERIOD_ORDER
        if _parse_time(PERIOD_TIMES[period][0]) < finish and _parse_time(PERIOD_TIMES[period][1]) > begin
    ]
    if not slots:
        raise ValueError(f"{start}～{end} 沒有對應的節次")
    return slots


# ---------- 教室篩選與配置 ----------

def room_problems(catalog: SchoolCatalog, room_id: str, time_slots: list[TimeSlot], headcount: int,
                  equipment: list[str] | tuple[str, ...] = (), ignore_id: str = "") -> list[str]:
    """回傳這間教室不符合的條件；空清單代表可以使用。"""
    room = catalog.classrooms.get(room_id)
    if room is None:
        return [f"教室 {room_id} 不存在"]
    problems: list[str] = []
    if room.capacity < headcount:
        problems.append(f"容量 {room.capacity} 小於需求人數 {headcount}")
    missing = [item for item in equipment if item not in room.equipment]
    if missing:
        problems.append(f"缺少設備：{'、'.join(missing)}")
    for conflict in room_conflicts(catalog, room_id, time_slots, ignore_id=ignore_id):
        problems.append(f"時段已被使用：{conflict.describe().split('｜')[0]} {conflict.other_id} {conflict.other_name}")
    return problems


def find_available_rooms(catalog: SchoolCatalog, time_slots: list[TimeSlot], headcount: int,
                         equipment: list[str] | tuple[str, ...] = (), ignore_id: str = "") -> RoomSearch:
    """依容量、可用時段與設備篩選教室；可用教室依容量由小到大排序，避免大教室被小活動占用。"""
    result = RoomSearch()
    for room_id in sorted(catalog.classrooms):
        problems = room_problems(catalog, room_id, time_slots, headcount, equipment, ignore_id)
        if problems:
            result.unmet[room_id] = problems
        else:
            result.available.append(catalog.classrooms[room_id])
    result.available.sort(key=lambda r: (r.capacity, r.room_id))
    return result


def _activity_room_errors(catalog: SchoolCatalog, activity: Activity) -> list[str]:
    if not activity.classroom:
        return []
    return room_problems(catalog, activity.classroom, activity.time_slots, activity.expected_participants,
                         activity.venue_requirements, ignore_id=activity.activity_id)


def create_activity(catalog: SchoolCatalog, activity: Activity) -> list[str]:
    """新增活動；有指定教室時一併檢查容量、設備與時段衝突。失敗時資料不變。"""
    errors = _activity_room_errors(catalog, activity) if activity.classroom in catalog.classrooms else []
    if errors:
        return validate_activity(activity) + errors
    return add_activity(catalog, activity)


def assign_room(catalog: SchoolCatalog, activity_id: str, room_id: str) -> list[str]:
    """把活動配置到指定教室；不符合條件時回傳原因，資料不變。"""
    activity = catalog.activities.get(activity_id)
    if activity is None:
        return [f"活動 {activity_id} 不存在"]
    errors = room_problems(catalog, room_id, activity.time_slots, activity.expected_participants,
                           activity.venue_requirements, ignore_id=activity_id)
    if not errors:
        activity.classroom = room_id
    return errors


# ---------- 修改、取消、查詢 ----------

def update_activity(catalog: SchoolCatalog, activity_id: str, /, **changes: Any) -> list[str]:
    """修改活動欄位（不可改代號與報名名單）；修改後重新檢查欄位與教室。失敗時資料不變。"""
    if activity_id not in catalog.activities:
        return [f"活動 {activity_id} 不存在"]
    allowed = {f.name for f in fields(Activity)} - {"activity_id", "participants"}
    unknown = sorted(set(changes) - allowed)
    if unknown:
        return [f"不可修改的欄位: {', '.join(unknown)}"]
    original = catalog.activities[activity_id]
    updated = replace(original, **changes)
    updated.participants = list(original.participants)
    errors = validate_activity(updated)
    if updated.classroom and updated.classroom not in catalog.classrooms:
        errors.append(f"教室 {updated.classroom} 不存在")
    elif not errors:
        errors += _activity_room_errors(catalog, updated)
    if not errors:
        catalog.activities[activity_id] = updated
    return errors


def cancel_activity(catalog: SchoolCatalog, activity_id: str) -> list[str]:
    """取消活動並移除報名，回傳被取消報名的學號；活動不存在時回傳空清單。"""
    activity = catalog.activities.pop(activity_id, None)
    return sorted(activity.participants) if activity else []


def find_activities(catalog: SchoolCatalog, activity_type: str | None = None, day: int | None = None,
                    classroom: str | None = None, student_id: str | None = None) -> list[Activity]:
    """依類型、星期、教室、報名學生查詢；未給的條件不篩選，結果依代號排序。"""
    found = []
    for activity in catalog.activities.values():
        if activity_type is not None and activity.activity_type != activity_type:
            continue
        if day is not None and all(slot.day != day for slot in activity.time_slots):
            continue
        if classroom is not None and activity.classroom != classroom:
            continue
        if student_id is not None and student_id not in activity.participants:
            continue
        found.append(activity)
    return sorted(found, key=lambda a: a.activity_id)


# ---------- 報名 ----------

def check_registration(catalog: SchoolCatalog, student_id: str, activity_id: str) -> CheckResult:
    """報名檢查：沿用 F2 的活動衝突與預計人數檢查，另外檢查教室容量。"""
    result = check_activity_join(catalog, student_id, activity_id)
    activity = catalog.activities.get(activity_id)
    if activity and activity.classroom in catalog.classrooms:
        room = catalog.classrooms[activity.classroom]
        if len(activity.participants) >= room.capacity:
            result.errors.append(f"教室 {room.room_id} 容量已滿（{len(activity.participants)}/{room.capacity}）")
    return result


def register_activity(catalog: SchoolCatalog, student_id: str, activity_id: str) -> CheckResult:
    result = check_registration(catalog, student_id, activity_id)
    if result.ok:
        catalog.activities[activity_id].participants.append(student_id)
    return result


def unregister_activity(catalog: SchoolCatalog, student_id: str, activity_id: str) -> list[str]:
    activity = catalog.activities.get(activity_id)
    if activity is None:
        return [f"活動 {activity_id} 不存在"]
    if student_id not in activity.participants:
        return [f"學生 {student_id} 沒有報名 {activity_id}"]
    activity.participants.remove(student_id)
    return []
