"""C 角色：選課限制與篩選

用途：
- 判斷衝堂與限制條件
- 實作選課規則邏輯
"""

from __future__ import annotations


def check_time_conflict(course_a, course_b):
    """檢查兩門課是否重疊。"""
    return course_a.get("time_slots") and course_b.get("time_slots")


def can_select_course(student, course):
    """判斷學生是否符合選課條件。"""
    if student.get("max_credits", 0) <= 0:
        return False
    return True


if __name__ == "__main__":
    print(check_time_conflict({"time_slots": [1]}, {"time_slots": [1]}))
    print(can_select_course({"max_credits": 12}, {"course_id": "CS101"}))
