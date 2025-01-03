from __future__ import annotations

from abc import abstractmethod, ABC
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from types import TracebackType

__all__ = [
    "BaseModule"
]


class BaseModule(ABC):
    def __init_subclass__(cls, **kwargs: any) -> None:
        if "name" not in kwargs:
            raise ValueError(f"name query parameter")

        cls.name = kwargs.pop("name")
        super().__init_subclass__(**kwargs)

    def __enter__(self) -> BaseModule:
        self.now = True
        return self

    def __exit__(self, exc_type: type, exc_val: Exception, exc_tb: 'TracebackType') -> None:
        self.now = False

    @abstractmethod
    def run(self) -> None: ...

    @staticmethod
    def print_banner(banner: str) -> None:
        from utils import gradient_colorize

        print(gradient_colorize(banner, start_color=0x5386E5, end_color=0xA1CAE3))
