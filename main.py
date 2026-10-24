from __future__ import annotations

from pathlib import Path

from campus_planner.data_manager import (
    SchoolCatalog,
    add_course,
    delete_course,
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
    slots = "、".join(f"週{DAY_NAMES[s.day - 1]}{s.period}" for s in course.time_slots)
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
    catalog, load_errors = load_catalog(SAMPLE_DATA)

    print("校園選課與課表規劃系統 v2 - 第 7 週（F1 資料管理、F2 選課檢查、F3 個人課表）")
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

    deleted = delete_course(catalog, "CS101")
    print(f"  刪除已有人選修的 CS101：{'成功' if deleted else '拒絕（需先退選或執行課程取消）'}")

    demo_f2(catalog)
    demo_f3(catalog, "S001")


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
