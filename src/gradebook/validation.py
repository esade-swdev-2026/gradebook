import math

from gradebook.models import COURSE_TOTAL_WEIGHT, MAX_SCORE, MIN_SCORE, Gradebook


def clean_name(raw_name: str) -> str:
    """The name without spaces around it, and with every run of spaces inside made one."""
    return " ".join(raw_name.split())


def require_name(raw_name: str, kind: str) -> str:
    """Return the cleaned name, or raise if nothing is left."""
    name = clean_name(raw_name)
    if not name:
        raise ValueError(f"{kind} name cannot be empty.")
    return name


def same_name(first: str, second: str) -> bool:
    """Two names are the same if they differ only in capitals or spaces: a typo, not a person."""
    return clean_name(first).casefold() == clean_name(second).casefold()


def find_same_name(names: list[str], name: str) -> str | None:
    """The name already in `names` that is the same as `name`, if there is one."""
    for existing in names:
        if same_name(existing, name):
            return existing
    return None


def already_exists(kind: str, name: str, existing: str) -> str:
    if existing == name:
        return f"{kind} '{name}' already exists."
    return f"{kind} '{name}' already exists as '{existing}'."


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
    for index, name in enumerate(names):
        earlier = find_same_name(names[:index], name)
        if earlier is None:
            continue
        if earlier == name:
            raise ValueError(f"{kind} '{name}' appears more than once.")
        raise ValueError(f"{kind} '{name}' and '{earlier}' are the same name.")
