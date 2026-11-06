from pathlib import Path
from typing import Annotated, NoReturn

import typer

from gradebook.coursework import add_assignment, find_grade, record_grade
from gradebook.grading import student_standing
from gradebook.models import Gradebook
from gradebook.report import format_grade_confirmation, format_report
from gradebook.roster import add_student, remove_student
from gradebook.storage import load_gradebook, save_gradebook, save_report_csv
from gradebook.student_report import format_student_detail

app = typer.Typer(help="A terminal gradebook for one class.")

DEFAULT_DATA_DIR = Path("gradebook-data")

DataDir = Annotated[
    Path,
    typer.Option("--data-dir", help="Folder holding students.csv, assignments.csv, grades.csv."),
]


@app.callback()
def main() -> None:
    """Manage students, weighted assignments and grades for your class."""


@app.command("add-student")
def add_student_command(name: str, data_dir: DataDir = DEFAULT_DATA_DIR) -> None:
    """Add a student to the class."""
    gradebook = _load(data_dir)
    try:
        updated = add_student(gradebook, name)
    except ValueError as error:
        _fail(error)
    _save(data_dir, updated)
    typer.echo(f"Added {updated.students[-1]} to {data_dir}")


@app.command("remove-student")
def remove_student_command(name: str, data_dir: DataDir = DEFAULT_DATA_DIR) -> None:
    """Remove a student and all of their grades."""
    gradebook = _load(data_dir)
    try:
        updated = remove_student(gradebook, name)
    except ValueError as error:
        _fail(error)
    _save(data_dir, updated)
    typer.echo(f"Removed {name.strip()} and their grades from {data_dir}")


@app.command("add-assignment")
def add_assignment_command(
    name: str,
    weight: Annotated[float, typer.Argument(help="Percent of the final grade, e.g. 30.")],
    data_dir: DataDir = DEFAULT_DATA_DIR,
) -> None:
    """Add an assignment worth WEIGHT percent of the final grade."""
    gradebook = _load(data_dir)
    try:
        updated = add_assignment(gradebook, name, weight)
    except ValueError as error:
        _fail(error)
    _save(data_dir, updated)
    added = updated.assignments[-1]
    typer.echo(f"Added {added.name} ({added.weight:g}% of the final grade)")


@app.command("record-grade")
def record_grade_command(
    student: str,
    assignment: str,
    score: Annotated[float, typer.Argument(help="Score from 0 to 10.")],
    data_dir: DataDir = DEFAULT_DATA_DIR,
) -> None:
    """Record a student's score for an assignment, or update it if one exists."""
    gradebook = _load(data_dir)
    try:
        updated = record_grade(gradebook, student, assignment, score)
    except ValueError as error:
        _fail(error)
    _save(data_dir, updated)

    recorded = updated.grades[-1]
    previous = find_grade(gradebook.grades, recorded.student, recorded.assignment)
    standing = student_standing(updated, recorded.student)
    for line in format_grade_confirmation(recorded, standing, is_update=previous is not None):
        typer.echo(line)


@app.command("report")
def report_command(data_dir: DataDir = DEFAULT_DATA_DIR) -> None:
    """Show every student's current grade, what they need to pass, and class statistics."""
    for line in format_report(_load(data_dir)):
        typer.echo(line)


@app.command("export")
def export_command(
    path: Annotated[Path, typer.Argument(help="CSV file to write, e.g. report.csv.")],
    data_dir: DataDir = DEFAULT_DATA_DIR,
) -> None:
    """Write the class report to a CSV file, for opening in a spreadsheet."""
    gradebook = _load(data_dir)
    try:
        save_report_csv(path, gradebook)
    except OSError as error:
        _fail(error)
    typer.echo(f"Exported {len(gradebook.students)} students to {path}")


@app.command("student")
def student_command(name: str, data_dir: DataDir = DEFAULT_DATA_DIR) -> None:
    """Show one student's score on every assignment, current grade and what they need."""
    gradebook = _load(data_dir)
    try:
        lines = format_student_detail(gradebook, name)
    except ValueError as error:
        _fail(error)
    for line in lines:
        typer.echo(line)


def _load(data_dir: Path) -> Gradebook:
    try:
        return load_gradebook(data_dir)
    except (OSError, ValueError) as error:
        _fail(error)


def _save(data_dir: Path, gradebook: Gradebook) -> None:
    try:
        save_gradebook(data_dir, gradebook)
    except OSError as error:
        _fail(error)


def _fail(error: Exception) -> NoReturn:
    typer.echo(f"Error: {error}", err=True)
    raise typer.Exit(code=1) from error


if __name__ == "__main__":
    app()
