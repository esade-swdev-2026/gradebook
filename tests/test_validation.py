from dataclasses import replace

import pytest

from gradebook.models import Assignment, Grade, Gradebook
from gradebook.validation import (
    require_name,
    require_score,
    require_valid_gradebook,
    require_weight,
)


def test_require_name_strips_surrounding_spaces() -> None:
    assert require_name("  Noa Ferrer  ", "student") == "Noa Ferrer"


@pytest.mark.parametrize("blank", ["", "   ", "\t"])
def test_require_name_rejects_blank_names(blank: str) -> None:
    with pytest.raises(ValueError, match="student name cannot be empty"):
        require_name(blank, "student")


@pytest.mark.parametrize("score", [0.0, 5.0, 10.0])
def test_require_score_accepts_the_whole_scale_including_limits(score: float) -> None:
    assert require_score(score) == score


@pytest.mark.parametrize("score", [-0.1, 10.1, 100.0])
def test_require_score_rejects_scores_outside_the_scale(score: float) -> None:
    with pytest.raises(ValueError, match="score must be between 0 and 10"):
        require_score(score)


@pytest.mark.parametrize("weight", [0.0, -5.0, 100.5])
def test_require_weight_rejects_zero_negative_and_over_100(weight: float) -> None:
    with pytest.raises(ValueError, match="weight must be more than 0"):
        require_weight(weight)


def test_require_weight_accepts_the_whole_course() -> None:
    assert require_weight(100.0) == 100.0


NOT_FINITE = [float("nan"), float("inf"), float("-inf")]


@pytest.mark.parametrize("score", NOT_FINITE)
def test_require_score_rejects_nan_and_infinity(score: float) -> None:
    with pytest.raises(ValueError, match="score must be a finite number"):
        require_score(score)


@pytest.mark.parametrize("weight", NOT_FINITE)
def test_require_weight_rejects_nan_and_infinity(weight: float) -> None:
    with pytest.raises(ValueError, match="weight must be a finite number"):
        require_weight(weight)


# --- whole-gradebook checks, for data that did not come through a command ---


def test_valid_gradebook_passes(demo_gradebook: Gradebook) -> None:
    assert require_valid_gradebook(demo_gradebook) == demo_gradebook


@pytest.mark.parametrize(
    ("broken_grade", "message"),
    [
        (Grade("Leo Martin", "Final exam", float("nan")), "score must be a finite number"),
        (Grade("Leo Martin", "Final exam", 50.0), "score must be between 0 and 10"),
        (Grade("Iris Soler", "Final exam", 5.0), "unknown student 'Iris Soler'"),
        (Grade("Leo Martin", "Quiz", 5.0), "unknown assignment 'Quiz'"),
        (Grade("Leo Martin", "Midterm exam", 6.0), "appears more than once"),
    ],
)
def test_invalid_grades_are_rejected(
    demo_gradebook: Gradebook, broken_grade: Grade, message: str
) -> None:
    broken = replace(demo_gradebook, grades=[*demo_gradebook.grades, broken_grade])
    with pytest.raises(ValueError, match=message):
        require_valid_gradebook(broken)


def test_weights_over_100_in_total_are_rejected(demo_gradebook: Gradebook) -> None:
    broken = replace(
        demo_gradebook, assignments=[*demo_gradebook.assignments, Assignment("Quiz", 5.0)]
    )
    with pytest.raises(ValueError, match="add up to 105"):
        require_valid_gradebook(broken)


def test_nan_weight_is_rejected() -> None:
    with pytest.raises(ValueError, match="weight must be a finite number"):
        require_valid_gradebook(Gradebook(assignments=[Assignment("Quiz", float("nan"))]))


def test_duplicate_students_are_rejected() -> None:
    with pytest.raises(ValueError, match="student 'Noa Ferrer' appears more than once"):
        require_valid_gradebook(Gradebook(students=["Noa Ferrer", "Noa Ferrer"]))


def test_decimal_weights_totalling_exactly_100_are_valid() -> None:
    assignments = [Assignment("Quiz", 0.4), Assignment("Midterm", 64.4), Assignment("Final", 35.2)]
    gradebook = Gradebook(assignments=assignments)
    assert require_valid_gradebook(gradebook) == gradebook
