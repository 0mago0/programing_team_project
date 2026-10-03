"""D 角色：課表與活動

用途：
- 建立週課表
- 安排活動與場地
- 處理時間矩陣
"""

from __future__ import annotations


def build_week_schedule(days=5, periods=8):
    """建立空白課表矩陣。"""
    return [[None for _ in range(periods)] for _ in range(days)]


def add_activity(schedule, day, period, activity_name):
    """將活動加入指定時段。"""
    schedule[day][period] = activity_name
    return schedule


if __name__ == "__main__":
    schedule = build_week_schedule()
    print(add_activity(schedule, 0, 1, "數學課"))
