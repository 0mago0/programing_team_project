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
from campus_planner.models import Course, TimeSlot

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

    print("校園選課專題 - 第 6 週 F1 課程與學生資料管理")
    print("=" * 50)
    print(f"資料檔：{SAMPLE_DATA.name}")
    print(f"課程 {len(catalog.courses)} 門、學生 {len(catalog.students)} 名、教室 {len(catalog.classrooms)} 間")
    if load_errors:
        print("載入時略過的資料：")
        for message in load_errors:
            print(f"  - {message}")

    print_courses(catalog, "林老師的課", find_courses(catalog, teacher="林老師"))
    print_courses(catalog, "星期一有上課的必修", find_courses(catalog, day=1, required=True))
    print_courses(catalog, "CS 開頭且已額滿", [
        c for c in find_courses(catalog, course_id="CS") if remaining_seats(catalog, c.course_id) == 0
    ])

    students = find_students(catalog, department="數學系")
    print(f"\n[數學系學生] 共 {len(students)} 名：" + "、".join(f"{s.student_id} {s.name}" for s in students))

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


if __name__ == "__main__":
    main()
