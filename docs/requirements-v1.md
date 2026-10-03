# 需求規格 v1（第 5 週）

## 1. 專案定位

本專題為「校園選課與活動管理系統」，採 Python 命令列架構，核心功能由可獨立測試的函式實作，資料不依賴全域變數或人工輸入。網頁層僅作為額外展示，不是本期必做項目。

## 2. 老師要求（保留）

- Python 專案，命令列介面即可。
- 核心函式需可獨立測試，不得依賴 input() 或全域變數。
- 每個模組要有明確輸入、輸出、錯誤處理與測試。
- 使用 Git 管理版本；可採用 AI 協作，但不能直接接受未驗證的 AI 生成內容。
- 期中前以 F1～F6 為主，後段為 F7～F11。

## 3. 團隊待確認的規格（第 5 週先定義）

1. 時間表示：星期 1～7，節次 1～9、a、b、c。
2. 課表矩陣定義：7 天 × 12 個時段，資料模型內統一保留同一順序。
3. 空堂判定：跨日空閒視為同一範圍內的兩個區段，而不是自動合併。
4. 選課紀錄：以唯一來源資料為準，避免同時維護多份不同步資料。
5. 修改/刪除規則：若有人已選課，須先退選或取消；修改後需保留一致性驗證。
6. 不可上課時段：硬限制值，與偏好條件分開處理。
7. 錯誤處理：所有模組回傳清楚錯誤訊息，不使用裸 exception 直接終止。

## 4. 需求範圍（第 5 週重點）

### F1：課程與學生資料管理
- 新增/修改/刪除/查詢課程與學生
- 唯一識別碼檢查
- 學分與人數上限驗證
- 可依代號、教師、星期、必選修、剩餘名額做篩選

### F2：多層次衝堂與選課檢查
- 學生衝堂檢查
- 教室衝堂檢查
- 活動衝突檢查
- 學分上限與人數限制
- 必須收集全部衝突，而不是停在第一個錯誤

### F3：個人課表與空閒時段
- 7×12 課表矩陣
- 依星期、節次、課程代號查詢
- 連續空閒時段掃描
- 每日節數、總學分、空堂數統計

### F4：校園活動與教室配置
- 活動新增/取消/修改/查詢
- 教室篩選與場地配置
- 用共用時段衝突腳本檢查教室占用

### F5：多條件課程篩選
- 依必修清單、學分範圍、不可上課時段、偏好星期做篩選
- 需在候選課程清單中保留可行性資訊

### F6：資料儲存與系統測試
- JSON/CSV 儲存與載入
- 單筆資料錯誤不能使整個系統崩潰
- 至少 30 個自動化測試案例

## 5. 建議資料格式

### Course

```json
{
  "course_id": "CS101",
  "name": "Python 程式設計",
  "credits": 3,
  "required": true,
  "teacher": "林老師",
  "capacity": 40,
  "classroom": "A101",
  "time_slots": [
    {"day": 1, "period": "3"},
    {"day": 1, "period": "4"}
  ]
}
```

### Student

```json
{
  "student_id": "S001",
  "name": "王小明",
  "department": "資工系",
  "enrolled_courses": ["CS101"],
  "credit_limit": 24
}
```

### Classroom

```json
{
  "room_id": "A101",
  "capacity": 60,
  "equipment": ["投影機", "白板"],
  "building": "資訊大樓"
}
```

## 6. 建議函式介面

- `validate_course(course: Course) -> list[str]`
- `validate_student(student: Student) -> list[str]`
- `check_time_conflict(slot_a: TimeSlot, slot_b: TimeSlot) -> bool`
- `evaluate_enrollment(student: Student, course: Course, enrolled_courses: dict[str, Course]) -> list[str]`
- `build_timetable(student: Student, courses: dict[str, Course], activities: list[Activity]) -> list[list[str | None]]`
- `save_school_data(path: str, data: dict) -> None`
- `load_school_data(path: str) -> dict`

## 7. 測試策略

- 正常案例：合法新增、合法加選、有效查詢。
- 邊界案例：人數上限 = 1、星期 7、節次 c、連續三節空閒。
- 錯誤案例：重複代號、學分 0、非法節次、刪除已被選課之課程。
- 回歸案例：失敗後資料不變、載入 JSON 失敗時回傳明確錯誤而不崩潰。

## 8. 第 5 週交付目標

- 需求規格 v1 完成
- Use Case 清楚列出主要使用場景
- 架構 v1 建立
- 資料格式與功能分工確認
- 最小專案骨架可執行
- 一個可運行的測試基線建立

## 9. 未決事項與建議

- 教室與建築物的具體命名原則需由團隊統一。
- 活動定義與課程時段合併規則需在第 6 週確認。
- 評分公式、搜尋條件與偏好權重待 F7 詳細設計。
- 若未來加入網頁，請保留命令列核心不依賴前端。
