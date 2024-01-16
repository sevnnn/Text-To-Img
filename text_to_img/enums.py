from enum import Enum


class Color(tuple[int, int, int], Enum):
    BLACK = (0, 0, 0)
    BLUE = (0, 0, 255)
    GREEN = (0, 255, 0)
    CYAN = (0, 255, 255)
    RED = (255, 0, 0)
    PINK = (255, 0, 255)
    YELLOW = (255, 255, 0)
    WHITE = (255, 255, 255)

    @classmethod
    def keys(cls) -> list[str]:
        return [element.name for element in cls]


class OptionCategory(str, Enum):
    FONT_OPTIONS = "Font options"
    IMAGE_OPTIONS = "Image options"
    FILE_OPTIONS = "File Options"
