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


def _azulejo(d, x, y, t):
    d.rectangle([x, y, x + t, y + t], fill=(246, 242, 232), outline=(200, 196, 186), width=2)
    c, azul = t // 2, (52, 74, 160)
    for dx, dy in ((0, -1), (0, 1), (-1, 0), (1, 0)):
        px, py = x + c + dx * t * 0.24, y + c + dy * t * 0.24
        d.ellipse([px - t * 0.13, py - t * 0.13, px + t * 0.13, py + t * 0.13], fill=azul)
    d.ellipse([x + c - t * 0.1, y + c - t * 0.1, x + c + t * 0.1, y + c + t * 0.1], fill=(236, 186, 60))
    for qx, qy in ((x, y), (x + t, y), (x, y + t), (x + t, y + t)):
        d.pieslice([qx - t * 0.18, qy - t * 0.18, qx + t * 0.18, qy + t * 0.18], 0, 360, fill=azul)


def _cocina(d, rnd):
    madera, oscura = (122, 78, 46), (84, 52, 30)
    for y in (0, 70):  # vigas
        d.rectangle([0, y, W, y + 52], fill=madera, outline=oscura, width=6)
    # ventana
    d.rectangle([330, 430, 820, 1010], fill=(150, 205, 238))
    d.rectangle([330, 800, 820, 1010], fill=(226, 196, 156))
    d.rectangle([330, 420, 820, 1020], outline=madera, width=26)
    d.line([575, 420, 575, 1020], fill=madera, width=18)
    d.rectangle([300, 1000, 850, 1050], fill=madera, outline=oscura, width=6)
    # cactus en maceta
    d.rounded_rectangle([395, 860, 445, 990], radius=25, fill=(92, 150, 80), outline=(40, 70, 36), width=6)
    d.rounded_rectangle([445, 900, 480, 950], radius=16, fill=(92, 150, 80), outline=(40, 70, 36), width=6)
    d.polygon([370, 960, 470, 960, 458, 1002, 382, 1002], fill=(196, 110, 70), outline=(110, 60, 36))
    # barra con cazuelas
    d.rectangle([0, 190, 300, 214], fill=oscura)
    for cx, r in ((60, 70), (190, 85)):
        d.line([cx, 214, cx, 280], fill=(60, 50, 40), width=6)
        d.ellipse([cx - r, 280, cx + r, 280 + r * 2.2], fill=(186, 104, 64), outline=(120, 62, 36), width=8)
        d.ellipse([cx - r * 0.7, 300, cx + r * 0.7, 280 + r * 1.9], fill=(170, 92, 56))
    # alacena verde menta
    menta, menta_os = (170, 214, 190), (120, 164, 140)
    d.rounded_rectangle([860, 300, 1100, 760], radius=14, fill=menta, outline=menta_os, width=8)
    d.rounded_rectangle([890, 340, 1060, 720], radius=10, outline=menta_os, width=6)
    # franja de azulejos
    t = 90
    for y in range(1060, 1300, t):
        for x in range(-20, W, t):
            _azulejo(d, x, y, t)
    # encimera y muebles
    d.rectangle([0, 1290, W, 1335], fill=(222, 190, 150), outline=(170, 136, 100), width=5)
    d.rectangle([0, 1335, W, 1720], fill=menta, outline=menta_os, width=6)
    for x in range(560, W, 260):
        d.rounded_rectangle([x, 1370, x + 230, 1690], radius=10, outline=menta_os, width=6)
        d.ellipse([x + 190, 1500, x + 214, 1524], fill=(100, 90, 80))
    # estufa
    crema = (238, 228, 206)
    d.rounded_rectangle([60, 1240, 520, 1730], radius=16, fill=crema, outline=(160, 150, 130), width=8)
    d.rectangle([60, 1240, 520, 1290], fill=(70, 70, 74))
    for x in range(110, 500, 85):
        d.ellipse([x, 1310, x + 46, 1356], fill=(90, 86, 80))
    d.rounded_rectangle([110, 1400, 470, 1660], radius=14, fill=(214, 204, 182), outline=(150, 140, 120), width=6)
    d.rounded_rectangle([160, 1450, 420, 1600], radius=10, fill=(60, 52, 48))
    d.rounded_rectangle([140, 1415, 440, 1432], radius=8, fill=(120, 110, 100))
    for x in (160, 220, 280):  # llamas
        d.polygon([x, 1240, x + 20, 1190, x + 40, 1240], fill=(80, 140, 240))
        d.polygon([x + 8, 1240, x + 20, 1200, x + 32, 1240], fill=(255, 170, 40))
    d.ellipse([120, 1200, 340, 1250], fill=(40, 40, 44), outline=(20, 20, 22), width=6)
    d.rectangle([330, 1214, 430, 1230], fill=(50, 40, 34))
    # piso de barro
    d.rectangle([0, 1720, W, H], fill=(196, 112, 82))
    for y in range(1720, H, 70):
        d.line([0, y, W, y], fill=(160, 88, 62), width=4)
    for x in range(0, W, 140):
        d.line([x, 1720, x - 40, H], fill=(160, 88, 62), width=4)


TEMAS = {
    "cocina": ((236, 206, 166), (216, 180, 138), _cocina),
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
