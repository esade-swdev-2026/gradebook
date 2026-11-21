from dataclasses import replace

from gradebook.models import Gradebook
from gradebook.validation import already_exists, find_same_name, require_name


def student_exists(gradebook: Gradebook, name: str) -> bool:
    return name in gradebook.students


def add_student(gradebook: Gradebook, raw_name: str) -> Gradebook:
    name = require_name(raw_name, "student")
    existing = find_same_name(gradebook.students, name)
    if existing is not None:
        raise ValueError(already_exists("student", name, existing))
    return replace(gradebook, students=[*gradebook.students, name])


def rename_student(gradebook: Gradebook, raw_old_name: str, raw_new_name: str) -> Gradebook:
    """Give a student a new name, keeping their place in the class and all their grades."""
    old_name = require_name(raw_old_name, "student")
    new_name = require_name(raw_new_name, "new student")
    if not student_exists(gradebook, old_name):
        raise ValueError(f"unknown student '{old_name}'.")
    if new_name == old_name:
        raise ValueError(f"student '{old_name}' already has that name.")
    # Fixing the capitals of a name ("noa ferrer" -> "Noa Ferrer") is allowed.
    other_students = [student for student in gradebook.students if student != old_name]
    existing = find_same_name(other_students, new_name)
    if existing is not None:
        raise ValueError(already_exists("student", new_name, existing))
    return replace(
        gradebook,
        students=[new_name if student == old_name else student for student in gradebook.students],
        grades=[
            replace(grade, student=new_name) if grade.student == old_name else grade
            for grade in gradebook.grades
        ],
    )


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
