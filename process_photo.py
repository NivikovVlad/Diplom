import os
from PIL import Image, ImageDraw, ImageFont

from io import BytesIO
import numpy as np
import cv2

def remove_metadata(image_path):
    # Удаление метаданных из фотографии
    pillow_image = Image.fromarray(cv2.imdecode(np.fromfile(image_path, dtype=np.uint8), cv2.IMREAD_COLOR))
    pillow_image.save(image_path)

def add_caption(image_path, caption):
    # Добавление подписи к фотографии
    image = Image.open(image_path)
    draw = ImageDraw.Draw(image)
    draw.text((100, 100), caption, fill='green', font_size=30)
    image.save(image_path)