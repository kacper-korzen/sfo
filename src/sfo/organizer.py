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

