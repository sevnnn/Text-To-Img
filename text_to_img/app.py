from typer import Typer
from sys import exit
from PIL.ImageFont import FreeTypeFont, truetype
from PIL.Image import Image as ImageClass, new
from PIL.ImageDraw import Draw
from os import scandir
from fontTools.ttLib import TTLibError, TTFont

from text_to_img.colors import TRANSPARENT


class Text2Img(Typer):
    def __init__(self) -> None:
        self.available_fonts = self.__read_fonts_folder()
        super().__init__(name="text-to-img")
        self.__register_app_commands()

    def calculate_image_dimentions(
        self, text: str, font: FreeTypeFont
    ) -> tuple[int, int]:
        temp_image = new("RGB", (1, 1))
        temp_draw = Draw(temp_image)

        return int(temp_draw.textlength(text, font)), font.size

    def crop_image(self, image: ImageClass) -> ImageClass:
        bounding_box = image.getbbox()
        image = image.crop(bounding_box)

        return image

    def select_font(self, font_name: str, font_size: int) -> FreeTypeFont:
        parsed_font_name = font_name.lower()
        try:
            if parsed_font_name in self.available_fonts.keys():
                font = truetype(self.available_fonts[parsed_font_name], size=font_size)
            else:
                font = truetype(parsed_font_name, size=font_size)
        except OSError:
            print(f"Font named '{font_name}' was not found.")

            exit(1)

        return font

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
            font_size: int = 100,
            font_name: str = "arial.ttf",
        ) -> int:
            font = self.select_font(font_name, font_size)
            x, y = self.calculate_image_dimentions(text, font)
            image = new("RGBA", (x, y), TRANSPARENT)
            draw = Draw(image)
            draw.text((0, 0), text, font=font, fill=(255, 255, 255))
            image = self.crop_image(image)
            image.save(f"{text.replace(' ', '_')}.png")

            return 0
