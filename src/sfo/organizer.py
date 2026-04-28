import shutil
from pathlib import Path
from typing import Annotated, Dict, List

import rich
import typer
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Confirm

from .backup import create_backup
from .config import AUTO_BACKUP, EXTENSIONS_MAP, SORTED_DIR_NAME

# =========================================================
# ======================= UTILS ============================
# =========================================================


def flatten_extensions_map(
    exts: Dict[str, List[str]] = EXTENSIONS_MAP,
) -> Dict[str, str]:
    """Flattens a dictionary mapping extensions to their respective categories.

    Args:
        exts: A dictionary mapping category names to lists of extensions.

    Returns:
        A dictionary mapping lowercase extensions to their category.
    """

    ext_map = {}

    for category, extensions in exts.items():
        for ext in extensions:
            ext_map[ext.lower()] = category

    return ext_map


def get_extension_category(ext: str, flat_ext_map: Dict[str, str]) -> str:
    """Determines the category of a given file extension.

    Args:
        ext: The file extension (e.g., "txt", "jpg").
        flat_ext_map: The pre-processed map of extensions to categories.

    Returns:
        The category name, or "Other" if the extension is unknown.
    """

    return flat_ext_map.get(ext, "Other")


# =========================================================
# ======================= FILES ============================
# =========================================================


def get_nonhidden_files(path: Path) -> List[Path]:
    """Returns a list of non-hidden files in the specified directory.

    Args:
        path: The directory path to scan.

    Returns:
        list[pathlib.Path]: A list of file paths that do not start with '.'."""
    if not path.exists() or not any(path.iterdir()):
        return []

    path = Path(path)
    filename_list: List[Path] = []

    for entry in path.iterdir():
        if entry.is_file() and not entry.name.startswith("."):
            filename_list.append(entry)

    return filename_list


def get_file_extension(file: Path) -> str:
    """Extracts the file extension (without the dot) from a given file path.

    Args:
        file: The path to the file.

    Returns:
        str: The lowercase file extension, or an empty string if none exists."""
    if not file.suffix:
        return ""
    return file.suffix[1:].lower()


def move_file(file_path: Path, destination_path: Path) -> None:
    """Moves a file from source to destination, handling existing file conflicts.

    Args:
        file_path: Path object of the file to move.
        destination_path: Path object of the target directory.
    Returns:
        None: Prints success or error messages to the console."""
    target = destination_path / file_path.name

    if not file_path.exists():
        rich.print(f"[red]Error:[/red] File not found: {file_path}")
        return

    if target.exists():
        if not Confirm.ask(
            f"[yellow]Warning:[/yellow] File '{file_path.name}' already exists in {target}. Do you want to replace it?",
            default="n",
        ):
            rich.print(f"[yellow]Skipping:[/yellow] {file_path.name}")
            return

        target.unlink()

    try:
        shutil.move(str(file_path), str(target))
        rich.print(f"[green]Moved:[/green] {file_path.name} → {target}")
    except OSError as e:
        rich.print(f"[bold red]Error moving file:[/bold red] {e}")


# =========================================================
# ==================== CORE LOGIC ==========================
# =========================================================


def sort_by_extension(
    path: Path, flat_ext_map: Dict[str, str]
) -> Dict[str, List[Path]]:
    """Sorts files in a directory into categories based on their extensions.

    Args:
        path: The directory path containing the files.
        flat_ext_map: A dictionary mapping file extensions to categories.

    Returns:
        dict[str, list[pathlib.Path]]: A dictionary where keys are categories and values are lists of file paths belonging to that category."""
    categories = set(flat_ext_map.values()) | {"Other"}

    sorted_files: Dict[str, List[Path]] = {category: [] for category in categories}

    for file in get_nonhidden_files(path):
        ext = get_file_extension(file)
        category = get_extension_category(ext, flat_ext_map)
        sorted_files[category].append(file)

    return sorted_files


