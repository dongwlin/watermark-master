from PIL import Image, ImageDraw, ImageFont, ImageFile


class WatermarkAdder:
    def __init__(self):
        self.position = (10, 10)
        self.font_size = 20
        self.font_color = (255, 255, 255)

    def set_position(self, position: tuple[int, int]):
        self.position = position

    def set_font_size(self, size: float):
        self.font_size = size

    def set_font_color(self, color: tuple[int, int, int]):
        self.font_color = color

    def apply(self, img_path: str, text: str) -> ImageFile.ImageFile:
        image = Image.open(img_path)
        draw = ImageDraw.Draw(image)
        font = ImageFont.load_default(self.font_size)
        draw.text(self.position, text, font=font, fill=self.font_color)
        return image
