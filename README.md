# Gradebook

Gradebook is a command-line tool for a teacher running one class. You add your students and
weighted assignments, record scores on a 0–10 scale, and it tells you:

- each student's **current grade** and band (Fail, Pass, Very good, Excellent)
- the **average score each student needs on the rest of the course to pass**
- **class statistics**: the class average, how many are passing, and the average, lowest,
  median and highest score of each assignment
- a **ranking** of the best students, a **detail view** of one student, and an **export** of
  the report to a CSV file for a spreadsheet

You can run it from the Docker image our pipeline publishes (all you need is Docker), or
from source with uv.

## Run with Docker

You need [Docker Desktop](https://www.docker.com/products/docker-desktop/), running.

The image lives in the GitHub Container Registry and is private to the course organisation.
Log in once, with your GitHub username in lowercase and, as the password, a personal access
token (classic) with the `read:packages` scope:

```bash
docker login ghcr.io -u <your-github-username>
```

Download the image and give it a short local name, `gradebook`:

```bash
docker pull ghcr.io/esade-swdev-2026/gradebook:v1.1
docker tag ghcr.io/esade-swdev-2026/gradebook:v1.1 gradebook
```

The image ships with an example class of four fictional students. Ask for its report:

```bash
docker run --rm gradebook report --data-dir examples/demo-class
```

```text
Class report: 4 students, 3 assignments (100% of the course defined)

Student                   Graded Current  Band       Needs on the rest to pass
------------------------------------------------------------------------
Hugo Navarro                 30%     6.0  Pass       4.6
Iris Soler                   60%     0.8  Fail       out of reach
Leo Martin                   60%     4.8  Fail       5.4
Noa Ferrer                   60%     8.8  Very good  secured

Assignment                Weight Average
------------------------------------------------------------------------
Midterm exam                 30%     4.9  4/4 graded
Group project                30%     5.0  3/4 graded
Final exam                   40%       -  0/4 graded

Score spread              Lowest  Median Highest
------------------------------------------------------------------------
Midterm exam                 1.0     5.0     8.5
Group project                0.5     5.5     9.0
Final exam                     -       -       -

Students per band: Excellent 0, Very good 1, Pass 1, Fail 2
Class average: 5.1    Passing right now: 2/4
```

Leo has 4.0 on the midterm and 5.5 on the project (30% each): 285 of the 500 points needed
to pass. The final exam is worth the remaining 40%, so he needs (500 − 285) ÷ 40 = 5.4 on it.

### Your own class, kept outside the container

A class is kept as three CSV files (`students.csv`, `assignments.csv`, `grades.csv`) in a
folder, `gradebook-data` by default. A container's own files are deleted together with it, so
the folder lives in a Docker **named volume**, also called `gradebook-data`, which you attach
to every command with `-v`:

```bash
docker run --rm -v gradebook-data:/app/gradebook-data gradebook add-student "Marta Puig"
docker run --rm -v gradebook-data:/app/gradebook-data gradebook add-student "Pol Serra"
docker run --rm -v gradebook-data:/app/gradebook-data gradebook add-assignment "Midterm exam" 40
docker run --rm -v gradebook-data:/app/gradebook-data gradebook add-assignment "Final exam" 60
docker run --rm -v gradebook-data:/app/gradebook-data gradebook record-grade "Marta Puig" "Midterm exam" 7.5
docker run --rm -v gradebook-data:/app/gradebook-data gradebook record-grade "Pol Serra" "Midterm exam" 3
docker run --rm -v gradebook-data:/app/gradebook-data gradebook report
```

```text
Class report: 2 students, 2 assignments (100% of the course defined)

Student                   Graded Current  Band       Needs on the rest to pass
------------------------------------------------------------------------
Marta Puig                   40%     7.5  Very good  3.3
Pol Serra                    40%     3.0  Fail       6.3
...
```

Each `docker run` starts a new container, and `--rm` deletes it when the command ends. The
class is still there for the next command because it lives in the volume, outside the
container and outside the image. Without the volume, the same command starts from an empty
class:

```bash
docker run --rm gradebook report
```

```text
No students yet. Add one with: gradebook add-student NAME
```

To export the report, write the file into the volume, then print it from there:

```bash
docker run --rm -v gradebook-data:/app/gradebook-data gradebook export gradebook-data/report.csv
docker run --rm -v gradebook-data:/app/gradebook-data --entrypoint cat gradebook gradebook-data/report.csv
```

```text
student,graded_percent,current_grade,band,needed_to_pass
Marta Puig,40,7.50,Very good,3.33
Pol Serra,40,3.00,Fail,6.33
```

`docker volume rm gradebook-data` deletes the class. For a second class, use another volume
name, for example `-v economics:/app/gradebook-data`.

## Run from source

You need [uv](https://docs.astral.sh/uv/getting-started/installation/). Clone the repository
and install:

```bash
git clone https://github.com/esade-swdev-2026/gradebook.git
cd gradebook
uv sync
```

The first result, the same example class as above:

```bash
uv run gradebook report --data-dir examples/demo-class
```

Every command works the same way, with `uv run gradebook` in place of
`docker run --rm -v gradebook-data:/app/gradebook-data gradebook`. The class is then kept in
the folder `gradebook-data` in the current directory:

```bash
uv run gradebook add-student "Marta Puig"
uv run gradebook report
```

`gradebook-data/` is git-ignored, so a real class kept there never ends up in the repository.

## Commands

The commands are the same however you run Gradebook. Write them after
`docker run --rm -v gradebook-data:/app/gradebook-data gradebook` (Docker) or after
`uv run gradebook` (from source), for example `... report` or `... student "Pol Serra"`.

| Command | What it does |
|---|---|
| `add-student NAME` | Adds a student to the class |
| `rename-student OLD NEW` | Renames a student and keeps all of their grades |
| `remove-student NAME` | Removes a student and all of their grades |
| `add-assignment NAME WEIGHT` | Adds an assignment worth `WEIGHT` % of the final grade |
| `record-grade STUDENT ASSIGNMENT SCORE` | Records a score from 0 to 10; recording it again replaces it |
| `report` | Every student's grade, band and what they need to pass, plus class statistics |
| `student NAME` | One student's score on every assignment, their grade and what they need |
| `ranking [--top N]` | The `N` best students by current grade (default 3; ties share a place) |
| `export FILE` | Writes the report to a CSV file |

Every command takes `--data-dir FOLDER` to use another class folder. `--help` after any
command explains it.

## Grading rules

- Scores go from 0 to 10, and a student passes with 5.0.
- Each assignment is worth a percentage of the final grade. Together they cannot exceed 100%.
- The **current grade** is the weighted average of the work graded so far.
- **Needs on the rest to pass** = (5.0 × 100 − points earned) ÷ the percentage not yet
  graded. `secured` means the student passes even with 0 on everything left; `out of reach`
  means they would need more than 10.
- Grades are shown with one decimal, rounded halves up (4.95 becomes 5.0), and the band
  follows the grade as shown: below 5.0 Fail, 5.0–6.9 Pass, 7.0–8.9 Very good, 9.0–10
  Excellent.

## When something is wrong

Bad input never crashes the program. It prints what is wrong and exits with a non-zero
code:

```text
$ docker run --rm -v gradebook-data:/app/gradebook-data gradebook record-grade "Pol Serra" "Midterm exam" 11
Error: score must be between 0 and 10, got 11.

$ docker run --rm -v gradebook-data:/app/gradebook-data gradebook add-student "marta  puig"
Error: student 'marta puig' already exists as 'Marta Puig'.
```

A new student or assignment whose name differs from an existing one only in capitals or
spaces is refused, so a typo cannot create a second "Marta Puig".

The CSV files can be edited by hand, so every command checks them when it loads them. A class
is **rejected, never silently repaired**, if a file contains a score or weight that is not a
number or is out of range, the same student or assignment twice, a grade for a student or
assignment that does not exist, or weights adding up to more than 100%. The error names the
folder or file and the problem, and nothing is written until you fix it.

## Development

### Checks

The same checks CI runs on every push (lint, formatting, strict types, tests):

```bash
bash scripts/check.sh
```

### Build the image yourself

```bash
docker build -t gradebook .
docker run --rm gradebook report --data-dir examples/demo-class
```

The `release` job in `.github/workflows/check.yml` does this for every merge to `main` and
every version tag, for Intel and Apple Silicon, once the checks are green. It publishes the
image to `ghcr.io/esade-swdev-2026/gradebook`, tagged with the commit and, for a tag such as
`v1.1`, with the version.

## Project structure

```text
src/gradebook/       the package (below)
tests/               one test file per module, plus tests of each command
examples/demo-class/ the fictional example class
scripts/check.sh     the checks CI runs
Dockerfile           the image; .dockerignore keeps .venv, .git and caches out of it
.github/workflows/   check.yml: the checks, building the image, and the release
pyproject.toml       dependencies, the gradebook command, ruff, mypy and pytest settings
uv.lock              the exact versions of every dependency
```

Inside the package:

```text
src/gradebook/
  models.py          dataclasses (Assignment, Grade, Gradebook) and the grading constants
  validation.py      the rules for names, scores, weights and whole class files
  roster.py          add, rename and remove students
  coursework.py      add assignments, record grades
  grading.py         current grades, rounding, bands, what is needed to pass
  class_stats.py     score spread per assignment, students per band
  ranking.py         orders students by grade; ties share a place
  report.py          turns the results into lines of text
  student_report.py  one student's detail view
  export.py          the report as rows for the CSV export
  storage.py         reads and writes the CSV files    <- the only module that touches files
  cli.py             the commands                       <- the only module that prints or exits
```

The core works on plain dataclasses and returns plain data; pandas is used only in
`storage.py`, to read and write the CSV files. That is why most tests need no files, and
why the storage could change without touching the grading.

## Product backlog

The backlog we planned the project with, the status of each item and our Definition of Done
are in [`backlog-brief.md`](backlog-brief.md).

## Use of AI

We used Claude throughout the project. Mostly it helped us understand concepts from class and
explore possible solutions, but we also used it to review our code, find errors, failing CI
runs and merge problems during development.

AI suggestions were treated as guidance rather than final solutions, we discussed and
evaluated proposed changes as a group, some were drafted by Claude, and every one was applied
by one of us, checked through the tests, and reviewed by another member in a pull request.
All final implementation decisions and submitted code were reviewed and approved by our team,
and we take responsibility for all of it.
