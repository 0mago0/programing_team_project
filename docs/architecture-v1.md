# 架構設計 v1（第 5 週）

## 1. 目標

本期先建立最小可執行骨架，讓後續 F1～F11 依循相同資料格式與模組界面開發，而不是各自建立獨立資料表。

## 2. 模組分層

```text
main.py
└── campus_planner/
    ├── __init__.py
    ├── models.py            # 資料模型：Course, Student, Classroom, Activity, TimeSlot
    ├── validation.py        # 驗證函式：時段、學分、重複代號、衝突
    ├── data_store.py        # JSON/CSV 載入、儲存與錯誤處理
    ├── planner.py           # 例行規劃、輸出摘要、範例資料產生
    └── timetable.py         # 課表產生與空閒時段規劃（後續擴充）

tests/
├── test_validation.py
├── test_data_store.py
└── test_timetable.py

data/
└── sample_school_data.json
```

## 3. 設計原則

- 以純函式為核心：輸入資料與輸出結果明確，不依賴全域狀態。
- 資料模型統一：所有模組共享相同 dataclass / dict 結構。
- 錯誤收集：一個檢查可以回傳多個錯誤，而不是只停在第一個。
- 可測試性：所有核心函式可直接單元測試，不需手動輸入。

## 4. 介面設計

### A. 資料層
- `models.py`：定義資料結構。
- `data_store.py`：儲存與檔案讀取。

### B. 檢查層
- `validation.py`：用於代號重複、節次合法性、時間衝突、學分限制。

### C. 規劃層
- `planner.py`：產生測試資料、檢查選課結論、輸出摘要。

### D. 進入點
- `main.py`：啟動系統、顯示版本資訊、輸出範例資料與測試提示。

## 5. 介面約定

- 函式不直接使用 `input()`。
- 返回結構要有清楚的 `errors` 或 `result`。
- 如果模組可能失敗，使用 `ValueError` / `RuntimeError` 包裝，但不要讓整個程式直接終止。

## 6. 後續延伸

- F1～F6 會在這個骨架上逐步增加術語、查詢功能與資料驗證。
- F7～F11 會加入搜尋器、路徑規劃、事件重規劃與 AI 品質改善。
- 若以後加入網頁，網頁應視為 UI 層，不改動核心資料與檢查邏輯。
