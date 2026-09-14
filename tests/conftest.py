"""Boundary tests use temporary state and never permit external network connections."""
import socket
import asyncio
import sys
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "src")]


@pytest.fixture
def no_network(monkeypatch):
    # Windows creates an internal socket pair when initializing an event loop.
    # Initialize before the guard; application/test work remains network-blocked.
    loop = asyncio.new_event_loop()
    def denied(*args, **kwargs):
        raise AssertionError("Network access is forbidden in boundary tests")
    monkeypatch.setattr(socket.socket, "connect", denied)
    monkeypatch.setattr(socket, "create_connection", denied)
    yield loop
    loop.close()
