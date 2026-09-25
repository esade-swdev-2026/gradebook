from pathlib import Path

import pandas as pd
from typer.testing import CliRunner

from gradebook.cli import app

runner = CliRunner()


def test_add_student_adds_student_to_class(tmp_path: Path) -> None:
    class_file = tmp_path / "class.csv"

    result = runner.invoke(
        app,
        ["add-student", "Ada Lovelace", "--class-file", str(class_file)],
    )

    assert result.exit_code == 0
    assert "Added Ada Lovelace" in result.stdout

    roster = pd.read_csv(class_file)
    assert "Ada Lovelace" in roster["name"].values


def test_add_student_rejects_empty_name(tmp_path: Path) -> None:
    class_file = tmp_path / "class.csv"

    result = runner.invoke(
        app,
        ["add-student", "   ", "--class-file", str(class_file)],
    )

    assert result.exit_code == 1
    assert "student name cannot be empty" in result.output
