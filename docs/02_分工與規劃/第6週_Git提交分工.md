# 第 6 週 Git 提交分工

老師會看每人的 Git 提交紀錄，所以**每個人用自己的 GitHub 帳號提交自己負責的檔案**。
每位成員的檔案都已放在 A 電腦上的 `archive/第6週_交接/成員X/`（資料夾結構與專案相同，直接複製到專案根目錄即可）。A 需要把對應的資料夾傳給每個人。

> ⚠ 誠實說明：本週 F1 程式、測試與範例資料的初版是 A 用 AI 助理產生的。提交者必須先讀懂、實際跑過測試，並在自己的「AI 協作紀錄」寫明「初版由 AI 產生、我檢查了什麼、改了什麼」。不要寫成是自己從零寫的。

## 提交順序與負責人

依照順序做，每一步合併後測試都會是綠的（已模擬驗證）。Review 依團隊約定 A → B → C → D → E → A。

| 順序 | 誰 | 分支 | 提交的檔案 | Reviewer | 合併後測試 |
| --- | --- | --- | --- | --- | --- |
| 0 | A | — | 撤銷外洩的 GitHub token，改遠端網址（見下方） | — | — |
| 1 | A | 直接推到 main | 專案結構整理：docs 重新分類、README、.gitignore、tools、刪除舊角色資料夾、F1 函式介面、需求規格 R1～R11、本文件 | — | 收集失敗（同目前狀態，第 2 步後恢復） |
| 2 | B | feature/role-B | `campus_planner/data_manager.py`、`campus_planner/validation.py`、`docs/04_個人紀錄/成員B/` | A | 8 passed |
| 3 | E | feature/role-E | `data/sample_school_data.json`、`docs/04_個人紀錄/成員E/` | D | 8 passed |
| 4 | C | feature/role-C | 把根目錄的 `test_f1_catalog.py` 搬到 `tests/`、`docs/04_個人紀錄/成員C/` | B | 49 passed |
| 5 | A | feature/role-A | `main.py`、`docs/03_週報/第6週_團隊繳交.md`（填完 Git 與 Review 紀錄）、`docs/04_個人紀錄/成員A/第6週_個人紀錄.md` | E | 49 passed |
| 6 | D | feature/role-D | `docs/04_個人紀錄/成員D/`（含 Review E 的範例資料紀錄） | C | 49 passed |

**C 注意：** 你 10/16 用網頁上傳的 `test_f1_catalog.py` 放在 repo 根目錄，正確位置是 `tests/`。兩份同名測試同時存在時 pytest 會報 import file mismatch，所以第 4 步請用 `git mv test_f1_catalog.py tests/test_f1_catalog.py` 搬過去（內容已確認與交接檔相同，不必再複製），再加上自己的個人紀錄。

之後請一律用分支加 Pull Request 提交，不要用 GitHub 網頁的「Add files via upload」，那樣檔案會落在根目錄，commit 訊息也看不出做了什麼。

第 3 步可以和第 2 步同時進行；第 4 步要等 B、E 都合併；第 5 步要等第 4 步。D 這週沒有程式檔，主要工作是 Review E 的範例資料（教室欄位、時段），並為第 7 週 F3 做準備。

## GitHub 帳號對照（⚠ 依上傳內容推斷，請各人確認）

| 角色 | GitHub 帳號 | 推斷依據 |
| --- | --- | --- |
| A | 0mago0 | 儲存庫擁有者 |
| B | dolphin12088 | 10/3 上傳 `B_資料模型.py` |
| C | zhiyun0916 | 10/3 上傳 `C_選課規則.py`；10/16 上傳 `test_f1_catalog.py` |
| D | nNn-3361 | 10/3 上傳 `D_課表排程.py` |
| E | linsam960421-lgtm | 10/3 上傳 `E_最佳課表搜尋.py` |

10/3 四人上傳到根目錄的舊草稿已在第 1 步移除（歷史紀錄仍保留在 git log，作為第 5 週的提交證據）。

## 第 0 步：A 先處理 token（一定要先做）

1. 到 GitHub → Settings → Developer settings → Personal access tokens，撤銷目前寫在遠端網址裡的 token。
2. 把遠端改成不含 token 的網址：

```powershell
git remote set-url origin https://github.com/0mago0/programing_team_project.git
```

之後推送時用 Git Credential Manager 登入。

## 第 1 步：A 推送結構整理

在 A 的專案根目錄：

```powershell
git add -A -- . ":!docs/03_週報/第6週_團隊繳交.md" ":!docs/04_個人紀錄/成員A/第6週_個人紀錄.md"
git status
git commit -m "整理專案結構：docs 分類、合併角色資料夾、F1 規格與介面文件"
git push origin main
```

`git status` 確認沒有 `main.py`、`data_manager.py` 等程式檔被加入後再 commit。

## 第 2～6 步：每位成員的做法

以 B 為例，其他人把 `B`／`role-B`／`成員B` 換成自己的：

```powershell
git config user.name "你的名字"
git config user.email "你的 GitHub 信箱"
git switch main
git pull
git switch -c feature/role-B
Copy-Item -Recurse -Force "<收到的資料夾>\成員B\*" .
python -m pytest -q
git add campus_planner/data_manager.py campus_planner/validation.py docs/04_個人紀錄/成員B
git commit -m "F1：課程、學生、教室資料管理與驗證"
git push -u origin feature/role-B
```

第一次的成員先 `git clone https://github.com/0mago0/programing_team_project.git`。

推送後到 GitHub 開 Pull Request，指定 Reviewer。Reviewer 在 PR 上實際看程式、留下意見；原開發者回應或修正後再合併。PR 上的意見就是 Code Review 紀錄的來源，請填進各自的個人紀錄與團隊繳交文件。

## A 的第 5 步

```powershell
git switch main
git pull
git switch -c feature/role-A
Copy-Item -Force archive\第6週_交接\成員A_第二次\main.py main.py
python -m pytest -q
python main.py
git add main.py docs/03_週報/第6週_團隊繳交.md docs/04_個人紀錄/成員A/第6週_個人紀錄.md
git commit -m "主程式接上 F1，第 6 週團隊繳交文件"
git push -u origin feature/role-A
```

## 各人本週還要填的

| 誰 | 要填 |
| --- | --- |
| 全部 | 自己的 `第6週_個人紀錄.md`：工作紀錄、Git 紀錄、程式理解說明、Code Review、AI 協作紀錄 |
| A | 團隊繳交文件的 Git 紀錄、Code Review 彙整、會議紀錄、Iteration Review |
| B | 能解釋 `data_manager.py` 每個函式；R1～R11 若團隊不同意要提出修改 |
| A、B、C、D、E | 開會確認 R1～R11，結果寫進需求規格第 11 節 |
