"""校園選課與課表規劃系統 v1.0（期中）。

python main.py          互動式選單
python main.py --demo   依序示範 F1～F6
"""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

from campus_planner.activities import cancel_activity, create_activity, find_available_rooms, register_activity, time_range_to_slots
from campus_planner.cli import run_menu
from campus_planner.course_filter import FilterCriteria, filter_courses, format_filter_result
from campus_planner.models import Activity
from campus_planner.storage import load_data, save_data
from campus_planner.data_manager import (
    SchoolCatalog,
    add_course,
    delete_course,
    enrolled_count,
    find_courses,
    find_students,
    load_catalog,
    remaining_seats,
)
from campus_planner.enrollment import check_enrollment, drop_course, enroll_course, format_check_result
from campus_planner.models import Course, TimeSlot
from campus_planner.timetable import build_student_timetable, find_free_blocks, render_timetable, timetable_stats

SAMPLE_DATA = Path(__file__).resolve().parent / "data" / "sample_school_data.json"
DAY_NAMES = "一二三四五六日"


def format_course(catalog: SchoolCatalog, course: Course) -> str:
    by_day: dict[int, list[str]] = {}
    for slot in course.time_slots:
        by_day.setdefault(slot.day, []).append(slot.period)
    slots = "；".join(f"週{DAY_NAMES[day - 1]} {'、'.join(periods)}" for day, periods in sorted(by_day.items()))
    kind = "必修" if course.required else "選修"
    return (
        f"{course.course_id} {course.name}｜{course.credits} 學分｜{kind}｜{course.teacher}｜"
        f"{course.classroom}｜{slots}｜剩餘 {remaining_seats(catalog, course.course_id)}/{course.capacity}"
    )


def print_courses(catalog: SchoolCatalog, title: str, courses: list[Course]) -> None:
    print(f"\n[{title}] 共 {len(courses)} 門")
    for course in courses:
        print("  " + format_course(catalog, course))


def main() -> None:
    if "--demo" in sys.argv[1:]:
        demo()
        return
    catalog, load_errors = load_catalog(SAMPLE_DATA)
    for message in load_errors:
        print(f"載入時略過：{message}")
    run_menu(catalog)


def demo() -> None:
    catalog, load_errors = load_catalog(SAMPLE_DATA)

    print("校園選課與課表規劃系統 v1.0（期中）- F1～F6 示範")
    print("=" * 50)
    print(f"資料檔：{SAMPLE_DATA.name}")
    print(f"課程 {len(catalog.courses)} 門、學生 {len(catalog.students)} 名、教室 {len(catalog.classrooms)} 間、活動 {len(catalog.activities)} 項")
    if load_errors:
        print("載入時略過的資料：")
        for message in load_errors:
            print(f"  - {message}")

    print_courses(catalog, "林老師的課", find_courses(catalog, teacher="林老師"))
    print_courses(catalog, "星期一有上課的必修", find_courses(catalog, day=1, required=True))
    print_courses(catalog, "已額滿的課程", [
        c for c in find_courses(catalog) if remaining_seats(catalog, c.course_id) == 0
    ])

    students = find_students(catalog, department="數學系二年級")
    print(f"\n[數學系二年級學生] 共 {len(students)} 名：" + "、".join(f"{s.student_id} {s.name}" for s in students))

    print("\n[錯誤資料檢查]")
    samples = [
        ("重複代號", Course("CS101", "重複課程", 3, True, "林老師", 30, "A101", [TimeSlot(4, "9")])),
        ("非法節次", Course("CS900", "測試課程", 3, False, "林老師", 30, "A101", [TimeSlot(1, "d")])),
        ("無效學分", Course("CS901", "測試課程", 0, False, "林老師", 30, "A101", [TimeSlot(1, "1")])),
    ]
    for label, course in samples:
        print(f"  {label} {course.course_id}：{'、'.join(add_course(catalog, course))}")

    for course_id in ("CS101", "ZZZ"):
        if course_id not in catalog.courses:
            print(f"  刪除 {course_id}：課程不存在")
        elif delete_course(catalog, course_id):
            print(f"  刪除 {course_id}：成功")
        else:
            print(f"  刪除 {course_id}：拒絕，已有 {enrolled_count(catalog, course_id)} 名學生選修，需先退選或執行課程取消")

    demo_f2(catalog)
    demo_f3(catalog, "S001")
    demo_f4(catalog)
    demo_f5(catalog)
    demo_f6(catalog)


