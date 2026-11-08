from pathlib import Path

from typer.testing import CliRunner

from gradebook.cli import app

runner = CliRunner()
DEMO_CLASS = Path(__file__).parent.parent / "examples" / "demo-class"


def test_export_writes_one_row_per_student(tmp_path: Path) -> None:
    exported = tmp_path / "report.csv"

    result = runner.invoke(app, ["export", str(exported), "--data-dir", str(DEMO_CLASS)])

    assert result.exit_code == 0
    assert "Exported 4 students" in result.output
    lines = exported.read_text().splitlines()
    assert lines[0] == "student,graded_percent,current_grade,band,needed_to_pass"
    assert len(lines) == 1 + 4


def test_export_to_a_folder_fails_cleanly(tmp_path: Path) -> None:
    result = runner.invoke(app, ["export", str(tmp_path), "--data-dir", str(DEMO_CLASS)])

    assert result.exit_code == 1
    assert "Error:" in result.output


def test_export_writes_each_students_numbers(tmp_path: Path) -> None:
    exported = tmp_path / "report.csv"

    runner.invoke(app, ["export", str(exported), "--data-dir", str(DEMO_CLASS)])

    # 4.0 and 5.5 on 30 % each: 285 of 500 points, 215 over the last 40 % is 5.375
    assert "Leo Martin,60,4.75,Fail,5.38" in exported.read_text().splitlines()


def test_export_of_an_empty_class_writes_only_the_header(tmp_path: Path) -> None:
    exported = tmp_path / "report.csv"

    result = runner.invoke(
        app, ["export", str(exported), "--data-dir", str(tmp_path / "empty-class")]
    )

    assert result.exit_code == 0
    assert "Exported 0 students" in result.output
    assert exported.read_text().splitlines() == [
        "student,graded_percent,current_grade,band,needed_to_pass"
    ]
