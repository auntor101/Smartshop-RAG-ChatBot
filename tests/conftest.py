"""Pytest fixtures shared across the test suite."""

from __future__ import annotations

import pytest

from src.config import reset_settings


@pytest.fixture(autouse=True)
def _reset_cached_settings() -> None:
    """Avoid leaked env between tests that toggle ``API_TOKEN`` / security flags."""
    reset_settings()
    yield
    reset_settings()
