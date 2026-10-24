# 專案工具

- `python tools/package_submission.py [資料夾名稱]`：將 deliverables 中的繳交資料夾打包成同名 ZIP（未指定時為第 5 週），不重建或覆寫個人紀錄。例：`python tools/package_submission.py A_第6週繳交包_五人版`。
- `split_submission_records.py`：將合併紀錄拆成教師指定項目的一次性遷移工具，已於 2026-10-09 執行完成，之後交付包已改為 PDF。現在預設拒絕執行；即使加上 `--run-migration`，也會在遷移來源不存在時停止，且不會覆寫任何既有檔案。請直接編輯 deliverables 內現有文件。
- `python tools/make_report_pdf.py`：由 docs/03_週報/第5週報告.md 產生同名 PDF。
- `python tools/make_formal_report_pdf.py`：由 docs/03_週報/第5週報告_正式版.md 產生同名 PDF。
- `python tools/make_personal_pdf.py <個人紀錄.md>`：把個人紀錄 Markdown 轉成與第 5 週個人繳交相同版面的 PDF（輸出在同資料夾、同檔名）。需要 reportlab 與微軟正黑體。
- `python tools/make_srs_sdd.py`：產生第 6 週「系統需求設計規格書（SRS／SDD）」PDF 到 docs/03_週報/。成員姓名改檔案開頭的 MEMBERS；附錄的執行結果、測試結果與 git log 在產生時實際執行取得。
- `python tools/make_srs_sdd_w7.py`：產生第 7 週「系統需求設計規格書 V2.0」PDF，版面與共用函式沿用 make_srs_sdd.py；本週 Commit 依 git log 自動列出，會議日期地點改檔案中的 MEETING。

PDF 工具需另外安裝 reportlab，使用 Windows 中文字型。舊報告 PDF 已刪除，需產生時請依最新 Markdown 重新生成並檢查版面。
舊產檔與補紀錄腳本已刪除，避免覆蓋已填入的姓名與副組長資訊。
