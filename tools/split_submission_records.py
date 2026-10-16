"""One-time migration of the existing submission into separate required records.

已於 2026-10-09 執行完成，交付包之後也已改為 PDF 結構。保留僅供紀錄；
預設拒絕執行，且任何情況下都不會覆寫已存在的檔案。
"""
from pathlib import Path
import os
import subprocess
import sys
import uuid

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'deliverables' / 'A_第5週繳交包_五人版'
TEAM = OUT / '團隊文件'
PERSON = OUT / 'A個人文件'
SOURCES = [
    OUT / '待補附件' / '會議與Review紀錄.md',
    PERSON / '角色與工作紀錄.md',
    OUT / '整合文件' / '模組介面與整合說明.md',
]
if '--run-migration' not in sys.argv:
    raise SystemExit('此遷移已執行完成，預設停用；請直接編輯 deliverables 內現有文件。')
missing = [str(p.relative_to(ROOT)) for p in SOURCES if not p.exists()]
if missing:
    raise SystemExit('找不到遷移來源，無法執行：' + '、'.join(missing))
if (TEAM / '功能完成表.md').exists():
    raise SystemExit('分檔已完成；請直接編輯現有文件，避免覆蓋紀錄。')

def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with path.open('x', encoding='utf-8') as file:
            file.write(text.strip() + '\n')
    except FileExistsError:
        raise SystemExit(f'拒絕覆寫既有檔案：{path.relative_to(ROOT)}') from None

env = os.environ | {'PYTHONIOENCODING': 'utf-8', 'PYTHONDONTWRITEBYTECODE': '1'}
temp = ROOT / '.test_runs' / ('a_' + uuid.uuid4().hex)
assert temp.resolve().is_relative_to(ROOT.resolve())
temp.parent.mkdir(exist_ok=True)
commands = [
    ('骨架測試', OUT, [sys.executable, '-m', 'pytest', '-q', '-p', 'no:cacheprovider', '--basetemp', str(temp)]),
    ('主程式', OUT, [sys.executable, 'main.py']),
    ('全專案測試限制', ROOT, [sys.executable, '-m', 'pytest', '-q', '-p', 'no:cacheprovider']),
]
results = {}
for label, cwd, command in commands:
    result = subprocess.run(command, cwd=cwd, env=env, capture_output=True, encoding='utf-8')
    results[label] = result
    write(OUT / '驗證結果' / (label + '.txt'),
          '日期：2026-10-09（Asia/Taipei）\n執行者：AI 助理\n工作目錄：' +
          ('交付包根目錄' if cwd == OUT else '原專案根目錄') +
          '\n命令：python ' + ' '.join(command[1:]) + '\n退出碼：' +
          str(result.returncode) + '\n' + result.stdout + result.stderr)
if results['骨架測試'].returncode or results['主程式'].returncode:
    raise SystemExit('骨架驗證未通過，請先檢查驗證結果再重新執行。')

write(TEAM / '可執行程式與執行說明.md', '''# 可執行程式與執行說明

週次：第 5 週 / Iteration 0。整合負責：A 張庭瑄（111590042）。副組長：E。

## 程式交付

實際程式碼位於交付包根目錄的 main.py、campus_planner/；資料為 data/sample_school_data.json，測試為 tests/test_minimal_contract.py。這些檔案可獨立解壓執行，不需其他組員工作資料夾。

```powershell
python -m pip install -r requirements.txt
python main.py
python -m pytest -q -p no:cacheprovider
```

環境：Python 3.10 以上；本次驗證使用 Python 3.11。主程式回傳碼 0，示範 3 門課、3 位學生及 3 間教室的驗證摘要。流程為建立示範資料 → 驗證課程與學生 → 終端機輸出。

## 目前範圍

本版為最小骨架：共同 dataclass、基本驗證、課表矩陣與 JSON 儲存讀取介面。主程式不會自動讀寫 sample_school_data.json；main.py 使用 build_demo_school_data() 產生示範資料。
原專案 F1 測試缺少 data_manager，未收錄至此骨架包；其失敗已另附，未認定為修復。完整 F1～F11 與期中驗收尚未完成。

執行證據：[主程式輸出](../驗證結果/主程式.txt)。
''')

