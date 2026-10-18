import pytest

from gradebook.models import Gradebook
from gradebook.roster import add_student, remove_student, student_exists


def test_add_student_appends_cleaned_name() -> None:
    gradebook = add_student(Gradebook(students=["Noa Ferrer"]), "  Leo Martin  ")
    assert gradebook.students == ["Noa Ferrer", "Leo Martin"]


def test_add_student_does_not_modify_the_original_gradebook() -> None:
    original = Gradebook(students=["Noa Ferrer"])
    add_student(original, "Leo Martin")
    assert original.students == ["Noa Ferrer"]


def test_add_student_rejects_duplicate_even_with_extra_spaces() -> None:
    with pytest.raises(ValueError, match="student 'Noa Ferrer' already exists"):
        add_student(Gradebook(students=["Noa Ferrer"]), " Noa Ferrer ")


def test_add_student_rejects_empty_name() -> None:
    with pytest.raises(ValueError, match="student name cannot be empty"):
        add_student(Gradebook(), "   ")


def test_student_exists() -> None:
    gradebook = Gradebook(students=["Noa Ferrer"])
    assert student_exists(gradebook, "Noa Ferrer")
    assert not student_exists(gradebook, "Leo Martin")


def test_remove_student_also_removes_their_grades(demo_gradebook: Gradebook) -> None:
    updated = remove_student(demo_gradebook, "Noa Ferrer")

    assert updated.students == ["Leo Martin"]
    assert all(grade.student != "Noa Ferrer" for grade in updated.grades)
    assert len(updated.grades) == 1


def test_remove_unknown_student_is_an_error(demo_gradebook: Gradebook) -> None:
    with pytest.raises(ValueError, match="unknown student 'Iris Soler'"):
        remove_student(demo_gradebook, "Iris Soler")
