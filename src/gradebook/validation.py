import math

from gradebook.models import COURSE_TOTAL_WEIGHT, MAX_SCORE, MIN_SCORE, Gradebook


def require_name(raw_name: str, kind: str) -> str:
    """Return the name without surrounding spaces, or raise if nothing is left."""
    name = raw_name.strip()
    if not name:
        raise ValueError(f"{kind} name cannot be empty.")
    return name


# Weights like 0.4 + 64.4 + 35.2 add up to 100.00000000000001 in floating point.
WEIGHT_TOLERANCE = 1e-9


def exceeds_course_weight(total_weight: float) -> bool:
    return total_weight > COURSE_TOTAL_WEIGHT + WEIGHT_TOLERANCE


def require_finite(value: float, kind: str) -> float:
    # NaN fails every comparison, so range checks alone are easy to get wrong.
    if not math.isfinite(value):
        raise ValueError(f"{kind} must be a finite number, got {value}.")
    return value


def require_score(score: float) -> float:
    require_finite(score, "score")
    if not MIN_SCORE <= score <= MAX_SCORE:
        raise ValueError(f"score must be between {MIN_SCORE:g} and {MAX_SCORE:g}, got {score:g}.")
    return score


def require_weight(weight: float) -> float:
    require_finite(weight, "weight")
    if not 0 < weight <= COURSE_TOTAL_WEIGHT:
        raise ValueError(
            f"weight must be more than 0 and at most {COURSE_TOTAL_WEIGHT:g}, got {weight:g}."
        )
    return weight


def require_valid_gradebook(gradebook: Gradebook) -> Gradebook:
    """Apply the command rules to a whole gradebook, e.g. one read from hand-edited files."""
    _require_valid_students(gradebook.students)
    _require_valid_assignments(gradebook)
    _require_valid_grades(gradebook)
    return gradebook


def _require_valid_students(students: list[str]) -> None:
    for student in students:
        require_name(student, "student")
    _require_no_duplicates(students, "student")


def _require_valid_assignments(gradebook: Gradebook) -> None:
    for assignment in gradebook.assignments:
        require_name(assignment.name, "assignment")
        require_weight(assignment.weight)
    _require_no_duplicates([assignment.name for assignment in gradebook.assignments], "assignment")

    total = sum(assignment.weight for assignment in gradebook.assignments)
    if exceeds_course_weight(total):
        raise ValueError(
            f"assignment weights add up to {total:g}, more than {COURSE_TOTAL_WEIGHT:g}."
        )


def _require_valid_grades(gradebook: Gradebook) -> None:
    assignment_names = {assignment.name for assignment in gradebook.assignments}
    for grade in gradebook.grades:
        require_score(grade.score)
        if grade.student not in gradebook.students:
            raise ValueError(f"a grade belongs to unknown student '{grade.student}'.")
        if grade.assignment not in assignment_names:
            raise ValueError(f"a grade belongs to unknown assignment '{grade.assignment}'.")
    _require_no_duplicates(
        [f"{grade.student} / {grade.assignment}" for grade in gradebook.grades], "grade for"
    )


def _require_no_duplicates(names: list[str], kind: str) -> None:
    seen: set[str] = set()
    for name in names:
        if name in seen:
            raise ValueError(f"{kind} '{name}' appears more than once.")
        seen.add(name)
