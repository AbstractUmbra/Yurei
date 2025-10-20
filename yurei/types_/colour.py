from typing import TypedDict

__all__ = ("Colour",)


class Colour(TypedDict):
    r: float
    g: float
    b: float
    a: float
