"""F 角色：路徑與事件

用途：
- 規劃校內移動路線
- 處理動態事件
- 影響課表重排
"""

from __future__ import annotations


def estimate_travel_time(start, end):
    """估計移動時間（簡化版本）。"""
    return abs(start - end) * 5


def handle_event(event):
    """處理事件並回傳建議。"""
    return {
        "event": event,
        "action": "check schedule and reroute if needed",
    }


if __name__ == "__main__":
    print(estimate_travel_time(1, 4))
    print(handle_event("下雨"))
