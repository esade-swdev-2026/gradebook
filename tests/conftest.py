import pytest

from gradebook.models import Assignment, Grade, Gradebook

# Fictional people only: the repository is public.


@pytest.fixture
def course_assignments() -> list[Assignment]:
    return [
        Assignment(name="Midterm exam", weight=30.0),
        Assignment(name="Group project", weight=30.0),
        Assignment(name="Final exam", weight=40.0),
    ]


@pytest.fixture
def demo_gradebook(course_assignments: list[Assignment]) -> Gradebook:
    return Gradebook(
        students=["Noa Ferrer", "Leo Martin"],
        assignments=course_assignments,
        grades=[
            Grade(student="Noa Ferrer", assignment="Midterm exam", score=8.0),
            Grade(student="Noa Ferrer", assignment="Group project", score=8.0),
            Grade(student="Leo Martin", assignment="Midterm exam", score=4.0),
        ],
    )
