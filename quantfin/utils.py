"""This module provides utilities."""
from enum import Enum
from typing import Any, List


class ListEnum(Enum):
    """This class provides a method to list enums values."""

    @classmethod
    def list(cls) -> List[Any]:
        return list(map(lambda c: c.value, cls))