write(TEAM / '功能完成表.md', '''# 功能完成表

版本：第 5 週最小骨架；狀態核對日期：2026-10-09。
四項骨架測試通過不等同完整功能驗收通過。下表為此交付包的實際範圍。

| 功能 | 主責 | 狀態 | 可確認內容與未完成事項 |
| --- | --- | --- | --- |
| F1 資料管理 | B | 開發中 | 已有模型與欄位驗證，CRUD 未整合；原專案缺 data_manager |
| F2 選課檢查 | C | 開發中 | 已有部分衝突與學分檢查；未涵蓋全部限制，額滿判斷有缺陷 |
| F3 課表查詢 | D | 開發中 | 已有 7×12 矩陣與放入課程基線；完整空堂及跨日查詢未驗收 |
| F4 活動與教室 | D | 未開始 | 有 Activity 模型，但完整管理與配置未實作 |
| F5 篩選 | C | 未開始 | 完整多條件篩選未交付 |
| F6 儲存與測試 | A | 開發中 | JSON 往返基線通過；單筆錯誤容忍與 30 項測試未達成 |
| F7 最佳課表 | E | 未開始 | 後續功能 |
| F8 演算法比較 | E | 未開始 | 後續功能 |
| F9 路徑 | D | 未開始 | 後續功能 |
| F10 動態事件 | C | 未開始 | 後續功能 |
| F11 品質改善 | 全員，A 統整 | 未開始 | 尚未完成三核心模組、各兩輪 AI 協作驗收 |
''')

write(TEAM / '需求與設計修改紀錄.md', '''# 需求與設計修改紀錄

整理日期：2026-10-09。依本次對話與工作區變更整理，尚未建立本次 Git Commit。

| 修改 | 原規劃 | 目前規劃 | 原因與影響 |
| --- | --- | --- | --- |
| 團隊人數 | 六人 A～F | 五人 A～E | 使用者告知人數調整；功能 F1～F11 仍保留 |
| F9 責任 | F | D | 使用者採用建議；與課表、場地的移動限制一併規劃 |
| F10 責任 | F | C | 使用者採用建議；與選課及限制重新檢查銜接 |
| 副組長 | 未指定 | E | 使用者明確提供 |
| 工作區目錄 | 最新、舊版及工具混置 | deliverables 為最新包，tools 為產檔工具 | 使用者要求整理並刪除舊版本 |
| 交付文件 | 功能與缺陷、修改與反思、會議與 Review 合併 | 依教師繳交項目逐項分檔 | 方便對照團隊與個人繳交要求 |

本次未修改核心函式或資料結構，未宣稱新功能完成。共用模型仍以 campus_planner/models.py 為準。
B 欄位草稿與共用模型差異、F1 缺模組及 F2 額滿問題列入缺陷，尚未實施介面變更。
10/3 會議討論與決議未提供；上述變更依後續對話確認，不追溯為會議當日決議。
''')

write(TEAM / '自動化測試與結果.md', '''# 自動化測試與結果

日期：2026-10-09；執行者：AI 助理。測試程式：[test_minimal_contract.py](../tests/test_minimal_contract.py)。

| 基線測試 | 驗證內容 | 結果 |
| --- | --- | --- |
| test_valid_course_passes | 合法課程欄位通過驗證 | 通過 |
| test_invalid_course_diagnostics | 空代號、無效學分與節次等回傳錯誤 | 通過 |
| test_student_and_conflict_checks | 合法學生與相同時段衝突判斷 | 通過 |
| test_timetable_generation_and_json_round_trip | 課表定位、7×12 結構、JSON 寫入讀回一致 | 通過 |

包內執行 pytest 結果：4 passed，退出碼 0。測試使用專案內唯一暫存路徑避免系統暫存權限問題；未修改測試斷言。
主程式執行退出碼 0。原專案根目錄執行全部測試時收集失敗，原因為 test_f1_data_management.py 匯入不存在的 campus_planner.data_manager。未將該失敗當成通過或已修復。

原始結果：[骨架測試](../驗證結果/骨架測試.txt)、[主程式](../驗證結果/主程式.txt)、[全專案測試限制](../驗證結果/全專案測試限制.txt)。

## 覆蓋限制

本版四個測試函式，不是 30 個案例。尚未驗收完整 CRUD、活動、路徑、動態事件、單筆錯誤容忍與所有選課限制。第 8 週須達至少 30 案例，正常、邊界、錯誤／衝突各至少 10。此次為既有功能驗證，沒有補造 TDD 歷程。
''')

