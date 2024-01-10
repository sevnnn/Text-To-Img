from typer import Typer
from PIL import Image, ImageDraw, ImageFont

app = Typer()


@app.command()
def main(text: str, font_size: int = 100) -> None:
    temp_image = Image.new("RGB", (1, 1))
    temp_draw = ImageDraw.Draw(temp_image)
    final_font = ImageFont.truetype("arial.ttf", size=font_size)
    width = temp_draw.textlength(text, final_font)
    x = width // 2
    y = font_size // 2

    final_image = Image.new("RGBA", (int(width) * 2, font_size * 2), (0, 0, 0, 0))
    final_draw = ImageDraw.Draw(final_image)
    final_draw.text((x, y), text, font=final_font, fill=(255, 255, 255))
    bounding_box = final_image.getbbox()
    final_image = final_image.crop(bounding_box)
    final_image.save("test.png")


if __name__ == "__main__":
    app()
