import os
from PIL import Image, ImageDraw, ImageFont


def add_caption(image_path, caption):
    # Добавление подписи к фотографии
    image = Image.open(image_path)
    draw = ImageDraw.Draw(image)
    draw.text((100, 100), caption, fill='green', font_size=30)
    image.save(image_path)