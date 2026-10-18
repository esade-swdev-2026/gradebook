from gradebook.coursework import find_assignment
from gradebook.models import (
    COURSE_TOTAL_WEIGHT,
    GRADE_BANDS,
    PASSING_GRADE,
    Assignment,
    AssignmentSummary,
    Grade,
    Gradebook,
    StudentStanding,
)
from gradebook.validation import WEIGHT_TOLERANCE


def grades_of_student(grades: list[Grade], student: str) -> list[Grade]:
    return [grade for grade in grades if grade.student == student]


def graded_weight(student_grades: list[Grade], assignments: list[Assignment]) -> float:
    """Percent of the course that has already been graded for this student."""
    weight = 0.0
    for grade in student_grades:
        assignment = find_assignment(assignments, grade.assignment)
        if assignment is not None:
            weight += assignment.weight
    return weight


def earned_points(student_grades: list[Grade], assignments: list[Assignment]) -> float:
    """Sum of score x weight over the graded assignments."""
    points = 0.0
    for grade in student_grades:
        assignment = find_assignment(assignments, grade.assignment)
        if assignment is not None:
            points += grade.score * assignment.weight
    return points


def current_grade(student_grades: list[Grade], assignments: list[Assignment]) -> float | None:
    """Weighted average of the work graded so far, or None if nothing is graded."""
    weight = graded_weight(student_grades, assignments)
    if weight == 0:
        return None
    return earned_points(student_grades, assignments) / weight


def needed_to_pass(student_grades: list[Grade], assignments: list[Assignment]) -> float | None:
    """Average score needed on the ungraded rest of the course to reach the passing grade.

    Returns None when the whole course is graded, 0.0 when the pass is already secured,
    and a value above MAX_SCORE when passing is no longer possible.
    """
    remaining_weight = COURSE_TOTAL_WEIGHT - graded_weight(student_grades, assignments)
    if remaining_weight <= WEIGHT_TOLERANCE:
        return None
    points_needed = PASSING_GRADE * COURSE_TOTAL_WEIGHT - earned_points(student_grades, assignments)
    return max(points_needed / remaining_weight, 0.0)


def grade_band(score: float) -> str:
    for band in GRADE_BANDS:
        if score >= band.minimum_score:
            return band.label
    raise ValueError(f"score {score:g} is below every grade band.")


def is_passing(standing: StudentStanding) -> bool:
    return standing.current_grade is not None and standing.current_grade >= PASSING_GRADE


def student_standing(gradebook: Gradebook, student: str) -> StudentStanding:
    student_grades = grades_of_student(gradebook.grades, student)
    return StudentStanding(
        student=student,
        graded_weight=graded_weight(student_grades, gradebook.assignments),
        current_grade=current_grade(student_grades, gradebook.assignments),
        needed_to_pass=needed_to_pass(student_grades, gradebook.assignments),
    )


def class_standings(gradebook: Gradebook) -> list[StudentStanding]:
    return [student_standing(gradebook, student) for student in sorted(gradebook.students)]


def class_average(standings: list[StudentStanding]) -> float | None:
    """Mean current grade of the students who have at least one grade."""
    graded = [s.current_grade for s in standings if s.current_grade is not None]
    if not graded:
        return None
    return sum(graded) / len(graded)


def passing_count(standings: list[StudentStanding]) -> int:
    return sum(1 for standing in standings if is_passing(standing))


def summarize_assignment(grades: list[Grade], assignment: Assignment) -> AssignmentSummary:
    scores = [grade.score for grade in grades if grade.assignment == assignment.name]
    average = sum(scores) / len(scores) if scores else None
    return AssignmentSummary(assignment=assignment, average_score=average, graded_count=len(scores))


def assignment_summaries(gradebook: Gradebook) -> list[AssignmentSummary]:
    return [
        summarize_assignment(gradebook.grades, assignment) for assignment in gradebook.assignments
    ]
