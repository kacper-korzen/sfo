import shutil
from datetime import datetime
from pathlib import Path
from typing import Annotated

import rich
import typer
from rich.progress import Progress, SpinnerColumn, TextColumn

from .config import BACKUP_NAME


def create_backup() -> None:
    """
    Creates a zip archive of the contents of the current working directory.

    Args:
        destination: The target directory where the archive should reside.
                     If '.' is provided, the archive is created in the
                     parent directory and then moved to the current directory
                     to mimic the original behavior.
    """
    timestamp = datetime.now().strftime("%Y-%m-%d_%H:%M")
    archive_name = f"{BACKUP_NAME}{timestamp}"

    current_path = Path.cwd()
    parent_path = current_path.parent
    shutil.make_archive(f"../backup/{archive_name}", "zip")
    shutil.move(f"{parent_path}/backup/", current_path)


# cli
app = typer.Typer()


@app.command()
def backup() -> None:
    """
    Performs a directory backup into a zip archive in current directory.
    """
    with Progress(SpinnerColumn(), TextColumn("Creating backup...")) as progress:
        task = progress.add_task("Zipping files", total=None)
        create_backup()
