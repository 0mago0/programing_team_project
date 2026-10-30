"""F6 資料儲存：JSON 與 CSV。

儲存課程、學生、教室、活動及選課紀錄。CSV 為一個資料夾內的 6 個檔案：
courses.csv、students.csv、classrooms.csv、activities.csv、
enrollments.csv（選課紀錄：學號、課程代號）、activity_participants.csv（活動報名：活動代號、學號）。

載入時 CSV 每一列先轉成與 JSON 相同的資料格式，再交給 catalog_from_dict，
因此兩種格式經過同一套驗證；單一列格式錯誤只略過該列並記錄原因，不會讓程式中止。
選課紀錄與活動報名是逐列套用：某一列指向不存在的課程或學生時只略過那一列，
不會連帶讓整位學生或整個活動載入失敗。
CSV 中的多值欄位以「;」分隔，時段寫成「星期-節次」，例如「1-3;1-4」。
"""
from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

from .data_manager import SchoolCatalog, catalog_from_dict, catalog_to_dict, load_catalog, save_catalog

CSV_FILES = {
    "courses": ["course_id", "name", "credits", "required", "teacher", "capacity", "classroom", "time_slots"],
    "students": ["student_id", "name", "department", "credit_limit"],
    "classrooms": ["room_id", "capacity", "equipment", "building"],
    "activities": ["activity_id", "name", "time_slots", "expected_participants", "activity_type",
                   "classroom", "venue_requirements"],
    "enrollments": ["student_id", "course_id"],
    "activity_participants": ["activity_id", "student_id"],
}


# ---------- 欄位轉換 ----------

def _slots_to_text(slots: list[dict[str, Any]]) -> str:
    return ";".join(f"{slot['day']}-{slot['period']}" for slot in slots)


def _text_to_slots(text: str) -> list[dict[str, Any]]:
    slots = []
    for part in filter(None, (p.strip() for p in text.split(";"))):
        day, sep, period = part.partition("-")
        if not sep or not day.strip().isdigit():
            raise ValueError(f"時段格式錯誤: {part}（應為「星期-節次」，例如 1-3）")
        slots.append({"day": int(day), "period": period.strip()})
    return slots


def _split(text: str) -> list[str]:
    return [p.strip() for p in text.split(";") if p.strip()]


def _to_int(text: str, field: str) -> int:
    try:
        return int(text)
    except (TypeError, ValueError):
        raise ValueError(f"{field} 必須為整數: {text!r}") from None


def _to_bool(text: str) -> bool:
    value = (text or "").strip().lower()
    if value in ("true", "1", "必修"):
        return True
    if value in ("false", "0", "選修"):
        return False
    raise ValueError(f"必選修格式錯誤: {text!r}（應為 true 或 false）")


# ---------- CSV 儲存 ----------

def save_catalog_csv(directory: str | Path, catalog: SchoolCatalog) -> list[Path]:
    """把 catalog 存成資料夾內的 6 個 CSV 檔，回傳寫出的檔案路徑。"""
    folder = Path(directory)
    folder.mkdir(parents=True, exist_ok=True)
    data = catalog_to_dict(catalog)
    rows: dict[str, list[dict[str, Any]]] = {
        "courses": [{**c, "required": str(c["required"]).lower(), "time_slots": _slots_to_text(c["time_slots"])}
                    for c in data["courses"]],
        "students": [{k: s[k] for k in CSV_FILES["students"]} for s in data["students"]],
        "classrooms": [{**r, "equipment": ";".join(r["equipment"])} for r in data["classrooms"]],
        "activities": [{**{k: a[k] for k in CSV_FILES["activities"]},
                        "time_slots": _slots_to_text(a["time_slots"]),
                        "venue_requirements": ";".join(a["venue_requirements"])} for a in data["activities"]],
        "enrollments": [{"student_id": s["student_id"], "course_id": cid}
                        for s in data["students"] for cid in s["enrolled_courses"]],
        "activity_participants": [{"activity_id": a["activity_id"], "student_id": sid}
                                  for a in data["activities"] for sid in a["participants"]],
    }
    written = []
    for name, fields in CSV_FILES.items():
        path = folder / f"{name}.csv"
        with path.open("w", encoding="utf-8-sig", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=fields, extrasaction="ignore")
            writer.writeheader()
            writer.writerows(rows[name])
        written.append(path)
    return written


# ---------- CSV 載入 ----------

def _read_rows(path: Path, errors: list[str]) -> list[dict[str, str]]:
    if not path.exists():
        return []
    try:
        with path.open("r", encoding="utf-8-sig", newline="") as file:
            return list(csv.DictReader(file))
    except (OSError, UnicodeDecodeError, csv.Error) as exc:
        errors.append(f"{path.name} 無法讀取：{exc}")
        return []


