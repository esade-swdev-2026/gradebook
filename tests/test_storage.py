from pathlib import Path

import pytest

from gradebook.models import Gradebook
from gradebook.storage import GRADES_FILE, load_gradebook, save_gradebook


def test_missing_folder_loads_as_an_empty_gradebook(tmp_path: Path) -> None:
    assert load_gradebook(tmp_path / "new-class") == Gradebook()


def test_save_then_load_gives_back_the_same_gradebook(
    tmp_path: Path, demo_gradebook: Gradebook
) -> None:
    save_gradebook(tmp_path, demo_gradebook)
    assert load_gradebook(tmp_path) == demo_gradebook


def test_non_numeric_score_is_a_clear_error(tmp_path: Path) -> None:
    (tmp_path / GRADES_FILE).write_text("student,assignment,score\nNoa Ferrer,Quiz,ten\n")
    with pytest.raises(ValueError, match="'ten', which is not a number"):
        load_gradebook(tmp_path)


def test_missing_column_is_a_clear_error(tmp_path: Path) -> None:
    (tmp_path / GRADES_FILE).write_text("student,score\nNoa Ferrer,7\n")
    with pytest.raises(ValueError, match=r"missing the column\(s\) \['assignment'\]"):
        load_gradebook(tmp_path)


def test_nan_score_in_a_file_is_rejected_on_load(tmp_path: Path, demo_gradebook: Gradebook) -> None:
    save_gradebook(tmp_path, demo_gradebook)
    with (tmp_path / GRADES_FILE).open("a") as grades_file:
        grades_file.write("Leo Martin,Final exam,nan\n")

    with pytest.raises(ValueError, match="invalid data: score must be a finite number"):
        load_gradebook(tmp_path)
