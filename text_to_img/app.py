from typing import Annotated, Union
from typer import Typer, Option
from PIL.ImageFont import FreeTypeFont, truetype
from PIL.Image import Image as ImageClass, new
from PIL.ImageDraw import Draw
from os import scandir
from fontTools.ttLib import TTLibError, TTFont
from rich import print
from re import match


from .colors import TRANSPARENT


class Text2Img(Typer):
    def __init__(self) -> None:
        self.available_fonts = self.__read_fonts_folder()
        super().__init__(name="text-to-img", pretty_exceptions_show_locals=False)
        self.__register_app_commands()

    def calculate_image_dimentions(
        self, text: str, font: FreeTypeFont
    ) -> tuple[int, int]:
        temp_draw = Draw(new("RGB", (1, 1)))

        return int(temp_draw.textlength(text, font)), font.size

    def select_font(self, font_name: str, font_size: int) -> FreeTypeFont:
        parsed_font_name = font_name.lower()
        try:
            font = truetype(
                self.available_fonts[parsed_font_name]
                if parsed_font_name in self.available_fonts.keys()
                else parsed_font_name,
                size=font_size,
            )
        except OSError:
            print(
                f":no_entry: [bold red]Font named '{font_name}' was not found.[/bold red]"
            )

            exit(1)

        return font

    def parse_color(
        self, color_str: str
    ) -> Union[tuple[int, int, int], tuple[int, int, int, int]]:
        color_str = color_str.strip()
        result = ()

        if match(
            "^\\d\\d?\\d?\\s*,\\s*\\d\\d?\\d?\\s*,\\s*\\d\\d?\\d?(?:\\s*,\\s*\\d\\d?\\d?)?$",
            color_str,
        ):
            for color_value in color_str.split(","):
                color_value = int(color_value)
                if color_value > 255:
                    color_value = 255

                result += (color_value,)

            return result  # type: ignore

        if match("^#(?:[0-9a-fA-F]{8}|[0-9a-fA-F]{6})$", color_str):
            color_str = color_str[1:]
            for color_value in [
                color_str[i : i + 2] for i in range(0, len(color_str), 2)
            ]:
                color_value = int(color_value, base=16)
                if color_value > 255:
                    color_value = 255

                result += (color_value,)

            return result  # type: ignore

        print(
            f':no_entry: [bold red]Cannot parse "{color_str}" to color value[/bold red]'
        )

        exit(1)

    def __read_fonts_folder(self) -> dict[str, str]:
        result = {}

        for file in scandir("C:\\Windows\\Fonts"):
            try:
                font = TTFont(f"C:\\Windows\\Fonts\\{file.name}")

                result[font["name"].getDebugName(4).lower()] = file.name  # type: ignore
            except TTLibError:
                continue

        return result

    def __register_app_commands(self) -> None:
        @self.command()
        def main(
            text: str,
            font_size: Annotated[
                int,
                Option(
                    help="Font size in pixels",
                    rich_help_panel="Font options",
                ),
            ] = 100,
            font_name: Annotated[
                str,
                Option(
                    help='Font to use, supports file names (ex. "arial.ttf") and font names (ex."Arial")',
                    rich_help_panel="Font options",
                ),
            ] = "arial.ttf",
            font_color: Annotated[
                str,
                Option(
                    help='RGB values split with "," (ex. 255,255,255) symbol, or a hex value starting '
                    'with "#" (ex. #FFFFFF) representing the color of the text on the image. Supports '
                    "transparency by providing 4th value (ex. 255,255,255,255 or #FFFFFFFF)",
                    rich_help_panel="Font options",
                ),
            ] = "255,255,255",
        ) -> int:
            font = self.select_font(font_name, font_size)
            width, height = self.calculate_image_dimentions(text, font)
            image = new("RGBA", (width, height), TRANSPARENT)
            Draw(image).text((0, 0), text, font=font, fill=self.parse_color(font_color))
            image = image.crop(image.getbbox())
            image.save(f"{text.replace(' ', '_')}.png")

            return 0