def ensure_directories(
    path: Path,
    sorted_dir_name: str = SORTED_DIR_NAME,
    ext_map: Dict[str, List[str]] = EXTENSIONS_MAP,
) -> None:
    """Ensures necessary subdirectory structure exists for sorting files.

    Args:
        path: The base directory path.
        sorted_dir_name: The name of the main subdirectory (default: SORTED_DIR_NAME).
        ext_map: Dictionary defining existing extension categories (default: EXTENSIONS_MAP).

    Returns:
        None: Creates directories if they do not already exist."""

    base = path / sorted_dir_name
    for category in ext_map.keys():
        (base / category).mkdir(parents=True, exist_ok=True)


def execute_organization(
    path: Path,
    sorted_files: Dict[str, List[Path]],
    sorted_dir_name: str,
    dry_run: bool,
) -> None:
    """Moves sorted files into their respective category directories.

    Args:
        path: The root directory containing the files.
        sorted_files: Dictionary of files grouped by category.
        sorted_dir_name: Name of the main subdirectory for sorted files.
        dry_run: If True, simulates the move without actual file operations.

    Returns:
        None: Prints status messages indicating the execution progress."""

    rich.print(
        f"\n[bold blue]--- Starting Organization Process for {path} ---[/bold blue]"
    )

    mode = "DRY RUN (no changes)" if dry_run else "APPLY (changes will be made)"

    rich.print(f"\n[bold blue]Mode:[/bold blue] {mode}")

    for category, files in sorted_files.items():
        destination_path = path / sorted_dir_name / category

        if not files:
            continue

        rich.print(
            f"\n[bold yellow]Category:[/bold yellow] {category} ({len(files)} files)"
        )

        for file in files:
            target = destination_path / file.name

            if dry_run:
                rich.print(
                    f"  [blue]DRY RUN:[/blue] {file.name} → {target.relative_to(Path('.'))}"
                )
            else:
                move_file(file, destination_path)

    rich.print("\n[bold green]Organization process finished![/bold green]")

    if dry_run:
        rich.print("\n[yellow]Dry run finished — no files were modified.[/yellow]")
    else:
        rich.print("\n[green]Organization complete — files were moved.[/green]")


def organize_files(
    path: Path,
    flat_ext_map: Dict[str, str] = flatten_extensions_map(),
    sorted_dir_name: str = SORTED_DIR_NAME,
    dry_run: bool = True,
) -> None:
    """Coordinates the entire file organization workflow.

    Args:
        path: The root directory where files are located.
        flat_ext_map: Map from extensions to categories (default: flattened map).
        sorted_dir_name: The name of the main directory for sorted files (default: SORTED_DIR_NAME).
        dry_run: If True, only reports actions without moving files (default: True).

    Returns:
        None: Executes directory setup and file movement."""

    if not dry_run:
        ensure_directories(path)
    sorted_files = sort_by_extension(path, flat_ext_map)

    execute_organization(path, sorted_files, sorted_dir_name, dry_run)


# =========================================================
# ========================= CLI ============================
# =========================================================
app = typer.Typer()


@app.command()
def organize(
    path: Annotated[Path, typer.Argument()] = Path("./"),
    apply: Annotated[
        bool,
        typer.Option("--apply", "-a", help="Actually move files (disable dry run)"),
    ] = False,
) -> None:
    """Orchestrates the file organization process on a specified path.

    Args:
        path: The directory containing the files to be organized.
        apply: If True, moves files; if False, runs in simulation (dry run).

    Returns:
        None: Runs the organization logic and handles backup procedures if required."""
    if apply:
        should_backup = AUTO_BACKUP or Confirm.ask("Create backup?")
        if should_backup:
            with Progress(
                SpinnerColumn(), TextColumn("Creating backup...")
            ) as progress:
                task = progress.add_task("Zipping files", total=None)
                create_backup()

    organize_files(path, dry_run=not apply)
