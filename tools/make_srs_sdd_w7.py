"""產生第 7 週團隊繳交的「系統需求設計規格書 V2.0（Iteration 2）」PDF。

用法：python tools/make_srs_sdd_w7.py
輸出：docs/03_週報/第7週_系統需求設計規格書.pdf

版面、字型與共用函式沿用 tools/make_srs_sdd.py（第 6 週 V1.0）。附錄中的執行輸出、
測試結果與 git log 在產生 PDF 時實際執行取得；本週 Commit 依 git log 自動列出。
會議日期與地點請修改下方 MEETING 後重新執行。
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import make_srs_sdd as base  # noqa: E402  共用字型註冊、樣式與繪圖函式
from make_srs_sdd import (  # noqa: E402
    BLUE_BG, FRAME_W, MEMBERS, S, P, SpecDoc, _actor, _arrow, _box, _text, _uc,
    code_block, esc, items, run, table, terminal_block,
)
from reportlab.graphics.shapes import Drawing, Ellipse, Line, Rect  # noqa: E402
from reportlab.lib import colors  # noqa: E402
from reportlab.lib.styles import ParagraphStyle  # noqa: E402
from reportlab.platypus import Image, KeepTogether, NextPageTemplate, PageBreak, Spacer  # noqa: E402
from reportlab.platypus.tableofcontents import TableOfContents  # noqa: E402

ROOT = base.ROOT
OUTPUT = ROOT / "docs" / "03_週報" / "第7週_系統需求設計規格書.pdf"
PHOTO = ROOT / "docs" / "05_會議" / "第7週_團隊討論照片.jpg"
DATE = "2026/10/24"
WEEK_SINCE = "2026-10-17"
AUTHORS = {"0mago0": "A", "dolphin12088": "B", "zhiyun0916": "C", "nNn-3361": "D", "linsam960421-lgtm": "E"}


# ---------- 圖 ----------

def use_case_diagram() -> Drawing:
    d = Drawing(FRAME_W, 290)
    d.add(Rect(70, 6, 360, 276, rx=14, ry=14, fillColor=BLUE_BG, strokeColor=colors.HexColor("#1F3864")))
    _text(d, 250, 268, "選課檢查與個人課表（F2／F3）", 8, font="JHB")
    base_uc = {"加選課程": 240, "退選課程": 198, "參加活動": 156, "查詢個人課表": 114, "查詢空閒時段": 72, "課表統計": 30}
    for name, y in base_uc.items():
        _uc(d, 150, y, name, 92)
    _uc(d, 345, 222, "檢查時段衝突", 100)
    _uc(d, 345, 170, "檢查學分與名額", 100)
    _uc(d, 345, 72, "產生 7×12 課表", 100)
    black = colors.black
    _arrow(d, 196, base_uc["加選課程"], 296, 224, dashed=True, color=black)
    _arrow(d, 196, base_uc["加選課程"] - 4, 296, 174, dashed=True, color=black)
    _arrow(d, 196, base_uc["參加活動"], 296, 218, dashed=True, color=black)
    for name in ("查詢個人課表", "查詢空閒時段", "課表統計"):
        _arrow(d, 196, base_uc[name], 296, 72 + (base_uc[name] - 72) * 0.15, dashed=True, color=black)
    _text(d, 250, 238, "«include»", 6.5)
    _text(d, 250, 104, "«include»", 6.5)
    _actor(d, 28, 140, "學生")
    for y in base_uc.values():
        _arrow(d, 38, 152, 104, y)
    return d


def architecture_diagram() -> Drawing:
    d = Drawing(FRAME_W, 300)
    d.add(Rect(38, 6, 300, 288, rx=18, ry=18, fillColor=colors.HexColor("#FBE4D5"), strokeColor=colors.HexColor("#C55A11")))
    _text(d, 188, 282, "campus_planner 核心（可獨立測試的純函式）", 7.5, font="JHB")
    _actor(d, 14, 250, "使用者")
    _box(d, 188, 258, 170, 30, "命令列介面 CLI v2", "main.py", colors.HexColor("#5B9BD5"))
    _box(d, 110, 200, 120, 34, "F2 選課檢查", "enrollment.py", colors.HexColor("#FFD966"))
    _box(d, 266, 200, 120, 34, "F3 個人課表", "timetable.py", colors.HexColor("#FFD966"))
    _box(d, 188, 140, 190, 34, "F1 資料管理", "data_manager.py（SchoolCatalog）", colors.HexColor("#FFD966"))
    _box(d, 128, 82, 110, 32, "資料驗證", "validation.py", colors.HexColor("#A9D18E"))
    _box(d, 248, 82, 110, 32, "資料模型", "models.py", colors.HexColor("#A9D18E"))
    _box(d, 188, 28, 170, 30, "資料存取", "data_store.py（JSON 讀寫）", colors.HexColor("#FFD966"))
    cx, cy = 400, 28
    d.add(Rect(cx - 32, cy - 18, 64, 34, fillColor=colors.HexColor("#C9C9F0"), strokeColor=colors.black, strokeWidth=0.8))
    d.add(Ellipse(cx, cy + 16, 32, 6, fillColor=colors.HexColor("#DADAF7"), strokeColor=colors.black, strokeWidth=0.8))
    d.add(Ellipse(cx, cy - 18, 32, 6, fillColor=colors.HexColor("#C9C9F0"), strokeColor=colors.black, strokeWidth=0.8))
    _text(d, cx, cy - 2, "JSON 資料檔", 7.5, font="JHB")
    _text(d, cx, cy - 12, "課程／學生／教室／活動", 5.5)
    _box(d, 400, 140, 100, 38, "F4 活動與教室", "第 8 週實作", colors.HexColor("#F4B183"), dashed=True)
    _box(d, 400, 210, 100, 38, "F5～F11", "依週次加入", colors.HexColor("#F4B183"), dashed=True)
    _arrow(d, 6 + 20, 258, 102, 258)
    _arrow(d, 150, 243, 120, 217)
    _arrow(d, 226, 243, 256, 217)
    _arrow(d, 188, 243, 188, 157)
    _arrow(d, 120, 183, 160, 157)
    _arrow(d, 256, 183, 216, 157)
    _arrow(d, 150, 123, 135, 98)
    _arrow(d, 226, 123, 241, 98)
    _arrow(d, 188, 123, 188, 43)
    _arrow(d, 273, 28, 367, 28)
    _arrow(d, 350, 140, 283, 140, dashed=True)
    _arrow(d, 350, 210, 326, 204, dashed=True)
    return d


def wbs_diagram() -> Drawing:
    d = Drawing(FRAME_W, 250)
    root_y = 228
    _box(d, FRAME_W / 2, root_y, 200, 24, "F2＋F3 選課檢查與個人課表（Iteration 2）", "", BLUE_BG)
    branches = [
        ("需求分析", ["F2／F3 規格 R12～R21", "F4 需求分析", "驗收條件對照"]),
        ("功能設計", ["活動資料格式", "函式介面", "系統架構圖", "F4 介面設計"]),
        ("功能實作", ["F2 選課檢查", "F3 課表與空堂", "缺陷修正", "範例活動資料", "CLI v2 main.py"]),
        ("功能測試", ["F2 測試 25 項", "F3 測試 20 項", "Code Review 追蹤", "Iteration Review"]),
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

ACTIVITY_FMT = [
    ["欄位", "中文", "型別與限制"],
    ["activity_id", "活動代號", "str，不可空白、不可重複"],
    ["name", "活動名稱", "str，不可空白"],
    ["time_slots", "活動時段", "list[{day, period}]，至少一個；規則與課程相同"],
    ["expected_participants", "預計人數", "正整數；報名人數不得超過"],
    ["activity_type", "活動類型", "str，例如讀書會、社團、講座"],
    ["classroom", "使用教室", "str，可空白；填寫時教室必須存在"],
    ["venue_requirements", "場地需求", "list[str]，例如投影機、電腦（F4 配置教室時使用）"],
    ["participants", "報名學生", "list[學號]，學生必須存在、不可重複；為學生參加活動的唯一來源"],
]
ACTIVITY_EX = [
    ["activity_id", "name", "time_slots", "expected", "type", "classroom", "participants"],
    ["A001", "程式設計讀書會", "週四 5", "20", "讀書會", "L102", "S001、S002"],
    ["A002", "社團博覽會", "週六 5、6", "60", "社團", "C305", "S004、S014"],
    ["A003", "系學會迎新", "週五 9", "50", "系學會", "A101", "S001、S006、S011"],
    ["A004", "英文檢定說明會", "週一 5", "40", "講座", "B201", "S005、S013"],
]

RULES = [
    ["編號", "規則", "採用做法", "理由", "狀態"],
    ["R12", "衝突的排序與合併", "依星期、節次、代號排序；同一門課在同一天的連續衝突合併成一筆（如「星期二第 3、4 節」）", "對應 F2 驗收「依星期及節次排序」與作業輸出範例", "已確認"],
    ["R13", "教室衝堂", "加選時一併檢查課程教室在同時段是否已被其他課程或活動使用", "規範：同一教室同時段不得安排兩門課程或活動", "已確認"],
    ["R14", "學分上限", "加選後總學分等於上限可通過，超過才拒絕", "規範：「不得超過」上限", "已確認"],
    ["R15", "額滿判斷", "選修人數（由學生已選課程計算）大於或等於人數上限即額滿", "沿用 R10 唯一資料來源，修正缺陷 D1", "已確認"],
    ["R16", "參加活動", "報名名單以活動的 participants 為唯一來源；檢查與已選課程、其他已參加活動的重疊及報名人數", "規範：檢查欲參加活動與已選課程或其他活動是否重疊", "已確認"],
    ["R17", "失敗時資料不變", "check 系列函式不修改資料；enroll／join 只在全部通過時寫入", "沿用 F1 的約定", "已確認"],
    ["R18", "課表格子", "每一格保存項目清單，同一格有多個項目時全部保留並可列出衝突", "避免後放入的課程覆蓋前一門（缺陷 D2）", "已確認"],
    ["R19", "空閒時段", "只在同一天內連續計算，跨日查詢時每天各自成為獨立區段；查詢範圍含頭尾", "對應第 5 週需求規格「跨日空閒不自動合併」", "已確認"],
    ["R20", "空堂數", "同一天第一節課與最後一節課之間沒有課的節數；活動不計入上課節數", "規範未定義空堂數，採最常見的解讀", "已確認"],
    ["R21", "活動時間表示", "活動以 TimeSlot（星期＋節次）表示，與課程共用同一套衝突檢查", "規範 F4：教室配置須與課程共用同一套時段衝突檢查機制", "已確認"],
]

F4_REQ = [
    ["項目", "內容"],
    ["輸入資料", "活動代號、名稱、日期、開始與結束時間、預計人數、活動類型、場地需求（規範 F4）。"],
    ["時間轉換（建議）", "日期換算為星期；開始與結束時間對照節次時間表換算為節次，例如 10:10～12:00 為第 3、4 節。節次時間表需由團隊確認。"],
    ["功能規則（規範）", "活動新增、取消、修改、查詢；依教室容量、可用時段及設備需求篩選場地；同一教室同時段不得重複配置；"
                       "報名人數不得超過活動或教室容量；無合適教室時顯示未滿足的條件；與課程共用時段衝突檢查。"],
    ["沿用的函式", "add_activity、activities_of_student、room_conflicts、check_activity_join、join_activity（本週已完成）。"],
    ["預計新增的函式", "update_activity(catalog, activity_id, **changes) → 錯誤清單\n"
                     "cancel_activity(catalog, activity_id) → 被取消報名的學號清單\n"
                     "find_activities(catalog, …) → 依類型、星期、教室查詢\n"
                     "find_available_rooms(catalog, time_slots, participants, equipment) → (可用教室清單, 未滿足條件清單)\n"
                     "assign_room(catalog, activity_id, room_id) → 錯誤清單"],
    ["驗收條件（規範）", "至少模擬 10 項活動，包含多人報名、活動取消、教室額滿及場地衝突等情況。"],
    ["負責", "D（F4 主責），C 協助衝突檢查；第 8 週實作。"],
]

CHANGES = [
    ["日期", "項目", "修改前（第 6 週）", "修改後（第 7 週）", "原因"],
    ["2026/10/24", "活動資料模型", "日期、開始與結束時間（字串）", "time_slots、classroom、participants", "與課程共用同一套時段衝突檢查（R21）"],
    ["2026/10/24", "節次定義", "models 與 timetable 各定義一次", "統一由 models.PERIOD_ORDER 定義", "缺陷 D7"],
    ["2026/10/24", "SchoolCatalog", "課程、學生、教室", "另加入 activities，JSON 存取包含活動", "F2／F3 需要活動資料；缺陷 D4"],
    ["2026/10/24", "選課檢查", "validation.evaluate_enrollment", "改為 enrollment.check_enrollment，舊函式移除", "缺陷 D1：額滿判斷錯誤"],
    ["2026/10/24", "課表矩陣", "格子存字串，衝突時覆蓋；星期 0 寫到星期日", "格子存清單；不合法星期或覆蓋時丟出 ValueError", "缺陷 D2、D3"],
    ["2026/10/24", "範例資料", "活動 0 項", "加入 4 項活動（A001～A004）", "F2 活動衝突與 F3 課表顯示活動"],
    ["2026/10/24", "主程式", "v1：只示範 F1", "v2：加入 F2 選課檢查與 F3 課表示範", "第 7 週可執行 v2"],
]

ACCEPTANCE = [
    ["驗收條件", "對應測試", "結果"],
    ["F2：一次列出所有衝突，依星期及節次排序", "test_all_conflicts_listed_and_sorted_by_day_and_period", "通過"],
    ["F2：不得因某項條件通過就忽略其他限制", "test_all_conflicts_listed_and_sorted_by_day_and_period（衝突與學分、額滿同時列出）", "通過"],
    ["F2：學生衝堂、活動衝突、教室衝堂", "test_student_time_conflict、test_activity_conflict、test_room_conflict", "通過"],
    ["F2：學分限制與人數限制", "test_credit_limit_exceeded、test_last_seat_can_be_taken", "通過"],
    ["F3：星期一至星期日 × 12 節的課表矩陣", "test_timetable_is_7_by_12", "通過"],
    ["F3：連續三節空堂", "test_three_consecutive_free_periods", "通過"],
    ["F3：跨日查詢", "test_cross_day_query_does_not_merge_days", "通過"],
    ["F3：同一天多門課程", "test_query_by_day_lists_multiple_courses_in_order", "通過"],
    ["F3：同一課程每週多次上課，所有時段正確顯示", "test_course_with_multiple_weekly_slots_shown_everywhere", "通過"],
]

TESTS_F2 = [
    ["測試編號", "類型", "測試情境", "預期結果"],
    ["TC-F2-01", "正常", "S001 加選與已選課程不重疊的 CS101", "成功；目前學分 4、加選後 7"],
    ["TC-F2-02", "正常", "只檢查不加選", "資料不變"],
    ["TC-F2-03", "邊界", "加選後學分剛好等於上限", "成功"],
    ["TC-F2-04", "邊界", "人數上限 2、已有 1 人，再加選 1 人", "成功；第 3 人加選時「課程已額滿（2/2）」"],
    ["TC-F2-05", "邊界", "相鄰節次（第 4 節與第 5 節）", "不算衝突"],
    ["TC-F2-06", "邊界", "學生已選 2 門其他課，加選人數上限 2 且無人選的課", "成功（缺陷 D1 回歸測試）"],
    ["TC-F2-07", "衝突", "與已選課程同為星期二第 4 節", "「星期二第 4 節｜已選課程：MA101」"],
    ["TC-F2-08", "衝突", "與已參加活動同時段", "列出「已參加活動」衝突"],
    ["TC-F2-09", "衝突", "課程教室同時段已被其他課程使用", "列出「教室衝堂」"],
    ["TC-F2-10", "衝突", "同時有教室、已選課程、活動、學分、額滿 5 種問題", "3 筆衝突依星期排序，並列出學分與額滿"],
    ["TC-F2-11", "錯誤", "學生或課程不存在、重複加選、退選未選修的課", "回傳對應錯誤訊息"],
    ["TC-F2-12", "錯誤", "參加與已選課程、其他活動重疊的活動", "兩筆衝突，報名名單不變"],
]
TESTS_F3 = [
    ["測試編號", "類型", "測試情境", "預期結果"],
    ["TC-F3-01", "正常", "產生 S001 的課表", "7 列 × 12 欄"],
    ["TC-F3-02", "正常", "CS101 一週上星期一、星期三", "所有對應時段都顯示 CS101"],
    ["TC-F3-03", "正常", "查詢星期一所有項目", "依節次列出 CS101、MA101"],
    ["TC-F3-04", "正常", "統計", "星期一 4 節、總學分 9、空堂 3"],
    ["TC-F3-05", "邊界", "星期一連續 3 節以上空閒", "第 3～5 節、第 8～c 節"],
    ["TC-F3-06", "邊界", "星期一第 8 節～星期二第 3 節", "兩段，不跨日合併"],
    ["TC-F3-07", "邊界", "星期日第 c 節", "可放入與查詢"],
    ["TC-F3-08", "邊界", "課程與活動同一格", "兩者都保留，列為 1 個衝突"],
    ["TC-F3-09", "錯誤", "星期 0、8、節次 d、範圍顛倒", "ValueError"],
    ["TC-F3-10", "錯誤", "星期 0、同一格覆蓋、查詢超出第 c 節、星期 1.0", "ValueError（缺陷 D2、D3 與 Code Review 第 4 項）"],
]

FEATURES = [
    ["功能", "狀態", "說明"],
    ["F1 課程與學生資料管理", "測試通過", "加入活動資料；Code Review 7 項問題尚待 B 修正"],
    ["F2 多層次衝堂與選課檢查", "測試通過", "25 項測試通過；含學生、活動、教室衝堂與學分、額滿"],
    ["F3 個人課表與空閒時段", "測試通過", "20 項測試通過；7×12 課表、空閒時段、統計"],
    ["F4 校園活動與教室配置", "開發中", "完成需求分析與介面設計（2.3.2），第 8 週實作"],
    ["F5 多條件課程篩選", "未開始", "第 8 週開發"],
    ["F6 資料儲存與系統測試", "開發中", "JSON 存取含活動；自動化測試 94 項；CSV 尚未實作"],
    ["F7 最佳課表搜尋", "未開始", "第 10 週開發"],
    ["F8 搜尋演算法比較", "未開始", "第 11 週開發"],
    ["F9 校園移動路徑規劃", "未開始", "第 12 週開發"],
    ["F10 動態事件與重新規劃", "未開始", "第 14 週開發"],
    ["F11 AI 輔助測試與品質改善", "未開始", "第 15 週開發"],
]

DEFECTS = [
    ["編號", "問題", "影響", "狀態", "處理方式／負責"],
    ["D1", "evaluate_enrollment 以學生已選課數判斷課程額滿", "F2", "已處理", "改用 check_enrollment 以選修人數判斷，加入回歸測試；C"],
    ["D2", "課表收到星期 0 時寫到星期日；同一格兩門課時覆蓋", "F3", "已處理", "檢查星期並在衝突時回報，格子改存清單；D"],
    ["D3", "find_available_slots 超出第 c 節時靜默截斷", "F3", "已處理", "超出範圍時丟出 ValueError；D"],
    ["D4", "save_catalog 不保留活動資料", "F4／F6", "已處理", "JSON 存取加入 activities，加入回歸測試；A"],
    ["D5", "新增課程不檢查教室是否存在、不比較人數與教室容量", "F2／F4", "部分處理", "教室時段衝突已於加選時檢查（R13）；存在與容量待 F4；C、D"],
    ["D6", "舊角色草稿欄位與共用資料模型不一致", "全組", "已處理", "統一以 models.py 為準；A"],
    ["D7", "節次定義重複", "共用", "已處理", "統一由 models.PERIOD_ORDER 定義；A"],
    ["D8", "範例資料中任兩門課程的時段都不重疊，無法以範例資料示範學生衝堂", "F2", "未處理", "加入幾門時段重疊的課程；主程式暫以示範用課程呈現；E"],
    ["D9", "星期 1.0 通過 F1 驗證後，F3 產生課表時出現 TypeError", "F1／F3", "部分處理", "F3 已改為回報「星期不合法」；F1 驗證仍待修正（Code Review 第 4 項）；B"],
]

REVIEW_INFO = [
    ["被檢視程式", "data_manager.py、validation.py（F1 資料管理，第 6 週 Code Review 追蹤）"],
    ["原開發者", "成員 B"],
    ["檢視者／日期", "成員 A｜2026/10/24"],
    ["檢視方式", "以第 6 週相同的檢查腳本，對目前程式重新執行 7 項問題的重現步驟，記錄實際輸出。"],
    ["結論", "7 項問題目前都仍可重現，尚未修正。其中第 4 項（星期 1.0）已影響本週 F3，F3 先自行擋下（缺陷 D9）。"],
]
REVIEW_ISSUES = [
    ["#", "問題", "本週重新執行結果", "狀態"],
    ["1", "JSON 中某個清單為 null 時載入中止", "catalog_from_dict({\"courses\": null}) 丟出 TypeError", "未修正"],
    ["2", "載入時不檢查人數上限", "PE101（上限 2）有 3 人選修仍可載入，剩餘名額 -1", "未修正"],
    ["3", "新增學生不檢查學分上限", "學分上限 1 的學生可選 3 學分課程", "未修正"],
    ["4", "星期 1.0 通過驗證", "validate_course 回傳 []；F3 產生課表時原本會 TypeError", "未修正"],
    ["5", "remaining_seats 查不存在課程丟 KeyError", "丟出 KeyError", "未修正"],
    ["6", "delete_course 無法分辨失敗原因", "刪除不存在與有人選修的課都回傳 False", "未修正"],
    ["7", "修改課程後共用 time_slots 清單", "新舊物件的 time_slots 為同一個清單", "未修正"],
]

MEETING = [
    ["日期／地點", "2026/10/20（二）18:00｜科研大樓一樓"],
    ["出席", "A、B、C、D、E（全員出席）"],
    ["討論事項", "1. 第 7 週 F2 選課檢查與 F3 個人課表的範圍與驗收條件。\n"
                "2. 活動時間改用星期＋節次表示，與課程共用衝突檢查。\n"
                "3. F2／F3 細部規則 R12～R21。\n"
                "4. 第 6 週 Code Review 7 項問題的修正進度，以及範例資料缺少時段重疊課程的問題。\n"
                "5. F4 活動與教室配置的需求與介面。"],
    ["工作分配", "A：主程式 v2 整合、活動資料存取、缺陷 D4、D7、Code Review 追蹤。\n"
                "B：修正 Code Review 7 項問題。\n"
                "C：F2 選課檢查與測試。\n"
                "D：F3 個人課表與測試、F4 需求分析與介面設計。\n"
                "E：範例活動資料，補充時段重疊的課程。"],
    ["決議", "1. F2／F3 細部規格 R12～R21 全部確認採用。\n2. 活動時間統一以星期＋節次表示。\n"
            "3. F2、F3 共用 SchoolCatalog，不另建資料。\n4. 第 8 週前完成 Code Review 問題修正。"],
    ["下週目標", "第 8 週：F4 活動與教室配置、F5 多條件課程篩選、F6 CSV／JSON 儲存；期中系統 v1.0、30 個以上自動化測試、影片 I。"],
]


def week_commits() -> list[list[str]]:
    out = subprocess.run(
        ["git", "-c", "core.quotepath=false", "log", f"--since={WEEK_SINCE}", "--format=%h|%ad|%an|%s", "--date=format:%Y/%m/%d"],
        cwd=ROOT, capture_output=True, encoding="utf-8",
    ).stdout.strip()
    rows = [["Commit", "日期", "負責成員", "內容"]]
    for line in out.splitlines():
        sha, date, author, subject = line.split("|", 3)
        rows.append([sha, date, AUTHORS.get(author, author), subject])
    if len(rows) == 1:
        rows.append(["（尚無）", "", "", "本週程式尚未提交"])
    return rows


# ---------- 內容 ----------

def cover() -> list:
    story = [Spacer(1, 70), P("校園選課與課表規劃系統", "cover_title"), Spacer(1, 26),
             P("系統需求設計規格書 V 2.0", "cover_sub"), Spacer(1, 10),
             P("Software Requirements Specification (SRS)", "cover_en"),
             P("Software Design Document (SDD)", "cover_en"), Spacer(1, 30),
             P("第 7 週 Iteration 2：F2 多層次衝堂與選課檢查、F3 個人課表與空閒時段", "cover_member"), Spacer(1, 140)]
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
        P("本系統提供學生與教務人員一套校園選課與課表規劃工具。本文件為 V2.0，描述第 7 週（Iteration 2）"
          "在 F1 資料管理之上完成的 F2 多層次衝堂與選課檢查、F3 個人課表與空閒時段查詢，以及 F4 活動與教室配置的需求分析與介面設計。"
          "F1 的需求與設計見 V1.0（第 6 週）。"),
        P("1.2 系統名稱 (Identification)", "h2"),
        P("校園選課與課表規劃系統（Campus Course Registration and Timetable Planning System），程式套件名稱為 campus_planner，本週版本為 v2。"),
        P("1.3 概觀 (Overview)", "h2"),
        P("v2 讓學生加選課程時，一次檢查學生衝堂、活動衝突、教室衝堂、學分上限與人數上限，所有衝突依星期、節次排序列出；"
          "並能把已選課程與參加的活動轉成星期一至星期日 × 12 節的個人課表，查詢指定範圍內的連續空閒時段，統計每日上課節數、總學分與空堂數。"),
        P("F2 與 F3 共用 F1 的 SchoolCatalog，不另建一套資料。活動改以與課程相同的星期＋節次表示，"
          "讓第 8 週的 F4 教室配置可以沿用同一套時段衝突檢查。"),
        PageBreak(),
    ]


def section_system() -> list:
    uc_add = [
        "Use Case ID：UC-F2-01　名稱：加選課程（Enroll Course）",
        "主要參與者：學生　前置條件：學生與課程資料已載入",
        "後置條件：成功時課程加入學生的已選課程；失敗時資料不變",
    ]
    flow_add = [
        "1. 學生提供學號與欲加選的課程代號。",
        "2. 系統檢查學生與課程是否存在、是否已選修。",
        "3. 系統找出與已選課程、已參加活動重疊的時段，以及課程教室同時段被占用的情況。",
        "4. 系統計算加選後學分與目前選修人數。",
        "5. 全部通過時加選，並顯示目前學分、加選後學分與學分上限。",
    ]
    alt_add = [
        "- 3a. 有任何時段衝突：全部列出，依星期、節次排序，同一門課同一天的連續節次合併。",
        "- 4a. 加選後學分超過上限：列出「加選後學分 X 超過上限 Y」。",
        "- 4b. 選修人數已達上限：列出「課程已額滿（n/n）」。",
        "- 以上情況同時發生時全部列出，不因某項通過而忽略其他限制；加選失敗。",
    ]
    uc_tt = [
        "Use Case ID：UC-F3-01　名稱：查詢個人課表與空閒時段（View Timetable）",
        "主要流程：學生提供學號 → 系統產生 7×12 課表（課程與活動）→ 學生可依星期、節次或課程代號查詢，"
        "並指定時間範圍與最少連續節數查詢空閒時段 → 系統顯示每日上課節數、總學分與空堂數。",
        "例外流程：星期不在 1～7、節次不合法或查詢範圍開始晚於結束時，回報錯誤。",
    ]
    return [
        P("2 系統 (System)", "h1"),
        P("2.1 系統描述 (System Description)", "h2"),
        P("v2 在第 6 週的分層架構上新增 F2 選課檢查模組（enrollment.py）與 F3 個人課表模組（timetable.py），"
          "兩者都以 F1 的 SchoolCatalog 為輸入；SchoolCatalog 本週加入活動資料。主程式 main.py 升級為 v2，示範 F1、F2、F3。"),
        P("2.1.1 使用案例模型 (Use Case Model)", "h3"),
        P("本週 F2、F3 之 Use Case Diagram 如圖一所示。"),
        use_case_diagram(),
        P("圖一、系統使用案例圖（F2／F3）", "caption"),
        P("F2 Use Case 描述：加選課程", "h4"),
        *items(uc_add),
        P("主要成功流程（Main Success Scenario）", "label"), *items(flow_add),
        P("替代流程（Alternative／Exception Flow）", "label"), *items(alt_add),
        P("輸出範例（main.py 實際執行）", "label"),
        code_block("學生：S001\n欲加選：CS120 演算法（示範用）\n選課結果：失敗\n"
                   "衝突 1：星期一第 3、4 節｜已選課程：CS101 計算機程式設計\n"
                   "衝突 2：星期三第 b 節｜教室衝堂：CS108 人工智慧導論\n"
                   "衝突 3：星期四第 5 節｜已參加活動：A001 程式設計讀書會\n"
                   "目前學分：9\n加選後學分：12\n學分上限：22"),
        P("F3 Use Case 描述：查詢個人課表與空閒時段", "h4"),
        *items(uc_tt),
        P("2.1.2 系統架構圖 (System Architecture Diagram)", "h3"),
        P("v2 之系統架構如圖二所示，實線為已完成的模組，虛線為後續週次加入的模組。"),
        architecture_diagram(),
        P("圖二、系統架構圖（v2）", "caption"),
        P("2.2 系統資料 (System Data)", "h2"),
        P("2.2.1 資料格式 (Data Format)", "h3"),
        P("課程、學生、教室格式與 V1.0 相同。本週新增活動（Activity），時間與課程一樣以 time_slots（星期＋節次）表示；"
          "範例資料加入 4 項活動，共 20 門課程、15 名學生、5 間教室、4 項活動。"),
        P("活動（Activity）", "label"), table(ACTIVITY_FMT, [26, 16, 58]), Spacer(1, 6),
        P("Example", "label"), table(ACTIVITY_EX, [12, 22, 13, 10, 11, 12, 20]),
        P("2.3 需求規格 (Requirements)", "h2"),
        P("2.3.1 F2／F3 細部規格 (Detailed Rules)", "h3"),
        P("老師規範中未明訂的細部規則，第 7 週實作時採下列做法，編號接續 V1.0 的 R1～R11；R12～R21 已於 10/20 團隊會議確認。"),
        table(RULES, [8, 15, 41, 26, 10]), Spacer(1, 6),
        P("2.3.2 F4 需求分析與介面設計 (F4 Analysis)", "h3"),
        P("依時程，第 7 週開始 F4 的需求分析與介面設計，第 8 週實作。"),
        table(F4_REQ, [20, 80]), Spacer(1, 6),
        P("2.3.3 需求／設計修改紀錄 (Change Log)", "h3"),
        table(CHANGES, [14, 16, 24, 26, 20]),
        PageBreak(),
    ]


def section_design() -> list:
    iface_f2 = [["項目", "說明"],
                ["函式名稱", "check_enrollment()（campus_planner/enrollment.py）"],
                ["功能描述", "檢查學生能否加選課程，一次回傳所有衝突與錯誤"],
                ["輸入（Input）", "catalog（SchoolCatalog）、學號 student_id、課程代號 course_id"],
                ["輸出（Output）", "CheckResult：conflicts（時段衝突，已排序）、errors（學分、額滿等）、目前學分、加選後學分、學分上限；ok 表示全部通過"],
                ["處理規則", "已選課程與已參加活動的時段重疊、課程教室同時段被占用、學分上限、人數上限，全部檢查（R12～R16）"],
                ["後置條件", "不修改任何資料；實際加選使用 enroll_course()"]]
    iface_f3 = [["項目", "說明"],
                ["函式名稱", "find_free_blocks()（campus_planner/timetable.py）"],
                ["功能描述", "查詢指定範圍內的連續空閒時段"],
                ["輸入（Input）", "課表 table、開始時段 start、結束時段 end（TimeSlot，可跨日）、最少連續節數 min_length"],
                ["輸出（Output）", "list[FreeBlock]：每段的星期、開始節次、結束節次、節數"],
                ["處理規則", "每天各自計算，跨日不合併（R19）；星期、節次不合法或開始晚於結束時丟出 ValueError"]]
    others = [["函式", "輸入 → 輸出", "說明"],
              ["enroll_course／drop_course", "學號、課程代號 → CheckResult／錯誤清單", "通過才加選；退選未選修的課回報錯誤"],
              ["check_activity_join／join_activity", "學號、活動代號 → CheckResult", "與已選課程、其他活動重疊及報名人數"],
              ["room_conflicts", "教室、時段 → 衝突清單", "課程與活動共用；F4 教室配置沿用"],
              ["format_check_result", "CheckResult → 文字", "依作業 F2 範例格式輸出"],
              ["build_student_timetable", "學號 → 7×12 課表", "格子為項目清單（課程、活動）"],
              ["entries_at／entries_on_day／slots_of", "星期、節次或代號 → 項目或時段", "依星期、節次、課程代號查詢"],
              ["timetable_stats", "學號 → 統計", "每日上課節數、總學分、空堂數、衝突數"],
              ["render_timetable", "課表 → 文字表格", "主程式顯示課表"]]
    return [
        P("3. 軟體設計 (Software Design)", "h1"),
        P("3.1 函式功能介面 (Functionality Interface)", "h2"),
        P("F2：check_enrollment()", "h4"), table(iface_f2, [22, 78]), Spacer(1, 6),
        P("Function:", "label"),
        code_block('''def check_enrollment(catalog: SchoolCatalog, student_id: str, course_id: str) -> CheckResult:
    """檢查學生能否加選課程，回傳所有衝突與錯誤；不修改資料。"""'''),
        P("使用範例", "label"),
        code_block('''result = check_enrollment(catalog, "S001", "CS120")
print(result.ok)                          # False
for conflict in result.conflicts:
    print(conflict.describe())            # 星期一第 3、4 節｜已選課程：CS101 計算機程式設計 …
print(format_check_result(result))        # 依作業範例格式輸出'''),
        P("F3：find_free_blocks()", "h4"), table(iface_f3, [22, 78]), Spacer(1, 6),
        P("使用範例", "label"),
        code_block('''table = build_student_timetable(catalog, "S001")
for block in find_free_blocks(table, TimeSlot(1, "1"), TimeSlot(2, "9"), min_length=3):
    print(block.describe())               # 星期一第 5～c 節（連續 8 節）…'''),
        P("其他 F2／F3 函式：", "label"),
        table(others, [32, 34, 34]),
        P("3.2 測試案例設計 (Test case design)", "h2"),
        P("本週新增 F2 測試 25 項（正常 6、邊界 5、錯誤與衝突 14）與 F3 測試 20 項（正常 6、邊界 5、錯誤 9），"
          "全部自動化測試共 94 項。"),
        P("F2 測試案例（節錄）", "label"), table(TESTS_F2, [14, 9, 45, 32]), Spacer(1, 6),
        P("F3 測試案例（節錄）", "label"), table(TESTS_F3, [14, 9, 45, 32]), Spacer(1, 6),
        P("F2／F3 驗收條件對照：", "label"), table(ACCEPTANCE, [34, 52, 14]), Spacer(1, 6),
        code_block('''def test_all_conflicts_listed_and_sorted_by_day_and_period(catalog) -> None:
    add_course(catalog, course("CS120", [(4, "5"), (2, "4"), (2, "3"), (1, "3")],
                               credits=21, capacity=1, room="A101"))
    add_student(catalog, Student("S002", "李小華", "資工系", ["CS120"], 24))
    result = check_enrollment(catalog, "S001", "CS120")
    assert [c.describe() for c in result.conflicts] == [
        "星期一第 3 節｜教室衝堂：CS101 課程CS101",
        "星期二第 3、4 節｜已選課程：MA101 課程MA101",
        "星期四第 5 節｜已參加活動：A001 程式設計讀書會",
    ]
    assert result.errors == ["加選後學分 25 超過上限 24", "課程已額滿（1/1）"]'''),
        P("3.3 專案審查 (Iteration Review 2)", "h2"),
        P("本次 Iteration 完成哪些工作？（Completed Work）", "label"),
        *items([
            "1. 完成 F2：學生衝堂、活動衝突、教室衝堂、學分與人數限制一次檢查，衝突依星期、節次排序；加選、退選、參加活動。",
            "2. 完成 F3：7×12 個人課表（含活動）、依星期／節次／課程代號查詢、連續空閒時段、每日節數與空堂統計。",
            "3. 修正缺陷 D1、D2、D3、D4、D7，各自加入回歸測試。",
            "4. 活動改用星期＋節次表示，範例資料加入 4 項活動，主程式升級為 v2。",
            "5. 自動化測試 94 項全部通過（F2 25 項、F3 20 項）。",
            "6. 完成 F4 需求分析與介面設計，並追蹤第 6 週 Code Review 問題。",
        ]),
        P("哪些工作尚未完成？（Incomplete Work）", "label"),
        *items([
            "1. 第 6 週 Code Review 的 7 項問題仍可重現，尚未修正。",
            "2. 範例資料缺少時段重疊的課程（缺陷 D8），學生衝堂只能以示範用課程呈現。",
            "3. F4 實作與 CSV 存取尚未進行（第 8 週）。",
        ]),
        P("本次 Iteration 遇到哪些問題？（Problems）", "label"),
        *items([
            "1. 原本的活動資料以日期與時:分表示，無法和課程共用時段衝突檢查，因此改為星期＋節次。",
            "2. 以範例資料窮舉所有學生與課程的組合時，找不到任何時段衝突；確認後是資料中沒有重疊的課程，而不是程式錯誤。",
            "3. F1 驗證允許星期 1.0，造成 F3 產生課表時出錯；F3 先自行檢查，F1 仍待修正。",
            "4. 加選成功後「目前學分」與「加選後學分」顯示相同數字，由執行主程式發現並修正。",
        ]),
        P("下一次 Iteration 如何改善？（Improvements）", "label"),
        *items([
            "1. 第 8 週前完成 Code Review 問題修正，因 F4、F5、F6 都依賴資料載入。",
            "2. 範例資料加入時段重疊與額滿的課程，讓驗收情境可直接用範例資料呈現。",
            "3. F4 沿用 room_conflicts 與 TimeSlot，不另寫一套衝突檢查。",
            "4. 每次提交前執行 python -m pytest -q，並持續累積期中所需的 30 個以上測試。",
        ]),
        PageBreak(),
    ]


def section_pm() -> list:
    def task(no, title, desc, days, owner):
        return P(esc(f"{no} {title}：{desc}預估工作量：{days} 人天。負責人：{owner}。"), "item")
    member_rows = [["組員", "擔任角色", "主要負責工作", "協作／檢視工作"],
                   ["A", "組長／整合", "主程式 v2、活動資料存取、缺陷 D4、D7", "Code Review 追蹤 B、Iteration Review"],
                   ["B", "資料管理", "修正第 6 週 Code Review 問題", "檢視 C 的 F2 程式"],
                   ["C", "選課限制", "F2 選課檢查與測試", "檢視 D 的 F3 程式"],
                   ["D", "課表活動", "F3 個人課表與測試、F4 需求分析", "檢視 E 的範例資料"],
                   ["E（副組長）", "搜尋效能", "範例活動資料、補充重疊課程", "檢視 A 的主程式 v2"]]
    return [
        P("4. 專案管理 (Project Management)", "h1"),
        P("4.1 工作分解表 (Work Breakdown Structure)", "h2"),
        P("2. 選課檢查與個人課表", "label"),
        P("2.1 需求分析", "label"),
        task("2.1.1", "F2／F3 細部規格", "整理衝突排序、教室衝堂、學分上限、額滿、空閒時段與空堂數的判斷規則（R12～R21）。", 1, "C、D"),
        task("2.1.2", "F4 需求分析", "整理活動與教室配置的輸入、規則、時間轉換方式與驗收條件。", 1, "D"),
        P("2.2 功能設計", "label"),
        task("2.2.1", "活動資料格式", "活動時間改為星期＋節次，加入使用教室與報名名單。", 1, "A、D"),
        task("2.2.2", "函式介面", "定義 F2、F3 函式的輸入、輸出與錯誤處理，以及 F4 預計新增的函式。", 1, "C、D"),
        P("2.3 功能實作", "label"),
        task("2.3.1", "F2 選課檢查", "實作衝堂、活動衝突、教室衝堂、學分與額滿檢查，以及加選、退選、參加活動。", 2, "C"),
        task("2.3.2", "F3 個人課表", "實作 7×12 課表、查詢、空閒時段與統計。", 2, "D"),
        task("2.3.3", "缺陷修正", "修正 D1、D2、D3、D4、D7。", 1, "A、C、D"),
        task("2.3.4", "範例活動資料", "建立 4 項活動並確認與報名學生的課程不衝突。", 1, "E"),
        task("2.3.5", "主程式 v2", "main.py 加入 F2 選課檢查與 F3 課表示範。", 1, "A"),
        P("2.4 功能測試", "label"),
        task("2.4.1", "單元測試", "F2 25 項、F3 20 項，含 F2、F3 驗收條件與缺陷回歸測試。", 2, "C、D"),
        task("2.4.2", "Code Review", "追蹤第 6 週問題，並依順序互相檢視本週程式。", 1, "全員"),
        task("2.4.3", "Iteration Review", "彙整完成情況、問題與改善項目，產出 Iteration Review 2。", 1, "A"),
        Spacer(1, 8),
        table(member_rows, [13, 14, 39, 34]),
        Spacer(1, 10),
        KeepTogether([wbs_diagram(), P("圖三、工作分解結構圖（Iteration 2）", "caption")]),
        P("4.2 版本控管 (Version Control)", "h2"),
        P("Git Repository：https://github.com/0mago0/programing_team_project"),
        P("本週主要 Commit 與負責成員：", "label"),
        table(week_commits(), [13, 15, 10, 62]), Spacer(1, 6),
        P("完整 git log：", "label"),
        terminal_block(base.git_log()),
        PageBreak(),
    ]


def section_end() -> list:
    glossary = [["名詞", "說明"],
                ["SchoolCatalog", "保存課程、學生、教室、活動的容器，F1～F3 都以它作為參數。"],
                ["TimeSlot", "一個時段，由星期（1～7）與節次（1～9、a、b、c）組成；課程與活動共用。"],
                ["CheckResult", "F2 檢查結果，包含時段衝突、其他錯誤與學分資訊；ok 表示全部通過。"],
                ["教室衝堂", "同一教室在同一時段被兩門課程或活動使用。"],
                ["空閒時段", "課表中連續沒有任何課程或活動的節次；每天各自計算。"],
                ["空堂數", "同一天第一節課與最後一節課之間沒有課的節數。"],
                ["回歸測試", "針對已修正的缺陷所寫的測試，確保缺陷不再出現。"]]
    refs = [
        "[1] 1151 計算機程式設計團體作業規範（docs/00_老師作業/assignment.pdf）。",
        "[2] 系統需求設計規格書 V1.0（第 6 週，docs/03_週報/第6週_系統需求設計規格書.pdf）。",
        "[3] Python 3.11 官方文件：dataclasses。https://docs.python.org/3.11/",
        "[4] pytest 官方文件。https://docs.pytest.org/",
    ]
    return [
        P("Glossary", "h1"), table(glossary, [24, 76]), PageBreak(),
        P("References", "h1"), *items(refs), PageBreak(),
        P("Appendix", "h1"),
        P("A. 功能完成表", "label"), table(FEATURES, [26, 14, 60]), Spacer(1, 8),
        P("B. 問題與缺陷紀錄", "label"), table(DEFECTS, [7, 40, 11, 12, 30]), Spacer(1, 8),
        P("C. Code Review 紀錄", "label"),
        table(REVIEW_INFO, [20, 80], header=False), Spacer(1, 6),
        P("第 6 週問題追蹤（本週重新執行）：", "label"),
        table(REVIEW_ISSUES, [6, 34, 46, 14]), Spacer(1, 8),
        P("D. 執行方式", "label"),
        code_block("python main.py          # v2：示範 F1、F2、F3\npython -m pytest -q     # 執行全部自動化測試"),
        P("E. main.py 執行結果", "label"),
        terminal_block("$ python main.py\n" + run(["main.py"])),
        Spacer(1, 6),
        P("F. 自動化測試結果", "label"),
        terminal_block("$ python -m pytest -q\n" + run(["-m", "pytest", "-q", "-p", "no:cacheprovider"])),
        Spacer(1, 8),
        P("G. 團隊會議紀錄與討論照片", "label"),
        table(MEETING, [18, 82], header=False), Spacer(1, 8),
        KeepTogether([Image(str(PHOTO), width=FRAME_W, height=FRAME_W * 1108 / 1477),
                      P("第 7 週團隊討論（2026/10/20，科研大樓一樓）", "caption")]),
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
    doc.title = "系統需求設計規格書 V2.0"
    doc.multiBuild(story)
    print(f"已產生：{OUTPUT}")


if __name__ == "__main__":
    build()
