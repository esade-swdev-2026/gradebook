# Product backlog

Status at v1.1, the final release (November 2026).

|N|Item|Status|Notes|
|-|----|------|-----|
|1|As a teacher, I can log in with my username, so that I get access to my own workspace|Dropped|See below|
|2|As a teacher, I can add/edit/remove students from my class, so I can manage my class|Done|`add-student`, `rename-student` (keeps their grades) and `remove-student`|
|3|As a teacher, I can record a students grade, by checking the name and adding the number, so that I can keep track|Done|`record-grade`|
|4|As a teacher, I can update a students grade, by checking the name and adding the number, so that I can keep track|Done|`record-grade` again replaces the old score|
|5|As a teacher, I can assign different weights to each assignment, so that they contribute differently to the final grade|Done|`add-assignment NAME WEIGHT`; weights cannot add up to more than 100|
|6|As a teacher, I can forecast/calculate their final grade, so that I know the minimum grades they should get to pass my course|Done|"Needs on the rest to pass" in `report` and `student`|
|7|As a teacher, I can see the statistics (averages) of students, so I can keep track of the overall performance|Done|`report`: class average, average, lowest, median and highest per assignment, students per band|
|8|As a teacher, I can see my students' current final grade for each course and overall gpa, so that I can see their academic performance|Partly done|Current grade and band per student; one class only, so no GPA across courses|

## Built beyond the backlog

- `student NAME`: one student's score on every assignment and where they stand
- `ranking --top N`: the best students by current grade
- `export FILE`: the class report as a CSV file for a spreadsheet
- Hand-edited CSV files are checked on load and rejected, never silently repaired
- A Docker image, built and run in CI and published to GHCR on every merge to main and every version tag, for Intel and Apple Silicon

## Dropped, and why

- **1, log in.** Gradebook is a command-line tool that keeps each class in a folder on the
  teacher's own computer (`--data-dir`). There is no shared server whose data a login would
  protect, so a login would add a password to remember and protect nothing.
- **8, GPA across courses.** The tool manages one class, as its README says. A GPA needs
  every course a student takes and each course's credits, which is a different product.

# Definition of Done

- The CI check is green
- There is at least one test for each new feature
- Errors such as invalid input are caught and print a message
