import shutil
from datetime import datetime
from pathlib import Path
from typing import Annotated

import typer
from rich.progress import Progress, SpinnerColumn, TextColumn

from .config import BACKUP_NAME


def create_backup(destination: str = ".") -> None:
    """
    Creates a zip archive of the contents of the current working directory.

    Args:
        destination: The target directory where the archive should reside.
                     If '.' is provided, the archive is created in the
                     parent directory and then moved to the current directory
                     to mimic the original behavior.
    """

    timestamp = datetime.now().strftime("%Y-%m-%d_%H:%M")

    current_path = Path.cwd()
    parent_path = current_path.parent

    archive_name = f"{BACKUP_NAME}{timestamp}"

    if destination == ".":
        shutil.make_archive(f"{parent_path}/{archive_name}", "zip", current_path)
        shutil.move(f"{parent_path}/{archive_name}.zip", current_path)
    else:
        shutil.make_archive(f"{destination}/{archive_name}", "zip", current_path)


# cli
app = typer.Typer()


@app.command()
def backup(
    dest: Annotated[
        str,
        typer.Option("--path", "-p", help="Path to where to save archive"),
    ] = ".",
) -> None:
    """
    Performs a directory backup into a zip archive.
    The destination path specifies where the archive should be saved.
    """
    with Progress(SpinnerColumn(), TextColumn("Creating backup...")) as progress:
        task = progress.add_task("Zipping files", total=None)
        create_backup(destination=dest)
