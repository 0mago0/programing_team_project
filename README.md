# 校園選課與活動管理系統（Campus Planner）

五人 Python 課堂團體專題，目前進度：第 6 週（Iteration 1）F1 課程與學生資料管理。

- GitHub 儲存庫：https://github.com/0mago0/programing_team_project.git
- 組長 A：張庭瑄（111590042）；副組長：E

## 快速導覽

| 我想看… | 去哪裡 |
| --- | --- |
| 老師的作業要求 | [docs/00_老師作業/](docs/00_老師作業/assignment.pdf) |
| 需求、Use Case、架構 | [docs/01_規格與設計/](docs/01_規格與設計/requirements-v1.md) |
| 分工、每週計畫、實作指南 | [docs/02_分工與規劃/](docs/02_分工與規劃/團隊規劃文件.md) |
| 本週（第 6 週）繳交 | [docs/03_週報/第6週_團隊繳交.md](docs/03_週報/第6週_團隊繳交.md) |
| F1 函式介面 | [docs/01_規格與設計/F1_函式介面.md](docs/01_規格與設計/F1_函式介面.md) |
| 全部文件索引 | [docs/README.md](docs/README.md) |
| 已繳交的 A 交付包 | deliverables/A_第5週繳交包_五人版/ |

## 專案結構

```text
campus-planner/
├── main.py              程式入口
├── campus_planner/      共用核心程式（models、validation、data_manager、data_store、planner、timetable）
├── tests/               自動化測試
├── data/                JSON 範例資料
├── docs/                文件（00 老師作業 ～ 05 會議，見 docs/README.md）
│   └── 04_個人紀錄/成員A～E/  每人自己的個人紀錄
├── deliverables/        已繳交的交付包
└── tools/               打包與 PDF 產生工具（見 tools/README.md）
```

deliverables/ 與 archive/（舊角色草稿）已列入 .gitignore，只存在本機，不會推送到 GitHub。

## 執行與測試

```powershell
python main.py
python -m pytest -q
python tools/package_submission.py
```

目前狀態（2026-10-16）：`python -m pytest -q` 共 49 項全部通過；`python main.py` 會載入 20 門課、15 名學生、5 間教室並示範 F1。

## 分工

| 角色 | 負責範圍 | 個人紀錄 |
| --- | --- | --- |
| A | 組長、整合、F6 儲存載入 | [成員A/](docs/04_個人紀錄/成員A/) |
| B | F1 資料管理 | [成員B/](docs/04_個人紀錄/成員B/) |
| C | F2 選課、F5 篩選、F10 動態事件 | [成員C/](docs/04_個人紀錄/成員C/) |
| D | F3 課表、F4 活動、F9 路徑 | [成員D/](docs/04_個人紀錄/成員D/) |
| E | F7 最佳課表、F8 搜尋比較 | [成員E/](docs/04_個人紀錄/成員E/) |

各角色詳細職責見 [角色職責與交付清單](docs/02_分工與規劃/角色職責與交付清單.md)；第 6 週誰提交哪些檔案見 [第 6 週 Git 提交分工](docs/02_分工與規劃/第6週_Git提交分工.md)。

F11 全員參與，由 A 統整。每人負責本人測試與紀錄，並 Review 其他模組，建議順序 A → B → C → D → E → A。老師原始作業文件不因團隊人數變更而修改。

## 使用方式（接續開發）

1. 以 VS Code 開啟 campus-planner 資料夾。
2. 在 AI 助理（如 Codex）對話貼上下方起始指令；有既有程式時，請它先檢查並沿用，避免覆蓋。
3. 老師原作業 assignment.pdf／assignment.txt 是權威來源，其他文件是整理與建議。

<details>
<summary>給 AI 助理的起始指令</summary>

```text
請先閱讀 README.md、docs/00_老師作業/assignment.txt、docs/02_分工與規劃/implementation-guide.txt 和 docs/02_分工與規劃/weekly-plan.txt。
這是五人 Python 校園選課與活動管理課堂專題。請用繁體中文協助我們逐步開發。
先整理第 5 週需求、未決規格、五人分工、資料格式與函式介面建議，並建立最小專案骨架及執行說明。
若有既有程式，先檢查並沿用。不要一次寫完 F1～F11。
請清楚區分老師要求、團隊尚待確認的規格及你的建議。核心函式須可獨立測試，不能依賴 input() 或用全域變數傳遞資料；網頁只是額外呈現層。
網頁技術尚未決定：之前建議 Streamlit，但不是團隊已確定的選擇。
不要代造會議照片、個人貢獻、Git 紀錄、AI 對話或 TDD 歷程。第 10 週起新增核心功能必須真實採測試先行，保留 Red/Green/Refactor/回歸紀錄。
每完成一小步，說明改了什麼、怎麼測試、哪些判斷需由學生理解與確認。
```

</details>
