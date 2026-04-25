import shutil
from datetime import datetime
from pathlib import Path

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
    current_path = Path.cwd()
    parent_path = current_path.parent
    backup_path = (parent_path / f"{current_path.name}_{BACKUP_NAME}")

    if not backup_path.exists():
        backup_path.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
    archive_name = f"{BACKUP_NAME}{timestamp}"

    shutil.make_archive(f"{backup_path}/{archive_name}", "zip")


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
