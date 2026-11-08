from pathlib import Path

import pytest
from typer.testing import CliRunner

from gradebook.cli import app

runner = CliRunner()
DEMO_CLASS = Path(__file__).parent.parent / "examples" / "demo-class"


def test_ranking_shows_the_best_students_first() -> None:
    result = runner.invoke(app, ["ranking", "--top", "2", "--data-dir", str(DEMO_CLASS)])

    assert result.exit_code == 0
    # Noa 8.8, Hugo 6.0, Leo 4.8, Iris 0.8: the top 2 are Noa, then Hugo
    lines = result.output.splitlines()
    assert len(lines) == 2
    assert "Noa Ferrer" in lines[0] and "8.8" in lines[0]
    assert "Hugo Navarro" in lines[1]


@pytest.mark.parametrize("top", ["0", "-1"])
def test_ranking_rejects_a_top_below_one(top: str) -> None:
    result = runner.invoke(app, ["ranking", "--top", top, "--data-dir", str(DEMO_CLASS)])

    assert result.exit_code == 1
    assert "count must be at least 1" in result.output


def test_ranking_of_an_empty_class_says_so(tmp_path: Path) -> None:
    result = runner.invoke(app, ["ranking", "--data-dir", str(tmp_path)])

    assert result.exit_code == 0
    assert "No student has a grade yet." in result.output


def test_ranking_of_students_without_grades_says_so(tmp_path: Path) -> None:
    runner.invoke(app, ["add-student", "Noa Ferrer", "--data-dir", str(tmp_path)])

    result = runner.invoke(app, ["ranking", "--data-dir", str(tmp_path)])

    assert result.exit_code == 0
    assert "No student has a grade yet." in result.output


def test_ranking_with_a_top_larger_than_the_class_shows_everyone() -> None:
    result = runner.invoke(app, ["ranking", "--top", "10", "--data-dir", str(DEMO_CLASS)])

    assert result.exit_code == 0
    assert len(result.output.splitlines()) == 4
