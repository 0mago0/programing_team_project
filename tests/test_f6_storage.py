from __future__ import annotations

import json
from pathlib import Path

import pytest

from campus_planner.data_manager import SchoolCatalog, catalog_from_dict, load_catalog
from campus_planner.storage import load_catalog_csv, load_data, save_catalog_csv, save_data

SAMPLE = Path(__file__).resolve().parents[1] / "data" / "sample_school_data.json"


@pytest.fixture
def sample() -> SchoolCatalog:
    catalog, errors = load_catalog(SAMPLE)
    assert errors == []
    return catalog


def write(folder: Path, name: str, text: str) -> None:
    (folder / name).write_text(text, encoding="utf-8")


# ---------- 正常案例 ----------

def test_csv_round_trip(sample: SchoolCatalog, tmp_path: Path) -> None:
    save_catalog_csv(tmp_path, sample)
    loaded, errors = load_catalog_csv(tmp_path)
    assert errors == []
    assert loaded == sample


def test_csv_writes_six_files(sample: SchoolCatalog, tmp_path: Path) -> None:
    names = [p.name for p in save_catalog_csv(tmp_path, sample)]
    assert names == ["courses.csv", "students.csv", "classrooms.csv", "activities.csv",
                     "enrollments.csv", "activity_participants.csv"]


def test_enrollment_records_saved(sample: SchoolCatalog, tmp_path: Path) -> None:
    save_catalog_csv(tmp_path, sample)
    lines = (tmp_path / "enrollments.csv").read_text(encoding="utf-8-sig").splitlines()
    total = sum(len(s.enrolled_courses) for s in sample.students.values())
    assert lines[0] == "student_id,course_id"
    assert len(lines) - 1 == total


def test_save_and_load_by_extension(sample: SchoolCatalog, tmp_path: Path) -> None:
    save_data(tmp_path / "school.json", sample)
    save_data(tmp_path / "csv", sample)
    assert load_data(tmp_path / "school.json")[0] == sample
    assert load_data(tmp_path / "csv")[0] == sample


# ---------- 邊界案例 ----------

def test_empty_catalog_round_trip(tmp_path: Path) -> None:
    save_catalog_csv(tmp_path, SchoolCatalog())
    assert load_catalog_csv(tmp_path) == (SchoolCatalog(), [])


def test_missing_csv_files_treated_as_empty(tmp_path: Path) -> None:
    write(tmp_path, "courses.csv", "course_id,name,credits,required,teacher,capacity,classroom,time_slots\n"
                                   "CS1,程式,3,true,林老師,1,A101,7-c\n")
    catalog, errors = load_catalog_csv(tmp_path)
    assert errors == []
    assert list(catalog.courses) == ["CS1"]


def test_required_accepts_chinese_values(tmp_path: Path) -> None:
    write(tmp_path, "courses.csv", "course_id,name,credits,required,teacher,capacity,classroom,time_slots\n"
                                   "CS1,程式,3,必修,林老師,30,A101,1-1\nCS2,網頁,2,選修,林老師,30,A101,1-2\n")
    catalog, _ = load_catalog_csv(tmp_path)
    assert [c.required for c in catalog.courses.values()] == [True, False]


def test_null_section_in_json_treated_as_empty() -> None:
    catalog, errors = catalog_from_dict({"courses": None, "students": None})
    assert catalog == SchoolCatalog() and errors == []


# ---------- 錯誤案例：單筆錯誤不得使程式中止 ----------

def test_non_list_section_reported_and_others_loaded(sample: SchoolCatalog, tmp_path: Path) -> None:
    """Code Review 第 1 項回歸測試：欄位不是清單時記錄錯誤，其他資料照常載入。"""
    data = json.loads(SAMPLE.read_text(encoding="utf-8"))
    data["activities"] = "壞掉的資料"
    path = tmp_path / "broken.json"
    path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    catalog, errors = load_catalog(path)
    assert errors == ["活動資料（activities）格式錯誤：應為清單，實際為 str，已略過"]
    assert len(catalog.courses) == 20 and catalog.activities == {}


@pytest.mark.parametrize("row, message", [
    ("CS9,壞,三,true,林老師,30,A101,1-1", "課程 CS9: 學分 必須為整數: '三'"),
    ("CS9,壞,3,maybe,林老師,30,A101,1-1", "課程 CS9: 必選修格式錯誤: 'maybe'（應為 true 或 false）"),
    ("CS9,壞,3,true,林老師,30,A101,星期一", "課程 CS9: 時段格式錯誤: 星期一（應為「星期-節次」，例如 1-3）"),
    ("CS9,壞,3,true,林老師,30,A101,1-d", "課程 CS9: 節次不合法: d"),
])
def test_bad_csv_row_skipped(tmp_path: Path, row: str, message: str) -> None:
    write(tmp_path, "courses.csv", "course_id,name,credits,required,teacher,capacity,classroom,time_slots\n"
                                   f"CS1,程式,3,true,林老師,30,A101,1-1\n{row}\n")
    catalog, errors = load_catalog_csv(tmp_path)
    assert list(catalog.courses) == ["CS1"]
    assert errors == [message]


def test_enrollment_to_unknown_course(sample: SchoolCatalog, tmp_path: Path) -> None:
    save_catalog_csv(tmp_path, sample)
    with (tmp_path / "enrollments.csv").open("a", encoding="utf-8") as file:
        file.write("S014,XX999\n")
    catalog, errors = load_catalog_csv(tmp_path)
    lines = len((tmp_path / "enrollments.csv").read_text(encoding="utf-8-sig").splitlines())
    assert errors == [f"選課紀錄 第 {lines} 列（S014, XX999）: 課程 XX999 不存在，已略過"]
    # 只略過該列：學生與他報名的活動都照常載入
    assert catalog.students["S014"].enrolled_courses == []
    assert "S014" in catalog.activities["A002"].participants


def test_missing_folder(tmp_path: Path) -> None:
    catalog, errors = load_catalog_csv(tmp_path / "不存在")
    assert catalog == SchoolCatalog()
    assert errors[0].startswith("找不到資料夾")


def test_missing_column_reported(tmp_path: Path) -> None:
    write(tmp_path, "classrooms.csv", "room_id,building\nA101,資訊大樓\n")
    catalog, errors = load_catalog_csv(tmp_path)
    assert catalog.classrooms == {}
    assert errors == ["教室 A101: 缺少欄位 'capacity'"]


def test_missing_json_file_reported(tmp_path: Path) -> None:
    """E 第 6 週 Code Review 第 2 項：資料檔不存在時要回報，而不是回傳空資料卻不說明。"""
    catalog, errors = load_catalog(tmp_path / "no_such.json")
    assert catalog == SchoolCatalog()
    assert errors == [f"找不到資料檔：{tmp_path / 'no_such.json'}"]
