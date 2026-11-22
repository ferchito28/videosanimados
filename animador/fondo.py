"""Fondos verticales 1080x1920 dibujados por código, o una imagen propia."""
import random
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

W, H = 1080, 1920
PISO = 1450


def _gradiente(c1, c2):
    a = np.linspace(0, 1, H)[:, None, None]
    arr = (np.array(c1)[None, None] * (1 - a) + np.array(c2)[None, None] * a)
    arr = np.repeat(arr, W, axis=1).astype(np.uint8)
    return Image.fromarray(arr, "RGB")


def _vineta(im):
    y, x = np.mgrid[0:H, 0:W]
    r = np.sqrt(((x - W / 2) / (W * 0.75)) ** 2 + ((y - H * 0.55) / (H * 0.7)) ** 2)
    f = np.clip(1.08 - 0.55 * r ** 2, 0.45, 1.0)
    arriba = np.clip(0.55 + y / 900, 0.55, 1.0)  # oscurece la zona del título
    arr = np.asarray(im).astype(np.float32) * (f * arriba)[..., None]
    return Image.fromarray(arr.clip(0, 255).astype(np.uint8), "RGB")


def _oficina(d, rnd):
    d.rectangle([0, 1120, W, PISO], fill=(122, 74, 46))
    for x in range(30, W, 260):
        d.rectangle([x, 1160, x + 220, PISO - 40], outline=(90, 52, 32), width=8)
    for i, y in enumerate(range(PISO, H, 70)):
        d.rectangle([0, y, W, y + 70], fill=(132, 86, 50) if i % 2 else (112, 70, 40))
        for x in range(-200 + (i % 3) * 140, W, 420):
            d.line([x, y, x, y + 70], fill=(80, 50, 30), width=4)
    d.rectangle([640, 560, 990, 1060], fill=(150, 205, 235), outline=(70, 44, 28), width=18)
    d.line([815, 560, 815, 1060], fill=(70, 44, 28), width=14)
    d.line([640, 810, 990, 810], fill=(70, 44, 28), width=14)
    d.rectangle([100, 640, 440, 900], fill=(232, 214, 170), outline=(92, 60, 30), width=16)
    for _ in range(6):
        x, y = rnd.randint(130, 390), rnd.randint(670, 850)
        d.ellipse([x, y, x + 50, y + 30], fill=(150, 170, 120))


def _campo(d, rnd):
    d.ellipse([760, 260, 960, 460], fill=(255, 226, 120))
    for _ in range(5):
        x, y = rnd.randint(-100, W), rnd.randint(450, 900)
        for k in range(4):
            d.ellipse([x + k * 70, y - (k % 2) * 30, x + k * 70 + 140, y + 80], fill=(255, 255, 255))
    d.ellipse([-400, 1180, 700, 1700], fill=(124, 176, 98))
    d.ellipse([400, 1220, 1500, 1750], fill=(108, 160, 84))
    d.rectangle([0, PISO, W, H], fill=(86, 150, 60))
    for x in (120, 900):
        d.rectangle([x - 25, 1100, x + 25, PISO + 20], fill=(100, 66, 40), outline=(40, 30, 20), width=8)
        d.ellipse([x - 170, 860, x + 170, 1180], fill=(60, 130, 60), outline=(30, 60, 30), width=10)
    for _ in range(500):
        x, y = rnd.randint(0, W), rnd.randint(PISO, H)
        d.line([x, y, x + rnd.randint(-8, 8), y - rnd.randint(18, 40)], fill=(60, 120, 44), width=4)


def _noche(d, rnd):
    for _ in range(160):
        x, y, r = rnd.randint(0, W), rnd.randint(0, 1200), rnd.choice((2, 3, 4))
        d.ellipse([x - r, y - r, x + r, y + r], fill=(255, 250, 220))
    d.ellipse([720, 330, 940, 550], fill=(246, 240, 205))
    d.ellipse([-300, 1200, 800, 1700], fill=(30, 44, 80))
    d.ellipse([350, 1250, 1450, 1750], fill=(24, 36, 66))
    d.rectangle([0, PISO, W, H], fill=(36, 58, 44))
    for _ in range(300):
        x, y = rnd.randint(0, W), rnd.randint(PISO, H)
        d.line([x, y, x, y - rnd.randint(16, 36)], fill=(26, 44, 32), width=4)


