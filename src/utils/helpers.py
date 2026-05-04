"""Small shared helpers for paths and configuration."""

from __future__ import annotations

import os
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]


def project_path(*parts: str) -> Path:
    """Return an absolute path inside the project root."""
    return PROJECT_ROOT.joinpath(*parts)


def get_env(name: str, default: str | None = None) -> str | None:
    """Read an environment variable without hiding application logic."""
    return os.getenv(name, default)