def _convert(rows: list[dict[str, str]], label: str, id_field: str, convert, errors: list[str]) -> list[dict[str, Any]]:
    records = []
    for line, row in enumerate(rows, start=2):  # 第 1 列為標題
        try:
            records.append(convert(row))
        except KeyError as exc:
            errors.append(f"{label} {row.get(id_field) or f'第 {line} 列'}: 缺少欄位 {exc}")
        except (ValueError, AttributeError) as exc:
            errors.append(f"{label} {row.get(id_field) or f'第 {line} 列'}: {exc}")
    return records


def load_catalog_csv(directory: str | Path) -> tuple[SchoolCatalog, list[str]]:
    """從資料夾讀取 CSV。缺少的檔案視為沒有資料；格式錯誤的列略過並記錄原因。"""
    folder = Path(directory)
    if not folder.is_dir():
        return SchoolCatalog(), [f"找不到資料夾：{folder}"]
    errors: list[str] = []
    raw = {name: _read_rows(folder / f"{name}.csv", errors) for name in CSV_FILES}

    data = {
        "classrooms": _convert(raw["classrooms"], "教室", "room_id", lambda r: {
            "room_id": r["room_id"], "capacity": _to_int(r["capacity"], "容量"),
            "equipment": _split(r.get("equipment") or ""), "building": r.get("building") or "校本部"}, errors),
        "courses": _convert(raw["courses"], "課程", "course_id", lambda r: {
            "course_id": r["course_id"], "name": r["name"], "credits": _to_int(r["credits"], "學分"),
            "required": _to_bool(r["required"]), "teacher": r["teacher"],
            "capacity": _to_int(r["capacity"], "人數上限"), "classroom": r["classroom"],
            "time_slots": _text_to_slots(r.get("time_slots") or "")}, errors),
        "students": _convert(raw["students"], "學生", "student_id", lambda r: {
            "student_id": r["student_id"], "name": r["name"], "department": r["department"],
            "credit_limit": _to_int(r["credit_limit"], "學分上限")}, errors),
        "activities": _convert(raw["activities"], "活動", "activity_id", lambda r: {
            "activity_id": r["activity_id"], "name": r["name"],
            "time_slots": _text_to_slots(r.get("time_slots") or ""),
            "expected_participants": _to_int(r["expected_participants"], "預計人數"),
            "activity_type": r.get("activity_type") or "一般", "classroom": r.get("classroom") or "",
            "venue_requirements": _split(r.get("venue_requirements") or "")}, errors),
    }
    catalog, more = catalog_from_dict(data)
    errors += more
    _apply_enrollments(catalog, raw["enrollments"], errors)
    _apply_participants(catalog, raw["activity_participants"], errors)
    return catalog, errors


def _apply_enrollments(catalog: SchoolCatalog, rows: list[dict[str, str]], errors: list[str]) -> None:
    for line, row in enumerate(rows, start=2):
        sid, cid = (row.get("student_id") or "").strip(), (row.get("course_id") or "").strip()
        where = f"選課紀錄 第 {line} 列（{sid}, {cid}）"
        if sid not in catalog.students:
            errors.append(f"{where}: 學生 {sid} 不存在，已略過")
        elif cid not in catalog.courses:
            errors.append(f"{where}: 課程 {cid} 不存在，已略過")
        elif cid in catalog.students[sid].enrolled_courses:
            errors.append(f"{where}: 重複的選課紀錄，已略過")
        else:
            catalog.students[sid].enrolled_courses.append(cid)


def _apply_participants(catalog: SchoolCatalog, rows: list[dict[str, str]], errors: list[str]) -> None:
    for line, row in enumerate(rows, start=2):
        aid, sid = (row.get("activity_id") or "").strip(), (row.get("student_id") or "").strip()
        where = f"活動報名 第 {line} 列（{aid}, {sid}）"
        activity = catalog.activities.get(aid)
        if activity is None:
            errors.append(f"{where}: 活動 {aid} 不存在，已略過")
        elif sid not in catalog.students:
            errors.append(f"{where}: 學生 {sid} 不存在，已略過")
        elif sid in activity.participants:
            errors.append(f"{where}: 重複的報名紀錄，已略過")
        elif len(activity.participants) >= activity.expected_participants:
            errors.append(f"{where}: 超過預計人數 {activity.expected_participants}，已略過")
        else:
            activity.participants.append(sid)


# ---------- 依副檔名自動選擇格式 ----------

def save_data(path: str | Path, catalog: SchoolCatalog) -> list[Path]:
    """路徑以 .json 結尾時存成 JSON，否則視為資料夾存成 CSV。"""
    target = Path(path)
    if target.suffix.lower() == ".json":
        return [save_catalog(target, catalog)]
    return save_catalog_csv(target, catalog)


def load_data(path: str | Path) -> tuple[SchoolCatalog, list[str]]:
    target = Path(path)
    if target.suffix.lower() == ".json":
        return load_catalog(target)
    return load_catalog_csv(target)
