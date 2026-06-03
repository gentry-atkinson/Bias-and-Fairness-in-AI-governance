"""Dataset loading helpers."""

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"
EXTERNAL_DATA_DIR = PROJECT_ROOT / "data" / "external"


def get_raw_data_path(filename: str) -> Path:
    """Return the path to a file stored in data/raw."""

    return RAW_DATA_DIR / filename


def get_external_data_path(filename: str) -> Path:
    """Return the path to a file stored in data/external."""

    return EXTERNAL_DATA_DIR / filename