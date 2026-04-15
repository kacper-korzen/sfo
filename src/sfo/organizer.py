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


