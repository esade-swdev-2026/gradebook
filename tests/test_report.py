from gradebook.models import Grade, Gradebook, StudentStanding
from gradebook.report import (
    PASS_OUT_OF_REACH,
    PASS_SECURED,
    format_grade_confirmation,
    format_needed_to_pass,
    format_report,
    format_score,
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