def demo_f4(catalog: SchoolCatalog) -> None:
    print("\n" + "=" * 50)
    print("F4 校園活動與教室配置")
    slots = time_range_to_slots("2026-11-04", "15:10", "17:00")
    print(f"2026-11-04 15:10～17:00 換算為：{'、'.join(f'星期{DAY_NAMES[s.day - 1]}第{s.period}節' for s in slots)}")
    search = find_available_rooms(catalog, slots, 50, ["投影機"])
    print("50 人、需要投影機的可用教室：" + ("、".join(r.room_id for r in search.available) or "無"))
    for room_id, reasons in search.unmet.items():
        print(f"  {room_id} 不符合：{'；'.join(reasons)}")
    new = Activity("A005", "程式競賽說明會", slots, 50, "講座", search.available[0].room_id, ["投影機"])
    print(f"新增 A005 於 {new.classroom}：{'、'.join(create_activity(catalog, new)) or '成功'}")
    for sid in ("S014", "S015"):
        result = register_activity(catalog, sid, "A005")
        print(f"  {sid} 報名：{'成功' if result.ok else '、'.join(result.errors)}")
    print(f"取消 A005，退回報名：{'、'.join(cancel_activity(catalog, 'A005'))}")


def demo_f5(catalog: SchoolCatalog) -> None:
    print("\n" + "=" * 50)
    print("F5 多條件課程篩選（必修 CS101、MA101，15～22 學分，星期一第 1、2 節不可上課，偏好星期二～四）")
    criteria = FilterCriteria(required=["CS101", "MA101"], min_credits=15, max_credits=22,
                              unavailable=[TimeSlot(1, "1"), TimeSlot(1, "2")], preferred_days=[2, 3, 4])
    print(format_filter_result(filter_courses(catalog, criteria)))
    print("\n[條件矛盾：最低 20 學分、最高 10 學分]")
    print(format_filter_result(filter_courses(catalog, FilterCriteria(min_credits=20, max_credits=10, wanted=["CS199"]))))


def demo_f6(catalog: SchoolCatalog) -> None:
    print("\n" + "=" * 50)
    print("F6 資料儲存與載入（JSON 與 CSV，模擬重新啟動後載入）")
    with tempfile.TemporaryDirectory() as folder:
        for target in (Path(folder) / "school.json", Path(folder) / "csv"):
            written = save_data(target, catalog)
            loaded, errors = load_data(target)
            print(f"  {target.name}：寫出 {len(written)} 個檔案，重新載入後與原資料{'相同' if loaded == catalog else '不同'}，略過 {len(errors)} 筆")
        bad = Path(folder) / "csv" / "courses.csv"
        bad.write_text(bad.read_text(encoding="utf-8-sig") + "BAD1,格式錯誤,三,true,林老師,30,A101,1-1\n", encoding="utf-8")
        loaded, errors = load_data(Path(folder) / "csv")
        print(f"  加入一筆格式錯誤的課程後載入：課程 {len(loaded.courses)} 門，略過原因：{errors[0]}")


def demo_f2(catalog: SchoolCatalog) -> None:
    print("\n" + "=" * 50)
    print("F2 多層次衝堂與選課檢查")
    # 範例資料中沒有時段重疊的課程，另建一門示範用課程（只存在記憶體，不寫回檔案）
    add_course(catalog, Course("CS120", "演算法（示範用）", 3, True, "王老師", 40, "A205",
                               [TimeSlot(1, "3"), TimeSlot(1, "4"), TimeSlot(3, "b"), TimeSlot(4, "5")]))
    print("\n[多項衝突一次列出]")
    print(format_check_result(check_enrollment(catalog, "S001", "CS120")))
    print("\n[課程已額滿]")
    print(format_check_result(check_enrollment(catalog, "S015", "PE101")))
    print("\n[加選成功後退選]")
    print(format_check_result(enroll_course(catalog, "S015", "CS109")))
    print(f"退選 CS109：{'、'.join(drop_course(catalog, 'S015', 'CS109')) or '成功'}")


def demo_f3(catalog: SchoolCatalog, student_id: str) -> None:
    print("\n" + "=" * 50)
    print(f"F3 個人課表與空閒時段（{student_id} {catalog.students[student_id].name}）")
    table = build_student_timetable(catalog, student_id)
    print(render_timetable(table))
    blocks = find_free_blocks(table, TimeSlot(1, "1"), TimeSlot(2, "9"), min_length=3)
    print("\n星期一第 1 節～星期二第 9 節、連續 3 節以上的空閒時段：")
    for block in blocks:
        print(f"  {block.describe()}")
    stats = timetable_stats(catalog, student_id)
    days = "、".join(f"週{'一二三四五六日'[d - 1]} {n} 節" for d, n in stats["daily_periods"].items() if n)
    print(f"\n每日上課節數：{days}")
    print(f"每週總學分：{stats['total_credits']}｜空堂數：{stats['total_gaps']}｜時段衝突：{stats['conflicts']}")


if __name__ == "__main__":
    main()
