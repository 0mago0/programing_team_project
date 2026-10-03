# 校園選課專題：Codex 移交包

這是規格與規劃資料，尚未實作程式，也沒有完成任何測試、Git 歷程或團隊紀錄。

## 使用

1. 解壓縮，以 VS Code 開啟 campus-planner 資料夾。
2. 在 Codex 對話貼上下方指令；有現成專案時，先把此包放入專案，請 Codex 檢查既有程式，避免覆蓋。
3. 原作業 assignment.pdf／assignment.txt 是權威來源；其他文件是整理與建議。

## 給 Codex 的起始指令

請先閱讀 README.md、docs/assignment.txt、docs/implementation-guide.txt 和 docs/weekly-plan.txt。
這是六人 Python 校園選課與活動管理課堂專題。請用繁體中文協助我們逐步開發。
先整理第 5 週需求、未決規格、六人分工、資料格式與函式介面建議，並建立最小專案骨架及執行說明。
若有既有程式，先檢查並沿用。不要一次寫完 F1～F11。
請清楚區分老師要求、團隊尚待確認的規格及你的建議。核心函式須可獨立測試，不能依賴 input() 或用全域變數傳遞資料；網頁只是額外呈現層。
網頁技術尚未決定：之前建議 Streamlit，但不是團隊已確定的選擇。
不要代造會議照片、個人貢獻、Git 紀錄、AI 對話或 TDD 歷程。第 10 週起新增核心功能必須真實採測試先行，保留 Red/Green/Refactor/回歸紀錄。
每完成一小步，說明改了什麼、怎麼測試、哪些判斷需由學生理解與確認。

## 分工建議

A：組長、整合、F6 儲存載入；B：F1 資料管理；C：F2 選課與 F5 篩選；D：F3 課表與 F4 活動；E：F7 最佳課表與 F8 搜尋比較；F：F9 路徑與 F10 動態事件。F11 全員參與、一人統整。每人都負責本人測試與紀錄，並 Review 其他模組。

## 內容

- docs/assignment.pdf、assignment.txt：老師原始作業及文字擷取。
- docs/implementation-guide.pdf、implementation-guide.txt：逐步實作指南。
- docs/weekly-plan.pdf、weekly-plan.txt：每週成果與分工建議。

文字擷取方便閱讀；有疑義請對照 PDF 原文。此包不會自動搬移 ChatGPT 對話，但包含接續工作所需的主要規格與規劃。
