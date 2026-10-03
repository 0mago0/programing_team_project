"""B 角色：資料模型

用途：
- 定義課程、學生、教室等核心資料
- 建立欄位規格與驗證邏輯
"""

from __future__ import annotations


def define_course_schema():
    """回傳課程資料欄位定義。"""
    return {
        "course_id": "string",
        "course_name": "string",
        "credits": "int",
        "teacher": "string",
        "classroom": "string",
        "time_slots": "list",
    }


def define_student_schema():
    """回傳學生資料欄位定義。"""
    return {
        "student_id": "string",
        "name": "string",
        "department": "string",
        "year": "int",
        "max_credits": "int",
    }


if __name__ == "__main__":
    print(define_course_schema())
    print(define_student_schema())
