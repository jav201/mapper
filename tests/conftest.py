"""Shared pytest fixtures for mapper tests."""
from __future__ import annotations

import pytest

from mapper.store import MapStore


@pytest.fixture
def tmp_store(tmp_path):
    """A MapStore backed by a temporary workspace."""
    ws = tmp_path / "workspace"
    return MapStore(ws)
