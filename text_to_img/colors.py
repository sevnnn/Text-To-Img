from enum import Enum

TRANSPARENT = (0, 0, 0, 0)


class Color(tuple[int, int, int], Enum):
    BLACK = (0, 0, 0)
    BLUE = (0, 0, 255)
    GREEN = (0, 255, 0)
    CYAN = (0, 255, 255)
    RED = (255, 0, 0)
    PINK = (255, 0, 255)
    YELLOW = (255, 255, 0)
    WHITE = (255, 255, 255)


def add_transparency(
    color: tuple[int, int, int],
    percentage: float = 0.0,
) -> tuple[int, int, int, int]:
    return (color[0], color[1], color[2], int(255 * (percentage / 100.0)))
