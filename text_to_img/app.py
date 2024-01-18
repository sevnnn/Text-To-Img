from os import scandir
from os.path import join
from re import match
from sys import platform
from typing import Annotated, Literal, Optional, Union

from fontTools.ttLib import TTFont, TTLibError
from PIL.Image import new
from PIL.ImageDraw import Draw
from PIL.ImageFont import FreeTypeFont, truetype
from rich import print
from typer import BadParameter, Option, Typer

from .callbacks import (
    generic_positive_int,
    parse_file_extensions,
    parse_file_name,
    parse_generic_text,
    parse_output_path,
)
from .enums import Color, OptionCategory, OSFontsFolder
from .tempfile import TempFile


class Text2Img(Typer):
    def __init__(self) -> None:
        self.available_fonts = self.__read_fonts_folder()
        super().__init__(name="text-to-img", pretty_exceptions_show_locals=False)
        self.__register_app_commands()

    def calculate_image_dimentions(
        self, text: str, font: FreeTypeFont
    ) -> tuple[int, int]:
        tempdraw = Draw(new("RGB", (1, 1)))

        return int(tempdraw.textlength(text, font) * 1.5), int(font.size * 1.5)

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
            raise BadParameter(f'Font named "{font_name}" was not found')

        return font

    def parse_color(
        self, color_str: str
    ) -> Union[tuple[int, int, int], tuple[int, int, int, int]]:
        color_str = color_str.strip().upper()
        result = ()

        if color_str in Color.keys():
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

        raise BadParameter(f'Cannot parse "{color_str}" to color value')

    def determine_image_mode(self, file_extension: str) -> Literal["RGBA", "RGB"]:
        tempfile = TempFile(file_extension)
        with tempfile:
            tempimage = new("RGBA", (1, 1))
            try:
                tempimage.save(tempfile.tempfile_path)
                image_mode = "RGBA"
            except:
                image_mode = "RGB"

        return image_mode

    def determine_platform(self) -> OSFontsFolder:
        match platform:
            case "linux" | "linux2":
                return OSFontsFolder.LINUX
            case "win32":
                return OSFontsFolder.WINDOWS
            case "darwin":
                return OSFontsFolder.MACOS
            case _:
                print(
                    "[yellow]:warning: Unsupported operating system. The app can"
                    " only recognize font files by their names. Plase report this"
                    f" issue on GitHub. (Detected platform: {platform})[/yellow]"
                )

                return OSFontsFolder.UNKNOWN

    def __read_fonts_folder(self) -> dict[str, str]:
        result = {}

        for fonts_folder in self.determine_platform():
            for file in scandir(fonts_folder):
                try:
                    font = TTFont(join(fonts_folder, file))

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
                    callback=generic_positive_int,
                ),
            ] = 100,
            font_name: Annotated[
                str,
                Option(
                    help='Font to use, supports file names (ex. "arial.ttf") and'
                    ' font names (ex. "Arial")',
                    rich_help_panel=OptionCategory.FONT_OPTIONS,
                    callback=parse_generic_text,
                ),
            ] = "arial.ttf",
            font_color: Annotated[
                str,
                Option(
                    help='RGB values split with "," (ex. 255,255,255) symbol, or'
                    ' a hex value starting with "#" (ex. #FFFFFF) representing the'
                    " color of the text on the image. Supports transparency by "
                    "providing 4th value (ex. 255,255,255,255 or #FFFFFFFF). Also"
                    ' supports some color words like "red", "green", "blue" etc.'
                    "If provided values are bigger then 255, they will be clamped"
                    "to said value",
                    rich_help_panel=OptionCategory.FONT_OPTIONS,
                    callback=parse_generic_text,
                ),
            ] = "255,255,255",
            background_color: Annotated[
                str,
                Option(
                    help='RGB values split with "," (ex. 255,255,255) symbol, or'
                    ' a hex value starting with "#" (ex. #FFFFFF) representing the'
                    " color of the backround. Supports transparency by "
                    "providing 4th value (ex. 255,255,255,255 or #FFFFFFFF). Also"
                    ' supports some color words like "red", "green", "blue" etc.'
                    "If provided values are bigger then 255, they will be clamped"
                    "to said value",
                    rich_help_panel=OptionCategory.IMAGE_OPTIONS,
                    callback=parse_generic_text,
                ),
            ] = "0,0,0,0",
            file_extension: Annotated[
                str,
                Option(
                    help="Extension of generated file",
                    rich_help_panel=OptionCategory.FILE_OPTIONS,
                    callback=parse_file_extensions,
                ),
            ] = "png",
            output_path: Annotated[
                str,
                Option(
                    help='Relative (ex. "./output") or absolute (ex. "C:\\Users\\output")'
                    " file path, that will be used to save generated image",
                    rich_help_panel=OptionCategory.FILE_OPTIONS,
                    callback=parse_output_path,
                ),
            ] = ".",
            file_name: Annotated[
                Optional[str],
                Option(
                    help="Custom file name that will be used while saving generated image."
                    " If not provided, will be parsed from the provided text",
                    rich_help_panel=OptionCategory.FILE_OPTIONS,
                    callback=parse_file_name,
                ),
            ] = None,
        ) -> None:
            full_file_name = f"{file_name or text.replace(' ', '_')}.{file_extension}"
            font = self.select_font(font_name, font_size)
            image = new(
                self.determine_image_mode(file_extension),
                self.calculate_image_dimentions(text, font),
                self.parse_color(background_color),
            )
            Draw(image).text((0, 0), text, font=font, fill=self.parse_color(font_color))
            image = image.crop(image.getbbox())
            image.save(join(output_path, full_file_name))
            print(f"[green]Generated file [bold]{full_file_name}[/bold][/green]")
