import csv
from dataclasses import replace
from pathlib import Path

from gradebook.export import EXPORT_COLUMNS, export_rows
from gradebook.models import Gradebook
from gradebook.storage import save_report_csv


def test_one_row_per_student_sorted_by_name(demo_gradebook: Gradebook) -> None:
    assert [row["student"] for row in export_rows(demo_gradebook)] == ["Leo Martin", "Noa Ferrer"]


def test_every_row_has_exactly_the_export_columns(demo_gradebook: Gradebook) -> None:
    for row in export_rows(demo_gradebook):
        assert list(row) == EXPORT_COLUMNS


def test_row_holds_the_report_numbers(demo_gradebook: Gradebook) -> None:
    noa = export_rows(demo_gradebook)[1]
    # 8.0 on 60 %: 480 of 500 points, 20 points over the last 40 %
    assert noa == {
        "student": "Noa Ferrer",
        "graded_percent": "60",
        "current_grade": "8.00",
        "band": "Very good",
        "needed_to_pass": "0.50",
    }


def test_student_with_no_grades_has_empty_cells(demo_gradebook: Gradebook) -> None:
    gradebook = replace(demo_gradebook, students=[*demo_gradebook.students, "Iris Soler"])
    iris = next(row for row in export_rows(gradebook) if row["student"] == "Iris Soler")
    assert iris["current_grade"] == ""
    assert iris["band"] == ""
    assert iris["needed_to_pass"] == "5.00"


def test_empty_class_has_no_rows() -> None:
    assert export_rows(Gradebook()) == []


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as file:
        return list(csv.DictReader(file))


def test_saved_csv_reads_back_as_the_same_rows(demo_gradebook: Gradebook, tmp_path: Path) -> None:
    path = tmp_path / "report.csv"
    save_report_csv(path, demo_gradebook)
    assert read_csv(path) == export_rows(demo_gradebook)


def test_saved_csv_starts_with_the_header(demo_gradebook: Gradebook, tmp_path: Path) -> None:
    path = tmp_path / "report.csv"
    save_report_csv(path, demo_gradebook)
    assert path.read_text().splitlines()[0] == ",".join(EXPORT_COLUMNS)


def test_empty_class_writes_only_the_header(tmp_path: Path) -> None:
    path = tmp_path / "report.csv"
    save_report_csv(path, Gradebook())
    assert path.read_text().splitlines() == [",".join(EXPORT_COLUMNS)]


def test_missing_folders_are_created(demo_gradebook: Gradebook, tmp_path: Path) -> None:
    path = tmp_path / "exports" / "2026" / "report.csv"
    save_report_csv(path, demo_gradebook)
    assert path.exists()
