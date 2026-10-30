"""產生第 8 週團隊繳交的「系統需求設計規格書 V3.0（Iteration 3，期中 v1.0）」PDF。

用法：python tools/make_srs_sdd_w8.py
輸出：docs/03_週報/第8週_系統需求設計規格書.pdf

版面與共用函式沿用 tools/make_srs_sdd.py。附錄中的執行輸出、測試結果、測試分類與 git log
在產生 PDF 時實際執行取得。會議日期地點改下方 MEETING；照片放在 PHOTO 路徑後重新執行。
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import make_srs_sdd as base  # noqa: E402
import test_report_data  # noqa: E402
from make_srs_sdd import (  # noqa: E402
    BLUE_BG, FRAME_W, MEMBERS, P, SpecDoc, _actor, _arrow, _box, _text, _uc,
    code_block, esc, items, run, table, terminal_block,
)
from reportlab.graphics.shapes import Drawing, Ellipse, Line, Rect  # noqa: E402
from reportlab.lib import colors  # noqa: E402
from reportlab.lib.styles import ParagraphStyle  # noqa: E402
from reportlab.platypus import Image, KeepTogether, NextPageTemplate, PageBreak, Spacer  # noqa: E402
from reportlab.platypus.tableofcontents import TableOfContents  # noqa: E402

ROOT = base.ROOT
OUTPUT = ROOT / "docs" / "03_週報" / "第8週_系統需求設計規格書.pdf"
PHOTO = ROOT / "docs" / "05_會議" / "第8週_團隊討論照片.jpg"
DATE = "2026/10/30"
WEEK_SINCE = "2026-10-25"
AUTHORS = {"0mago0": "A", "dolphin12088": "B", "zhiyun0916": "C", "nNn-3361": "D", "linsam960421-lgtm": "E"}


# ---------- 圖 ----------

def use_case_diagram() -> Drawing:
    d = Drawing(FRAME_W, 300)
    d.add(Rect(70, 6, 330, 288, rx=14, ry=14, fillColor=BLUE_BG, strokeColor=colors.HexColor("#1F3864")))
    _text(d, 235, 280, "活動配置、課程篩選與資料儲存（F4／F5／F6）", 8, font="JHB")
    left = {"新增／修改活動": 252, "取消活動": 214, "查詢可用教室": 176, "報名活動": 138, "多條件篩選課程": 96, "儲存資料": 54, "載入資料": 20}
    for name, y in left.items():
        _uc(d, 150, y, name, 100)
    _uc(d, 320, 214, "檢查教室條件", 100)
    _uc(d, 320, 138, "檢查時段衝突", 100)
    _uc(d, 320, 96, "可行性檢查", 100)
    _uc(d, 320, 36, "逐筆驗證資料", 100)
    black = colors.black
    for src, dst in (("新增／修改活動", 214), ("查詢可用教室", 214), ("新增／修改活動", 138), ("報名活動", 138),
                     ("多條件篩選課程", 96), ("載入資料", 36)):
        _arrow(d, 200, left[src], 270, dst + (4 if dst > left[src] else -4 if dst < left[src] else 0), dashed=True, color=black)
    _text(d, 236, 230, "«include»", 6.5)
    _actor(d, 28, 200, "教務助理")
    _actor(d, 28, 70, "學生")
    for name in ("新增／修改活動", "取消活動", "查詢可用教室", "儲存資料", "載入資料"):
        _arrow(d, 38, 212, 100, left[name])
    for name in ("報名活動", "多條件篩選課程"):
        _arrow(d, 38, 82, 100, left[name])
    return d


def architecture_diagram() -> Drawing:
    d = Drawing(FRAME_W, 330)
    d.add(Rect(30, 6, 400, 318, rx=18, ry=18, fillColor=colors.HexColor("#FBE4D5"), strokeColor=colors.HexColor("#C55A11")))
    _text(d, 230, 312, "campus_planner 核心（可獨立測試的純函式）", 7.5, font="JHB")
    _actor(d, 10, 286, "使用者")
    _box(d, 230, 290, 200, 30, "命令列介面 v1.0", "main.py ＋ cli.py（唯一處理輸入輸出的模組）", colors.HexColor("#5B9BD5"))
    green, yellow = colors.HexColor("#A9D18E"), colors.HexColor("#FFD966")
    for x, title, sub in ((80, "F2 選課檢查", "enrollment.py"), (180, "F3 個人課表", "timetable.py"),
                          (280, "F4 活動與教室", "activities.py"), (380, "F5 課程篩選", "course_filter.py")):
        _box(d, x, 228, 90, 34, title, sub, yellow)
    _box(d, 230, 162, 200, 34, "F1 資料管理", "data_manager.py（SchoolCatalog）", yellow)
    _box(d, 160, 100, 110, 30, "資料驗證", "validation.py", green)
    _box(d, 300, 100, 110, 30, "資料模型", "models.py", green)
    _box(d, 230, 40, 200, 32, "F6 資料儲存", "storage.py（CSV）＋ data_store.py（JSON）", yellow)
    cx, cy = 465, 40
    d.add(Rect(cx - 26, cy - 18, 52, 34, fillColor=colors.HexColor("#C9C9F0"), strokeColor=colors.black, strokeWidth=0.8))
    d.add(Ellipse(cx, cy + 16, 26, 5, fillColor=colors.HexColor("#DADAF7"), strokeColor=colors.black, strokeWidth=0.8))
    d.add(Ellipse(cx, cy - 18, 26, 5, fillColor=colors.HexColor("#C9C9F0"), strokeColor=colors.black, strokeWidth=0.8))
    _text(d, cx, cy - 1, "JSON／CSV", 7, font="JHB")
    _text(d, cx, cy - 11, "資料檔", 6.5)
    _arrow(d, 22, 290, 128, 290)
    for x in (80, 180, 280, 380):
        _arrow(d, 230 + (x - 230) * 0.4, 275, x, 245)
        _arrow(d, x, 211, 230 + (x - 230) * 0.5, 179)
    _arrow(d, 190, 145, 165, 115)
    _arrow(d, 270, 145, 295, 115)
    _arrow(d, 230, 145, 230, 56)
    _arrow(d, 330, 40, 439, 40)
    return d


def wbs_diagram() -> Drawing:
    d = Drawing(FRAME_W, 250)
    root_y = 228
    _box(d, FRAME_W / 2, root_y, 210, 24, "F4＋F5＋F6 與期中系統 v1.0（Iteration 3）", "", BLUE_BG)
    branches = [
        ("需求分析", ["F4／F5／F6 規格", "節次時間表", "驗收條件對照"]),
        ("功能設計", ["CSV 檔案格式", "函式介面", "系統架構圖", "選單設計"]),
        ("功能實作", ["F4 活動與教室", "F5 課程篩選", "F6 CSV／JSON", "CLI 選單 v1.0", "Review 問題修正"]),
        ("功能測試", ["F4～F6 測試", "整合測試", "測試報告", "Iteration Review"]),
    ]
    col_w = FRAME_W / 4
    d.add(Line(col_w / 2, 196, FRAME_W - col_w / 2, 196))
    d.add(Line(FRAME_W / 2, root_y - 12, FRAME_W / 2, 196))
    for i, (title, children) in enumerate(branches):
        cx = col_w * i + col_w / 2
        d.add(Line(cx, 196, cx, 186))
        _box(d, cx, 174, 90, 22, title, "", BLUE_BG)
        x_line = cx - 40
        y = 140
        d.add(Line(x_line, 163, x_line, y - 30 * (len(children) - 1)))
        for child in children:
            d.add(Line(x_line, y, x_line + 8, y))
            _box(d, cx + 8, y, 88, 20, child, "", BLUE_BG)
            y -= 30
    return d


# ---------- 資料表 ----------

CSV_FMT = [
    ["檔案", "欄位", "說明"],
    ["courses.csv", "course_id, name, credits, required, teacher, capacity, classroom, time_slots", "required 為 true／false（也接受必修／選修）；time_slots 寫成 1-3;1-4"],
    ["students.csv", "student_id, name, department, credit_limit", "已選課程另存於 enrollments.csv"],
    ["classrooms.csv", "room_id, capacity, equipment, building", "equipment 以「;」分隔"],
    ["activities.csv", "activity_id, name, time_slots, expected_participants, activity_type, classroom, venue_requirements", "報名名單另存於 activity_participants.csv"],
    ["enrollments.csv", "student_id, course_id", "選課紀錄，一列一筆"],
    ["activity_participants.csv", "activity_id, student_id", "活動報名，一列一筆"],
]
PERIOD_TABLE = [["節次", "1", "2", "3", "4", "5", "6", "7", "8", "9", "a", "b", "c"],
                ["開始", "08:10", "09:10", "10:10", "11:10", "13:10", "14:10", "15:10", "16:10", "17:10", "18:30", "19:25", "20:20"],
                ["結束", "09:00", "10:00", "11:00", "12:00", "14:00", "15:00", "16:00", "17:00", "18:00", "19:20", "20:15", "21:10"]]

RULES = [
    ["編號", "規則", "採用做法", "狀態"],
    ["R22", "時間換算", "依節次時間表，與起訖時間有重疊的節次都算在內；日期換算成星期", "已確認"],
    ["R23", "教室篩選", "容量須 ≥ 需求人數、具備全部設備、時段無課程或活動；可用教室依容量由小到大排序", "已確認"],
    ["R24", "未滿足條件", "沒有合適教室時，逐間列出容量、設備、時段三類未滿足的原因", "已確認"],
    ["R25", "報名人數", "不得超過活動預計人數，也不得超過教室容量", "已確認"],
    ["R26", "取消活動", "移除活動與所有報名，回傳被取消報名的學號", "已確認"],
    ["R27", "篩選基本條件", "排除額滿、位於不可上課時段、與必修衝堂的課程；所有時段都在偏好星期內者標示並排在前面", "已確認"],
    ["R28", "可行性檢查", "最低學分大於最高、必修互相衝堂、必修額滿或位於不可上課時段、必修學分超過上限、必修加所有候選仍不足最低學分，都列為問題", "已確認"],
    ["R29", "CSV 格式", "6 個檔案；選課紀錄與活動報名一列一筆", "已確認"],
    ["R30", "逐筆載入", "格式錯誤只略過該筆；選課紀錄與報名逐列套用，壞的一列不連帶影響學生或活動", "已確認"],
    ["R31", "資料檔不存在", "回報「找不到資料檔」，不無聲回傳空資料", "已確認"],
]

CHANGES = [
    ["日期", "項目", "修改前（第 7 週）", "修改後（第 8 週）", "原因"],
    ["2026/10/30", "資料載入", "清單為 null 時 TypeError 中止", "null 視為空清單；非清單記錄錯誤並略過", "F6；Code Review 第 1 項"],
    ["2026/10/30", "資料檔不存在", "無聲回傳空資料", "回報「找不到資料檔」", "E 的 Code Review 第 2 項"],
    ["2026/10/30", "CSV 儲存", "只有 JSON", "新增 6 個 CSV 檔，選課紀錄、活動報名各自成檔", "F6 要求 CSV 或 JSON"],
    ["2026/10/30", "主程式", "v2：固定示範", "v1.0：互動式選單；--demo 示範 F1～F6", "期中系統 v1.0"],
    ["2026/10/30", "課程顯示", "週一3、週一4", "週一 3、4", "E 的 Code Review 第 4 項"],
    ["2026/10/30", "刪除訊息", "不分原因顯示「需先退選」", "區分課程不存在與已有學生選修", "E 的 Code Review 第 3 項"],
]

ACCEPTANCE = [
    ["驗收條件", "對應測試", "結果"],
    ["F4：至少模擬 10 項活動，含多人報名、活動取消、教室額滿及場地衝突", "test_ten_activities_acceptance_scenario", "通過"],
    ["F4：無合適教室時顯示未滿足的條件", "test_no_suitable_room_lists_unmet_conditions", "通過"],
    ["F4：與課程共用時段衝突檢查", "test_venue_conflict_with_course、test_activity_and_course_share_conflict_check", "通過"],
    ["F5：至少五種限制情境（條件矛盾、課程額滿、無法滿足最低學分等）", "test_contradiction_min_greater_than_max、test_full_course、test_cannot_reach_minimum_credits、"
     "test_required_courses_conflict_with_each_other、test_required_course_in_unavailable_slot、test_required_credits_exceed_maximum", "通過"],
    ["F6：儲存課程、學生、教室、活動及選課紀錄", "test_csv_round_trip、test_enrollment_records_saved", "通過"],
    ["F6：重新啟動後載入原有資料", "test_changes_survive_save_and_reload（JSON、CSV）", "通過"],
    ["F6：單一筆格式錯誤不使程式中止", "test_bad_csv_row_skipped（4 種）、test_non_list_section_reported_and_others_loaded", "通過"],
    ["F6：至少 30 個自動化測試，正常、邊界、錯誤各 10 個以上", "見附錄 B 測試分類表", "通過"],
]

FEATURES = [
    ["功能", "狀態", "說明"],
    ["F1 課程與學生資料管理", "測試通過", "Code Review 第 2～7 項尚待 B 修正"],
    ["F2 多層次衝堂與選課檢查", "測試通過", "25 項測試"],
    ["F3 個人課表與空閒時段", "測試通過", "20 項測試；C 的 Review 建議 2 項待 D 回應"],
    ["F4 校園活動與教室配置", "測試通過", "26 項測試；含 10 項活動驗收情境"],
    ["F5 多條件課程篩選", "測試通過", "18 項測試；含 6 種限制情境"],
    ["F6 資料儲存與系統測試", "測試通過", "JSON 與 CSV；全部自動化測試 169 項"],
    ["F7 最佳課表搜尋", "未開始", "第 10 週（導入 TDD）"],
    ["F8 搜尋演算法比較", "未開始", "第 11 週"],
    ["F9 校園移動路徑規劃", "未開始", "第 12 週"],
    ["F10 動態事件與重新規劃", "未開始", "第 14 週"],
    ["F11 AI 輔助測試與品質改善", "未開始", "第 15 週"],
]

DEFECTS = [
    ["編號", "問題", "狀態", "處理方式／負責"],
    ["D1～D4、D6、D7", "第 6、7 週缺陷（額滿判斷、課表索引、查詢截斷、活動存檔、草稿欄位、節次重複）", "已處理", "第 7 週修正並有回歸測試"],
    ["D5", "新增課程不檢查教室是否存在、不比較人數與教室容量", "部分處理", "活動已在 F4 檢查；課程仍待決定；C、D"],
    ["D8", "範例資料任兩門課時段都不重疊，無法直接示範學生衝堂", "未處理", "E"],
    ["D9", "星期 1.0 通過 F1 驗證", "部分處理", "F3 已擋下；F1 驗證待 B"],
    ["D10", "CSV 一列選課紀錄指向不存在的課程，會連帶讓整位學生及其報名的活動載入失敗", "已處理", "開發 F6 時由測試發現，改為逐列套用；A"],
    ["D11", "資料檔不存在時無聲回傳空資料；刪除訊息不分原因；時段顯示未合併", "已處理", "回應 E 的 Code Review；A"],
    ["D12", "課表文字表格標題與內容不對齊；已選課程不存在時無聲略過", "未處理", "C 的 Code Review，待 D 回應"],
]

REVIEW_ROWS = [
    ["被檢視程式", "原開發者", "Reviewer", "發現", "處理狀態"],
    ["main.py（commit 85b074f）", "A", "E", "示範依賴特定資料、資料檔不存在無提示、刪除訊息、時段顯示共 4 項", "第 1 項第 7 週修正；第 2～4 項本週修正（D11）"],
    ["timetable.py、test_f3_timetable.py", "D", "C", "標題不對齊、不存在的課程無聲略過共 2 項；錯誤輸入處理正常", "待 D 回應（D12）"],
    ["data_manager.py、validation.py", "B", "A", "第 6 週 7 項問題", "第 1 項本週由 A 於 F6 修正；第 2～7 項仍可重現，待 B"],
]

MEETING = [
    ["日期／地點", "2026/10/28（三）12:00｜科研大樓一樓"],
    ["出席", "A、B、C、D、E（全員出席）"],
    ["討論事項", "1. 第 8 週 F4、F5、F6 的範圍與驗收條件。\n2. 期中系統 v1.0 的選單功能。\n3. 自動化測試數量與分類（正常、邊界、錯誤各 10 個以上）。\n"
                "4. Code Review 問題的處理進度。\n5. 影片 I 的主題、分工與錄製方式。"],
    ["工作分配", "A：F6 CSV／JSON 儲存、選單 v1.0、整合測試、測試報告。\nB：修正 Code Review 第 2～7 項。\nC：F5 多條件課程篩選與測試。\n"
                "D：F4 活動與教室配置與測試、回應 C 的 Review。\nE：範例資料補充重疊課程、影片 I 剪輯。"],
    ["決議", "1. F4／F5／F6 細部規格 R22～R31 全部確認採用。\n2. 期中系統以互動式選單作為 v1.0，核心函式不依賴 input()。\n"
            "3. 影片 I 以 F2 多層次衝堂檢查為主題，I-4 使用實際對話紀錄。\n4. 第 10 週起新增功能採 TDD。"],
    ["下週目標", "第 9 週第一次上機測驗；第 10 週 F7 最佳課表搜尋，正式導入 TDD。"],
]


def week_commits() -> list[list[str]]:
    out = subprocess.run(
        ["git", "-c", "core.quotepath=false", "log", f"--since={WEEK_SINCE}", "--format=%h|%ad|%an|%s", "--date=format:%Y/%m/%d"],
        cwd=ROOT, capture_output=True, encoding="utf-8",
    ).stdout.strip()
    rows = [["Commit", "日期", "負責成員", "內容"]]
    for line in out.splitlines():
        sha, date, author, subject = line.split("|", 3)
        if subject.startswith("Add files via upload"):
            names = subprocess.run(["git", "-c", "core.quotepath=false", "show", "--name-only", "--format=", sha],
                                   cwd=ROOT, capture_output=True, encoding="utf-8").stdout.split()
            subject += "（" + "、".join(names) + "）"
        rows.append([sha, date, AUTHORS.get(author, author), subject])
    if len(rows) == 1:
        rows.append(["（尚無）", "", "", "本週程式尚未提交"])
    return rows


def test_table() -> tuple[list[list[str]], str]:
    counts = test_report_data.collect()
    rows = [["測試檔", "正常", "邊界", "錯誤", "合計"]]
    total = {c: 0 for c in test_report_data.CATEGORIES}
    for file, counter in sorted(counts.items()):
        rows.append([file.replace("tests/", ""), *(str(counter[c]) for c in test_report_data.CATEGORIES), str(sum(counter.values()))])
        for c in total:
            total[c] += counter[c]
    rows.append(["全部", *(str(total[c]) for c in test_report_data.CATEGORIES), str(sum(total.values()))])
    return rows, test_report_data.run_tests()


# ---------- 內容 ----------

def cover() -> list:
    story = [Spacer(1, 70), P("校園選課與課表規劃系統", "cover_title"), Spacer(1, 26),
             P("系統需求設計規格書 V 3.0", "cover_sub"), Spacer(1, 10),
             P("Software Requirements Specification (SRS)", "cover_en"),
             P("Software Design Document (SDD)", "cover_en"), Spacer(1, 30),
             P("第 8 週 Iteration 3：F4 活動與教室配置、F5 多條件課程篩選、F6 資料儲存（期中系統 v1.0）", "cover_member"),
             Spacer(1, 130)]
    for _, name, sid, mail in MEMBERS:
        story.append(P(esc(f"{name}　{sid}　{mail}"), "cover_member"))
    story += [Spacer(1, 50), P("計算機程式設計團體作業｜第 15 組", "cover_member"),
              P("Department of Computer Science &amp; Information Engineering", "cover_en"),
              P("National Taipei University of Technology", "cover_en"), Spacer(1, 30), P(DATE, "cover_en")]
    return story


def section_intro() -> list:
    return [
        P("1. 簡介 (Introduction)", "h1"),
        P("1.1 目標 (Purpose)", "h2"),
        P("本文件為 V3.0，描述第 8 週（Iteration 3）完成的 F4 校園活動與教室配置、F5 多條件課程篩選、F6 資料儲存與系統測試，"
          "以及整合 F1～F6 的期中系統 v1.0。F1 見 V1.0，F2、F3 見 V2.0。"),
        P("1.2 系統名稱 (Identification)", "h2"),
        P("校園選課與課表規劃系統（Campus Course Registration and Timetable Planning System），套件 campus_planner，期中版本 v1.0。"),
        P("1.3 概觀 (Overview)", "h2"),
        P("v1.0 提供互動式命令列選單，學生與教務助理可以查詢課程、加退選、查看個人課表與空堂、報名活動、多條件篩選課程、查詢可用教室，"
          "並把所有資料儲存為 JSON 或 CSV、重新啟動後再載入。所有判斷都在可獨立測試的核心函式中完成，只有介面層 cli.py 處理輸入輸出。"),
        P("本週同時對 F1～F6 執行整合測試與回歸測試，自動化測試共 169 項，正常、邊界、錯誤案例各 10 個以上。"),
        PageBreak(),
    ]


def section_system() -> list:
    return [
        P("2 系統 (System)", "h1"),
        P("2.1 系統描述 (System Description)", "h2"),
        P("v1.0 在 V2.0 的架構上新增 F4 activities.py、F5 course_filter.py、F6 storage.py 與介面層 cli.py。"
          "F4 配置教室時沿用 F2 的 room_conflicts，課程與活動共用同一套時段衝突檢查；F5 以 F1 的剩餘名額與 F2 的時段比對篩選課程；"
          "F6 的 CSV 與 JSON 經過同一套 F1 驗證。"),
        P("2.1.1 使用案例模型 (Use Case Model)", "h3"),
        use_case_diagram(),
        P("圖一、系統使用案例圖（F4／F5／F6）", "caption"),
        P("F4 Use Case 描述：新增活動並配置教室", "h4"),
        *items(["Use Case ID：UC-F4-01　主要參與者：教務助理",
                "主要流程：輸入活動名稱、日期、起訖時間、預計人數、類型與設備需求 → 系統換算成星期與節次 → 依容量、設備、時段篩選教室 → 選定教室新增活動。",
                "例外流程：沒有合適教室時，逐間列出未滿足的條件（容量、設備、時段已被使用）；日期或時間格式錯誤、開始晚於結束時回報錯誤。"]),
        P("F5 Use Case 描述：多條件篩選課程", "h4"),
        *items(["Use Case ID：UC-F5-01　主要參與者：學生",
                "主要流程：輸入必修清單、最低與最高學分、不可上課時段、偏好星期 → 系統列出候選課程（偏好星期的排在前面）與被排除課程的原因 → 顯示是否可行。",
                "例外流程：條件互相矛盾、必修衝堂或額滿、無法湊到最低學分時，列出具體原因。"]),
        P("F6 Use Case 描述：儲存與重新載入", "h4"),
        *items(["Use Case ID：UC-F6-01　主要參與者：教務助理",
                "主要流程：選擇儲存位置（.json 檔或 CSV 資料夾）→ 系統寫出課程、學生、教室、活動與選課紀錄 → 重新啟動後載入。",
                "例外流程：某一筆資料格式錯誤時只略過該筆並列出原因，其餘資料照常載入；資料檔不存在時回報。"]),
        P("2.1.2 系統架構圖 (System Architecture Diagram)", "h3"),
        architecture_diagram(),
        P("圖二、系統架構圖（v1.0）", "caption"),
        P("2.2 系統資料 (System Data)", "h2"),
        P("2.2.1 資料格式 (Data Format)", "h3"),
        P("JSON 格式與 V2.0 相同。本週新增 CSV 格式，以一個資料夾存放 6 個檔案："),
        table(CSV_FMT, [22, 46, 32]), Spacer(1, 6),
        P("節次時間表（F4 日期與時間換算使用）：", "label"),
        table(PERIOD_TABLE, [10] + [7.5] * 12),
        P("2.3 需求規格 (Requirements)", "h2"),
        P("2.3.1 F4／F5／F6 細部規格 (Detailed Rules)", "h3"),
        table(RULES, [8, 15, 65, 12]), Spacer(1, 6),
        P("2.3.2 需求／設計修改紀錄 (Change Log)", "h3"),
        table(CHANGES, [14, 14, 24, 28, 20]),
        PageBreak(),
    ]


def section_design() -> list:
    funcs = [["模組", "函式", "說明"],
             ["F4 activities.py", "time_range_to_slots(date, start, end)", "日期與起訖時間換算成星期＋節次"],
             ["", "find_available_rooms(catalog, time_slots, headcount, equipment)", "回傳可用教室與其餘教室未滿足的條件"],
             ["", "create_activity／update_activity／assign_room", "新增、修改、配置教室；失敗時資料不變"],
             ["", "cancel_activity／find_activities", "取消（回傳被取消報名的學號）、依類型／星期／教室／學生查詢"],
             ["", "check_registration／register_activity／unregister_activity", "報名檢查含活動衝突、預計人數與教室容量"],
             ["F5 course_filter.py", "filter_courses(catalog, criteria) → FilterResult", "候選課程、被排除課程原因、可行性問題"],
             ["", "format_filter_result(result)", "文字輸出，偏好星期的課程以 ★ 標示"],
             ["F6 storage.py", "save_catalog_csv／load_catalog_csv", "6 個 CSV 檔；逐筆驗證、逐列套用選課紀錄"],
             ["", "save_data／load_data(path)", "依副檔名自動選擇 JSON 或 CSV"],
             ["介面 cli.py", "run_menu(catalog, ask, say)", "互動式選單；輸入輸出函式以參數傳入，可自動化測試"]]
    rows, summary = test_table()
    return [
        P("3. 軟體設計 (Software Design)", "h1"),
        P("3.1 函式功能介面 (Functionality Interface)", "h2"),
        table(funcs, [20, 42, 38]), Spacer(1, 6),
        P("使用範例", "label"),
        code_block('''slots = time_range_to_slots("2026-11-04", "15:10", "17:00")   # 星期三第 7、8 節
search = find_available_rooms(catalog, slots, 50, ["投影機"])
print([r.room_id for r in search.available])        # ['A101']
print(search.unmet["C305"])                          # ['時段已被使用：星期三第 8 節 GE102 通識：台灣史']

criteria = FilterCriteria(required=["CS101", "MA101"], min_credits=15, max_credits=22,
                          unavailable=[TimeSlot(1, "1"), TimeSlot(1, "2")], preferred_days=[2, 3, 4])
print(format_filter_result(filter_courses(catalog, criteria)))

save_data("backup", catalog)                         # 寫出 6 個 CSV
catalog, errors = load_data("backup")                # 格式錯誤的列略過並列在 errors'''),
        P("3.2 測試案例設計 (Test case design)", "h2"),
        P(f"自動化測試依測試檔的區段分為正常、邊界、錯誤三類。目前執行結果：{esc(summary)}。詳細見另附之測試報告。"),
        table(rows, [40, 15, 15, 15, 15]), Spacer(1, 6),
        P("F4／F5／F6 驗收條件對照：", "label"), table(ACCEPTANCE, [34, 52, 14]),
        P("3.3 專案審查 (Iteration Review 3)", "h2"),
        P("本次 Iteration 完成哪些工作？（Completed Work）", "label"),
        *items([
            "1. F4：時間換算、教室篩選（列出未滿足條件）、活動新增／修改／取消／查詢、報名檢查含教室容量。",
            "2. F5：多條件篩選與可行性檢查，涵蓋條件矛盾、額滿、必修衝堂、無法滿足最低學分等情境。",
            "3. F6：CSV 與 JSON 儲存載入，單筆錯誤只略過該筆；修正 Code Review 第 1 項。",
            "4. 期中系統 v1.0：互動式選單與 F1～F6 示範；回應 E 對 main.py 的 Code Review。",
            "5. 自動化測試 169 項全部通過，含 F1～F6 整合測試。",
        ]),
        P("哪些工作尚未完成？（Incomplete Work）", "label"),
        *items([
            "1. Code Review 第 2～7 項（B）、C 對 F3 的 2 項建議（D）尚未處理。",
            "2. 範例資料仍缺少時段重疊的課程（D8）。",
            "3. 影片 I 待錄製。",
        ]),
        P("本次 Iteration 遇到哪些問題？（Problems）", "label"),
        *items([
            "1. CSV 載入的第一版把選課紀錄併入學生資料再驗證，一列錯誤的選課紀錄會讓整位學生和他報名的活動一起載入失敗；由測試發現後改為逐列套用。",
            "2. 活動的日期與時間需要對應節次，團隊先前沒有節次時間表，本週定義並寫入規格。",
            "3. 互動式選單需要使用 input()，為了維持核心函式可測試，把輸入輸出集中在 cli.py，並以參數傳入。",
        ]),
        P("下一次 Iteration 如何改善？（Improvements）", "label"),
        *items([
            "1. 第 10 週起新增功能採 TDD：先寫失敗的測試，再實作，保留 Red／Green／Refactor 紀錄。",
            "2. Code Review 的問題設定處理期限，在每週會議追蹤。",
            "3. 範例資料補充重疊與額滿情境，讓驗收可直接以範例資料呈現。",
        ]),
        PageBreak(),
    ]


def section_pm() -> list:
    def task(no, title, desc, days, owner):
        return P(esc(f"{no} {title}：{desc}預估工作量：{days} 人天。負責人：{owner}。"), "item")
    member_rows = [["組員", "擔任角色", "主要負責工作", "協作／檢視工作"],
                   ["A", "組長／整合", "F6 儲存、選單 v1.0、整合測試、測試報告", "回應 E 的 Review、追蹤 B 的問題"],
                   ["B", "資料管理", "修正 Code Review 第 2～7 項", "檢視 C 的 F5"],
                   ["C", "選課限制", "F5 多條件課程篩選與測試", "檢視 D 的 F4"],
                   ["D", "課表活動", "F4 活動與教室配置與測試", "檢視 E 的資料"],
                   ["E（副組長）", "搜尋效能", "範例資料補充、影片 I 剪輯", "檢視 A 的 F6"]]
    return [
        P("4. 專案管理 (Project Management)", "h1"),
        P("4.1 工作分解表 (Work Breakdown Structure)", "h2"),
        P("3. 期中系統 v1.0", "label"),
        task("3.1", "需求分析", "F4／F5／F6 細部規格 R22～R31、節次時間表、驗收條件。", 1, "C、D、A"),
        task("3.2", "F4 活動與教室配置", "時間換算、教室篩選、活動管理、報名檢查與測試。", 3, "D"),
        task("3.3", "F5 多條件課程篩選", "篩選、可行性檢查與測試。", 2, "C"),
        task("3.4", "F6 資料儲存", "CSV 與 JSON 儲存載入、逐筆驗證與測試。", 2, "A"),
        task("3.5", "選單 v1.0 與整合測試", "互動式選單、F1～F6 整合測試、測試報告。", 2, "A"),
        task("3.6", "Code Review 修正", "B 修正第 2～7 項；A 回應 E 的 Review；D 回應 C 的 Review。", 1, "A、B、D"),
        task("3.7", "影片 I", "選題、分鏡、錄製與剪輯。", 2, "全員（E 剪輯）"),
        Spacer(1, 8),
        table(member_rows, [13, 14, 39, 34]),
        Spacer(1, 10),
        KeepTogether([wbs_diagram(), P("圖三、工作分解結構圖（Iteration 3）", "caption")]),
        P("4.2 版本控管 (Version Control)", "h2"),
        P("Git Repository：https://github.com/0mago0/programing_team_project"),
        P("本週主要 Commit 與負責成員：", "label"),
        table(week_commits(), [13, 15, 10, 62]), Spacer(1, 6),
        P("完整 git log：", "label"),
        terminal_block(base.git_log()),
        PageBreak(),
    ]


def _photo(path: Path, max_height: float = 420) -> Image:
    """依照片實際比例縮放，直式照片限制高度。"""
    from reportlab.lib.utils import ImageReader
    w, h = ImageReader(str(path)).getSize()
    scale = min(FRAME_W / w, max_height / h)
    return Image(str(path), width=w * scale, height=h * scale)


def section_end() -> list:
    glossary = [["名詞", "說明"],
                ["v1.0", "期中系統版本，整合 F1～F6 並提供互動式選單。"],
                ["節次時間表", "每一節的起訖時間，用來把活動的日期與時間換算成星期＋節次。"],
                ["未滿足條件", "教室不適合活動的原因：容量不足、缺少設備或時段已被使用。"],
                ["可行性檢查", "F5 檢查篩選條件本身是否矛盾、能否湊到最低學分。"],
                ["整合測試", "把多個模組串在一起執行的測試，例如加選後存檔再載入。"],
                ["回歸測試", "針對已修正的缺陷所寫的測試，確保缺陷不再出現。"]]
    refs = ["[1] 1151 計算機程式設計團體作業規範（docs/00_老師作業/assignment.pdf）。",
            "[2] 系統需求設計規格書 V1.0、V2.0（docs/03_週報/）。",
            "[3] 第 8 週測試報告、AI 協作紀錄（docs/03_週報/）。",
            "[4] Python 3.11 官方文件：csv、datetime。https://docs.python.org/3.11/"]
    photo = ([_photo(PHOTO), P("第 8 週團隊討論（2026/10/28，科研大樓一樓）", "caption")]
             if PHOTO.exists() else [P("（第 8 週團隊討論照片待補）", "caption")])
    review_note = P("另：第 6 週 B 的 7 項問題中，第 1 項（清單為 null 時載入中止）已由 A 在 F6 修正並加入回歸測試；第 2～7 項本週重新執行仍可重現。")
    return [
        P("Glossary", "h1"), table(glossary, [24, 76]), PageBreak(),
        P("References", "h1"), *items(refs), PageBreak(),
        P("Appendix", "h1"),
        P("A. 功能完成表", "label"), table(FEATURES, [26, 14, 60]), Spacer(1, 8),
        P("B. 問題與缺陷紀錄", "label"), table(DEFECTS, [13, 47, 11, 29]), Spacer(1, 8),
        P("C. Code Review 紀錄", "label"), table(REVIEW_ROWS, [22, 10, 10, 30, 28]), Spacer(1, 4), review_note, Spacer(1, 8),
        P("D. 執行方式", "label"),
        code_block("python main.py           # 互動式選單 v1.0\npython main.py --demo    # 依序示範 F1～F6\npython -m pytest -q      # 執行全部自動化測試"),
        P("E. main.py --demo 執行結果", "label"),
        terminal_block("$ python main.py --demo\n" + run(["main.py", "--demo"])),
        Spacer(1, 6),
        P("F. 自動化測試結果", "label"),
        terminal_block("$ python -m pytest -q\n" + run(["-m", "pytest", "-q", "-p", "no:cacheprovider"])),
        Spacer(1, 8),
        P("G. 團隊會議紀錄與討論照片", "label"),
        table(MEETING, [18, 82], header=False), Spacer(1, 8),
        KeepTogether(photo),
    ]


def build() -> None:
    toc = TableOfContents(dotsMinLevel=0)
    toc.levelStyles = [
        ParagraphStyle("t0", fontName="JHB", fontSize=11, leading=18, leftIndent=0),
        ParagraphStyle("t1", fontName="KAI", fontSize=11, leading=17, leftIndent=18),
        ParagraphStyle("t2", fontName="KAI", fontSize=10.5, leading=16, leftIndent=36),
    ]
    story = [*cover(), NextPageTemplate("front"), PageBreak(),
             P("目錄 (Table of Contents)", "toc_title"), toc,
             NextPageTemplate("body"), PageBreak(),
             *section_intro(), *section_system(), *section_design(), *section_pm(), *section_end()]
    doc = SpecDoc(str(OUTPUT))
    doc.title = "系統需求設計規格書 V3.0"
    doc.multiBuild(story)
    print(f"已產生：{OUTPUT}")


if __name__ == "__main__":
    build()
