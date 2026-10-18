from dataclasses import dataclass, field

MIN_SCORE = 0.0
MAX_SCORE = 10.0
PASSING_GRADE = 5.0
COURSE_TOTAL_WEIGHT = 100.0


@dataclass(frozen=True)
class GradeBand:
    minimum_score: float
    label: str


# Highest first: a score belongs to the first band whose minimum it reaches.
GRADE_BANDS = (
    GradeBand(minimum_score=9.0, label="Excellent"),
    GradeBand(minimum_score=7.0, label="Very good"),
    GradeBand(minimum_score=PASSING_GRADE, label="Pass"),
    GradeBand(minimum_score=MIN_SCORE, label="Fail"),
)


@dataclass(frozen=True)
class Assignment:
    name: str
    weight: float  # percent of the final grade, e.g. 30.0 means 30 %


@dataclass(frozen=True)
class Grade:
    student: str
    assignment: str
    score: float


@dataclass(frozen=True)
class Gradebook:
    students: list[str] = field(default_factory=list)
    assignments: list[Assignment] = field(default_factory=list)
    grades: list[Grade] = field(default_factory=list)


@dataclass(frozen=True)
class StudentStanding:
    student: str
    graded_weight: float
    current_grade: float | None
    needed_to_pass: float | None


@dataclass(frozen=True)
class AssignmentSummary:
    assignment: Assignment
    average_score: float | None
    graded_count: int
