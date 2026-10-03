"""E 角色：搜尋與效能

用途：
- 搜尋可行課表
- 比較多種方案
- 評估優先順序與效率
"""

from __future__ import annotations


def score_course_plan(plan):
    """簡易評分函式。"""
    return sum(plan.get("scores", [0]))


def rank_plans(plans):
    """依分數排序方案。"""
    return sorted(plans, key=lambda p: p.get("scores", [0])[0], reverse=True)


if __name__ == "__main__":
    plans = [{"scores": [70]}, {"scores": [90]}, {"scores": [80]}]
    print(rank_plans(plans))
