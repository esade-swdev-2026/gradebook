"""Reading and writing the gradebook's CSV files. The only module that touches the disk."""

from pathlib import Path

import pandas as pd

from gradebook.models import Assignment, Grade, Gradebook
from gradebook.validation import require_valid_gradebook

STUDENTS_FILE = "students.csv"
ASSIGNMENTS_FILE = "assignments.csv"
GRADES_FILE = "grades.csv"

STUDENT_COLUMNS = ["name"]
ASSIGNMENT_COLUMNS = ["name", "weight"]
GRADE_COLUMNS = ["student", "assignment", "score"]


def load_gradebook(data_dir: Path) -> Gradebook:
    """Read and check the three CSV files. Missing files count as empty, so a new class works."""
    gradebook = _parse_gradebook(data_dir)
    try:
        return require_valid_gradebook(gradebook)
    except ValueError as error:
        raise ValueError(f"the class in {data_dir} has invalid data: {error}") from error


def _parse_gradebook(data_dir: Path) -> Gradebook:
    students = _read_table(data_dir / STUDENTS_FILE, STUDENT_COLUMNS)
    assignments = _read_table(data_dir / ASSIGNMENTS_FILE, ASSIGNMENT_COLUMNS)
    grades = _read_table(data_dir / GRADES_FILE, GRADE_COLUMNS)
    return Gradebook(
        students=[str(name) for name in students["name"].tolist()],
        assignments=[
            Assignment(name=str(name), weight=_parse_number(weight, data_dir / ASSIGNMENTS_FILE))
            for name, weight in zip(
                assignments["name"].tolist(), assignments["weight"].tolist(), strict=True
            )
        ],
        grades=[
            Grade(
                student=str(student),
                assignment=str(assignment),
                score=_parse_number(score, data_dir / GRADES_FILE),
            )
            for student, assignment, score in zip(
                grades["student"].tolist(),
                grades["assignment"].tolist(),
                grades["score"].tolist(),
                strict=True,
            )
        ],
    )


def save_gradebook(data_dir: Path, gradebook: Gradebook) -> None:
    data_dir.mkdir(parents=True, exist_ok=True)
    pd.DataFrame({"name": gradebook.students}, columns=STUDENT_COLUMNS).to_csv(
        data_dir / STUDENTS_FILE, index=False
    )
    pd.DataFrame(
        {
            "name": [assignment.name for assignment in gradebook.assignments],
            "weight": [assignment.weight for assignment in gradebook.assignments],
        },
        columns=ASSIGNMENT_COLUMNS,
    ).to_csv(data_dir / ASSIGNMENTS_FILE, index=False)
    pd.DataFrame(
        {
            "student": [grade.student for grade in gradebook.grades],
            "assignment": [grade.assignment for grade in gradebook.grades],
            "score": [grade.score for grade in gradebook.grades],
        },
        columns=GRADE_COLUMNS,
    ).to_csv(data_dir / GRADES_FILE, index=False)


def _read_table(path: Path, required_columns: list[str]) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame(columns=required_columns, dtype=str)
    try:
        table = pd.read_csv(path, dtype=str, keep_default_na=False)
    except pd.errors.EmptyDataError as error:
        raise ValueError(f"{path} is empty; expected columns {required_columns}.") from error

    missing_columns = [column for column in required_columns if column not in table.columns]
    if missing_columns:
        raise ValueError(f"{path} is missing the column(s) {missing_columns}.")
    return table


def _parse_number(raw_value: object, path: Path) -> float:
    try:
        return float(str(raw_value))
    except ValueError as error:
        raise ValueError(f"{path} contains '{raw_value}', which is not a number.") from error
