# 專案工具

- `python tools/package_submission.py`：將 deliverables 中已編輯的 A 繳交資料夾重新打包；不重建或覆寫個人紀錄。
- `split_submission_records.py`：將合併紀錄拆成教師指定項目的一次性遷移工具，已於 2026-10-09 執行完成，之後交付包已改為 PDF。現在預設拒絕執行；即使加上 `--run-migration`，也會在遷移來源不存在時停止，且不會覆寫任何既有檔案。請直接編輯 deliverables 內現有文件。
- `python tools/make_report_pdf.py`：由 docs/03_週報/第5週報告.md 產生同名 PDF。
- `python tools/make_formal_report_pdf.py`：由 docs/03_週報/第5週報告_正式版.md 產生同名 PDF。

PDF 工具需另外安裝 reportlab，使用 Windows 中文字型。舊報告 PDF 已刪除，需產生時請依最新 Markdown 重新生成並檢查版面。
舊產檔與補紀錄腳本已刪除，避免覆蓋已填入的姓名與副組長資訊。
