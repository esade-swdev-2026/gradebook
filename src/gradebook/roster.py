from dataclasses import replace

from gradebook.models import Gradebook
from gradebook.validation import require_name


def student_exists(gradebook: Gradebook, name: str) -> bool:
    return name in gradebook.students


def add_student(gradebook: Gradebook, raw_name: str) -> Gradebook:
    name = require_name(raw_name, "student")
    if student_exists(gradebook, name):
        raise ValueError(f"student '{name}' already exists.")
    return replace(gradebook, students=[*gradebook.students, name])


def remove_student(gradebook: Gradebook, raw_name: str) -> Gradebook:
    """Remove the student and every grade recorded for them."""
    name = require_name(raw_name, "student")
    if not student_exists(gradebook, name):
        raise ValueError(f"unknown student '{name}'.")
    return replace(
        gradebook,
        students=[student for student in gradebook.students if student != name],
        grades=[grade for grade in gradebook.grades if grade.student != name],
    )
