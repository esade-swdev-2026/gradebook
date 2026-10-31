"""Ranking students by their current weighted grade."""

import math
from dataclasses import dataclass

from gradebook.models import StudentStanding


@dataclass(frozen=True)
class RankedStudent:
    position: int
    student: str
    current_grade: float


def rank_students(standings: list[StudentStanding]) -> list[RankedStudent]:
    """Best current grade first. Students with nothing graded yet are left out.

    Tied students share a position and the next position is skipped (1, 2, 2, 4),
    the way sports tables do it. Within a tie, students are listed by name.
    """
    graded = [
        (standing.student, standing.current_grade)
        for standing in standings
        if standing.current_grade is not None
    ]
    graded.sort(key=lambda pair: (-pair[1], pair[0]))

    ranked: list[RankedStudent] = []
    for index, (student, grade) in enumerate(graded):
        if ranked and math.isclose(grade, ranked[-1].current_grade):
            position = ranked[-1].position
        else:
            position = index + 1
        ranked.append(RankedStudent(position=position, student=student, current_grade=grade))
    return ranked


def top_students(standings: list[StudentStanding], count: int) -> list[RankedStudent]:
    """The students in the first `count` positions.

    A tie on the last place is kept whole, so the result can be longer than `count`:
    the top 2 of 9.0, 7.0, 7.0 is all three students.
    """
    if count < 1:
        raise ValueError(f"count must be at least 1, got {count}.")
    return [ranked for ranked in rank_students(standings) if ranked.position <= count]
