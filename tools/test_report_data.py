"""收集自動化測試的分類與結果，供測試報告使用。

python tools/test_report_data.py   印出各測試檔正常／邊界／錯誤案例數與執行結果

分類方式：測試檔內以「# ---------- 正常案例 ----------」等區段標題分組，測試歸入其上方最近的區段；
沒有區段標題的早期測試檔以 LEGACY 對照表分類。參數化測試每一組參數各算一個案例。
"""
from __future__ import annotations

import re
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CATEGORIES = ("正常", "邊界", "錯誤")
LEGACY = {
    "test_valid_course_passes": "正常",
    "test_invalid_course_diagnostics": "錯誤",
    "test_student_and_conflict_checks": "正常",
    "test_timetable_generation_and_json_round_trip": "正常",
    "test_add_and_find_courses": "正常",
    "test_reject_duplicate_and_invalid_course_data": "錯誤",
    "test_delete_course_protected_when_students_enrolled": "錯誤",
    "test_student_management_and_queries": "正常",
}


def _python() -> str:
    venv = ROOT / ".venv" / "Scripts" / "python.exe"
    return str(venv) if venv.exists() else sys.executable


def section_map(path: Path) -> dict[str, str]:
    """測試函式名稱 → 分類。"""
    result: dict[str, str] = {}
    current = ""
    for line in path.read_text(encoding="utf-8").splitlines():
        header = re.match(r"#\s*-+\s*(.+?)\s*-+\s*$", line.strip())
        if header:
            text = header.group(1)
            current = next((c for c in CATEGORIES if text.startswith(c)), current)
        match = re.match(r"def (test_\w+)", line)
        if match:
            result[match.group(1)] = current or LEGACY.get(match.group(1), "未分類")
    return result


def collect() -> dict[str, Counter]:
    out = subprocess.run([_python(), "-m", "pytest", "--collect-only", "-q", "-p", "no:cacheprovider"],
                         cwd=ROOT, capture_output=True, encoding="utf-8").stdout
    maps: dict[str, dict[str, str]] = {}
    counts: dict[str, Counter] = defaultdict(Counter)
    for nodeid in out.splitlines():
        if "::" not in nodeid:
            continue
        file, name = nodeid.split("::", 1)
        func = name.split("[", 1)[0]
        if file not in maps:
            maps[file] = section_map(ROOT / file)
        counts[file][maps[file].get(func, "未分類")] += 1
    return counts


def run_tests() -> str:
    out = subprocess.run([_python(), "-m", "pytest", "-q", "-p", "no:cacheprovider"],
                         cwd=ROOT, capture_output=True, encoding="utf-8").stdout
    return out.strip().splitlines()[-1]


if __name__ == "__main__":
    counts = collect()
    total: Counter = Counter()
    for file, counter in sorted(counts.items()):
        total.update(counter)
        print(f"{file:35} " + "  ".join(f"{c} {counter[c]:3}" for c in (*CATEGORIES, "未分類")) + f"  合計 {sum(counter.values())}")
    print(f"{'全部':35} " + "  ".join(f"{c} {total[c]:3}" for c in (*CATEGORIES, "未分類")) + f"  合計 {sum(total.values())}")
    print(run_tests())
