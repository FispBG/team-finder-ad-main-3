# Стандартные библиотеки
import re
from urllib.parse import urlparse
import io
import random

# Сторонние библиотеки
from django import forms
from django.core.files.base import ContentFile
from django.contrib.auth import get_user_model
from PIL import Image, ImageDraw, ImageFont


AVATAR_IMAGE_SIZE = 200
AVATAR_FONT_SIZE = 100
AVATAR_TEXT_Y_OFFSET = 10
DEFAULT_TEXT_WIDTH = 70
DEFAULT_TEXT_HEIGHT = 100

COLOR_WHITE = (255, 255, 255)
COLOR_BLUE = (41, 128, 185)
COLOR_GREEN = (39, 174, 96)
COLOR_PURPLE = (142, 68, 173)
COLOR_ORANGE = (230, 126, 34)
COLOR_RED = (192, 57, 43)
COLOR_DARK_BLUE = (44, 62, 80)

AVATAR_BG_COLORS = [
    COLOR_BLUE,
    COLOR_GREEN,
    COLOR_PURPLE,
    COLOR_ORANGE,
    COLOR_RED,
    COLOR_DARK_BLUE,
]


def validate_github(url):
    """Проверка, что предоставленная ссылка ведет на Github."""
    if url:
        parsed = urlparse(url)
        if 'github.com' not in parsed.netloc.lower():
            raise forms.ValidationError("Ссылка должна вести именно на Github.")
    return url


def validate_phone_number(phone, exclude_pk=None):
    """Проверяем, что номер телефона соответствует формату и не занят другим пользователем."""
    if not phone:
        return phone

    if not re.match(r'^\+7\d{10}$|^8\d{10}$', phone):
        raise forms.ValidationError(
            "Номер телефона должен быть в формате 8XXXXXXXXXX или +7XXXXXXXXXX."
        )

    if phone.startswith('8'):
        normalized = '+7' + phone[1:]
    else:
        normalized = phone

    User = get_user_model()

    qs = User.objects.filter(phone=normalized)
    if exclude_pk:
        qs = qs.exclude(pk=exclude_pk)

    if phone.startswith('+7'):
        alt_qs = User.objects.filter(phone='8' + phone[2:])
    else:
        alt_qs = User.objects.filter(phone='+7' + phone[1:])

    if exclude_pk:
        alt_qs = alt_qs.exclude(pk=exclude_pk)

    qs = qs | alt_qs
    if qs.exists():
        raise forms.ValidationError("Пользователь с таким номером телефона уже существует.")

    return phone


def generate_default_avatar(name):
    """Генерирует аватарку с первой буквой имени пользователя."""
    if not name:
        return None, None

    first_letter = name[0].upper()
    bg_color = random.choice(AVATAR_BG_COLORS)

    img = Image.new("RGB", (AVATAR_IMAGE_SIZE, AVATAR_IMAGE_SIZE), color=bg_color)
    draw = ImageDraw.Draw(img)

    try:
        font = ImageFont.truetype("Arial.ttf", AVATAR_FONT_SIZE)
    except IOError:
        font = ImageFont.load_default()

    if hasattr(draw, "textsize"):
        text_width, text_height = draw.textsize(first_letter, font=font)
    elif hasattr(draw, "textbbox"):
        bbox = draw.textbbox((0, 0), first_letter, font=font)
        text_width, text_height = bbox[2] - bbox[0], bbox[3] - bbox[1]
    else:
        text_width, text_height = (DEFAULT_TEXT_WIDTH, DEFAULT_TEXT_HEIGHT)

    position = (
        (AVATAR_IMAGE_SIZE - text_width) / 2,
        (AVATAR_IMAGE_SIZE - text_height) / 2 - AVATAR_TEXT_Y_OFFSET,
    )
    draw.text(position, first_letter, fill=COLOR_WHITE, font=font)

    buffer = io.BytesIO()
    img.save(buffer, format="PNG")

    filename = f"avatar_{random.randint(1000, 9999)}.png"
    return filename, ContentFile(buffer.getvalue())
