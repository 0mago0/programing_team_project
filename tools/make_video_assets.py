"""產生影片 I 使用的畫面圖片（1920×1080 PNG）。

用法：python tools/make_video_assets.py
輸出：docs/03_週報/影片I素材/

程式碼畫面取自 git 歷史中的實際版本；終端機畫面在產生時實際執行取得。
I-4 的對話截圖必須使用團隊實際紀錄，本工具不產生。需要 Pillow 與 Windows 字型。
"""
from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "03_週報" / "影片I素材"
W, H = 1920, 1080
FONTS = Path(r"C:\Windows\Fonts")
NAVY, BLUE, LIGHT, GREY, RED, GREEN = "#1F3864", "#2E74B5", "#DCE6F2", "#595959", "#C00000", "#2E7D32"
TERM_BG, TERM_FG = "#1E1E1E", "#E6E6E6"


def font(size: int, bold: bool = False, mono: bool = False) -> ImageFont.FreeTypeFont:
    if mono:
        return ImageFont.truetype(str(FONTS / "consola.ttf"), size)
    return ImageFont.truetype(str(FONTS / ("msjhbd.ttc" if bold else "msjh.ttc")), size)


def is_cjk(ch: str) -> bool:
    return ord(ch) > 0x2E7F


def draw_mixed(d: ImageDraw.ImageDraw, xy: tuple[int, int], text: str, size: int, fill: str) -> int:
    """英數用 Consolas、中文用微軟正黑體，逐字繪製；回傳結束時的 x。"""
    x, y = xy
    mono, cjk = font(size, mono=True), font(size)
    for ch in text:
        f = cjk if is_cjk(ch) else mono
        d.text((x, y + (0 if f is mono else -size * 0.12)), ch, font=f, fill=fill)
        x += d.textlength(ch, font=f)
    return int(x)


def canvas(title: str, tag: str = "") -> tuple[Image.Image, ImageDraw.ImageDraw]:
    img = Image.new("RGB", (W, H), "white")
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W, 120], fill=NAVY)
    d.text((70, 30), title, font=font(54, bold=True), fill="white")
    if tag:
        tw = d.textlength(tag, font=font(34))
        d.text((W - 70 - tw, 42), tag, font=font(34), fill="#BDD7EE")
    d.text((70, H - 55), "第 15 組｜影片 I：F2 多層次衝堂檢查", font=font(26), fill=GREY)
    return img, d


def box(d, xy, text, fill=LIGHT, outline=BLUE, size=34, bold=False, color=NAVY):
    x0, y0, x1, y1 = xy
    d.rounded_rectangle(xy, radius=18, fill=fill, outline=outline, width=4)
    lines = text.split("\n")
    f = font(size, bold=bold)
    total = len(lines) * size * 1.35
    for i, line in enumerate(lines):
        tw = d.textlength(line, font=f)
        d.text(((x0 + x1 - tw) / 2, (y0 + y1 - total) / 2 + i * size * 1.35), line, font=f, fill=color)


def arrow(d, x0, y0, x1, y1, color=BLUE, width=6):
    d.line([x0, y0, x1, y1], fill=color, width=width)
    import math
    a = math.atan2(y1 - y0, x1 - x0)
    p1 = (x1 - 22 * math.cos(a - 0.45), y1 - 22 * math.sin(a - 0.45))
    p2 = (x1 - 22 * math.cos(a + 0.45), y1 - 22 * math.sin(a + 0.45))
    d.polygon([(x1, y1), p1, p2], fill=color)


def terminal(d, xy, lines: list[str], size: int = 30, highlight: dict[str, str] | None = None):
    x0, y0, x1, y1 = xy
    d.rounded_rectangle(xy, radius=14, fill=TERM_BG)
    for cx, c in ((x0 + 30, "#FF5F56"), (x0 + 60, "#FFBD2E"), (x0 + 90, "#27C93F")):
        d.ellipse([cx - 9, y0 + 16, cx + 9, y0 + 34], fill=c)
    y = y0 + 55
    for line in lines:
        color = TERM_FG
        for key, c in (highlight or {}).items():
            if key in line:
                color = c
        draw_mixed(d, (x0 + 30, y), line, size, color)
        y += int(size * 1.45)


