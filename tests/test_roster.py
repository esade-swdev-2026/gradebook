import pytest

from gradebook.models import Gradebook
from gradebook.roster import add_student, remove_student, rename_student, student_exists


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


def test_rename_student_keeps_their_place_and_their_grades(demo_gradebook: Gradebook) -> None:
    updated = rename_student(demo_gradebook, "Noa Ferrer", "  Noa Ferrer Puig  ")

    assert updated.students == ["Noa Ferrer Puig", "Leo Martin"]
    assert [grade.student for grade in updated.grades] == [
        "Noa Ferrer Puig",
        "Noa Ferrer Puig",
        "Leo Martin",
    ]
    assert [grade.score for grade in updated.grades] == [8.0, 8.0, 4.0]


def test_rename_student_does_not_modify_the_original_gradebook(demo_gradebook: Gradebook) -> None:
    rename_student(demo_gradebook, "Noa Ferrer", "Noa Puig")
    assert demo_gradebook.students == ["Noa Ferrer", "Leo Martin"]
    assert demo_gradebook.grades[0].student == "Noa Ferrer"


def test_rename_unknown_student_is_an_error(demo_gradebook: Gradebook) -> None:
    with pytest.raises(ValueError, match="unknown student 'Iris Soler'"):
        rename_student(demo_gradebook, "Iris Soler", "Iris Puig")


def test_rename_to_an_existing_student_is_an_error(demo_gradebook: Gradebook) -> None:
    with pytest.raises(ValueError, match="student 'Leo Martin' already exists"):
        rename_student(demo_gradebook, "Noa Ferrer", "Leo Martin")


def test_rename_to_the_same_name_is_an_error(demo_gradebook: Gradebook) -> None:
    with pytest.raises(ValueError, match="already has that name"):
        rename_student(demo_gradebook, "Noa Ferrer", " Noa Ferrer ")


def test_rename_to_an_empty_name_is_an_error(demo_gradebook: Gradebook) -> None:
    with pytest.raises(ValueError, match="new student name cannot be empty"):
        rename_student(demo_gradebook, "Noa Ferrer", "   ")
