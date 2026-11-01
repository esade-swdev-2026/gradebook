from pathlib import Path

from typer.testing import CliRunner

from gradebook.cli import app

runner = CliRunner()
DEMO_CLASS = Path(__file__).parent.parent / "examples" / "demo-class"


def test_student_command_shows_the_detail() -> None:
    result = runner.invoke(app, ["student", "Leo Martin", "--data-dir", str(DEMO_CLASS)])
    assert result.exit_code == 0
    assert "Leo Martin" in result.output
    # 4.0 and 5.5 on 30 % each: 285 of 500 points, 215 over the last 40 %
    assert "Current grade: 4.8 (Fail)" in result.output
    assert "Needs on the rest to pass: 5.4" in result.output


def test_student_command_for_unknown_student_fails_cleanly() -> None:
    result = runner.invoke(app, ["student", "Nobody", "--data-dir", str(DEMO_CLASS)])
    assert result.exit_code == 1
    assert "unknown student 'Nobody'" in result.output
