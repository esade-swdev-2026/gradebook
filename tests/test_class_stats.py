from dataclasses import replace

import pytest

from gradebook.class_stats import ScoreRange, band_distribution, score_ranges
from gradebook.grading import class_standings
from gradebook.models import Grade, Gradebook, StudentStanding


def ranges_by_name(gradebook: Gradebook) -> dict[str, ScoreRange]:
    return {score_range.assignment: score_range for score_range in score_ranges(gradebook)}


def test_highest_and_lowest_per_assignment(demo_gradebook: Gradebook) -> None:
    midterm = ranges_by_name(demo_gradebook)["Midterm exam"]
    assert midterm.highest == 8.0
    assert midterm.lowest == 4.0


def test_assignment_nobody_has_done_has_no_range(demo_gradebook: Gradebook) -> None:
    final_exam = ranges_by_name(demo_gradebook)["Final exam"]
    assert final_exam.highest is None
    assert final_exam.lowest is None
    assert final_exam.median_score is None


def test_one_range_per_assignment_in_course_order(demo_gradebook: Gradebook) -> None:
    names = [score_range.assignment for score_range in score_ranges(demo_gradebook)]
    assert names == ["Midterm exam", "Group project", "Final exam"]


def test_median_of_an_even_count_is_the_middle_two_averaged(demo_gradebook: Gradebook) -> None:
    # Midterm: Noa 8.0, Leo 4.0
    assert ranges_by_name(demo_gradebook)["Midterm exam"].median_score == pytest.approx(6.0)


def test_median_is_not_pulled_by_one_outlier(demo_gradebook: Gradebook) -> None:
    gradebook = replace(
        demo_gradebook,
        students=[*demo_gradebook.students, "Iris Soler"],
        grades=[*demo_gradebook.grades, Grade("Iris Soler", "Midterm exam", 0.5)],
    )
    # scores 0.5, 4.0, 8.0: the average is 4.2, the median stays 4.0
    assert ranges_by_name(gradebook)["Midterm exam"].median_score == pytest.approx(4.0)


def test_band_distribution_counts_students_per_band(demo_gradebook: Gradebook) -> None:
    # Noa 8.0 (Very good), Leo 4.0 (Fail)
    assert band_distribution(class_standings(demo_gradebook)) == {
        "Excellent": 0,
        "Very good": 1,
        "Pass": 0,
        "Fail": 1,
    }


def test_band_distribution_lists_the_best_band_first() -> None:
    assert list(band_distribution([])) == ["Excellent", "Very good", "Pass", "Fail"]


def test_students_without_grades_are_in_no_band() -> None:
    ungraded = StudentStanding("Iris Soler", graded_weight=0, current_grade=None, needed_to_pass=5)
    assert sum(band_distribution([ungraded]).values()) == 0


def test_exactly_the_passing_grade_is_in_pass() -> None:
    passing = StudentStanding(
        "Noa Ferrer", graded_weight=100, current_grade=5.0, needed_to_pass=None
    )
    assert band_distribution([passing])["Pass"] == 1