log = subprocess.run(['git', 'log', '-5', '--format=%H|%ad|%an|%s', '--date=short'], cwd=ROOT, capture_output=True, encoding='utf-8', check=True).stdout
rows = '\n'.join('| ' + ' | '.join(line.split('|', 3)) + ' |' for line in log.splitlines())
write(TEAM / 'Git紀錄.md', '''# 團隊 Git 紀錄

儲存庫：https://github.com/0mago0/programing_team_project.git
本機已有 remote；此次未驗證網頁最新版本、未建立 Commit 或推送。

| Commit SHA | 日期 | 作者顯示名稱 | 功能說明 |
| --- | --- | --- | --- |
''' + rows + '''

以上為本機實際歷史。作者 0mago0 對應成員尚未確認；未提供 Merge 紀錄。本次五人分工、文件整理與刪除舊檔仍是工作區變更，不能列為已提交紀錄。
deliverables 依目前 .gitignore 不納入 Git；繳交 ZIP 與 Git 程式倉庫需分別保存。
''')

write(TEAM / 'CodeReview紀錄.md', '''# 團隊 Code Review 紀錄

目前尚未提供由非原開發學生完成的 Review。下列是 2026-10-09 AI 輔助靜態檢查結果，供實際 Reviewer 核對，不能計入已完成的學生 Review。

| 檢查位置 | 問題與改善建議 | 狀態 |
| --- | --- | --- |
| B_資料管理/B_資料模型.py 與 models.py | course_name/name、max_credits/credit_limit 不一致；B 草稿缺 required、capacity、enrolled_courses。建議統一或明確定義轉換 | AI 提出，B 回應與修正未提供 |
| validation.evaluate_enrollment | 比較學生已選課數與課程容量，無法代表該課實際修課人數。建議使用完整選課紀錄統計 | AI 提出，尚未修正與重測 |
| data_store.load_school_data | 僅解析 JSON object，未逐筆驗證；I/O 錯誤可能向外傳遞。建議定義逐筆錯誤收集與呼叫端處理 | AI 提出，尚未完成 |

## 學生 Review 完成條件

| 功能／版本 | 原開發者 | 非原開發 Reviewer | 日期 | 意見與回應 | 修正與重測 |
| --- | --- | --- | --- | --- | --- |
| A 儲存／整合 | 作者歸屬需確認 | 尚未提供 | 尚未提供 | 尚未提供 | 尚未提供 |
| B 資料模型 | 作者歸屬需確認 | A（規劃，尚未確認完成） | 尚未提供 | 尚未提供 | 尚未提供 |

教師要求至少一項功能由非原開發者檢視。本文件提供現況與具體待處理問題，未宣稱該要求已完成。
''')

write(TEAM / '問題與缺陷紀錄.md', '''# 問題與缺陷紀錄

核對日期：2026-10-09。以下均未認定已修復；責任欄為建議處理分工。

| 編號 | 發現與證據 | 影響 | 處理方式與責任 | 狀態 |
| --- | --- | --- | --- | --- |
| D01 | 全專案 pytest 收集時缺 campus_planner.data_manager | F1 測試無法執行 | B 提供模組、A 整合並重跑全部測試 | 未解決 |
| D02 | 主程式只有 3 課、3 生、3 教室 | 未達第 6 週 20/15/5 資料量 | B 建立驗收資料；A 核對載入流程 | 後續驗收缺口 |
| D03 | load_school_data 未逐筆驗證，JSON 錯誤丟出 ValueError | 未滿足 F6 單筆錯誤容忍 | A 與 B 定義錯誤回報與轉換規則 | 未解決 |
| D04 | B 草稿命名、必選修／容量／選課欄位與共用模型不一致 | 模組銜接可能失敗 | B 核對共用欄位，A 統一介面 | 未解決 |
| D05 | evaluate_enrollment 以學生選課數判斷課程容量 | 可能錯判額滿 | C 與 B 提供實際修課人數資料並測試 | 未解決 |
| D06 | 會議討論決議、學生 Review、本人提交未提供 | 繳交證據不完整 | A 彙整真實資料；10/3 照片與全員出席已補 | 部分完成 |

骨架四项測試通過只能驗證既有覆蓋範圍，不能消除上述缺陷。
''')

