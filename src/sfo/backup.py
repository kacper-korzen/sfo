import shutil
from datetime import datetime
from pathlib import Path

import typer
from rich.progress import Progress, SpinnerColumn, TextColumn

from .config import BACKUP_NAME


def create_backup() -> None:
    """Creates a timestamped zip backup of the current directory into the parent folder."""
    current_path = Path.cwd()
    parent_path = current_path.parent
    backup_path = parent_path / f"{current_path.name}_{BACKUP_NAME}"

    if not backup_path.exists():
        backup_path.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
    archive_name = f"{BACKUP_NAME}{timestamp}"

    shutil.make_archive(f"{backup_path}/{archive_name}", "zip")


# cli
app = typer.Typer()


@app.command()
def backup() -> None:
    """Initializes and executes the backup routine, displaying progress to the user."""
    with Progress(SpinnerColumn(), TextColumn("Creating backup...")) as progress:
        task = progress.add_task("Zipping files", total=None)
        create_backup()