def code_card(d, xy, lines: list[str], size: int = 32, marks: dict[int, str] | None = None):
    x0, y0, x1, y1 = xy
    d.rounded_rectangle(xy, radius=14, fill="#F5F5F5", outline="#BFBFBF", width=2)
    y = y0 + 25
    for no, line in enumerate(lines, 1):
        if marks and no in marks:
            d.rectangle([x0 + 4, y - 6, x1 - 4, y + size + 6], fill="#FFE4E1")
        draw_mixed(d, (x0 + 25, y), f"{no:>2}  ", size, "#A0A0A0")
        draw_mixed(d, (x0 + 25 + int(d.textlength('00  ', font=font(size, mono=True))), y), line, size, "#202020")
        y += int(size * 1.5)


def run(args: list[str]) -> str:
    python = ROOT / ".venv" / "Scripts" / "python.exe"
    env = {**os.environ, "PYTHONIOENCODING": "utf-8"}
    out = subprocess.run([str(python) if python.exists() else sys.executable, *args], cwd=ROOT,
                         capture_output=True, encoding="utf-8", env=env)
    return out.stdout + out.stderr


def git_show(rev_path: str) -> list[str]:
    out = subprocess.run(["git", "-c", "core.quotepath=false", "show", rev_path], cwd=ROOT,
                         capture_output=True, encoding="utf-8").stdout
    return out.replace("\r", "").splitlines()


