import pytest

from gradebook.models import StudentStanding
from gradebook.ranking import rank_students, top_students


def standing(student: str, grade: float | None) -> StudentStanding:
    weight = 0.0 if grade is None else 30.0
    return StudentStanding(student, graded_weight=weight, current_grade=grade, needed_to_pass=5.0)


def test_best_grade_comes_first() -> None:
    ranked = rank_students([standing("Leo Martin", 4.8), standing("Noa Ferrer", 8.8)])
    assert [r.student for r in ranked] == ["Noa Ferrer", "Leo Martin"]
    assert [r.position for r in ranked] == [1, 2]


def test_students_without_grades_are_left_out() -> None:
    ranked = rank_students([standing("Noa Ferrer", 8.8), standing("Iris Soler", None)])
    assert [r.student for r in ranked] == ["Noa Ferrer"]


def test_ties_share_a_position_and_skip_the_next() -> None:
    ranked = rank_students(
        [
            standing("Noa Ferrer", 9.0),
            standing("Leo Martin", 7.0),
            standing("Hugo Navarro", 7.0),
            standing("Iris Soler", 2.0),
        ]
    )
    assert [(r.position, r.student) for r in ranked] == [
        (1, "Noa Ferrer"),
        (2, "Hugo Navarro"),
        (2, "Leo Martin"),
        (4, "Iris Soler"),
    ]


def test_floating_point_noise_still_counts_as_a_tie() -> None:
    # 0.1 + 0.2 is 0.30000000000000004 in floating point
    ranked = rank_students([standing("Noa Ferrer", 0.1 + 0.2), standing("Leo Martin", 0.3)])
    assert [r.position for r in ranked] == [1, 1]


def test_empty_class_has_an_empty_ranking() -> None:
    assert rank_students([]) == []


def test_top_students_takes_the_first_positions() -> None:
    standings = [
        standing("Noa Ferrer", 9.0),
        standing("Leo Martin", 7.0),
        standing("Iris Soler", 2.0),
    ]
    assert [r.student for r in top_students(standings, 2)] == ["Noa Ferrer", "Leo Martin"]


def test_top_students_keeps_a_tie_on_the_last_place() -> None:
    standings = [
        standing("Noa Ferrer", 9.0),
        standing("Leo Martin", 7.0),
        standing("Hugo Navarro", 7.0),
    ]
    assert len(top_students(standings, 2)) == 3


def test_top_students_with_more_than_the_class_returns_everyone() -> None:
    assert len(top_students([standing("Noa Ferrer", 9.0)], 5)) == 1


def test_top_students_rejects_a_count_below_one() -> None:
    with pytest.raises(ValueError, match="at least 1"):
        top_students([standing("Noa Ferrer", 9.0)], 0)
