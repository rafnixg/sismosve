"""Application version shared by the API and release tooling."""
from pathlib import Path

__version__ = (Path(__file__).resolve().parents[1] / 'VERSION').read_text(encoding='ascii').strip()
