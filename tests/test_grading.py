import pytest

from gradebook.grading import (
    assignment_summaries,
    class_average,
    class_standings,
    current_grade,
    grade_band,
    graded_weight,
    grades_of_student,
    needed_to_pass,
    passing_count,
    student_standing,
)
from gradebook.models import Assignment, Grade, Gradebook, StudentStanding


def grades_for(scores: dict[str, float]) -> list[Grade]:
    return [
        Grade(student="Noa Ferrer", assignment=assignment, score=score)
        for assignment, score in scores.items()
    ]


# --- weighted average -------------------------------------------------------


def test_current_grade_is_weighted_not_a_plain_average() -> None:
    assignments = [Assignment("Quiz", 10.0), Assignment("Final exam", 90.0)]
    grades = grades_for({"Quiz": 10.0, "Final exam": 5.0})
    # plain average would be 7.5; weighted is (10*10 + 5*90) / 100
    assert current_grade(grades, assignments) == pytest.approx(5.5)


def test_current_grade_only_counts_graded_work(course_assignments: list[Assignment]) -> None:
    grades = grades_for({"Midterm exam": 8.0, "Group project": 9.0})
    assert current_grade(grades, course_assignments) == pytest.approx(8.5)


def test_current_grade_with_no_grades_is_none(course_assignments: list[Assignment]) -> None:
    assert current_grade([], course_assignments) is None


def test_grades_for_unknown_assignments_are_ignored(
    course_assignments: list[Assignment],
) -> None:
    grades = grades_for({"Midterm exam": 6.0, "Deleted quiz": 0.0})
    assert graded_weight(grades, course_assignments) == 30
    assert current_grade(grades, course_assignments) == pytest.approx(6.0)


# --- forecast: what is needed to pass ---------------------------------------


def test_needed_to_pass_on_the_remaining_weight(course_assignments: list[Assignment]) -> None:
    grades = grades_for({"Midterm exam": 4.0})
    # needs 5.0 * 100 = 500 points; has 4 * 30 = 120; 380 left over 70 % of the course
    assert needed_to_pass(grades, course_assignments) == pytest.approx(380 / 70)


def test_needed_to_pass_with_nothing_graded_is_the_passing_grade(
    course_assignments: list[Assignment],
) -> None:
    assert needed_to_pass([], course_assignments) == pytest.approx(5.0)


def test_needed_to_pass_is_zero_once_the_pass_is_secured(
    course_assignments: list[Assignment],
) -> None:
    grades = grades_for({"Midterm exam": 10.0, "Group project": 10.0})
    assert needed_to_pass(grades, course_assignments) == 0.0


def test_needed_to_pass_above_ten_means_out_of_reach(
    course_assignments: list[Assignment],
) -> None:
    grades = grades_for({"Midterm exam": 0.0, "Group project": 0.0})
    assert needed_to_pass(grades, course_assignments) == pytest.approx(12.5)


def test_needed_to_pass_is_none_when_the_course_is_fully_graded(
    course_assignments: list[Assignment],
) -> None:
    grades = grades_for({"Midterm exam": 5.0, "Group project": 5.0, "Final exam": 5.0})
    assert needed_to_pass(grades, course_assignments) is None


def test_needed_to_pass_is_none_when_decimal_weights_are_fully_graded() -> None:
    # 33.4 + 33.3 + 33.3 is 99.99999999999999 in floating point, not 100
    assignments = [Assignment("A", 33.4), Assignment("B", 33.3), Assignment("C", 33.3)]
    grades = grades_for({"A": 4.0, "B": 4.0, "C": 4.0})
    assert needed_to_pass(grades, assignments) is None


def test_needed_to_pass_counts_assignments_not_yet_created() -> None:
    assignments = [Assignment("Midterm exam", 50.0)]
    grades = grades_for({"Midterm exam": 4.0})
    # the other 50 % of the course still exists, even if not entered yet
    assert needed_to_pass(grades, assignments) == pytest.approx(6.0)


# --- grade boundaries -------------------------------------------------------


@pytest.mark.parametrize(
    ("score", "band"),
    [
        (0.0, "Fail"),
        (4.99, "Fail"),
        (5.0, "Pass"),
        (6.99, "Pass"),
        (7.0, "Very good"),
        (8.99, "Very good"),
        (9.0, "Excellent"),
        (10.0, "Excellent"),
    ],
)
def test_grade_band_boundaries(score: float, band: str) -> None:
    assert grade_band(score) == band


def test_grade_band_rejects_negative_scores() -> None:
    with pytest.raises(ValueError, match="below every grade band"):
        grade_band(-1.0)


# --- class statistics -------------------------------------------------------


def test_grades_of_student_filters_by_name(demo_gradebook: Gradebook) -> None:
    grades = grades_of_student(demo_gradebook.grades, "Leo Martin")
    assert [grade.assignment for grade in grades] == ["Midterm exam"]


def test_student_standing(demo_gradebook: Gradebook) -> None:
    standing = student_standing(demo_gradebook, "Noa Ferrer")
    assert standing.graded_weight == 60
    assert standing.current_grade == pytest.approx(8.0)
    # has 8 * 60 = 480 of the 500 points needed; 20 points over the last 40 %
    assert standing.needed_to_pass == pytest.approx(0.5)


def test_class_standings_are_sorted_by_name(demo_gradebook: Gradebook) -> None:
    names = [standing.student for standing in class_standings(demo_gradebook)]
    assert names == ["Leo Martin", "Noa Ferrer"]


def test_class_average_skips_students_without_grades() -> None:
    standings = [
        StudentStanding("Noa Ferrer", graded_weight=30, current_grade=8.0, needed_to_pass=0),
        StudentStanding("Leo Martin", graded_weight=30, current_grade=4.0, needed_to_pass=5.4),
        StudentStanding("Iris Soler", graded_weight=0, current_grade=None, needed_to_pass=5.0),
    ]
    assert class_average(standings) == pytest.approx(6.0)
    assert passing_count(standings) == 1


def test_class_average_of_ungraded_class_is_none() -> None:
    assert class_average([]) is None


def test_exactly_the_passing_grade_counts_as_passing() -> None:
    standing = StudentStanding(
        "Noa Ferrer", graded_weight=100, current_grade=5.0, needed_to_pass=None
    )
    assert passing_count([standing]) == 1


def test_assignment_summaries(demo_gradebook: Gradebook) -> None:
    summaries = {s.assignment.name: s for s in assignment_summaries(demo_gradebook)}

    assert summaries["Midterm exam"].average_score == pytest.approx(6.0)
    assert summaries["Midterm exam"].graded_count == 2
    assert summaries["Final exam"].average_score is None
    assert summaries["Final exam"].graded_count == 0
