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
