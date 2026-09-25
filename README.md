# Gradebook

Gradebook is a command-line application for teachers to manage students, assignments, and grades. It helps teachers keep track of their class and academic performance directly from the terminal.

## Installation

Install the project and its dependencies:

```bash
uv sync
```

## Usage

View the available commands:

```bash
uv run gradebook --help
```

Add a student to the class:

```bash
uv run gradebook add-student "Ada Lovelace"
```

By default, students are stored in `class.csv`.

To use a different class file:

```bash
uv run gradebook add-student "Ada Lovelace" --class-file economics.csv
```
