import shutil
from pathlib import Path
from typing import Annotated

import rich
import typer

from .config import SORTED_DIR_NAME
from .organizer import move_file


def execute_restore(dry_run: bool) -> None:
    current_dir_parts: tuple = Path.cwd().parts
    current_dir = Path(*current_dir_parts[-1:])
    sorted_path: str = f"{current_dir}/{SORTED_DIR_NAME}"
    full_current_path = Path(*current_dir_parts[:])

    rich.print(
        f"\n[bold blue]--- Starting Restoring Process for {sorted_path} ---[/bold blue]"
    )

    mode = "DRY RUN (no changes)" if dry_run else "APPLY (changes will be made)"

    rich.print(f"\n[bold blue]Mode:[/bold blue] {mode}")

    for dir in Path(SORTED_DIR_NAME).iterdir():
        rich.print(f"\n[bold yellow]Directory:[/bold yellow] {str(dir).split('/')[1]} ")

        for file in dir.iterdir():
            if dry_run:
                rich.print(f"[blue]DRY RUN:[/blue] {file.name} → /{current_dir}")
            else:
                move_file(file, full_current_path)
                rich.print(f"[green]Moved:[/green] {file} -> /{current_dir}")
                shutil.move(file, full_current_path)

        print()

    if dry_run:
        rich.print(f"{sorted_path}[bold red] directory removed[/bold red]")
        print(f"{full_current_path}")
    else:
        shutil.rmtree(f"{full_current_path}/sorted")

    rich.print("[bold green]Restoring process finished![/bold green]")


app = typer.Typer()


@app.command()
def restore(
    apply: Annotated[
        bool,
        typer.Option("--apply", "-a", help="Actually move files (disable dry run)"),
    ] = False,
) -> None:
    """
    Performs a directory backup into a zip archive in current directory.
    """
    execute_restore(dry_run=not apply)
