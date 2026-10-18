from dataclasses import replace

from gradebook.models import COURSE_TOTAL_WEIGHT, Assignment, Grade, Gradebook
from gradebook.roster import student_exists
from gradebook.validation import (
    exceeds_course_weight,
    require_name,
    require_score,
    require_weight,
)


def total_weight(assignments: list[Assignment]) -> float:
    return sum(assignment.weight for assignment in assignments)


def find_assignment(assignments: list[Assignment], name: str) -> Assignment | None:
    for assignment in assignments:
        if assignment.name == name:
            return assignment
    return None


def find_grade(grades: list[Grade], student: str, assignment: str) -> Grade | None:
    for grade in grades:
        if grade.student == student and grade.assignment == assignment:
            return grade
    return None


def add_assignment(gradebook: Gradebook, raw_name: str, weight: float) -> Gradebook:
    name = require_name(raw_name, "assignment")
    require_weight(weight)
    if find_assignment(gradebook.assignments, name) is not None:
        raise ValueError(f"assignment '{name}' already exists.")

    if exceeds_course_weight(total_weight(gradebook.assignments) + weight):
        weight_left = COURSE_TOTAL_WEIGHT - total_weight(gradebook.assignments)
        raise ValueError(
            f"weight {weight:g} is too much: only {weight_left:g} of "
            f"{COURSE_TOTAL_WEIGHT:g} is left to assign."
        )

    new_assignment = Assignment(name=name, weight=weight)
    return replace(gradebook, assignments=[*gradebook.assignments, new_assignment])


def record_grade(
    gradebook: Gradebook, raw_student: str, raw_assignment: str, score: float
) -> Gradebook:
    """Set a student's score for an assignment, replacing any earlier score."""
    student = require_name(raw_student, "student")
    assignment = require_name(raw_assignment, "assignment")
    require_score(score)
    if not student_exists(gradebook, student):
        raise ValueError(f"unknown student '{student}'. Add them first with add-student.")
    if find_assignment(gradebook.assignments, assignment) is None:
        raise ValueError(f"unknown assignment '{assignment}'. Add it first with add-assignment.")

    other_grades = [
        grade
        for grade in gradebook.grades
        if not (grade.student == student and grade.assignment == assignment)
    ]
    new_grade = Grade(student=student, assignment=assignment, score=score)
    return replace(gradebook, grades=[*other_grades, new_grade])
