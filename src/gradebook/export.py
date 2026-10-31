"""The class report as rows of plain values, ready to be written out as a spreadsheet."""

from gradebook.grading import class_standings, grade_band
from gradebook.models import Gradebook

EXPORT_COLUMNS = ["student", "graded_percent", "current_grade", "band", "needed_to_pass"]


def _number(value: float | None) -> str:
    """Two decimals, or an empty cell when there is no value."""
    return "" if value is None else f"{value:.2f}"


def export_rows(gradebook: Gradebook) -> list[dict[str, str]]:
    """One row per student, sorted by name, with the same numbers as the report.

    `needed_to_pass` is the plain number: 0.00 means the pass is secured, above 10
    means it is out of reach, and an empty cell means the course is fully graded.
    """
    rows: list[dict[str, str]] = []
    for standing in class_standings(gradebook):
        grade = standing.current_grade
        rows.append(
            {
                "student": standing.student,
                "graded_percent": f"{standing.graded_weight:g}",
                "current_grade": _number(grade),
                "band": "" if grade is None else grade_band(grade),
                "needed_to_pass": _number(standing.needed_to_pass),
            }
        )
    return rows
