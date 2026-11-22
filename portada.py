"""Portadas para TikTok / Reels / Shorts (1080x1920).

Toma un cuadro del video (sin subtítulos) y le pone el título gancho arriba,
en letras gruesas blancas con borde negro y la palabra clave en amarillo.

  python generar3d.py titanic --voz salida/voces/titanic.mp3 --sin-subs --cuadros 22
  python portada.py salida/titanic_cuadros/cuadro_22.00.jpg salida/portada_titanic.jpg \
      "¿POR QUÉ SE" "*HUNDIÓ?"

Cada argumento después de las rutas es una línea; si empieza con * va en amarillo.
"""
import sys
from PIL import Image, ImageDraw, ImageFont

ANCHO, ALTO = 1080, 1920
FUENTE = "fuentes/Anton-Regular.ttf"
AMARILLO = (255, 214, 0)


def portada(cuadro, salida, lineas, y0=150):
    im = Image.open(cuadro).convert("RGB").resize((ANCHO, ALTO))
    # degradado oscuro arriba para que el texto siempre se lea
    sombra = Image.new("L", (1, ALTO))
    for y in range(ALTO):
        sombra.putpixel((0, y), int(235 * max(0.0, 1 - y / 950) ** 1.1))
    negro = Image.new("RGB", (ANCHO, ALTO), (0, 0, 0))
    im = Image.composite(negro, im, sombra.resize((ANCHO, ALTO)))
    d = ImageDraw.Draw(im)
    y = y0
    for linea in lineas:
        amarilla = linea.startswith("*")
        txt = linea.lstrip("*")
        tam = 230
        while True:
            f = ImageFont.truetype(FUENTE, tam)
            caja = d.textbbox((0, 0), txt, font=f, stroke_width=16)
            if caja[2] - caja[0] <= ANCHO * 0.9 or tam < 60:
                break
            tam -= 6
        w = caja[2] - caja[0]
        x = (ANCHO - w) / 2 - caja[0]
        d.text((x + 8, y + 10), txt, font=f, fill=(0, 0, 0), stroke_width=16, stroke_fill=(0, 0, 0))
        d.text((x, y), txt, font=f, fill=AMARILLO if amarilla else (255, 255, 255),
               stroke_width=16, stroke_fill=(0, 0, 0))
        y += (caja[3] - caja[1]) + 10
    im.save(salida, quality=93)
    print("Portada →", salida)


if __name__ == "__main__":
    portada(sys.argv[1], sys.argv[2], sys.argv[3:])
