"""Class statistics beyond the averages in grading.py: score spread and band counts."""

from dataclasses import dataclass
from statistics import median

from gradebook.grading import grade_band
from gradebook.models import GRADE_BANDS, Gradebook, StudentStanding


@dataclass(frozen=True)
class ScoreRange:
    assignment: str
    highest: float | None
    lowest: float | None
    median_score: float | None


def score_ranges(gradebook: Gradebook) -> list[ScoreRange]:
    """Highest, lowest and median score per assignment; None where nobody is graded yet."""
    ranges: list[ScoreRange] = []
    for assignment in gradebook.assignments:
        scores = [grade.score for grade in gradebook.grades if grade.assignment == assignment.name]
        ranges.append(
            ScoreRange(
                assignment=assignment.name,
                highest=max(scores) if scores else None,
                lowest=min(scores) if scores else None,
                median_score=median(scores) if scores else None,
            )
        )
    return ranges


def band_distribution(standings: list[StudentStanding]) -> dict[str, int]:
    """How many students are in each grade band now, best band first.

    Every band is listed, even with nobody in it. Students with nothing graded yet
    are in no band, so the counts can add up to fewer than the class size.
    """
    counts = {band.label: 0 for band in GRADE_BANDS}
    for standing in standings:
        if standing.current_grade is not None:
            counts[grade_band(standing.current_grade)] += 1
    return counts
