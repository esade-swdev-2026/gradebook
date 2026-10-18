import pytest

from gradebook.coursework import add_assignment, find_grade, record_grade, total_weight
from gradebook.models import Assignment, Gradebook


def test_total_weight_of_no_assignments_is_zero() -> None:
    assert total_weight([]) == 0


def test_total_weight_adds_up(course_assignments: list[Assignment]) -> None:
    assert total_weight(course_assignments) == 100


def test_add_assignment_stores_name_and_weight() -> None:
    gradebook = add_assignment(Gradebook(), "  Midterm exam ", 30)
    assert gradebook.assignments == [Assignment(name="Midterm exam", weight=30)]


def test_add_assignment_can_fill_the_course_exactly() -> None:
    gradebook = add_assignment(Gradebook(), "Midterm exam", 60)
    gradebook = add_assignment(gradebook, "Final exam", 40)
    assert total_weight(gradebook.assignments) == 100


def test_add_assignment_accepts_decimal_weights_that_total_exactly_100() -> None:
    gradebook = Gradebook()
    for name, weight in [("Quiz", 0.4), ("Midterm exam", 64.4), ("Final exam", 35.2)]:
        gradebook = add_assignment(gradebook, name, weight)
    assert len(gradebook.assignments) == 3


def test_add_assignment_rejects_weights_above_what_is_left() -> None:
    gradebook = add_assignment(Gradebook(), "Midterm exam", 70)
    with pytest.raises(ValueError, match="only 30 of 100 is left"):
        add_assignment(gradebook, "Final exam", 40)


def test_add_assignment_rejects_duplicate_name(demo_gradebook: Gradebook) -> None:
    with pytest.raises(ValueError, match="assignment 'Final exam' already exists"):
        add_assignment(demo_gradebook, "Final exam", 1)


def test_add_assignment_rejects_zero_weight() -> None:
    with pytest.raises(ValueError, match="weight must be more than 0"):
        add_assignment(Gradebook(), "Quiz", 0)


def test_record_grade_adds_a_new_grade(demo_gradebook: Gradebook) -> None:
    updated = record_grade(demo_gradebook, "Leo Martin", "Final exam", 6.5)

    grade = find_grade(updated.grades, "Leo Martin", "Final exam")
    assert grade is not None
    assert grade.score == 6.5
    assert len(updated.grades) == len(demo_gradebook.grades) + 1


def test_record_grade_replaces_an_existing_grade(demo_gradebook: Gradebook) -> None:
    updated = record_grade(demo_gradebook, "Leo Martin", "Midterm exam", 7.0)

    grade = find_grade(updated.grades, "Leo Martin", "Midterm exam")
    assert grade is not None
    assert grade.score == 7.0
    assert len(updated.grades) == len(demo_gradebook.grades)


def test_record_grade_rejects_unknown_student(demo_gradebook: Gradebook) -> None:
    with pytest.raises(ValueError, match="unknown student 'Iris Soler'"):
        record_grade(demo_gradebook, "Iris Soler", "Midterm exam", 5)


def test_record_grade_rejects_unknown_assignment(demo_gradebook: Gradebook) -> None:
    with pytest.raises(ValueError, match="unknown assignment 'Quiz'"):
        record_grade(demo_gradebook, "Leo Martin", "Quiz", 5)


def test_record_grade_rejects_score_above_maximum(demo_gradebook: Gradebook) -> None:
    with pytest.raises(ValueError, match="score must be between 0 and 10"):
        record_grade(demo_gradebook, "Leo Martin", "Final exam", 10.5)


def test_find_grade_returns_none_when_missing(demo_gradebook: Gradebook) -> None:
    assert find_grade(demo_gradebook.grades, "Leo Martin", "Final exam") is None
