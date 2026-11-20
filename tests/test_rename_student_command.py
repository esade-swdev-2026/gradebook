from pathlib import Path

from typer.testing import CliRunner

from gradebook.cli import app

runner = CliRunner()


def run(data_dir: Path, *args: str) -> tuple[int, str]:
    result = runner.invoke(app, [*args, "--data-dir", str(data_dir)])
    return result.exit_code, result.output


def make_class(data_dir: Path) -> None:
    run(data_dir, "add-student", "Noa Ferrer")
    run(data_dir, "add-student", "Leo Martin")
    run(data_dir, "add-assignment", "Quiz", "10")
    run(data_dir, "record-grade", "Noa Ferrer", "Quiz", "8")


def test_rename_student_keeps_their_grades(tmp_path: Path) -> None:
    make_class(tmp_path)

    exit_code, output = run(tmp_path, "rename-student", "Noa Ferrer", "Noa Puig")

    assert exit_code == 0
    assert "Renamed Noa Ferrer to Noa Puig" in output
    detail = run(tmp_path, "student", "Noa Puig")[1]
    assert "8.0" in detail
    assert "Noa Ferrer" not in (tmp_path / "grades.csv").read_text()


def test_rename_to_an_existing_student_fails_and_changes_nothing(tmp_path: Path) -> None:
    make_class(tmp_path)
    students_before = (tmp_path / "students.csv").read_text()

    exit_code, output = run(tmp_path, "rename-student", "Noa Ferrer", "Leo Martin")

    assert exit_code == 1
    assert "student 'Leo Martin' already exists" in output
    assert (tmp_path / "students.csv").read_text() == students_before


def test_rename_unknown_student_fails_cleanly(tmp_path: Path) -> None:
    make_class(tmp_path)

    exit_code, output = run(tmp_path, "rename-student", "Nobody", "Somebody")

    assert exit_code == 1
    assert "unknown student 'Nobody'" in output