write(TEAM / 'IterationReview.md', '''# Iteration Review — 第 5 週 / Iteration 0

整理日期：2026-10-09。依現有檔案與對話摘要整理，供團隊確認。

## 完成什麼

確定五人分工與副組長 E；A 負責整合及 F6，C 接 F10、D 接 F9。整理需求、Use Case、架構、分工與共用模型資料。最小骨架可執行，AI 重跑四項基線測試通過。10/3 會議 A～E 全員出席資訊與照片已納入。繳交文件依教師項目拆分。

## 未完成什麼

完整 F1 CRUD 尚未整合，原專案測試缺 data_manager。F2～F6 尚有未驗收條件，F7～F11 尚未實作。本人 Git 與學生 Review 無完成佐證；10/3 實際討論、決議及下週目標未提供。

## 遇到什麼問題

人數調整造成舊分工過時；不同模型欄位不一致；部分函式只有骨架，容易誤認為已完成全部需求。全專案與交付骨架測試結果需分別記錄。

## 下一 Iteration 如何改善（規劃）

B 統一欄位並補 F1 模組與 20/15/5 資料；A 訂定序列化與錯誤回報介面，整合後重測；C 核對容量與衝突檢查；D 確認課表、活動介面；E 協助檢查覆蓋範圍。各成員實際互相 Review 並記錄意見、修正與結果。確認內容後提交 Git，保留可追溯版本。
''')

meeting = (OUT / '待補附件/會議與Review紀錄.md').read_text(encoding='utf-8').split('## A 檢視其他成員模組')[0].replace('# 會議與學生 Review 狀態', '# 團隊會議紀錄')
write(TEAM / '會議紀錄.md', meeting)
write(PERSON / '個人Git紀錄.md', '''# A 個人 Git 紀錄

姓名：張庭瑄；學號：111590042。整理日期：2026-10-09。

本機歷史有 2026-10-03 作者 0mago0 的兩筆 Commit，完整 SHA 與功能說明见 [團隊 Git 紀錄](../團隊文件/Git紀錄.md)。目前尚未確認此帳號對應 A，因此未將兩筆提交直接歸為本人貢獻。
此次整理尚未提交與推送；無本次已完成 Commit 可列。本人實際主要 Commit、功能說明與日期應以真實 Git 提交補入，不能用文件產生日替代提交日。
''')
write(PERSON / '檢視其他成員程式Review紀錄.md', '''# A 檢視其他成員程式的 Review 紀錄

姓名：張庭瑄；學號：111590042。

狀態：尚未提供 A 本人已完成的 Review 紀錄。建議檢視 B 的 define_course_schema()、define_student_schema() 與共用 Course／Student 的對應。

AI 發現：course_name 與 name、max_credits 與 credit_limit 不一致，B 草稿缺必選修、容量及已選課程欄位。這是 AI 輔助發現，需 A 實際閱讀並確認，不能直接當成本人完成 Review。

| 必記項目 | 目前資料 |
| --- | --- |
| 被檢視模組 | B 資料模型（規劃） |
| 原開發者與版本 | 尚未確認作者及版本 |
| A 實際檢視日期 | 尚未提供 |
| 本人問題／改善建議 | 尚未提供 |
| B 回應與修正 Commit | 尚未提供 |
| 本人重測結果 | 尚未提供 |

目前以 AI 檢查意見作為閱讀切入點，尚未達教師要求的本人 Review 紀錄。
''')

