import pytest

from gradebook.core import (
    add_student,
    clean_student_name,
    count_students,
    is_valid_student_name,
    student_exists,
)


def test_clean_student_name_removes_spaces() -> None:
    assert clean_student_name("  Jannat Moufid  ") == "Jannat Moufid"


def test_clean_student_name_empty_name() -> None:
    assert clean_student_name("   ") == ""


@pytest.mark.parametrize(
    ("name", "expected"),
    [
        ("Varvara Lilchitskaia", True),
        ("  Varvara Lilchitskaia  ", True),
        ("", False),
        ("   ", False),
    ],
)
def test_is_valid_student_name(name: str, expected: bool) -> None:
    assert is_valid_student_name(name) is expected


def test_student_exists() -> None:
    assert student_exists("Kirill Mushinskii", ["Kirill Mushinskii", "Dayana Bukenova"])


def test_student_does_not_exist() -> None:
    assert not student_exists("Varvara Lilchitskaia", ["Kirill Mushinskii", "Dayana Bukenova"])


def test_add_student() -> None:
    result = add_student(["Jannat Moufid"], "  Varvara Lilchitskaia  ")
    assert result == ["Jannat Moufid", "Varvara Lilchitskaia"]


def test_add_student_does_not_modify_original_list() -> None:
    names = ["Dayana Bukenova"]

    result = add_student(names, "Jannat Moufid")

    assert names == ["Dayana Bukenova"]
    assert result == ["Dayana Bukenova", "Jannat Moufid"]


def test_add_student_rejects_empty_name() -> None:
    with pytest.raises(ValueError, match="student name cannot be empty"):
        add_student(["Kirill Mushinskii"], "   ")


def test_add_student_rejects_duplicate() -> None:
    with pytest.raises(ValueError, match="student 'Varvara Lilchitskaia' already exists"):
        add_student(["Varvara Lilchitskaia"], "  Varvara Lilchitskaia  ")


def test_count_students() -> None:
    assert count_students(["Jannat Moufid", "Dayana Bukenova"]) == 2


def test_count_students_empty() -> None:
    assert count_students([]) == 0
