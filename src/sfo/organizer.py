import shutil
from pathlib import Path
from typing import Annotated, Dict, List

import rich
import typer
from rich.prompt import Confirm

from .config import EXTENSIONS_MAP, SORTED_DIR_NAME

# =========================================================
# ======================= UTILS ============================
# =========================================================


def flatten_extensions_map(
    exts: Dict[str, List[str]] = EXTENSIONS_MAP,
) -> Dict[str, str]:
    """Flattens a nested map of extensions into a single dictionary.

    The resulting dictionary maps each unique extension (in lowercase) to its
    assigned category.

    :param exts: The original nested map of extensions, where keys are categories
                  and values are lists of extensions.
    :type exts: Dict[str, List[str]]
    :return: A flattened dictionary mapping extensions to categories.
    :rtype: Dict[str, str]
    """
    # Możliwe poprawki:
    # Uruchamianie raz w startowej funkcji dla oszczędzenia
    # czasu i ustawienie globalnej zmiennej
    ext_map = {}

    for category, extensions in exts.items():
        for ext in extensions:
            ext_map[ext.lower()] = category

    return ext_map


def get_extension_category(ext: str, flat_ext_map: Dict[str, str]) -> str:
    """Retrieves the category assigned to a specific file extension.

    It searches the provided flattened map and defaults to 'Other' if the
    extension is not found.

    :param ext: The file extension (e.g., 'py', 'txt').
    :type ext: str
    :param flat_ext_map: The pre-computed, flattened extension map.
    :type flat_ext_map: Dict[str, str]
    :return: The category of the extension, or 'Other' if unknown.
    :rtype: str
    """

    return flat_ext_map.get(ext, "Other")


# =========================================================
# ======================= FILES ============================
# =========================================================


def get_nonhidden_files(path: Path) -> List[Path]:
    """Retrieves a list of visible files from a specified directory path.

    The function ignores hidden files (those starting with '.') and returns only
    the actual file paths within the directory.

    :param path: The directory Path object to scan.
    :type path: Path
    :return: A list of Path objects representing the non-hidden files. Returns an
             empty list if the path does not exist or is empty.
    :rtype: List[Path]
    """
    if not path.exists() or not any(path.iterdir()):
        return []

    path = Path(path)
    filename_list: List[Path] = []

    for entry in path.iterdir():
        if entry.is_file() and not entry.name.startswith("."):
            filename_list.append(entry)

    return filename_list


def get_file_extension(file: Path) -> str:
    """Extracts and normalizes the file extension from a given Path object.

    The function removes the leading dot from the suffix and converts the result
    to lowercase. Returns an empty string if no suffix is present.

    :param file: The Path object of the file.
    :type file: Path
    :return: The lowercase file extension without the leading dot (e.g., 'txt', 'py').
    :rtype: str
    """
    if not file.suffix:
        return ""
    return file.suffix[1:].lower()


def move_file(file_path: Path, destination_path: Path) -> None:
    """Moves a file from a source path to a destination directory, handling potential
    collisions by prompting the user for replacement confirmation.

    If the target file already exists, the user is asked if the source file
    should overwrite it. If no confirmation is given, the operation is skipped.

    :param file_path: The Path object of the file to be moved (source).
    :type file_path: Path
    :param destination_path: The Path object representing the directory where the file should move.
    :type destination_path: Path
    :raises FileNotFoundError: If the source file does not exist.
    :returns: None. Prints success or error messages to the console.
    """
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
        rich.print(
            f"[green]Moved:[/green] {file_path.name} → {target.relative_to(Path('.'))}"
        )
    except OSError as e:
        rich.print(f"[bold red]Error moving file:[/bold red] {e}")


# =========================================================
# ==================== CORE LOGIC ==========================
# =========================================================


def sort_by_extension(
    path: Path, flat_ext_map: Dict[str, str]
) -> Dict[str, List[Path]]:
    """Groups file paths found in a directory into a dictionary based on their assigned extension category.

    This function iterates through all visible files in the given path, determines the category
    for each file based on its extension, and organizes the paths into a dictionary where
    keys are categories and values are lists of corresponding file paths.

    :param path: The directory Path object containing the files to be sorted.
    :type path: Path
    :param flat_ext_map: The pre-computed, flattened map linking extensions to categories.
    :type flat_ext_map: Dict[str, str]
    :return: A dictionary mapping extension categories (including 'Other') to lists of file Paths.
    :rtype: Dict[str, List[Path]]"""
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
    """Creates the necessary subdirectory structure within a given path based on the
    provided extension map.

    It ensures that all categories listed in `ext_map` exist as directories under the
    specified sorted directory name. This operation is safe against existing directories.

    :param path: The base Path object where the organized structure will be created.
    :type path: Path
    :param sorted_dir_name: The name of the main directory containing all sub-category folders. Defaults to
    `SORTED_DIR_NAME`.
    :type sorted_dir_name: str
    :param ext_map: The map defining the extensions, used to determine the required sub-categories. Defaults to
    `EXTENSIONS_MAP`.
    :type ext_map: Dict[str, List[str]]
    :return: None. Creates directories in place.
    """

    base = path / sorted_dir_name
    for category in ext_map.keys():
        (base / category).mkdir(parents=True, exist_ok=True)


def execute_organization(
    path: Path,
    sorted_files: Dict[str, List[Path]],
    sorted_dir_name: str,
    dry_run: bool,
) -> None:
    """Executes the file organization process by moving (or simulating the move) of files
    into their respective category folders.

    The function iterates through the sorted file lists, calculates the final destination path,
    and either calls `move_file` (if not a dry run) or prints a simulation message.

    :param path: The base directory Path object where the organization will occur.
    :type path: Path
    :param sorted_files: A dictionary mapping categories to lists of file Paths that need moving.
    :type sorted_files: Dict[str, List[Path]]
    :param sorted_dir_name: The name of the main destination directory.
    :type sorted_dir_name: str
    :param dry_run: If True, only prints what would happen without making any changes.
                     If False, physically moves the files.
    :type dry_run: bool
    :return: None. Prints operation status to the console.
    """

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
    """Orchestrates the entire file organization workflow.

    This function performs the following steps:
    1. Ensures all required category directories exist (if not in dry-run mode).
    2. Sorts all visible files in the source directory by their extension category.
    3. Executes the file movement (or simulation) into the structured destination directories.

    :param path: The Path object of the directory containing the unsorted files.
    :type path: Path
    :param flat_ext_map: The flattened extension map used for categorization. Defaults to calling
    `flatten_extensions_map()`.
    :type flat_ext_map: Dict[str, str]
    :param sorted_dir_name: The name of the main destination folder for sorted files. Defaults to `SORTED_DIR_NAME`.
    :type sorted_dir_name: str
    :param dry_run: If True (default), the process simulates file moves without altering any files.
                     If False, actual file movements are performed.
    :type dry_run: bool
    :return: None. Controls the execution flow of the organization process.
    """
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
    """Organizes files within a specified directory into structured subdirectories based on their file extension.
    
    The files found in the source path are automatically sorted and moved into categories
    (e.g., 'py', 'txt', 'images', 'Other'), preventing clutter.
    
    :param path: The source directory containing the unsorted files. Defaults to the current directory.
    :param apply: If provided, files will be physically moved to their new location.
                    If omitted (default), the operation runs in dry-run mode, only printing
                    what would happen without making any changes.
    """
    organize_files(path, dry_run=not apply)
