from pathlib import Path

from typer.testing import CliRunner

from gradebook.cli import app

runner = CliRunner()


def run(data_dir: Path, *args: str) -> tuple[int, str]:
    result = runner.invoke(app, [*args, "--data-dir", str(data_dir)])
    return result.exit_code, result.output


def test_full_workflow_ends_in_a_report(tmp_path: Path) -> None:
    assert run(tmp_path, "add-student", "Noa Ferrer")[0] == 0
    assert run(tmp_path, "add-assignment", "Midterm exam", "40")[0] == 0
    assert run(tmp_path, "add-assignment", "Final exam", "60")[0] == 0

    exit_code, output = run(tmp_path, "record-grade", "Noa Ferrer", "Midterm exam", "2.5")
    assert exit_code == 0
    assert "Current grade: 2.5 (Fail)" in output

    exit_code, output = run(tmp_path, "report")
    assert exit_code == 0
    # needs (500 - 2.5 * 40) / 60 = 6.67 on the final exam
    assert "6.7" in output


def test_add_student_rejects_empty_name(tmp_path: Path) -> None:
    exit_code, output = run(tmp_path, "add-student", "   ")
    assert exit_code == 1
    assert "student name cannot be empty" in output


def test_record_grade_for_unknown_student_fails_cleanly(tmp_path: Path) -> None:
    exit_code, output = run(tmp_path, "record-grade", "Nobody", "Quiz", "5")
    assert exit_code == 1
    assert "unknown student 'Nobody'" in output


def test_corrupt_file_gives_a_message_not_a_traceback(tmp_path: Path) -> None:
    (tmp_path / "grades.csv").write_text("student,assignment,score\nNoa Ferrer,Quiz,ten\n")
    exit_code, output = run(tmp_path, "report")
    assert exit_code == 1
    assert "not a number" in output


def test_nan_in_a_hand_edited_file_gives_a_message_not_a_traceback(tmp_path: Path) -> None:
    (tmp_path / "students.csv").write_text("name\nNoa Ferrer\n")
    (tmp_path / "assignments.csv").write_text("name,weight\nQuiz,10\n")
    (tmp_path / "grades.csv").write_text("student,assignment,score\nNoa Ferrer,Quiz,nan\n")

    exit_code, output = run(tmp_path, "report")

    assert exit_code == 1
    assert "score must be a finite number" in output


def test_nan_typed_on_the_command_line_is_rejected(tmp_path: Path) -> None:
    run(tmp_path, "add-student", "Noa Ferrer")
    run(tmp_path, "add-assignment", "Quiz", "10")

    exit_code, output = run(tmp_path, "record-grade", "Noa Ferrer", "Quiz", "nan")

    assert exit_code == 1
    assert "score must be a finite number" in output