rolework = (PERSON / '角色與工作紀錄.md').read_text(encoding='utf-8')
write(PERSON / '個人工作紀錄.md', rolework.replace('# A 個人角色與本週工作紀錄', '# A 個人本週工作紀錄').replace('會議與Review紀錄.md', '../團隊文件/會議紀錄.md'))
write(PERSON / '個人角色與負責工作說明.md', '''# A 個人角色與負責工作說明

- 姓名：張庭瑄
- 學號：111590042
- 週次：第 5 週 / Iteration 0
- 角色：組長、系統整合與 F6 儲存載入負責人
- 副組長：E

主要工作為安排分工與進度、管理 Git、統一資料格式與模組介面、整合主流程、追蹤缺陷及維護執行說明。F11 全員參與，由 A 統整；各成員仍需自行測試與記錄。
本次可查證個人參與為提出五人調整、採用分工建議與委託 AI 整理交付；AI 執行的檢查及測試另有標示，未歸為本人獨立開發。
''')

integration = OUT / '整合文件/模組介面與整合說明.md'
write(TEAM / '模組介面與整合說明.md', integration.read_text(encoding='utf-8'))
write(OUT / 'README.md', '''# A 第 5 週繳交包（五人版）

A：張庭瑄（111590042）；副組長：E。此包為第 5 週 / Iteration 0 最小骨架，依教師指定內容分檔。

## 團隊繳交文件

| 項目 | 檔案 |
| --- | --- |
| 需求規格、Use Case、架構、分工、進度 | 團隊文件內既有 requirements-v1.md、use-cases.md、architecture-v1.md、work-breakdown.md、weekly-plan.txt、團隊規劃文件.md |
| 資料格式與模組介面 | campus_planner/models.py、團隊文件/模組介面與整合說明.md |
| 可執行程式 | main.py、campus_planner/、團隊文件/可執行程式與執行說明.md |
| 功能完成表 | [功能完成表](團隊文件/功能完成表.md) |
| 需求／設計修改紀錄 | [需求與設計修改紀錄](團隊文件/需求與設計修改紀錄.md) |
| 自動化測試與結果 | [測試報告](團隊文件/自動化測試與結果.md)、tests/、驗證結果/ |
| Git 紀錄 | [團隊 Git 紀錄](團隊文件/Git紀錄.md) |
| Code Review | [Code Review 紀錄](團隊文件/CodeReview紀錄.md) |
| 問題與缺陷 | [問題與缺陷紀錄](團隊文件/問題與缺陷紀錄.md) |
| Iteration Review | [Iteration Review](團隊文件/IterationReview.md) |
| 會議紀錄與照片 | [會議紀錄](團隊文件/會議紀錄.md)、[會議照片](會議照片.jpg) |

## 個人繳交文件

- [個人角色與負責工作說明](A個人文件/個人角色與負責工作說明.md)
- [個人工作紀錄](A個人文件/個人工作紀錄.md)
- [個人 Git 紀錄](A個人文件/個人Git紀錄.md)
- [重要函式的程式理解說明](A個人文件/程式理解說明.md)
- [檢視其他成員程式 Review 紀錄](A個人文件/檢視其他成員程式Review紀錄.md)
- [AI 協作紀錄](A個人文件/AI協作紀錄.md)

## 執行與更新

```powershell
python -m pip install -r requirements.txt
python main.py
python -m pytest -q -p no:cacheprovider
```

在原專案根目錄執行 `python tools/package_submission.py` 可重新打包已編輯文件。
包內四項基線通過，原專案 F1 收集失敗另有紀錄。尚未提供的學生 Review、本人 Commit、會議討論與決議保持實際狀態；文件已生成不等同這些活動已完成。第 5 週不提供尚未發生的 TDD 歷程。
''')

# Remove superseded combined records only after their contents have been split.
for rel in ['A個人文件/角色與工作紀錄.md', '待補附件', '整合文件']:
    target = OUT / rel
    assert target.resolve().is_relative_to(OUT.resolve())
    if target.is_file():
        target.unlink()
    elif target.is_dir():
        for child in target.iterdir():
            if child.suffix == '.md':
                child.unlink()
        target.rmdir()
print('分檔完成；骨架測試通過，全專案失敗紀錄已保留。')
