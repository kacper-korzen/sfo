import shutil
from pathlib import Path
from typing import Annotated

import rich
import typer

from .config import SORTED_DIR_NAME
from .organizer import move_file


def execute_restore(dry_run: bool) -> None:
    """Restores files from the sorted directory, optionally performing a dry run.

    Args:
        dry_run: If True, simulates the restore process without making changes.
    """
    if not Path(SORTED_DIR_NAME).exists():
        rich.print(f"[yellow]There is no directory named {SORTED_DIR_NAME}[/yellow]")
        return

    current_path = Path.cwd()
    sorted_path: str = f"{current_path.name}/{SORTED_DIR_NAME}"

    rich.print(
        f"\n[bold blue]--- Starting Restoring Process for {sorted_path} ---[/bold blue]"
    )

    mode = "DRY RUN (no changes)" if dry_run else "APPLY (changes will be made)"

    rich.print(f"\n[bold blue]Mode:[/bold blue] {mode}")

    for dir in Path(SORTED_DIR_NAME).iterdir():
        rich.print(f"\n[bold yellow]Directory:[/bold yellow] {str(dir).split('/')[1]} ")

        for file in dir.iterdir():
            if dry_run:
                rich.print(f"[blue]DRY RUN:[/blue] {file.name} → /{current_path.name}")
            else:
                move_file(file, current_path)

        print()

    if dry_run:
        rich.print(f"{sorted_path}[bold red] directory removed[/bold red]")
    else:
        shutil.rmtree(f"{current_path}/sorted")

    rich.print("[bold green]Restoring process finished![/bold green]")


app = typer.Typer()


@app.command()
def restore(
    apply: Annotated[
        bool,
        typer.Option("--apply", "-a", help="Actually move files (disable dry run)"),
    ] = False,
) -> None:
    """Runs the restore process, applying changes only if the --apply flag is provided."""
    execute_restore(dry_run=not apply)
