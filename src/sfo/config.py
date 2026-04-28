from typing import Dict, List

# IMPORTANT! Keep the same structure for EXTENSIONS_MAP
EXTENSIONS_MAP: Dict[str, List[str]] = {
    "Images": ["jpg", "jpeg", "png", "webp"],
    "Documents": ["pdf", "docx", "txt", "doc"],
    "Videos": ["mp4"],
    "Archives": ["zip"],
    "Other": [],
}

SORTED_DIR_NAME: str = "sorted"
BACKUP_NAME: str = "sfo_backup"
AUTO_BACKUP: bool = False
