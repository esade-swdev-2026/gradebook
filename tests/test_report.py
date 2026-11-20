from gradebook.class_stats import ScoreRange
from gradebook.models import Grade, Gradebook, StudentStanding
from gradebook.report import (
    PASS_OUT_OF_REACH,
    PASS_SECURED,
    format_band_counts,
    format_grade_confirmation,
    format_needed_to_pass,
    format_report,
    format_score,
    format_score_range_row,
)


def test_format_score_rounds_to_one_decimal() -> None:
    assert format_score(4.75) == "4.8"


def test_format_score_of_missing_grade_is_a_dash() -> None:
    assert format_score(None) == "-"


def test_format_needed_to_pass_cases() -> None:
    assert format_needed_to_pass(None) == "-"
    assert format_needed_to_pass(0.0) == PASS_SECURED
    assert format_needed_to_pass(12.5) == PASS_OUT_OF_REACH
    assert format_needed_to_pass(5.43) == "5.4"


def test_report_for_empty_class_explains_what_to_do() -> None:
    assert format_report(Gradebook()) == [
        "No students yet. Add one with: gradebook add-student NAME"
    ]


def test_report_has_a_row_per_student_and_a_class_summary(demo_gradebook: Gradebook) -> None:
    report = "\n".join(format_report(demo_gradebook))

    assert "Noa Ferrer" in report
    assert "Leo Martin" in report
    assert "Very good" in report
    assert "Class average: 6.0" in report  # (8.0 + 4.0) / 2
    assert "Passing right now: 1/2" in report


def test_grade_confirmation_says_updated_for_an_existing_grade() -> None:
    grade = Grade(student="Leo Martin", assignment="Midterm exam", score=6.0)
    standing = StudentStanding(
        "Leo Martin", graded_weight=30, current_grade=6.0, needed_to_pass=4.6
    )

    lines = format_grade_confirmation(grade, standing, is_update=True)

    assert lines == [
        "Updated 6 for Leo Martin on Midterm exam.",
        "Current grade: 6.0 (Pass)",
    ]


def test_score_range_row_shows_lowest_median_and_highest() -> None:
    row = format_score_range_row(
        ScoreRange(assignment="Midterm exam", highest=8.5, lowest=1.0, median_score=5.0)
    )

    assert row.startswith("Midterm exam")
    assert row.split()[-3:] == ["1.0", "5.0", "8.5"]


def test_score_range_row_of_an_ungraded_assignment_shows_dashes() -> None:
    row = format_score_range_row(
        ScoreRange(assignment="Final exam", highest=None, lowest=None, median_score=None)
    )

    assert row.split()[-3:] == ["-", "-", "-"]


def test_band_counts_list_every_band_best_first() -> None:
    counts = {"Excellent": 0, "Very good": 1, "Pass": 0, "Fail": 1}

    assert format_band_counts(counts) == (
        "Students per band: Excellent 0, Very good 1, Pass 0, Fail 1"
    )


def test_report_shows_the_score_spread_and_the_bands(demo_gradebook: Gradebook) -> None:
    report = "\n".join(format_report(demo_gradebook))

    assert "Score spread" in report
    assert "Students per band: Excellent 0, Very good 1, Pass 0, Fail 1" in report


def test_report_without_assignments_has_no_score_spread() -> None:
    report = "\n".join(format_report(Gradebook(students=["Noa Ferrer"])))

    assert "Score spread" not in report
    assert "Students per band: Excellent 0, Very good 0, Pass 0, Fail 0" in report
