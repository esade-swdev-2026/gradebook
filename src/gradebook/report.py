from gradebook.coursework import total_weight
from gradebook.grading import (
    assignment_summaries,
    class_average,
    class_standings,
    grade_band,
    passing_count,
)
from gradebook.models import MAX_SCORE, AssignmentSummary, Grade, Gradebook, StudentStanding
from gradebook.ranking import RankedStudent

NAME_WIDTH = 24
NUMBER_WIDTH = 8
BAND_WIDTH = 11
RULE_WIDTH = 72
NOT_AVAILABLE = "-"
PASS_SECURED = "secured"
PASS_OUT_OF_REACH = "out of reach"


def format_score(score: float | None) -> str:
    return NOT_AVAILABLE if score is None else f"{score:.1f}"


def format_needed_to_pass(needed: float | None) -> str:
    if needed is None:
        return NOT_AVAILABLE
    if needed == 0:
        return PASS_SECURED
    if needed > MAX_SCORE:
        return PASS_OUT_OF_REACH
    return f"{needed:.1f}"


def format_standing_row(standing: StudentStanding) -> str:
    band = NOT_AVAILABLE if standing.current_grade is None else grade_band(standing.current_grade)
    return (
        f"{standing.student:<{NAME_WIDTH}}"
        f"{standing.graded_weight:>{NUMBER_WIDTH - 1}.0f}%"
        f"{format_score(standing.current_grade):>{NUMBER_WIDTH}}  "
        f"{band:<{BAND_WIDTH}}"
        f"{format_needed_to_pass(standing.needed_to_pass)}"
    )


def format_assignment_row(summary: AssignmentSummary, student_count: int) -> str:
    return (
        f"{summary.assignment.name:<{NAME_WIDTH}}"
        f"{summary.assignment.weight:>{NUMBER_WIDTH - 1}.0f}%"
        f"{format_score(summary.average_score):>{NUMBER_WIDTH}}  "
        f"{summary.graded_count}/{student_count} graded"
    )


def format_grade_confirmation(
    grade: Grade, standing: StudentStanding, is_update: bool
) -> list[str]:
    verb = "Updated" if is_update else "Recorded"
    band = "" if standing.current_grade is None else f" ({grade_band(standing.current_grade)})"
    return [
        f"{verb} {grade.score:g} for {grade.student} on {grade.assignment}.",
        f"Current grade: {format_score(standing.current_grade)}{band}",
    ]


def format_report(gradebook: Gradebook) -> list[str]:
    if not gradebook.students:
        return ["No students yet. Add one with: gradebook add-student NAME"]

    standings = class_standings(gradebook)
    student_count = len(gradebook.students)
    lines = [
        f"Class report: {student_count} students, {len(gradebook.assignments)} assignments "
        f"({total_weight(gradebook.assignments):g}% of the course defined)",
        "",
        f"{'Student':<{NAME_WIDTH}}{'Graded':>{NUMBER_WIDTH}}{'Current':>{NUMBER_WIDTH}}  "
        f"{'Band':<{BAND_WIDTH}}Needs on the rest to pass",
        "-" * RULE_WIDTH,
    ]
    lines.extend(format_standing_row(standing) for standing in standings)

    if gradebook.assignments:
        lines.extend(
            [
                "",
                f"{'Assignment':<{NAME_WIDTH}}{'Weight':>{NUMBER_WIDTH}}"
                f"{'Average':>{NUMBER_WIDTH}}",
                "-" * RULE_WIDTH,
            ]
        )
        lines.extend(
            format_assignment_row(summary, student_count)
            for summary in assignment_summaries(gradebook)
        )

    lines.extend(
        [
            "",
            f"Class average: {format_score(class_average(standings))}    "
            f"Passing right now: {passing_count(standings)}/{student_count}",
        ]
    )
    return lines


def format_ranking(ranked: list[RankedStudent]) -> list[str]:
    """One line per student: position, name and current grade, best first."""
    if not ranked:
        return ["No student has a grade yet."]
    return [f"{r.position:>3}. {r.student:<{NAME_WIDTH}} {r.current_grade:.1f}" for r in ranked]
