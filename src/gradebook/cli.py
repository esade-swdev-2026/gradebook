from pathlib import Path

import pandas as pd
import typer

from gradebook.gradebook import add_student

app = typer.Typer(help="A terminal gradebook for one class.")

CLASS_FILE = Path("class.csv")


@app.callback()
def main() -> None:
    """Manage students and grades for your class."""


@app.command("add-student")
def add_student_command(name: str, class_file: Path = CLASS_FILE) -> None:
    """Add a student to the class list."""
    my_class = _load_roster(class_file)
    names = my_class["name"].tolist()

    try:
        updated_names = add_student(names, name)
    except ValueError as error:
        typer.echo(f"Error: {error}", err=True)
        raise typer.Exit(code=1) from error

    updated_class = pd.DataFrame({"name": updated_names})
    _save_roster(class_file, updated_class)

    typer.echo(f"Added {updated_names[-1]} to {class_file}")


def _load_roster(class_file: Path) -> pd.DataFrame:
    """Load the class list or return an empty roster if the file is missing."""
    if class_file.exists():
        return pd.read_csv(class_file, dtype=str, keep_default_na=False)

    return pd.DataFrame({"name": pd.Series(dtype=str)})


def _save_roster(class_file: Path, roster: pd.DataFrame) -> None:
    """Save the class list to CSV."""
    roster[["name"]].to_csv(class_file, index=False)


if __name__ == "__main__":
    app()
