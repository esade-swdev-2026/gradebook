from dataclasses import dataclass, field


@dataclass(frozen=True)
class Gradebook:
    students: list[str] = field(default_factory=list)


def clean_student_name(name: str) -> str:
    return name.strip()


def is_valid_student_name(name: str) -> bool:
    return bool(clean_student_name(name))


def student_exists(name: str, names: list[str]) -> bool:
    return name in names


def add_student(names: list[str], name: str) -> list[str]:
    cleaned = clean_student_name(name)

    if not is_valid_student_name(cleaned):
        raise ValueError("student name cannot be empty.")

    if student_exists(cleaned, names):
        raise ValueError(f"student '{cleaned}' already exists.")

    return [*names, cleaned]


def count_students(names: list[str]) -> int:
    return len(names)