def photo_into(img: Image.Image, path: Path, box_xy: tuple[int, int, int, int]) -> None:
    x0, y0, x1, y1 = box_xy
    p = Image.open(path).convert("RGB")
    scale = min((x1 - x0) / p.width, (y1 - y0) / p.height)
    p = p.resize((int(p.width * scale), int(p.height * scale)))
    img.paste(p, (x0 + (x1 - x0 - p.width) // 2, y0 + (y1 - y0 - p.height) // 2))


# ---------- 各畫面 ----------

def s01_title():
    img = Image.new("RGB", (W, H), NAVY)
    d = ImageDraw.Draw(img)
    photo_into(img, ROOT / "docs" / "05_會議" / "第7週_團隊討論照片.jpg", (1000, 140, 1850, 780))
    d.text((90, 200), "從需求分析到可執行系統", font=font(72, bold=True), fill="white")
    d.text((90, 300), "我們如何與生成式 AI 協作", font=font(72, bold=True), fill="white")
    d.text((90, 450), "主題：F2 多層次衝堂與選課檢查", font=font(44), fill="#BDD7EE")
    d.text((90, 620), "計算機程式設計團體作業｜第 15 組", font=font(36), fill="white")
    d.text((90, 680), "校園選課與課表規劃系統", font=font(36), fill="white")
    return img


def s02_problem():
    img, d = canvas("I-1 問題情境", "說明：C")
    d.text((90, 170), "學生加選一門課時，可能同時遇到五種問題：", font=font(40, bold=True), fill=NAVY)
    items = [("學生衝堂", "與已選課程同時段"), ("活動衝突", "與參加的活動撞時間"), ("教室衝堂", "教室該時段已被用"),
             ("學分限制", "加選後超過上限"), ("人數限制", "課程已額滿")]
    for i, (a, b) in enumerate(items):
        x = 90 + i * 355
        box(d, (x, 260, x + 320, 430), "", size=30)
        for text, y, f in ((a, 295, font(38, bold=True)), (b, 360, font(30))):
            d.text((x + (320 - d.textlength(text, font=f)) / 2, y), text, font=f, fill=NAVY)
    d.rounded_rectangle((90, 500, 1830, 720), radius=18, fill="#FFF2CC", outline="#BF9000", width=4)
    d.text((130, 530), "作業要求", font=font(38, bold=True), fill="#7F6000")
    d.text((130, 595), "必須檢查所有衝突，不能發現第一項錯誤就停止；", font=font(36), fill="#3F3F3F")
    d.text((130, 650), "一次列出所有衝突，並依星期及節次排序。", font=font(36), fill="#3F3F3F")
    d.text((90, 780), "難處：五種檢查的資料來源不同（已選課程、活動、教室、學分、名額），", font=font(34), fill=GREY)
    d.text((90, 835), "結果卻要合併成一份排好序的清單。", font=font(34), fill=GREY)
    return img


def s03_decompose():
    img, d = canvas("I-2 問題分解", "說明：B")
    box(d, (80, 450, 330, 610), "加選請求\n學號＋課程", fill="#E2EFDA", outline=GREEN, color="#375623")
    checks = ["① 時段是否重疊", "② 學生衝堂", "③ 活動衝突", "④ 教室衝堂", "⑤ 學分與額滿"]
    for i, text in enumerate(checks):
        y = 170 + i * 165
        box(d, (480, y, 860, y + 120), text, size=36)
        arrow(d, 330, 530, 480, y + 60)
        arrow(d, 860, y + 60, 1040, 530)
    box(d, (1040, 440, 1360, 620), "合併\n同一天連續節次\n合併成一筆", size=32)
    arrow(d, 1360, 530, 1460, 530)
    box(d, (1460, 440, 1840, 620), "依星期、節次排序\n一次全部列出", size=32, fill="#FFF2CC", outline="#BF9000", color="#7F6000")
    d.text((1040, 700), "例：星期二第 3、4 節｜已選課程：MA101", font=font(30), fill=GREY)
    d.text((1040, 750), "每個小問題都能單獨寫測試，最後再組合", font=font(30), fill=GREY)
    return img


def s04_draft():
    img, d = canvas("I-3 原始解法：第 5 週草稿", "說明：C")
    lines = git_show("c53c649:C_選課規則.py")
    start = next(i for i, l in enumerate(lines) if l.startswith("def check_time_conflict"))
    code = lines[start:start + 3]
    code_card(d, (90, 180, 1830, 340), code, size=34, marks={3: "x"})
    d.text((90, 360), "commit c53c649（C_選課規則.py）", font=font(28), fill=GREY)
    d.rounded_rectangle((90, 440, 1830, 760), radius=18, fill="#FDE9E7", outline=RED, width=4)
    d.text((130, 470), "問題", font=font(40, bold=True), fill=RED)
    d.text((130, 540), "只要兩門課「都有時段」就回傳 True，", font=font(38), fill="#3F3F3F")
    d.text((130, 600), "完全沒有比對是哪一天、哪一節。", font=font(38), fill="#3F3F3F")
    d.text((130, 670), "星期一第 1 節 與 星期五第 9 節 也會被判定為衝堂。", font=font(34), fill=GREY)
    return img


def s05_old_capacity():
    img, d = canvas("I-3 原始解法：第 6 週額滿判斷", "說明：C")
    lines = git_show("3487ed4:campus_planner/validation.py")
    start = next(i for i, l in enumerate(lines) if "len(student.enrolled_courses) >= course.capacity" in l)
    code = lines[start:start + 2]
    code_card(d, (90, 180, 1830, 300), code, size=34, marks={1: "x"})
    d.text((90, 320), "validation.evaluate_enrollment（第 6 週，缺陷 D1）", font=font(28), fill=GREY)
    d.rounded_rectangle((90, 400, 1830, 790), radius=18, fill="#FDE9E7", outline=RED, width=4)
    d.text((130, 430), "問題", font=font(40, bold=True), fill=RED)
    d.text((130, 500), "用「這個學生自己選了幾門課」判斷額滿，", font=font(38), fill="#3F3F3F")
    d.text((130, 560), "而不是「這門課有幾個人選」。", font=font(38), fill="#3F3F3F")
    d.text((130, 640), "例：學生已選 2 門其他課，加選上限 2、沒人選的課 → 被判定「已額滿」", font=font(32), fill=GREY)
    d.text((130, 700), "另外只回傳文字錯誤，沒有衝突的時段資訊。", font=font(32), fill=GREY)
    return img


def s07_reject_data():
    img, d = canvas("I-5 AI 建議的驗證①：不讓資料配合程式", "說明：E")
    box(d, (90, 200, 880, 420), "問題\n主程式示範時，部分查詢查不到資料", size=36)
    box(d, (1040, 200, 1830, 420), "AI 建議\n修改範例資料：系級去掉年級、\n讓某門課額滿", size=34, fill="#FDE9E7", outline=RED, color=RED)
    arrow(d, 880, 310, 1040, 310)
    d.rounded_rectangle((90, 500, 1830, 820), radius=18, fill="#E2EFDA", outline=GREEN, width=4)
    d.text((130, 530), "團隊判斷：不採用", font=font(40, bold=True), fill="#375623")
    d.text((130, 600), "這是讓資料去配合程式；資料應反映真實情況。", font=font(36), fill="#3F3F3F")
    d.text((130, 660), "改由 A 修改主程式的查詢條件（「已額滿的課程」「數學系二年級」），", font=font(34), fill="#3F3F3F")
    d.text((130, 715), "用原本的資料就能查到 PE101 與 S004、S009、S014。", font=font(34), fill="#3F3F3F")
    d.text((90, 860), "來源：成員 E 第 6 週個人紀錄（AI 協作紀錄）", font=font(28), fill=GREY)
    return img


def s08_credit_display():
    img, d = canvas("I-5 AI 建議的驗證②：加選後的學分顯示", "說明：A")
    d.text((90, 170), "AI 產生的 enroll_course，加選成功後把「目前學分」改成加選後的數字", font=font(36), fill="#3F3F3F")
    terminal(d, (90, 250, 930, 640), ["修正前（執行主程式時看到）", "選課結果：成功", "目前學分：3", "加選後學分：3", "學分上限：22"],
             highlight={"目前學分": "#FF7B72", "加選後學分": "#FF7B72"})
    terminal(d, (990, 250, 1830, 640), ["修正後", "選課結果：成功", "目前學分：0", "加選後學分：3", "學分上限：22"],
             highlight={"目前學分": "#7EE787", "加選後學分": "#7EE787"})
    d.text((90, 690), "發現方式：實際執行 main.py，看到兩行數字一模一樣", font=font(34), fill=NAVY)
    d.text((90, 750), "處理：保留加選前學分，並修改測試 test_enroll_without_conflict_succeeds", font=font(34), fill=NAVY)
    d.text((90, 810), "　　　assert (current, projected, limit) == (4, 7, 24)", font=font(32), fill=GREY)
    return img


def s09_zero_conflicts():
    img, d = canvas("I-5 AI 建議的驗證③：窮舉找不到衝突", "說明：A")
    script = (
        "from collections import Counter\n"
        "from campus_planner.data_manager import load_catalog\n"
        "from campus_planner.enrollment import check_enrollment\n"
        "c, _ = load_catalog('data/sample_school_data.json')\n"
        "pairs = sum(1 for s in c.students for k in c.courses if check_enrollment(c, s, k).conflicts)\n"
        "cnt = Counter(t for x in c.courses.values() for t in x.time_slots)\n"
        "print(f'學生 {len(c.students)} 名 × 課程 {len(c.courses)} 門：有時段衝突的組合 {pairs} 筆')\n"
        "print(f'任兩門課程時段重疊的格數：{sum(1 for v in cnt.values() if v > 1)}')\n"
    )
    out = run(["-c", script]).strip().splitlines()
    terminal(d, (90, 170, 1830, 400), ["$ 窮舉範例資料中每位學生 × 每門課程", *out], size=34,
             highlight={"格數": "#FFD866"})
    d.text((90, 440), "不能直接下結論：", font=font(38, bold=True), fill=RED)
    d.text((90, 500), "「程式沒問題」或「程式壞了」都還沒有證據", font=font(36), fill="#3F3F3F")
    d.text((90, 590), "檢查資料 → 範例資料中任兩門課的時段都不重疊", font=font(36), fill=NAVY)
    d.text((90, 660), "另建一門示範課程 CS120 → 三種衝突都正確列出（見下一頁）", font=font(36), fill=NAVY)
    d.text((90, 750), "後續：列為缺陷 D8，請 E 在範例資料加入時段重疊的課程", font=font(32), fill=GREY)
    return img


def s10_f2_output():
    img, d = canvas("I-6 修改後：一次列出所有衝突", "說明：D")
    out = run(["main.py", "--demo"]).splitlines()
    start = out.index("[多項衝突一次列出]")
    lines = ["$ python main.py --demo"] + out[start:start + 10]
    terminal(d, (90, 160, 1830, 880), lines, size=36,
             highlight={"衝突": "#FFD866", "失敗": "#FF7B72"})
    d.text((90, 905), "依星期排序：星期一 → 星期三 → 星期四；三種衝突（已選課程、教室、活動）同時列出", font=font(30), fill=NAVY)
    return img


def s11_tests():
    img, d = canvas("I-6 自動化測試結果", "說明：D")
    f2 = run(["-m", "pytest", "tests/test_f2_enrollment.py", "-q", "-p", "no:cacheprovider"]).strip().splitlines()[-1]
    allr = run(["-m", "pytest", "-q", "-p", "no:cacheprovider"]).strip().splitlines()[-1]
    terminal(d, (90, 170, 1830, 470), ["$ python -m pytest tests/test_f2_enrollment.py -q", f2,
                                       "$ python -m pytest -q", allr], size=40,
             highlight={"passed": "#7EE787"})
    for i, (name, desc) in enumerate([
        ("test_all_conflicts_listed_and_sorted_by_day_and_period", "F2 驗收：全部列出並依星期、節次排序"),
        ("test_capacity_counts_real_enrollment_not_student_course_count", "缺陷 D1 回歸測試：額滿以實際選修人數判斷"),
        ("test_failed_enrollment_keeps_data", "加選失敗時資料不變"),
    ]):
        y = 530 + i * 120
        draw_mixed(d, (90, y), name, 30, NAVY)
        d.text((90, y + 45), desc, font=font(30), fill=GREY)
    return img


def s12_compare():
    img, d = canvas("I-6 修改前後比較", "說明：D")
    rows = [("", "修改前", "修改後"),
            ("時段比對", "沒有比對星期與節次", "逐一比對，連續節次合併"),
            ("額滿判斷", "看學生自己選幾門課", "看這門課實際選修人數"),
            ("衝突數量", "只回傳文字錯誤", "一次列出所有衝突並排序"),
            ("檢查範圍", "學分、名額", "學生、活動、教室、學分、名額"),
            ("測試", "無", "F2 25 項（含回歸測試）全部通過")]
    widths = [300, 720, 720]
    y = 180
    for r, row in enumerate(rows):
        x = 90
        for c, cell in enumerate(row):
            fill = NAVY if r == 0 else (LIGHT if c == 0 else ("#FDE9E7" if c == 1 else "#E2EFDA"))
            color = "white" if r == 0 else ("#3F3F3F" if c else NAVY)
            d.rectangle([x, y, x + widths[c], y + 120], fill=fill, outline="white", width=4)
            d.text((x + 30, y + 38), cell, font=font(36, bold=(r == 0 or c == 0)), fill=color)
            x += widths[c]
        y += 120
    return img


def s13_team():
    img, d = canvas("I-7 團隊反思", "說明：全員")
    photo_into(img, ROOT / "docs" / "05_會議" / "第8週_團隊討論照片.jpg", (90, 150, 760, 1010))
    for i, (who, text) in enumerate([
        ("AI 有幫助的地方", "快速產生初版程式與測試骨架\n提供測試寫法、找錯誤原因"),
        ("仍要自己判斷的地方", "規格沒寫清楚的規則\n資料是否合理、建議是否正確"),
        ("我們的做法", "先拆問題、先定規則\n每個建議都用測試或執行驗證"),
    ]):
        y = 180 + i * 270
        d.rounded_rectangle((850, y, 1830, y + 230), radius=18, fill=LIGHT, outline=BLUE, width=4)
        d.text((890, y + 25), who, font=font(38, bold=True), fill=NAVY)
        for j, line in enumerate(text.split("\n")):
            d.text((890, y + 95 + j * 55), line, font=font(34), fill="#3F3F3F")
    return img


def s14_end():
    img = Image.new("RGB", (W, H), NAVY)
    d = ImageDraw.Draw(img)
    d.text((120, 200), "謝謝收看", font=font(90, bold=True), fill="white")
    d.text((120, 380), "影片中使用的 Prompt、程式碼版本、測試案例與執行結果", font=font(40), fill="#BDD7EE")
    d.text((120, 445), "都附在繳交資料中，可逐一對照。", font=font(40), fill="#BDD7EE")
    for i, line in enumerate(["程式碼：commit c53c649（第 5 週草稿）、b76260f（F2 enrollment.py）",
                              "測試：tests/test_f2_enrollment.py（25 項）、全部 169 項",
                              "文件：規格書 V2.0、V3.0、第 8 週團隊 AI 協作紀錄"]):
        draw_mixed(d, (120, 600 + i * 70), line, 34, "white")
    d.text((120, 900), "第 15 組｜校園選課與課表規劃系統", font=font(34), fill="white")
    return img


SCENES = [
    ("01_開場_片名.png", s01_title),
    ("02_I-1_問題情境.png", s02_problem),
    ("03_I-2_問題分解.png", s03_decompose),
    ("04_I-3_第5週草稿.png", s04_draft),
    ("05_I-3_舊版額滿判斷.png", s05_old_capacity),
    ("07_I-5_拒絕修改資料.png", s07_reject_data),
    ("08_I-5_學分顯示修正.png", s08_credit_display),
    ("09_I-5_窮舉找不到衝突.png", s09_zero_conflicts),
    ("10_I-6_F2執行結果.png", s10_f2_output),
    ("11_I-6_測試結果.png", s11_tests),
    ("12_I-6_前後比較.png", s12_compare),
    ("13_I-7_團隊反思.png", s13_team),
    ("14_結尾.png", s14_end),
]

if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    for name, make in SCENES:
        make().save(OUT / name)
        print(f"已產生：{name}")
    (OUT / "06_I-4_請放實際對話截圖.txt").write_text(
        "I-4 AI 協作過程：請放團隊實際與 AI 的兩輪對話截圖（只截相關片段）。\n"
        "作業規定影片內容必須能由繳交資料追溯，不可事後重寫 Prompt 代替原始紀錄。\n", encoding="utf-8")
