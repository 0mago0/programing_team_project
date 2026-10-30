"""期中系統 v1.0 命令列選單（介面層）。

只有這個模組處理輸入與輸出；所有判斷都交給 F1～F6 的核心函式。
輸入與輸出函式以參數傳入，測試時可以用預先寫好的輸入代替鍵盤。
"""
from __future__ import annotations

from pathlib import Path
from typing import Callable

from .activities import find_available_rooms, register_activity
from .course_filter import FilterCriteria, filter_courses, format_filter_result
from .data_manager import SchoolCatalog, find_courses, remaining_seats
from .enrollment import drop_course, enroll_course, format_check_result
from .models import TimeSlot
from .storage import load_data, save_data
from .timetable import build_student_timetable, find_free_blocks, render_timetable, timetable_stats

MENU = """
==== 校園選課與課表規劃系統 v1.0 ====
1. 查詢課程        2. 加選課程        3. 退選課程
4. 個人課表與空堂  5. 報名活動        6. 多條件篩選課程
7. 查詢可用教室    8. 儲存資料        9. 載入資料
0. 離開"""


def _slots(text: str) -> list[TimeSlot]:
    """「1-3 1-4」或「1-3,1-4」轉成時段清單。"""
    slots = []
    for part in text.replace(",", " ").split():
        day, _, period = part.partition("-")
        if not day.isdigit() or not period:
            raise ValueError(f"時段格式錯誤: {part}（例如 1-3 代表星期一第 3 節）")
        slots.append(TimeSlot(int(day), period))
    return slots


def _ints(text: str) -> list[int]:
    return [int(x) for x in text.replace(",", " ").split()]


def run_menu(catalog: SchoolCatalog, ask: Callable[[str], str] = input,
             say: Callable[[str], None] = print) -> SchoolCatalog:
    """執行選單直到使用者選 0；回傳最後的 catalog（載入資料後會換成新的）。"""
    while True:
        say(MENU)
        choice = ask("請選擇：").strip()
        try:
            if choice == "0":
                say("再見！")
                return catalog
            if choice == "1":
                teacher = ask("教師（可空白）：").strip() or None
                day_text = ask("星期 1～7（可空白）：").strip()
                prefix = ask("課程代號開頭（可空白）：").strip() or None
                found = find_courses(catalog, course_id=prefix, teacher=teacher,
                                     day=int(day_text) if day_text else None)
                say(f"共 {len(found)} 門")
                for c in found:
                    say(f"  {c.course_id} {c.name}｜{c.credits} 學分｜{c.teacher}｜剩餘 {remaining_seats(catalog, c.course_id)}/{c.capacity}")
            elif choice == "2":
                say(format_check_result(enroll_course(catalog, ask("學號：").strip(), ask("課程代號：").strip())))
            elif choice == "3":
                errors = drop_course(catalog, ask("學號：").strip(), ask("課程代號：").strip())
                say("退選成功" if not errors else "；".join(errors))
            elif choice == "4":
                sid = ask("學號：").strip()
                table = build_student_timetable(catalog, sid)
                say(render_timetable(table))
                for block in find_free_blocks(table, TimeSlot(1, "1"), TimeSlot(5, "9"), min_length=3):
                    say(f"  空閒：{block.describe()}")
                stats = timetable_stats(catalog, sid)
                say(f"總學分 {stats['total_credits']}｜每週 {stats['total_periods']} 節｜空堂 {stats['total_gaps']}")
            elif choice == "5":
                say(format_check_result(register_activity(catalog, ask("學號：").strip(), ask("活動代號：").strip())))
            elif choice == "6":
                criteria = FilterCriteria(
                    required=ask("必修課程代號（空白分隔）：").split(),
                    min_credits=int(ask("最低學分：").strip() or 0),
                    max_credits=int(ask("最高學分：").strip() or 25),
                    unavailable=_slots(ask("不可上課時段（例如 1-1 1-2）：")),
                    preferred_days=_ints(ask("偏好星期（例如 2 4）：")),
                )
                say(format_filter_result(filter_courses(catalog, criteria)))
            elif choice == "7":
                result = find_available_rooms(catalog, _slots(ask("時段（例如 3-5 3-6）：")),
                                              int(ask("人數：").strip()), ask("設備（空白分隔）：").split())
                say("可用教室：" + ("、".join(r.room_id for r in result.available) or "無"))
                for room_id, reasons in result.unmet.items():
                    say(f"  {room_id} 不符合：{'；'.join(reasons)}")
            elif choice == "8":
                path = ask("儲存位置（.json 檔或 CSV 資料夾）：").strip()
                say("已儲存：" + "、".join(p.name for p in save_data(Path(path), catalog)))
            elif choice == "9":
                loaded, errors = load_data(Path(ask("載入位置（.json 檔或 CSV 資料夾）：").strip()))
                for message in errors:
                    say(f"  略過：{message}")
                if loaded.courses or loaded.students:
                    catalog = loaded
                    say(f"已載入：課程 {len(catalog.courses)}、學生 {len(catalog.students)}、教室 {len(catalog.classrooms)}、活動 {len(catalog.activities)}")
                else:
                    say("沒有載入任何資料，保留原本的資料")
            else:
                say("請輸入 0～9")
        except (ValueError, KeyError) as exc:
            say(f"輸入有誤：{exc}")
