"""依新版團體作業繳交格式打包第 8 週繳交檔。

用法：python tools/package_group_submission.py <影片檔.mp4>
輸出（deliverables/）：
  第15組_第8週_Group.zip           只含 Group/，給組員放進自己的資料夾，確保 Group 內容完全一致
  第15組_111590042_張庭瑄.zip      組別_學號_姓名/ 底下 Personal/ 與 Group/

結構：
  組別_學號_姓名/
    Personal/  個人繳交 PDF
    Group/     團體作業 PDF、程式碼/、其他檔案/
"""
from __future__ import annotations

import shutil
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "deliverables"
WEEK = ROOT / "docs" / "03_週報"
TOP = "第15組_111590042_張庭瑄"
CODE_FILES = ["main.py", "pytest.ini", "requirements.txt"]
CODE_DIRS = ["campus_planner", "data", "tests"]
SKIP = {"__pycache__", ".pytest_cache"}

RUN_NOTE = """校園選課與課表規劃系統 期中系統 v1.0｜第 15 組｜第 8 週（Iteration 3）F4 活動與教室配置、F5 多條件課程篩選、F6 資料儲存

環境：Python 3.11 以上，測試需要 pytest（pip install -r requirements.txt）

在本資料夾執行：
  python main.py           互動式選單：查詢、加退選、課表、活動報名、課程篩選、查詢教室、儲存與載入
  python main.py --demo    依序示範 F1～F6
  python -m pytest -q      執行全部自動化測試（169 項：正常 50、邊界 33、錯誤 86）

主要檔案：
  campus_planner/activities.py     F4 活動建立、教室篩選與報名
  campus_planner/course_filter.py  F5 多條件課程篩選
  campus_planner/storage.py        F6 CSV／JSON 儲存與載入
  campus_planner/cli.py            互動式選單 v1.0
  campus_planner/enrollment.py     F2 多層次衝堂與選課檢查
  campus_planner/timetable.py      F3 個人課表與空閒時段
  campus_planner/data_manager.py   F1 課程、學生、教室、活動資料管理
  tests/test_integration.py        F1～F6 整合測試
"""


def build(video: Path) -> Path:
    base = OUT / TOP
    if base.exists():
        shutil.rmtree(base)
    group = base / "Group"
    code = group / "程式碼"
    other = group / "其他檔案"
    personal = base / "Personal"
    for d in (code, other / "影片I", personal):
        d.mkdir(parents=True)

    shutil.copy2(WEEK / "第8週_系統需求設計規格書.pdf", group / "第15組_第8週_系統需求設計規格書V3.0.pdf")
    for name in CODE_FILES:
        shutil.copy2(ROOT / name, code / name)
    for name in CODE_DIRS:
        shutil.copytree(ROOT / name, code / name, ignore=shutil.ignore_patterns(*SKIP))
    (code / "執行說明.txt").write_text(RUN_NOTE, encoding="utf-8")

    shutil.copy2(WEEK / "第8週_測試報告.pdf", other / "測試報告.pdf")
    shutil.copy2(WEEK / "第8週_AI協作紀錄.pdf", other / "AI協作紀錄.pdf")
    shutil.copy2(ROOT / "docs" / "05_會議" / "第8週_團隊討論照片.jpg", other / "團隊討論照片.jpg")
    shutil.copy2(video, other / "影片I" / "第十五組程式影片.mp4")
    for src, dst in (("第8週_影片I投影片.pdf", "影片I投影片.pdf"), ("第8週_影片I講稿.pdf", "影片I講稿.pdf"),
                     ("第8週_影片I腳本.pdf", "影片I腳本與附件清單.pdf")):
        shutil.copy2(WEEK / src, other / "影片I" / dst)

    shutil.copy2(ROOT / "docs" / "04_個人紀錄" / "成員A" / "第8週_個人紀錄.pdf",
                 personal / "111590042_張庭瑄_個人工作報告I.pdf")
    return base


def zip_dir(src: Path, archive: Path, root: Path) -> None:
    with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as z:
        for path in sorted(src.rglob("*")):
            if path.is_file():
                z.write(path, path.relative_to(root))
    with zipfile.ZipFile(archive) as z:
        if z.testzip():
            raise RuntimeError(f"ZIP 驗證失敗：{archive}")
        print(f"{archive.name}：{len(z.namelist())} 個檔案，{archive.stat().st_size / 1e6:.1f} MB")


def main() -> None:
    if len(sys.argv) != 2 or not Path(sys.argv[1]).is_file():
        raise SystemExit("用法：python tools/package_group_submission.py <影片檔.mp4>")
    base = build(Path(sys.argv[1]))
    zip_dir(base / "Group", OUT / "第15組_第8週_Group.zip", base)
    zip_dir(base, OUT / f"{TOP}.zip", base.parent)


if __name__ == "__main__":
    main()
