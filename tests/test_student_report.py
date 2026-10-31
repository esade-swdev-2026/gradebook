from dataclasses import replace

import pytest

from gradebook.models import Gradebook
from gradebook.student_report import format_student_detail


def test_detail_lists_every_assignment_with_the_score(demo_gradebook: Gradebook) -> None:
    lines = format_student_detail(demo_gradebook, "Noa Ferrer")
    text = "\n".join(lines)

    assert lines[0] == "Noa Ferrer"
    assert "Midterm exam" in text
    assert "Group project" in text
    assert "Final exam" in text
    assert "8.0" in text


def test_ungraded_assignment_shows_a_dash(demo_gradebook: Gradebook) -> None:
    lines = format_student_detail(demo_gradebook, "Leo Martin")
    final_exam_row = next(line for line in lines if line.startswith("Final exam"))
    assert final_exam_row.rstrip().endswith("-")


def test_detail_shows_grade_band_and_what_is_needed(demo_gradebook: Gradebook) -> None:
    text = "\n".join(format_student_detail(demo_gradebook, "Noa Ferrer"))
    # 8.0 on 60 % of the course: 480 of 500 points, 20 points over the last 40 %
    assert "Current grade: 8.0 (Very good)" in text
    assert "Graded: 60% of the course" in text
    assert "Needs on the rest to pass: 0.5" in text


def test_name_is_trimmed(demo_gradebook: Gradebook) -> None:
    assert format_student_detail(demo_gradebook, "  Noa Ferrer  ")[0] == "Noa Ferrer"


def test_unknown_student_is_an_error(demo_gradebook: Gradebook) -> None:
    with pytest.raises(ValueError, match="unknown student 'Nobody'"):
        format_student_detail(demo_gradebook, "Nobody")


def test_class_without_assignments_says_so(demo_gradebook: Gradebook) -> None:
    empty_course = replace(demo_gradebook, assignments=[], grades=[])
    text = "\n".join(format_student_detail(empty_course, "Noa Ferrer"))
    assert "No assignments yet" in text
    assert "Current grade: -" in text
