"""Título grande con relieve y subtítulos palabra por palabra."""
from functools import lru_cache
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

FUENTES = [
    Path(__file__).resolve().parent.parent / "fuentes" / "titulo.ttf",  # pon aquí tu fuente
    Path("/usr/share/fonts/opentype/inter/Inter-Black.otf"),
    Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"),
]


@lru_cache(maxsize=64)
def fuente(tam):
    for f in FUENTES:
        if f.exists():
            return ImageFont.truetype(str(f), tam)
    return ImageFont.load_default(tam)


def _medir(txt, f, borde):
    x0, y0, x1, y1 = ImageDraw.Draw(Image.new("L", (1, 1))).textbbox((0, 0), txt, font=f, stroke_width=borde)
    return x1 - x0, y1 - y0, x0, y0


def titulo(lineas, ancho_max=1000):
    """lineas: lista de (texto, color). Devuelve una imagen RGBA."""
    capas = []
    for txt, color in lineas:
        txt = txt.upper()
        tam = 150
        while tam > 50:
            f = fuente(tam)
            w, h, ox, oy = _medir(txt, f, 14)
            if w <= ancho_max:
                break
            tam -= 6
        relieve = max(8, tam // 14)
        im = Image.new("RGBA", (w + 20, h + relieve + 20), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        for k in range(relieve, 0, -2):  # extrusión 3D hacia abajo
            d.text((10 - ox, 10 - oy + k), txt, font=f, fill=(20, 16, 20), stroke_width=14, stroke_fill=(20, 16, 20))
        d.text((10 - ox, 10 - oy), txt, font=f, fill=color, stroke_width=14, stroke_fill=(20, 16, 20))
        capas.append(im)
    total_h = sum(c.height for c in capas) - 18 * (len(capas) - 1)
    out = Image.new("RGBA", (max(c.width for c in capas), total_h), (0, 0, 0, 0))
    y = 0
    for c in capas:
        out.alpha_composite(c, ((out.width - c.width) // 2, y))
        y += c.height - 18
    return out


@lru_cache(maxsize=512)
def subtitulo(palabras, activa, tam=96, ancho_max=1000):
    """Grupo de palabras; la activa va en amarillo y un poco más grande."""
    f, fa = fuente(tam), fuente(int(tam * 1.12))
    piezas = []
    for i, p in enumerate(palabras):
        ff = fa if i == activa else f
        w, h, ox, oy = _medir(p, ff, 12)
        piezas.append((p, ff, w, h, ox, oy, i == activa))
    esp = tam // 4
    w_tot = sum(p[2] for p in piezas) + esp * (len(piezas) - 1)
    h_max = max(p[3] for p in piezas)
    im = Image.new("RGBA", (w_tot + 20, h_max + 30), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    x = 10
    for p, ff, w, h, ox, oy, act in piezas:
        y = 10 + (h_max - h)
        d.text((x - ox, y - oy + 8), p, font=ff, fill=(0, 0, 0), stroke_width=12, stroke_fill=(0, 0, 0))
        d.text((x - ox, y - oy), p, font=ff, fill=(255, 214, 10) if act else (255, 255, 255),
               stroke_width=12, stroke_fill=(15, 12, 15))
        x += w + esp
    if im.width > ancho_max:
        k = ancho_max / im.width
        im = im.resize((ancho_max, int(im.height * k)), Image.LANCZOS)
    return im
