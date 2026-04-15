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
    """Zwraca spłaszczoną wersje mapy rozszerzeń"""
    # Możliwe poprawki:
    # Uruchamianie raz w startowej funkcji dla oszczędzenia
    # czasu i ustawienie globalnej zmiennej
    ext_map = {}

    for category, extensions in exts.items():
        for ext in extensions:
            ext_map[ext.lower()] = category

    return ext_map


def get_extension_category(ext: str, flat_ext_map: Dict[str, str]) -> str:
    """Zwraca kategorie z pliku config.py przypisaną do rozszerzenia"""

    return flat_ext_map.get(ext, "Other")


# =========================================================
# ======================= FILES ============================
# =========================================================


def get_nonhidden_files(path: Path) -> List[Path]:
    """Zwraca listę plików z podanej ścieżki"""
    if not path.exists() or not any(path.iterdir()):
        return []

    path = Path(path)
    filename_list: List[Path] = []

    for entry in path.iterdir():
        if entry.is_file() and not entry.name.startswith("."):
            filename_list.append(entry)

    return filename_list


def get_file_extension(file: Path) -> str:
    """Zwraca roszerzenie z pliku"""
    if not file.suffix:
        return ""
    return file.suffix[1:].lower()


def move_file(file_path: Path, destination_path: Path) -> None:
    """Przenosi plik do podanej ścieżki z pytaniem o zastąpienie."""
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
    """Zwraca słownik z przypisanymi ścieżkami plików do kategorii"""
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
    """
    Tworzy foldery z EXTENSIONS_MAP w path.
    Bezpieczne: exist_ok=True, parents=True.
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
    """
    Przeprowadza proces porządkowania plików (przenoszenia plików) zgodnie z posortowanym planem.
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
    """
    Domyślnie opcja dry run pokazuje tylko potencjalne działanie
    Funkcja łącząca całą logike komendy organize.
    1. Sprawdza istniene folderów.
    2. Sortuje pliki po rozszerzeniu
    3. Przenosi pliki do ścieżek
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
    organize_files(path, dry_run=not apply)
