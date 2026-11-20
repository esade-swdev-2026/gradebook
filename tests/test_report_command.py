from pathlib import Path

from typer.testing import CliRunner

from gradebook.cli import app

runner = CliRunner()
DEMO_CLASS = Path(__file__).parent.parent / "examples" / "demo-class"


def report_lines() -> list[str]:
    result = runner.invoke(app, ["report", "--data-dir", str(DEMO_CLASS)])
    assert result.exit_code == 0
    return result.output.splitlines()


def line_starting_with(lines: list[str], start: str, after: str) -> str:
    """The first line that starts with `start`, below the line that starts with `after`."""
    below = lines[next(i for i, line in enumerate(lines) if line.startswith(after)) :]
    return next(line for line in below if line.startswith(start))


def test_report_shows_lowest_median_and_highest_per_assignment() -> None:
    lines = report_lines()

    # Midterm: 8.5, 4.0, 1.0, 6.0. Group project: 9.0, 5.5, 0.5. Final exam: nobody yet
    midterm = line_starting_with(lines, "Midterm exam", after="Score spread")
    project = line_starting_with(lines, "Group project", after="Score spread")
    final_exam = line_starting_with(lines, "Final exam", after="Score spread")
    assert midterm.split()[-3:] == ["1.0", "5.0", "8.5"]
    assert project.split()[-3:] == ["0.5", "5.5", "9.0"]
    assert final_exam.split()[-3:] == ["-", "-", "-"]


def test_report_counts_the_students_in_each_band() -> None:
    # Noa 8.8 Very good, Hugo 6.0 Pass, Leo 4.8 and Iris 0.8 Fail
    assert "Students per band: Excellent 0, Very good 1, Pass 1, Fail 2" in report_lines()
