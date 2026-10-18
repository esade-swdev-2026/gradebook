# Gradebook

Gradebook is a command-line tool for a teacher running one class. You add students and
weighted assignments, record scores on a 0–10 scale, and it tells you:

- each student's **current weighted grade** and grade band (Fail, Pass, Very good, Excellent)
- the **average score each student needs on the rest of the course to pass** (pass mark 5.0)
- **class statistics**: the class average, how many are passing now, and the average per assignment

## Installation

You need [uv](https://docs.astral.sh/uv/getting-started/installation/). Then:

```bash
git clone https://github.com/esade-swdev-2026/gradebook.git
cd gradebook
uv sync
```

## First result in one command

The repository ships a small example class (fictional students) in `examples/demo-class`:

```bash
uv run gradebook report --data-dir examples/demo-class
```

```text
Class report: 4 students, 3 assignments (100% of the course defined)

Student                   Graded Current  Band       Needs on the rest to pass
------------------------------------------------------------------------
Hugo Navarro                 30%     6.0  Pass       4.6
Iris Soler                   60%     0.8  Fail       out of reach
Leo Martin                   60%     4.8  Fail       5.4
Noa Ferrer                   60%     8.8  Very good  secured
...
```

Leo has 4.0 on the midterm and 5.5 on the project (30 % each), so he has 285 of the 500
points needed to pass and must average 215 / 40 = 5.4 on the final exam.

## Usage: your own class

Every command takes `--data-dir`, the folder where your class is kept as three CSV files
(`students.csv`, `assignments.csv`, `grades.csv`). It defaults to `gradebook-data`. The
folder is created on the first write.

```bash
uv run gradebook add-student "Marta Puig" --data-dir my-class
uv run gradebook add-student "Pol Serra" --data-dir my-class
uv run gradebook add-assignment "Midterm exam" 40 --data-dir my-class
uv run gradebook add-assignment "Final exam" 60 --data-dir my-class
uv run gradebook record-grade "Marta Puig" "Midterm exam" 7.5 --data-dir my-class
uv run gradebook record-grade "Pol Serra" "Midterm exam" 3 --data-dir my-class
uv run gradebook report --data-dir my-class
```

| Command | What it does |
|---|---|
| `add-student NAME` | Adds a student to the class |
| `remove-student NAME` | Removes a student and all of their grades |
| `add-assignment NAME WEIGHT` | Adds an assignment worth `WEIGHT` % of the final grade |
| `record-grade STUDENT ASSIGNMENT SCORE` | Records a 0–10 score; running it again updates it |
| `report` | Current grades, bands, what each student needs to pass, class statistics |

Run `uv run gradebook --help` or `uv run gradebook COMMAND --help` for details.

### Grading rules

- Scores go from 0 to 10. The passing grade is 5.0.
- Assignment weights are percentages of the final grade; together they cannot exceed 100.
- **Current grade** = weighted average of the work graded so far.
- **Needs on the rest to pass** = (5.0 × 100 − points earned) ÷ weight not yet graded.
  `secured` means the student passes even with 0 on everything left; `out of reach` means
  they would need more than 10.
- Bands: 9.0–10 Excellent · 7.0–8.9 Very good · 5.0–6.9 Pass · below 5.0 Fail.

### Errors

Bad input (an empty name, an unknown student, a score of 11, a weight that would push the
total over 100, a damaged CSV file) prints a message on stderr and exits with code 1:

```bash
uv run gradebook record-grade "Pol Serra" "Midterm exam" 11 --data-dir my-class
# Error: score must be between 0 and 10, got 11.
```

The CSV files can be edited by hand, so every command checks them on load with the same
rules. A class folder is **rejected, never silently repaired**, if it contains:

- a score or weight that is not a number, is `nan`/`inf`, or is out of range
- a duplicate student, a duplicate assignment, or two grades for the same student and assignment
- a grade for a student or assignment that does not exist
- assignment weights that add up to more than 100

The error names the folder and the problem, and nothing is written until you fix the file.

## Running the checks

The same four checks CI runs:

```bash
uv run ruff check . && uv run ruff format --check . && uv run mypy src tests && uv run pytest
```

or, in one script:

```bash
bash scripts/check.sh
```

## Project structure

```text
src/gradebook/
  models.py      dataclasses and grading constants (scale, pass mark, bands)
  validation.py  name, score and weight rules
  roster.py      add and remove students
  coursework.py  add assignments, record grades
  grading.py     weighted grades, what is needed to pass, class statistics
  report.py      turns results into lines of text
  storage.py     reads and writes the CSV files    <- the only module touching files
  cli.py         typer commands                     <- the only module printing / exiting
```

Everything except `storage.py` and `cli.py` takes plain data and returns plain data, which
is why most tests need no files.
