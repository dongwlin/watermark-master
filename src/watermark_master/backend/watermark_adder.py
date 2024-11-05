from PIL import Image, ImageDraw, ImageFont, ImageFile

class WatermarkAdder:
    def __init__(self):
        self.file_paths: list[str] = []

    def add_watermark(self, img_path: str, text: str, font_size: float) -> ImageFile.ImageFile:
        image = Image.open(img_path)
        draw = ImageDraw.Draw(image)
        font = ImageFont.load_default(font_size)
        draw.text((10, 10), text, font=font, fill=(255, 255, 255))
        return image
