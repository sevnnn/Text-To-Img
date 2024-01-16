from tempfile import TemporaryFile
from typing import Annotated, Literal, Union
from typer import Typer, Option
from PIL.ImageFont import FreeTypeFont, truetype
from PIL.Image import new
from PIL.ImageDraw import Draw
from os import scandir
from fontTools.ttLib import TTLibError, TTFont
from rich import print
from re import match


from .enums import Color, OptionCategory


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

        if color_str.upper() in Color.keys():
            return Color[color_str]

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

    def parse_file_extensions(self, file_extension: str) -> str:
        file_extension = file_extension.strip().lower()
        if file_extension[0] == ".":
            file_extension = file_extension[1:]

        with TemporaryFile(
            suffix=f".{file_extension}", delete_on_close=True
        ) as tempfile:
            temp_image = new("RGB", (1, 1))
            try:
                temp_image.save(tempfile.name)
            except ValueError:
                print(
                    f':no_entry: [bold red]".{file_extension}" is not a valid file extension[/bold red]'
                )

                exit(1)

        return file_extension

    def determine_image_mode(self, file_name: str) -> Literal["RGBA", "RGB"]:
        with TemporaryFile(suffix=f"{file_name}", delete_on_close=True) as tempfile:
            temp_image = new("RGBA", (1, 1))
            try:
                temp_image.save(tempfile.name)

                return "RGBA"
            except:
                return "RGB"

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
                    rich_help_panel=OptionCategory.FONT_OPTIONS,
                ),
            ] = 100,
            font_name: Annotated[
                str,
                Option(
                    help='Font to use, supports file names (ex. "arial.ttf") and'
                    ' font names (ex. "Arial")',
                    rich_help_panel=OptionCategory.FONT_OPTIONS,
                ),
            ] = "arial.ttf",
            font_color: Annotated[
                str,
                Option(
                    help='RGB values split with "," (ex. 255,255,255) symbol, or'
                    ' a hex value starting with "#" (ex. #FFFFFF) representing the'
                    " color of the text on the image. Supports transparency by "
                    "providing 4th value (ex. 255,255,255,255 or #FFFFFFFF). Also"
                    ' supports some color words like "red", "green", "blue" etc.',
                    rich_help_panel=OptionCategory.FONT_OPTIONS,
                ),
            ] = "255,255,255",
            background_color: Annotated[
                str,
                Option(
                    help='RGB values split with "," (ex. 255,255,255) symbol, or'
                    ' a hex value starting with "#" (ex. #FFFFFF) representing the'
                    " color of the backround. Supports transparency by "
                    "providing 4th value (ex. 255,255,255,255 or #FFFFFFFF). Also"
                    ' supports some color words like "red", "green", "blue" etc.',
                    rich_help_panel=OptionCategory.IMAGE_OPTIONS,
                ),
            ] = "0,0,0,0",
            file_extension: Annotated[
                str, Option(help="Extension of generated file")
            ] = "png",
        ) -> None:
            full_file_name = (
                f"{text.replace(' ', '_')}.{self.parse_file_extensions(file_extension)}"
            )
            font = self.select_font(font_name, font_size)
            image = new(
                self.determine_image_mode(full_file_name),
                self.calculate_image_dimentions(text, font),
                self.parse_color(background_color),
            )
            Draw(image).text((0, 0), text, font=font, fill=self.parse_color(font_color))
            image = image.crop(image.getbbox())
            image.save(full_file_name)
            print(f"[green]Generated file [bold]{full_file_name}[/bold][/green]")
