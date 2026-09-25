from pathlib import Path

import pandas as pd
import typer

app = typer.Typer(help="A terminal gradebook for one class.")

CLASS_FILE = Path("class.csv")


@app.callback()
def main() -> None:
    """Manage students and grades for your class."""


@app.command()
def add_student(name: str, class_file: Path = CLASS_FILE) -> None:
    """Add a student to the class list."""
    cleaned = name.strip()

    if not cleaned:
        typer.echo("Error: student name cannot be empty.", err=True)
        raise typer.Exit(code=1)

    my_class = _load_roster(class_file)

    if cleaned in my_class["name"].values:
        typer.echo(f"Error: student '{cleaned}' already exists.", err=True)
        raise typer.Exit(code=1)

    my_class = pd.concat(
        [my_class, pd.DataFrame({"name": [cleaned]})],
        ignore_index=True,
    )

    _save_roster(class_file, my_class)
    typer.echo(f"Added {cleaned} to {class_file}")


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