def _ciudad(d, rnd):
    x = -40
    while x < W:
        w, h = rnd.randint(150, 260), rnd.randint(450, 900)
        col = rnd.choice([(180, 120, 90), (140, 110, 130), (200, 160, 110), (120, 130, 150)])
        d.rectangle([x, PISO - h, x + w, PISO], fill=col, outline=(50, 40, 40), width=8)
        for wy in range(PISO - h + 40, PISO - 60, 90):
            for wx in range(x + 25, x + w - 40, 60):
                d.rectangle([wx, wy, wx + 34, wy + 50],
                            fill=(255, 225, 140) if rnd.random() < 0.4 else (70, 70, 90))
        x += w + rnd.randint(-10, 20)
    d.rectangle([0, PISO, W, PISO + 120], fill=(170, 165, 160))
    d.rectangle([0, PISO + 120, W, H], fill=(80, 80, 86))
    for x in range(0, W, 220):
        d.rectangle([x, 1700, x + 120, 1720], fill=(240, 220, 120))


def _calor(d, rnd):
    d.ellipse([290, 380, 790, 880], fill=(255, 236, 120))
    d.ellipse([340, 430, 740, 830], fill=(255, 250, 190))
    for x0, y0, x1, y1, col in ((-500, 1250, 700, 1700, (236, 170, 90)), (300, 1300, 1600, 1750, (222, 150, 74))):
        d.ellipse([x0, y0, x1, y1], fill=col)
    d.rectangle([0, PISO, W, H], fill=(240, 190, 110))
    for _ in range(120):
        x, y = rnd.randint(0, W), rnd.randint(PISO, H)
        d.ellipse([x, y, x + 10, y + 6], fill=(214, 160, 86))
    for cx, base, alto in ((130, PISO + 30, 360), (960, PISO + 10, 280)):
        verde, borde = (80, 150, 70), (30, 60, 30)
        d.rounded_rectangle([cx - 38, base - alto, cx + 38, base], radius=38, fill=verde, outline=borde, width=8)
        d.rounded_rectangle([cx - 110, base - alto + 90, cx - 60, base - alto + 220], radius=25, fill=verde, outline=borde, width=8)
        d.rectangle([cx - 80, base - alto + 190, cx - 30, base - alto + 220], fill=verde)
        d.rounded_rectangle([cx + 60, base - alto + 130, cx + 110, base - alto + 240], radius=25, fill=verde, outline=borde, width=8)
        d.rectangle([cx + 30, base - alto + 210, cx + 80, base - alto + 240], fill=verde)


TEMAS = {
    "calor": ((255, 140, 50), (255, 214, 140), _calor),
    "oficina": ((214, 190, 140), (186, 158, 110), _oficina),
    "campo": ((120, 196, 240), (214, 238, 255), _campo),
    "noche": ((10, 20, 60), (44, 64, 120), _noche),
    "ciudad": ((242, 160, 100), (250, 220, 160), _ciudad),
}


def crear(nombre, base=Path("."), semilla=7):
    if nombre in TEMAS:
        c1, c2, fn = TEMAS[nombre]
        im = _gradiente(c1, c2)
        fn(ImageDraw.Draw(im), random.Random(semilla))
    else:  # ruta a una imagen propia: se recorta para cubrir 9:16
        src = Image.open(base / nombre).convert("RGB")
        k = max(W / src.width, H / src.height)
        src = src.resize((int(src.width * k) + 1, int(src.height * k) + 1), Image.LANCZOS)
        l, t = (src.width - W) // 2, (src.height - H) // 2
        im = src.crop((l, t, l + W, t + H))
    return _vineta(im)
