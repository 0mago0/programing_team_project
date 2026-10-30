from __future__ import annotations

from pathlib import Path

import pytest

from campus_planner.cli import run_menu
from campus_planner.data_manager import SchoolCatalog, load_catalog

SAMPLE = Path(__file__).resolve().parents[1] / "data" / "sample_school_data.json"


def run(catalog: SchoolCatalog, inputs: list[str]) -> tuple[SchoolCatalog, str]:
    answers = iter(inputs)
    output: list[str] = []
    result = run_menu(catalog, ask=lambda _: next(answers), say=output.append)
    return result, "\n".join(output)


@pytest.fixture
def catalog() -> SchoolCatalog:
    return load_catalog(SAMPLE)[0]


# ---------- 正常案例 ----------

def test_enroll_through_menu(catalog: SchoolCatalog) -> None:
    _, text = run(catalog, ["2", "S015", "CS109", "0"])
    assert "選課結果：成功" in text
    assert "CS109" in catalog.students["S015"].enrolled_courses


def test_save_and_load_through_menu(catalog: SchoolCatalog, tmp_path: Path) -> None:
    target = str(tmp_path / "csv")
    result, text = run(catalog, ["2", "S015", "CS109", "8", target, "9", target, "0"])
    assert "已載入：課程 20、學生 15、教室 5、活動 4" in text
    assert result == catalog


# ---------- 邊界案例 ----------

def test_exit_immediately(catalog: SchoolCatalog) -> None:
    result, text = run(catalog, ["0"])
    assert result is catalog and text.endswith("再見！")


# ---------- 錯誤案例 ----------

def test_invalid_input_does_not_crash(catalog: SchoolCatalog) -> None:
    _, text = run(catalog, ["x", "4", "S999", "6", "", "abc", "0"])
    assert "請輸入 0～9" in text
    assert "輸入有誤：學生 S999 不存在" in text
    assert "輸入有誤：invalid literal for int()" in text


def test_loading_missing_folder_keeps_data(catalog: SchoolCatalog, tmp_path: Path) -> None:
    result, text = run(catalog, ["9", str(tmp_path / "nothing"), "0"])
    assert "沒有載入任何資料，保留原本的資料" in text
    assert result is catalog
