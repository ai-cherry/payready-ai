"""Minimal Team implementation for offline tests."""

from __future__ import annotations

from typing import Iterable, List


class Team:
    """Simple container for Agent instances."""

    def __init__(self, members: Iterable) -> None:
        self.members: List = list(members)

    def add_member(self, member) -> None:
        self.members.append(member)


__all__ = ["Team"]
