from __future__ import annotations

from campus_planner.planner import build_demo_school_data
from campus_planner.validation import validate_course, validate_student


def main() -> None:
    data = build_demo_school_data()
    courses = data["courses"]
    students = data["students"]

    print("校園選課專題 - 第 5 週最小骨架")
    print("=" * 50)
    print(f"課程數量: {len(courses)}")
    print(f"學生數量: {len(students)}")
    print(f"教室數量: {len(data['classrooms'])}")
    print()
    print("核心模組：models / validation / data_store / planner / timetable")
    print("執行方式：python main.py")
    print("測試方式：python -m pytest")
    print()

    for course in courses:
        errors = validate_course(course)
        if errors:
            print(f"{course.course_id} 驗證錯誤: {errors}")
        else:
            print(f"{course.course_id} 驗證成功")

    for student in students:
        result = validate_student(student)
        print(f"{student.student_id} -> {result if result else 'OK'}")


if __name__ == "__main__":
    main()
