"""One student's detail view: every assignment, their score on it, and where they stand."""

from gradebook.coursework import find_grade
from gradebook.grading import grade_band, student_standing
from gradebook.models import Gradebook
from gradebook.report import (
    NAME_WIDTH,
    NUMBER_WIDTH,
    RULE_WIDTH,
    format_needed_to_pass,
    format_score,
)
from gradebook.roster import student_exists
from gradebook.validation import require_name


def format_student_detail(gradebook: Gradebook, raw_name: str) -> list[str]:
    name = require_name(raw_name, "student")
    if not student_exists(gradebook, name):
        raise ValueError(f"unknown student '{name}'. Add them first with add-student.")

    lines = [name, ""]
    if gradebook.assignments:
        lines.extend(
            [
                f"{'Assignment':<{NAME_WIDTH}}{'Weight':>{NUMBER_WIDTH}}{'Score':>{NUMBER_WIDTH}}",
                "-" * RULE_WIDTH,
            ]
        )
        for assignment in gradebook.assignments:
            grade = find_grade(gradebook.grades, name, assignment.name)
            score = None if grade is None else grade.score
            lines.append(
                f"{assignment.name:<{NAME_WIDTH}}"
                f"{assignment.weight:>{NUMBER_WIDTH - 1}.0f}%"
                f"{format_score(score):>{NUMBER_WIDTH}}"
            )
    else:
        lines.append("No assignments yet. Add one with: gradebook add-assignment NAME WEIGHT")

    standing = student_standing(gradebook, name)
    band = "" if standing.current_grade is None else f" ({grade_band(standing.current_grade)})"
    lines.extend(
        [
            "",
            f"Current grade: {format_score(standing.current_grade)}{band}    "
            f"Graded: {standing.graded_weight:g}% of the course",
            f"Needs on the rest to pass: {format_needed_to_pass(standing.needed_to_pass)}",
        ]
    )
    return lines
