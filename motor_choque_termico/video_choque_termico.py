#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
==========================================================================
  "EL CUÑADO, LA HIELERA Y EL MOTOR"  -  Short vertical 1080x1920 @ 30 fps
==========================================================================

Mito vs. realidad: echar agua con hielo a un motor sobrecalentado
(choque térmico) vs. enfriar gradualmente como el mecánico viejo.

Todo se dibuja por código con PIL + NumPy y se exporta con MoviePy.
No necesita imágenes externas. Incluye efectos de sonido sintetizados
(hielo, vapor, "CRACK", claxon...) y, opcionalmente, tu voz en off.

USO RÁPIDO
    python video_choque_termico.py                      # render completo -> choque_termico.mp4
    python video_choque_termico.py --voz narracion.mp3  # mezcla tu voz en off
    python video_choque_termico.py --frame 37.5         # guarda solo un PNG de ese segundo (para revisar)
    python video_choque_termico.py --fps 15 --salida preview.mp4   # vista previa rápida

Funciona con MoviePy 1.x y 2.x.

LÍNEA DE TIEMPO (segundos)
    Escena 1   0.0 - 12.0  Carretera, humo, hielera (gancho), cronómetro de la boda, llega Don Chuy
    Escena 2  12.0 - 26.0  Pantalla dividida: cuñado (hielo) vs. Don Chuy (esperar + agua tibia)
    Escena 3  26.0 - 42.0  Zoom microscópico: átomos expandidos (rojo) -> contracción (azul) -> grieta
    Escena 4  42.0 - 55.0  ¡CRACK! -> llegan a la boda en grúa -> pregunta para comentarios
"""

import argparse
import math
import os
import sys
from functools import lru_cache

import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageOps

# MoviePy cambió su API en la versión 2.0: soportamos ambas.
try:  # MoviePy 2.x
    from moviepy import VideoClip, AudioFileClip, CompositeAudioClip
    from moviepy.audio.AudioClip import AudioArrayClip
    MOVIEPY2 = True
except ImportError:  # MoviePy 1.x
    from moviepy.editor import VideoClip, AudioFileClip, CompositeAudioClip
    from moviepy.audio.AudioClip import AudioArrayClip
    MOVIEPY2 = False

# ==========================================================================
# CONFIGURACIÓN GENERAL
# ==========================================================================
W, H = 1080, 1920          # lienzo vertical 9:16
FPS = 30
DURACION = 55.0            # segundos
SR = 44100                 # frecuencia de muestreo del audio

# Tiempos de cada escena (inicio, fin)
S1 = (0.0, 12.0)
S2 = (12.0, 26.0)
S3 = (26.0, 42.0)
S4 = (42.0, 55.0)
T_CRACK = 43.0             # momento exacto del "CRACK" final
T_GRUA = 44.5              # empieza la escena de la grúa
T_CTA = 51.0               # pregunta para comentarios

# Paleta
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
YELLOW = (255, 221, 0)
RED = (235, 45, 45)
GREEN = (40, 200, 90)
BLUE = (60, 140, 255)
ORANGE = (255, 140, 0)
SKIN = (240, 192, 152)
SKIN_TAN = (205, 150, 110)
HOT = (255, 75, 35)
COLD = (70, 160, 255)

# ==========================================================================
# SUBTÍTULOS (voz en off). Las palabras entre *asteriscos* salen en amarillo.
# Cada tupla: (inicio, fin, texto)
# ==========================================================================
SUBTITULOS = [
    (0.0, 2.2, "¡Mi cuñado le está echando una *HIELERA ENTERA*..."),
    (2.2, 4.2, "...a un *motor hirviendo*!"),
    (5.0, 7.3, "Contexto: faltan *2 horas* para la boda de mi mejor amigo"),
    (7.3, 8.6, "...y nosotros llevamos *los anillos*."),
    (8.6, 10.4, "A media carretera, el coche empezó a *echar humo*."),
    (10.4, 12.0, "Y llegó *Don Chuy*, mecánico de carretera de toda la vida."),
    (12.0, 15.8, "Mi cuñado: *¡Hielo!* ¡Así se enfría más rápido!"),
    (15.8, 19.0, "Don Chuy: apágalo, abre el cofre y *espera 15 a 20 minutos*."),
    (19.0, 22.6, "Luego *agua tibia*, poquito a poco y con el motor encendido."),
    (22.6, 26.0, "Mi cuñado, obviamente... *no esperó*."),
    (26.0, 31.0, "El metal caliente está *expandido*: sus átomos vibran y se separan."),
    (31.0, 36.0, "Con hielo, la parte de afuera se *encoge de golpe*... mientras por dentro *sigue hirviendo*."),
    (36.0, 39.2, "Afuera jala, adentro empuja... *y el bloque se parte*."),
    (39.2, 42.0, "Como un *vaso caliente en agua fría*."),
    (42.0, 44.5, "*¡CRACK!*"),
    (44.5, 47.6, "Y así llegamos a la boda: *a tiempo*..."),
    (47.6, 51.0, "...pero *en grúa*."),
    (51.0, 55.0, "Te leo en *comentarios* 👇"),
]

# Textos grandes de pantalla (titulares) por tramo: (inicio, fin, texto, color)
TITULARES = [
    (0.15, 4.2, "¿UNA HIELERA\nAL MOTOR?", YELLOW),
    (5.0, 8.6, "FALTAN 2 HORAS\nPARA LA BODA", WHITE),
    (8.6, 12.0, "...Y LLEVAMOS\nLOS ANILLOS", YELLOW),
    (26.3, 31.0, "CALOR =\nMETAL EXPANDIDO", HOT),
    (31.0, 36.0, "HIELO: AFUERA SE\nENCOGE DE GOLPE", COLD),
    (36.0, 42.0, "AFUERA JALA,\nADENTRO EMPUJA", YELLOW),
    (45.0, 51.0, "LLEGAMOS\nA TIEMPO...", WHITE),
]

# ==========================================================================
# UTILIDADES MATEMÁTICAS
# ==========================================================================
def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def lerp(a, b, t):
    return a + (b - a) * t


def prog(t, t0, t1):
    """Progreso 0..1 de t dentro del intervalo [t0, t1]."""
    return clamp((t - t0) / (t1 - t0))


def ease_out(x):
    return 1 - (1 - x) ** 3


def ease_in_out(x):
    return x * x * (3 - 2 * x)


def back_out(x, k=1.9):
    """Rebote tipo 'pop' (se pasa un poco y regresa)."""
    x = x - 1
    return 1 + x * x * ((k + 1) * x + k)


def lerp_col(c1, c2, t):
    t = clamp(t)
    return tuple(int(round(lerp(a, b, t))) for a, b in zip(c1, c2))


def rot_pts(cx, cy, pts, ang_deg):
    """Rota una lista de puntos (relativos a cx, cy) y los devuelve absolutos."""
    a = math.radians(ang_deg)
    ca, sa = math.cos(a), math.sin(a)
    return [(cx + x * ca - y * sa, cy + x * sa + y * ca) for x, y in pts]


def hash01(i, salt=0):
    """Pseudo-aleatorio determinista en 0..1 (igual en cada frame)."""
    v = math.sin(i * 12.9898 + salt * 78.233) * 43758.5453
    return v - math.floor(v)


# ==========================================================================
# FUENTES Y TEXTO
# ==========================================================================
FUENTE_USUARIO = None   # se puede fijar con --fuente
FONT_CANDIDATES = [
    "Montserrat-ExtraBold.ttf", "Montserrat-Black.ttf", "Poppins-ExtraBold.ttf",
    "DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/TTF/DejaVuSans-Bold.ttf",
    "C:/Windows/Fonts/arialbd.ttf",
    "C:/Windows/Fonts/verdanab.ttf",
    "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
    "/Library/Fonts/Arial Bold.ttf",
    "arialbd.ttf", "Arial Bold.ttf", "Arial.ttf",
]


@lru_cache(maxsize=None)
def F(size):
    """Devuelve una fuente negrita del tamaño pedido (con varios respaldos)."""
    size = int(size)
    cands = ([FUENTE_USUARIO] if FUENTE_USUARIO else []) + FONT_CANDIDATES
    for p in cands:
        try:
            return ImageFont.truetype(p, size)
        except (OSError, IOError):
            continue
    try:
        return ImageFont.load_default(size=size)   # Pillow >= 10.1
    except TypeError:
        return ImageFont.load_default()


def _quitar_emoji(txt):
    """Las fuentes comunes no traen emojis: los quitamos para evitar cuadritos."""
    return "".join(ch for ch in txt if ord(ch) < 0x2190).strip()


def rich_text(d, cx, cy, txt, size, fill=WHITE, hl=YELLOW, maxw=960,
              stroke=None, stroke_fill=BLACK, lh=1.17):
    """
    Dibuja texto centrado en (cx, cy), con salto de línea automático.
    Palabras marcadas con *asteriscos* se pintan con el color `hl`.
    """
    txt = _quitar_emoji(txt)
    f = F(size)
    stroke = max(2, size // 9) if stroke is None else stroke
    space = f.getlength(" ")

    # 1) tokenizar respetando saltos de línea manuales y marcas *...*
    lineas = []
    for parrafo in txt.split("\n"):
        palabras = []
        marcado = False
        for w in parrafo.split(" "):
            if not w:
                continue
            inicia = w.startswith("*")
            if inicia:
                marcado = True
            limpio = w.replace("*", "")
            palabras.append((limpio, marcado))
            if w.endswith("*") or (w.count("*") == 2) or w.rstrip(".,!?;:").endswith("*"):
                marcado = False
        # 2) partir en líneas que quepan en maxw
        actual, ancho = [], 0
        for w, m in palabras:
            wl = f.getlength(w)
            extra = wl if not actual else ancho + space + wl
            if actual and extra > maxw:
                lineas.append(actual)
                actual, ancho = [(w, m)], wl
            else:
                actual.append((w, m))
                ancho = extra
        if actual:
            lineas.append(actual)

    # 3) dibujar
    alto_linea = size * lh
    y = cy - alto_linea * len(lineas) / 2 + alto_linea / 2
    for linea in lineas:
        anchos = [f.getlength(w) for w, _ in linea]
        total = sum(anchos) + space * (len(linea) - 1)
        x = cx - total / 2
        for (w, m), wl in zip(linea, anchos):
            d.text((x, y), w, font=f, fill=hl if m else fill, anchor="lm",
                   stroke_width=stroke, stroke_fill=stroke_fill)
            x += wl + space
        y += alto_linea


def pill(d, cx, cy, txt, size, bg, fg=WHITE, padx=34, pady=16, outline=None):
    """Etiqueta redondeada con texto centrado."""
    f = F(size)
    w = f.getlength(txt)
    box = [cx - w / 2 - padx, cy - size / 2 - pady, cx + w / 2 + padx, cy + size / 2 + pady]
    d.rounded_rectangle(box, radius=int(size / 2 + pady), fill=bg,
                        outline=outline, width=6 if outline else 0)
    d.text((cx, cy), txt, font=f, fill=fg, anchor="mm")
    return box


def name_tag(d, x, y, txt, bg, appear):
    """Etiqueta de personaje con 'pop' y triangulito apuntando hacia abajo."""
    if appear <= 0:
        return
    s = back_out(clamp(appear))
    size = int(34 * s) + 1
    if size < 8:
        return
    pill(d, x, y, txt, size, bg, padx=int(22 * s), pady=int(12 * s), outline=WHITE)
    d.polygon([(x - 14 * s, y + 28 * s), (x + 14 * s, y + 28 * s), (x, y + 48 * s)], fill=WHITE)


# ==========================================================================
# FONDOS (se generan una vez y se reutilizan)
# ==========================================================================
def vgrad(w, h, c1, c2):
    """Degradado vertical."""
    t = np.linspace(0, 1, h)[:, None, None]
    arr = np.array(c1, float)[None, None, :] * (1 - t) + np.array(c2, float)[None, None, :] * t
    arr = np.repeat(arr, w, axis=1).astype(np.uint8)
    return Image.fromarray(arr)


def draw_cactus(d, x, base, s):
    g, g2 = (60, 140, 70), (45, 110, 55)
    d.rounded_rectangle([x - 22 * s, base - 200 * s, x + 22 * s, base], radius=int(22 * s), fill=g)
    d.rounded_rectangle([x - 75 * s, base - 140 * s, x - 45 * s, base - 70 * s], radius=int(15 * s), fill=g2)
    d.rounded_rectangle([x - 75 * s, base - 90 * s, x - 15 * s, base - 65 * s], radius=int(12 * s), fill=g2)
    d.rounded_rectangle([x + 45 * s, base - 170 * s, x + 75 * s, base - 100 * s], radius=int(15 * s), fill=g2)
    d.rounded_rectangle([x + 15 * s, base - 120 * s, x + 75 * s, base - 95 * s], radius=int(12 * s), fill=g2)


@lru_cache(maxsize=1)
def bg_road():
    """Carretera en el desierto a pleno sol."""
    img = Image.new("RGB", (W, H))
    img.paste(vgrad(W, 1000, (255, 160, 80), (255, 226, 165)), (0, 0))
    img.paste(vgrad(W, H - 1000, (236, 196, 132), (204, 152, 92)), (0, 1000))
    d = ImageDraw.Draw(img, "RGBA")
    # sol con halo
    for r, a in ((260, 40), (190, 70), (140, 120)):
        d.ellipse([860 - r, 420 - r, 860 + r, 420 + r], fill=(255, 250, 200, a))
    d.ellipse([760, 320, 960, 520], fill=(255, 248, 210))
    # montañas
    d.polygon([(0, 1000), (0, 840), (160, 760), (330, 880), (480, 790), (640, 900),
               (800, 800), (960, 880), (1080, 820), (1080, 1000)], fill=(196, 120, 92))
    d.polygon([(0, 1000), (0, 920), (220, 860), (420, 940), (700, 880), (900, 950),
               (1080, 900), (1080, 1000)], fill=(170, 100, 80))
    # carretera
    d.rectangle([0, 1180, W, 1420], fill=(72, 72, 80))
    d.rectangle([0, 1186, W, 1196], fill=(235, 235, 235))
    d.rectangle([0, 1404, W, 1414], fill=(235, 235, 235))
    for x in range(-40, W, 170):
        d.rectangle([x, 1294, x + 95, 1306], fill=(250, 205, 40))
    # cactus y piedras
    draw_cactus(d, 110, 1130, 0.9)
    draw_cactus(d, 990, 1150, 0.7)
    for x, y, r in ((300, 1120, 18), (700, 1140, 12), (180, 1700, 26), (930, 1760, 20)):
        d.ellipse([x - r * 1.5, y - r, x + r * 1.5, y + r], fill=(160, 120, 80))
    return img


def draw_heart(d, cx, cy, s, col):
    d.ellipse([cx - 20 * s, cy - 14 * s, cx + 2 * s, cy + 8 * s], fill=col)
    d.ellipse([cx - 2 * s, cy - 14 * s, cx + 20 * s, cy + 8 * s], fill=col)
    d.polygon([(cx - 19 * s, cy + 1 * s), (cx + 19 * s, cy + 1 * s), (cx, cy + 22 * s)], fill=col)


@lru_cache(maxsize=1)
def bg_wedding():
    """Salón/capilla de la boda con cielo azul."""
    img = Image.new("RGB", (W, H))
    img.paste(vgrad(W, 1000, (110, 180, 255), (215, 238, 255)), (0, 0))
    img.paste(vgrad(W, H - 1000, (120, 196, 96), (80, 150, 70)), (0, 1000))
    d = ImageDraw.Draw(img, "RGBA")
    # nubes
    for cx, cy, s in ((200, 420, 1.0), (620, 330, 0.8), (930, 520, 0.7)):
        for dx, dy, r in ((-60, 10, 50), (0, -15, 65), (60, 10, 50), (0, 25, 45)):
            d.ellipse([cx + (dx - r) * s, cy + (dy - r) * s, cx + (dx + r) * s, cy + (dy + r) * s],
                      fill=(255, 255, 255, 235))
    # capilla
    d.rectangle([740, 820, 1060, 1200], fill=(250, 244, 230))
    d.polygon([(720, 830), (900, 690), (1080, 830)], fill=(200, 90, 80))
    d.rectangle([850, 540, 950, 720], fill=(250, 244, 230))
    d.polygon([(835, 550), (900, 440), (965, 550)], fill=(200, 90, 80))
    d.ellipse([880, 590, 920, 630], fill=(230, 180, 40))                 # campana
    d.rounded_rectangle([860, 1040, 940, 1200], radius=40, fill=(130, 80, 45))  # puerta
    for wx in (780, 980):
        d.rounded_rectangle([wx - 25, 900, wx + 25, 990], radius=25, fill=(150, 200, 240))
    # letrero "BODA" con corazones
    d.rounded_rectangle([780, 850, 1020, 900], radius=20, fill=(255, 120, 160))
    d.text((900, 875), "BODA", font=F(36), fill=WHITE, anchor="mm")
    draw_heart(d, 800, 873, 0.7, WHITE)
    draw_heart(d, 1000, 873, 0.7, WHITE)
    # carretera
    d.rectangle([0, 1270, W, 1430], fill=(80, 80, 88))
    for x in range(-20, W, 170):
        d.rectangle([x, 1344, x + 95, 1354], fill=(250, 250, 250))
    # flores
    for i in range(28):
        x = int(hash01(i, 3) * W)
        y = int(1460 + hash01(i, 5) * 420)
        col = [(255, 90, 120), (255, 220, 60), (255, 255, 255)][i % 3]
        d.ellipse([x - 9, y - 9, x + 9, y + 9], fill=col)
    return img


@lru_cache(maxsize=1)
def bg_split():
    """Fondo de pantalla dividida: arriba rojo (error), abajo verde (correcto)."""
    img = Image.new("RGB", (W, H))
    img.paste(vgrad(W, 860, (70, 12, 12), (130, 30, 24)), (0, 0))
    img.paste(vgrad(W, 640, (10, 60, 36), (24, 100, 56)), (0, 860))
    img.paste(vgrad(W, H - 1500, (18, 18, 24), (8, 8, 12)), (0, 1500))
    return img


@lru_cache(maxsize=1)
def bg_lab():
    """Fondo oscuro tipo laboratorio con cuadrícula para la escena microscópica."""
    img = vgrad(W, H, (10, 16, 40), (4, 6, 16))
    d = ImageDraw.Draw(img, "RGBA")
    for x in range(0, W, 60):
        d.line([(x, 0), (x, H)], fill=(80, 120, 200, 28), width=2)
    for y in range(0, H, 60):
        d.line([(0, y), (W, y)], fill=(80, 120, 200, 28), width=2)
    return img


# ==========================================================================
# PERSONAJES Y OBJETOS
# ==========================================================================
def draw_head(d, x, hy, s, kind, expr="calm", hair=(60, 40, 25)):
    """Cabeza con rasgos según el personaje."""
    r = 52 * s
    skin = SKIN_TAN if kind == "mecanico" else SKIN
    if kind == "novia":   # velo detrás de la cabeza
        d.polygon([(x - 40 * s, hy - 40 * s), (x + 40 * s, hy - 40 * s),
                   (x + 75 * s, hy + 150 * s), (x - 75 * s, hy + 150 * s)], fill=(255, 255, 255, 170))
    d.ellipse([x - r, hy - r, x + r, hy + r], fill=skin)

    # pelo / gorra
    if kind == "cunado":
        pts = [(x - 52 * s, hy - 15 * s)]
        for k in range(7):
            px = x - 52 * s + k * 104 * s / 6
            pts.append((px - 8 * s, hy - (75 if k % 2 == 0 else 50) * s))
        pts += [(x + 52 * s, hy - 15 * s), (x, hy - 40 * s)]
        d.polygon(pts, fill=(40, 25, 15))
    elif kind == "mecanico":
        d.ellipse([x - 56 * s, hy - 14 * s, x - 38 * s, hy + 18 * s], fill=(200, 200, 200))
        d.ellipse([x + 38 * s, hy - 14 * s, x + 56 * s, hy + 18 * s], fill=(200, 200, 200))
        d.chord([x - 55 * s, hy - 62 * s, x + 55 * s, hy + 12 * s], 180, 360, fill=(205, 40, 40))
        d.rounded_rectangle([x + 10 * s, hy - 28 * s, x + 85 * s, hy - 16 * s], radius=int(6 * s) + 1,
                            fill=(160, 25, 25))
        d.text((x - 6 * s, hy - 40 * s), "DC", font=F(max(8, int(22 * s))), fill=WHITE, anchor="mm")
    elif kind == "novia":
        d.chord([x - 54 * s, hy - 56 * s, x + 54 * s, hy + 10 * s], 180, 360, fill=(120, 70, 30))
        for k in range(5):
            d.ellipse([x - 40 * s + k * 18 * s, hy - 62 * s, x - 28 * s + k * 18 * s, hy - 50 * s],
                      fill=(255, 255, 255))
    else:
        d.chord([x - 54 * s, hy - 58 * s, x + 54 * s, hy + 4 * s], 180, 360, fill=hair)

    # ojos
    if kind == "cunado":   # lentes oscuros de "sabelotodo"
        d.rounded_rectangle([x - 44 * s, hy - 16 * s, x - 6 * s, hy + 6 * s], radius=int(8 * s) + 1, fill=(15, 15, 20))
        d.rounded_rectangle([x + 6 * s, hy - 16 * s, x + 44 * s, hy + 6 * s], radius=int(8 * s) + 1, fill=(15, 15, 20))
        d.line([(x - 6 * s, hy - 8 * s), (x + 6 * s, hy - 8 * s)], fill=(15, 15, 20), width=max(1, int(4 * s)))
        d.line([(x - 36 * s, hy - 12 * s), (x - 24 * s, hy - 12 * s)], fill=(255, 255, 255, 180), width=max(1, int(3 * s)))
    else:
        er = 6 * s if expr != "shock" else 9 * s
        for ex in (x - 18 * s, x + 18 * s):
            if expr == "shock":
                d.ellipse([ex - er - 4 * s, hy - 6 * s - er - 4 * s, ex + er + 4 * s, hy - 6 * s + er + 4 * s], fill=WHITE)
            d.ellipse([ex - er, hy - 6 * s - er, ex + er, hy - 6 * s + er], fill=(20, 20, 20))
        if kind == "mecanico":   # cejas canosas
            for ex in (x - 18 * s, x + 18 * s):
                d.line([(ex - 12 * s, hy - 22 * s), (ex + 12 * s, hy - 22 * s)], fill=(210, 210, 210),
                       width=max(1, int(6 * s)))

    # boca
    w = max(1, int(5 * s))
    if kind == "mecanico":
        d.ellipse([x - 30 * s, hy + 8 * s, x + 30 * s, hy + 26 * s], fill=(215, 215, 215))  # bigote
        if expr == "shock":
            d.ellipse([x - 8 * s, hy + 26 * s, x + 8 * s, hy + 40 * s], fill=(120, 30, 30))
    elif expr == "smug":
        d.arc([x - 26 * s, hy, x + 22 * s, hy + 32 * s], 15, 150, fill=(90, 30, 20), width=w)
    elif expr == "happy":
        d.chord([x - 24 * s, hy + 4 * s, x + 24 * s, hy + 36 * s], 0, 180, fill=(140, 30, 30))
    elif expr == "shock":
        d.ellipse([x - 13 * s, hy + 12 * s, x + 13 * s, hy + 40 * s], fill=(120, 30, 30))
    else:
        d.line([(x - 14 * s, hy + 22 * s), (x + 14 * s, hy + 22 * s)], fill=(90, 30, 20), width=w)


def draw_person(d, x, feet, s, kind, arm_l=-12, arm_r=12, expr="calm", shirt=None, walk=0.0):
    """
    Personaje estilo 'muñeco'. Ángulos de brazo en grados medidos desde
    'hacia abajo' (0 = colgando, 180 = arriba, positivo = hacia la derecha).
    Devuelve las posiciones de manos y cabeza para colgarles objetos.
    """
    estilos = {
        "cunado":   dict(shirt=(255, 128, 20), pants=(30, 150, 160), sleeve=(255, 128, 20)),
        "mecanico": dict(shirt=(45, 85, 165), pants=(45, 85, 165), sleeve=(45, 85, 165)),
        "padrino":  dict(shirt=(35, 35, 48), pants=(35, 35, 48), sleeve=(35, 35, 48)),
        "novia":    dict(shirt=(255, 255, 255), pants=(255, 255, 255), sleeve=(255, 255, 255)),
        "invitado": dict(shirt=shirt or (90, 140, 230), pants=(50, 50, 70), sleeve=shirt or (90, 140, 230)),
    }
    st = estilos[kind]
    sh = feet - 250 * s          # altura de hombros
    hip = feet - 120 * s
    skin = SKIN_TAN if kind == "mecanico" else SKIN

    # --- piernas / vestido
    if kind == "novia":
        d.polygon([(x - 30 * s, sh), (x + 30 * s, sh), (x + 85 * s, feet), (x - 85 * s, feet)], fill=(255, 255, 255))
        d.polygon([(x - 30 * s, sh), (x + 30 * s, sh), (x + 85 * s, feet), (x - 85 * s, feet)],
                  outline=(220, 220, 235), width=max(1, int(4 * s)))
    else:
        for side, ph in ((-1, 1), (1, -1)):
            fx = x + side * 22 * s + ph * walk * 30 * s
            leg_col = skin if kind == "cunado" else st["pants"]
            d.line([(x + side * 18 * s, hip), (fx, feet - 6 * s)], fill=leg_col, width=max(2, int(28 * s)))
            if kind == "cunado":   # shorts
                d.line([(x + side * 18 * s, hip), (lerp(x + side * 18 * s, fx, 0.45), lerp(hip, feet, 0.45))],
                       fill=st["pants"], width=max(2, int(34 * s)))
            d.ellipse([fx - 22 * s, feet - 14 * s, fx + 28 * s, feet + 6 * s], fill=(30, 30, 30))
        # torso
        d.rounded_rectangle([x - 48 * s, sh - 15 * s, x + 48 * s, hip + 12 * s], radius=max(1, int(28 * s)),
                            fill=st["shirt"])
        if kind == "cunado":   # camisa floreada
            for k in range(6):
                fx = x - 30 * s + (k % 3) * 30 * s
                fy = sh + 15 * s + (k // 3) * 55 * s
                d.ellipse([fx - 9 * s, fy - 9 * s, fx + 9 * s, fy + 9 * s], fill=(255, 235, 120))
        elif kind == "mecanico":   # overol con tirantes y trapo
            d.rectangle([x - 34 * s, sh - 10 * s, x - 20 * s, hip], fill=(30, 60, 125))
            d.rectangle([x + 20 * s, sh - 10 * s, x + 34 * s, hip], fill=(30, 60, 125))
            d.rectangle([x + 30 * s, hip - 20 * s, x + 52 * s, hip + 30 * s], fill=(200, 60, 50))
        elif kind == "padrino":    # camisa blanca y corbata
            d.polygon([(x - 18 * s, sh - 14 * s), (x + 18 * s, sh - 14 * s), (x, sh + 50 * s)], fill=WHITE)
            d.polygon([(x - 6 * s, sh - 8 * s), (x + 6 * s, sh - 8 * s), (x + 9 * s, sh + 70 * s),
                       (x, sh + 82 * s), (x - 9 * s, sh + 70 * s)], fill=(210, 30, 50))

    # --- brazos
    manos = []
    for sx_, ang in ((x - 42 * s, arm_l), (x + 42 * s, arm_r)):
        a = math.radians(ang)
        L = 112 * s
        hx, hy_ = sx_ + L * math.sin(a), sh + L * math.cos(a)
        d.line([(sx_, sh), (hx, hy_)], fill=st["sleeve"], width=max(2, int(24 * s)))
        d.ellipse([hx - 14 * s, hy_ - 14 * s, hx + 14 * s, hy_ + 14 * s], fill=skin)
        manos.append((hx, hy_))

    # --- cabeza
    hy = sh - 78 * s
    hair = {"invitado": (90, 60, 30), "padrino": (55, 35, 20)}.get(kind, (60, 40, 25))
    draw_head(d, x, hy, s, kind, expr, hair)
    return {"mano_izq": manos[0], "mano_der": manos[1], "cabeza": (x, hy)}


def draw_cooler(d, cx, cy, ang, s=1.0):
    """Hielera azul con tapa blanca, rotada `ang` grados."""
    body = [(-110, -60), (110, -60), (110, 70), (-110, 70)]
    lid = [(-118, -82), (118, -82), (118, -55), (-118, -55)]
    stripe = [(-110, 20), (110, 20), (110, 34), (-110, 34)]
    sc = lambda pts: [(px * s, py * s) for px, py in pts]
    d.polygon(rot_pts(cx, cy, sc(body), ang), fill=(30, 110, 210))
    d.polygon(rot_pts(cx, cy, sc(stripe), ang), fill=(255, 255, 255))
    if ang > -20:   # tapa cerrada solo si no está volteada
        d.polygon(rot_pts(cx, cy, sc(lid), ang), fill=(245, 245, 250))
    else:           # tapa abierta y cubos visibles en la boca
        d.polygon(rot_pts(cx, cy, sc([(-110, -62), (110, -62), (110, -48), (-110, -48)]), ang),
                  fill=(190, 235, 255))
    d.text(rot_pts(cx, cy, sc([(0, -10)]), ang)[0], "HIELO", font=F(max(10, int(30 * s))),
           fill=WHITE, anchor="mm")
    # punto de salida (esquina superior izquierda) para los cubos
    return rot_pts(cx, cy, sc([(-105, -60)]), ang)[0]


def draw_ice(d, x, y, size, ang):
    pts = rot_pts(x, y, [(-size, -size), (size, -size), (size, size), (-size, size)], ang)
    d.polygon(pts, fill=(200, 238, 255, 235), outline=(255, 255, 255), width=3)
    hl = rot_pts(x, y, [(-size * 0.6, -size * 0.6), (-size * 0.1, -size * 0.6), (-size * 0.6, -size * 0.1)], ang)
    d.polygon(hl, fill=(255, 255, 255, 220))


def falling_ice(d, t, t0, t1, src, target_y, dt=0.07, vx=-90, spread=50, size=18, salt=0):
    """
    Lluvia de cubos de hielo desde `src` hasta `target_y`.
    Devuelve la lista de impactos recientes (x, edad) para dibujar vapor.
    """
    impactos = []
    g = 2600.0
    n = int((t1 - t0) / dt)
    for i in range(n):
        ts = t0 + i * dt
        age = t - ts
        if age < 0:
            break
        x0 = src[0] + (hash01(i, salt) - 0.5) * spread
        vxi = vx + (hash01(i, salt + 1) - 0.5) * 120
        y = src[1] + 0.5 * g * age * age - 80 * age
        x = x0 + vxi * age
        y_hit = target_y + (hash01(i, salt + 2) - 0.5) * 30
        if y < y_hit:
            draw_ice(d, x, y, size * (0.8 + 0.4 * hash01(i, salt + 3)), age * 400 + i * 37)
        else:
            t_hit = (80 + math.sqrt(80 * 80 + 2 * g * max(0.0, y_hit - src[1]))) / g
            edad_imp = age - t_hit
            if edad_imp < 0.8:
                impactos.append((x0 + vxi * t_hit, y_hit, edad_imp))
    return impactos


def draw_steam(d, impactos, col=(255, 255, 255)):
    """Bocanadas de vapor donde el hielo toca el metal caliente."""
    for x, y, age in impactos:
        k = age / 0.8
        for j in range(3):
            r = 18 + 60 * k + j * 10
            px = x + (j - 1) * 26 * (0.5 + k)
            py = y - 30 - 160 * k - j * 18
            d.ellipse([px - r, py - r, px + r, py + r], fill=col + (int(150 * (1 - k)),))


def draw_smoke(d, t, x, y, intensity=1.0, col=(215, 215, 215), n=22, height=520, spread=60, salt=1):
    """Columna de humo/vapor animada (partículas que suben y se desvanecen)."""
    if intensity <= 0:
        return
    for i in range(n):
        phase = hash01(i, salt)
        age = (t * 0.55 + phase) % 1.0
        px = x + (hash01(i, salt + 7) - 0.5) * spread + math.sin(t * 2 + i) * 30 * age + 90 * age
        py = y - age * height
        r = 22 + age * 95
        a = int(165 * (1 - age) * intensity)
        d.ellipse([px - r, py - r, px + r, py + r], fill=col + (a,))


@lru_cache(maxsize=8)
def car_sprite(hood=1.0, broken=False, color=(210, 40, 45)):
    """Coche de perfil (frente a la derecha) como imagen RGBA reutilizable."""
    sp = Image.new("RGBA", (680, 380), (0, 0, 0, 0))
    d = ImageDraw.Draw(sp)
    dark = tuple(int(c * 0.68) for c in color)
    # cabina y ventanas
    d.polygon([(150, 170), (225, 75), (415, 75), (480, 170)], fill=dark)
    d.polygon([(175, 165), (235, 92), (305, 92), (305, 165)], fill=(170, 220, 255))
    d.polygon([(320, 165), (320, 92), (405, 92), (455, 165)], fill=(170, 220, 255))
    # carrocería
    d.rounded_rectangle([20, 160, 640, 300], radius=45, fill=color)
    d.line([(40, 230), (620, 230)], fill=dark, width=5)
    d.rounded_rectangle([250, 188, 292, 200], radius=4, fill=dark)
    d.rounded_rectangle([605, 195, 652, 228], radius=8, fill=(255, 240, 150))   # faro
    d.rounded_rectangle([10, 195, 40, 225], radius=6, fill=(255, 80, 60))       # calavera
    d.rounded_rectangle([600, 262, 668, 290], radius=8, fill=(160, 160, 170))   # defensa
    # llantas
    for wx in (150, 500):
        d.ellipse([wx - 60, 246, wx + 60, 366], fill=(28, 28, 32))
        d.ellipse([wx - 29, 277, wx + 29, 335], fill=(175, 175, 185))
        d.ellipse([wx - 8, 298, wx + 8, 314], fill=(90, 90, 95))
    # cofre (abierto o cerrado)
    if hood > 0:
        d.rectangle([455, 150, 625, 172], fill=(40, 30, 30))   # hueco del motor
        a = math.radians(hood * 62)
        end = (455 + 175 * math.cos(a), 163 - 175 * math.sin(a))
        d.line([(455, 163), end], fill=color, width=18)
        d.line([(470, 163), (470, 130)], fill=(120, 120, 120), width=5)   # varilla
    else:
        d.line([(455, 162), (630, 162)], fill=dark, width=4)
    # motor partido
    if broken:
        crack = [(560, 150), (540, 185), (575, 210), (545, 245), (585, 270), (560, 300)]
        d.line(crack, fill=(10, 10, 10), width=12, joint="curve")
        d.line(crack, fill=(255, 150, 40), width=4, joint="curve")
        d.polygon([(600, 262), (668, 290), (660, 312), (596, 282)], fill=(130, 130, 140))
    return sp


def paste_car(img, x, y_ground, hood=1.0, broken=False, scale=1.0):
    """Pega el coche con las llantas apoyadas en y_ground. Devuelve el origen."""
    sp = car_sprite(hood, broken)
    if scale != 1.0:
        sp = sp.resize((int(sp.width * scale), int(sp.height * scale)), Image.LANCZOS)
    oy = int(y_ground - 366 * scale)
    img.paste(sp, (int(x), oy), sp)
    return int(x), oy


def heat_color(h):
    """0 = metal frío gris, 0.5 = naranja, 1 = rojo vivo."""
    if h < 0.5:
        return lerp_col((115, 120, 132), (230, 120, 40), h / 0.5)
    return lerp_col((230, 120, 40), (255, 55, 30), (h - 0.5) / 0.5)


def draw_engine(d, cx, cy, s, heat, t, crack=0.0):
    """Bloque de motor (vista frontal) con color según temperatura y grieta opcional."""
    col = heat_color(heat)
    pulse = 0.5 + 0.5 * math.sin(t * 8)
    if heat > 0.45:   # resplandor
        for k, a in ((1.55, 35), (1.3, 55), (1.12, 80)):
            ga = int(a * (heat - 0.45) / 0.55 * (0.8 + 0.2 * pulse))
            d.rounded_rectangle([cx - 200 * s * k, cy - 130 * s * k, cx + 200 * s * k, cy + 130 * s * k],
                                radius=int(60 * s * k), fill=(255, 90, 30, ga))
    dark = tuple(int(c * 0.7) for c in col)
    # cabeza de cilindros
    d.rounded_rectangle([cx - 190 * s, cy - 150 * s, cx + 190 * s, cy - 95 * s], radius=int(14 * s), fill=dark)
    for k in range(4):
        px = cx - 135 * s + k * 90 * s
        d.ellipse([px - 26 * s, cy - 175 * s, px + 26 * s, cy - 125 * s], fill=col, outline=dark, width=max(1, int(5 * s)))
    # bloque
    d.rounded_rectangle([cx - 200 * s, cy - 100 * s, cx + 200 * s, cy + 120 * s], radius=int(22 * s), fill=col)
    for k in range(5):   # aletas
        yy = cy - 70 * s + k * 38 * s
        d.line([(cx - 170 * s, yy), (cx + 170 * s, yy)], fill=dark, width=max(1, int(8 * s)))
    d.rounded_rectangle([cx - 230 * s, cy + 20 * s, cx - 200 * s, cy + 80 * s], radius=int(6 * s), fill=dark)
    d.ellipse([cx + 195 * s, cy + 10 * s, cx + 255 * s, cy + 70 * s], fill=dark)   # polea
    if crack > 0:
        path = [(cx - 20 * s, cy - 175 * s), (cx + 15 * s, cy - 120 * s), (cx - 25 * s, cy - 60 * s),
                (cx + 30 * s, cy), (cx - 10 * s, cy + 55 * s), (cx + 20 * s, cy + 120 * s)]
        draw_partial_path(d, path, crack, (15, 10, 10), max(2, int(12 * s)), glow=(255, 200, 80))


def draw_partial_path(d, path, p, col, width, glow=None):
    """Dibuja una polilínea hasta la fracción p de su longitud total (grietas animadas)."""
    segs = [math.dist(a, b) for a, b in zip(path, path[1:])]
    total = sum(segs)
    rem = total * clamp(p)
    pts = [path[0]]
    for (a, b), L in zip(zip(path, path[1:]), segs):
        if rem >= L:
            pts.append(b)
            rem -= L
        else:
            f = rem / L if L else 0
            pts.append((lerp(a[0], b[0], f), lerp(a[1], b[1], f)))
            break
    if len(pts) >= 2:
        d.line(pts, fill=col, width=width, joint="curve")
        if glow:
            d.line(pts, fill=glow, width=max(1, width // 3))
    return pts[-1]


def draw_gauge(d, cx, cy, r, v, t):
    """Medidor de temperatura (C -> H)."""
    d.ellipse([cx - r - 18, cy - r - 18, cx + r + 18, cy + r + 18], fill=(25, 25, 30, 220))
    seg = 24
    for k in range(seg):
        a0 = 180 + k * 180 / seg
        col = lerp_col(COLD, HOT, k / (seg - 1))
        d.arc([cx - r, cy - r, cx + r, cy + r], a0, a0 + 180 / seg + 0.5, fill=col, width=18)
    a = math.radians(180 + v * 180 + math.sin(t * 40) * 2.5 * v)
    d.line([(cx, cy), (cx + (r - 14) * math.cos(a), cy + (r - 14) * math.sin(a))], fill=WHITE, width=8)
    d.ellipse([cx - 14, cy - 14, cx + 14, cy + 14], fill=WHITE)
    d.text((cx - r + 12, cy + 30), "C", font=F(32), fill=COLD, anchor="mm")
    d.text((cx + r - 12, cy + 30), "H", font=F(32), fill=HOT, anchor="mm")
    if v > 0.85 and int(t * 4) % 2 == 0:
        d.text((cx, cy - r * 0.45), "!", font=F(54), fill=RED, anchor="mm", stroke_width=4, stroke_fill=WHITE)


def draw_rings(d, cx, cy, s=1.0):
    """Dos anillos dorados entrelazados."""
    for dx in (-16, 16):
        d.ellipse([cx + dx * s - 24 * s, cy - 24 * s, cx + dx * s + 24 * s, cy + 24 * s],
                  outline=(250, 200, 50), width=max(2, int(8 * s)))
    d.polygon([(cx + 16 * s - 8 * s, cy - 28 * s), (cx + 16 * s + 8 * s, cy - 28 * s), (cx + 16 * s, cy - 40 * s)],
              fill=(180, 240, 255))


def draw_ringbox(d, cx, cy, s=1.0):
    d.rounded_rectangle([cx - 34 * s, cy - 10 * s, cx + 34 * s, cy + 34 * s], radius=int(8 * s), fill=(170, 20, 50))
    d.rounded_rectangle([cx - 34 * s, cy - 40 * s, cx + 34 * s, cy - 8 * s], radius=int(8 * s), fill=(200, 30, 70))
    draw_rings(d, cx, cy - 2 * s, 0.55 * s)


def draw_timer(d, t, remaining, color=None):
    """Tarjeta de cuenta regresiva para la boda (arriba a la derecha)."""
    x0, y0, x1, y1 = 600, 450, 1050, 600
    d.rounded_rectangle([x0, y0, x1, y1], radius=30, fill=(20, 20, 28, 225), outline=(255, 255, 255, 180), width=4)
    draw_rings(d, x0 + 70, y0 + 82, 1.25)
    d.text((x0 + 140, y0 + 40), "BODA EN", font=F(34), fill=(255, 210, 230), anchor="lm")
    remaining = max(0, int(remaining))
    hh, mm, ss = remaining // 3600, (remaining % 3600) // 60, remaining % 60
    col = color or (RED if int(t * 2) % 2 == 0 else WHITE)
    d.text((x0 + 140, y0 + 98), f"{hh}:{mm:02d}:{ss:02d}", font=F(64), fill=col, anchor="lm")


def draw_clock(d, cx, cy, r, t, speed=6.0):
    d.ellipse([cx - r - 8, cy - r - 8, cx + r + 8, cy + r + 8], fill=(240, 240, 240))
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=WHITE, outline=(40, 40, 40), width=6)
    for k in range(12):
        a = k * math.pi / 6
        d.line([(cx + (r - 14) * math.cos(a), cy + (r - 14) * math.sin(a)),
                (cx + (r - 4) * math.cos(a), cy + (r - 4) * math.sin(a))], fill=(40, 40, 40), width=4)
    a = t * speed - math.pi / 2
    d.line([(cx, cy), (cx + (r - 18) * math.cos(a), cy + (r - 18) * math.sin(a))], fill=RED, width=6)
    a2 = t * speed / 12 - math.pi / 2
    d.line([(cx, cy), (cx + (r - 34) * math.cos(a2), cy + (r - 34) * math.sin(a2))], fill=(30, 30, 30), width=8)
    d.ellipse([cx - 8, cy - 8, cx + 8, cy + 8], fill=(30, 30, 30))


def draw_check(d, cx, cy, s, p):
    """Palomita verde con 'pop'."""
    if p <= 0:
        return
    k = back_out(clamp(p)) * s
    d.ellipse([cx - 70 * k, cy - 70 * k, cx + 70 * k, cy + 70 * k], fill=GREEN, outline=WHITE, width=max(1, int(8 * k)))
    d.line([(cx - 35 * k, cy), (cx - 8 * k, cy + 28 * k), (cx + 38 * k, cy - 30 * k)], fill=WHITE,
           width=max(2, int(16 * k)), joint="curve")


def draw_x(d, cx, cy, s, p):
    """Tache rojo con 'pop'."""
    if p <= 0:
        return
    k = back_out(clamp(p)) * s
    d.ellipse([cx - 80 * k, cy - 80 * k, cx + 80 * k, cy + 80 * k], fill=RED, outline=WHITE, width=max(1, int(8 * k)))
    for a, b in (((-38, -38), (38, 38)), ((-38, 38), (38, -38))):
        d.line([(cx + a[0] * k, cy + a[1] * k), (cx + b[0] * k, cy + b[1] * k)], fill=WHITE, width=max(2, int(18 * k)))


def draw_arrow(d, x1, y1, x2, y2, col, w=12):
    d.line([(x1, y1), (x2, y2)], fill=col, width=w)
    a = math.atan2(y2 - y1, x2 - x1)
    L = w * 2.6
    p1 = (x2 + L * math.cos(a + 2.5), y2 + L * math.sin(a + 2.5))
    p2 = (x2 + L * math.cos(a - 2.5), y2 + L * math.sin(a - 2.5))
    d.polygon([(x2 + 6 * math.cos(a), y2 + 6 * math.sin(a)), p1, p2], fill=col)


def headline(d, t):
    """Titulares grandes con animación de entrada tipo 'pop'."""
    for t0, t1, txt, col in TITULARES:
        if t0 <= t < t1:
            p = back_out(prog(t, t0, t0 + 0.35))
            size = max(10, int(82 * (0.6 + 0.4 * p)))
            rich_text(d, W / 2, 330, txt, size, fill=col, stroke=10, maxw=1000)


def subtitles(img, t, band=False):
    """Subtítulos grandes, centrados y con contorno, sincronizados con la voz."""
    d = ImageDraw.Draw(img, "RGBA")
    for t0, t1, txt in SUBTITULOS:
        if t0 <= t < t1:
            p = prog(t, t0, t0 + 0.15)
            size = int(66 * (0.85 + 0.15 * back_out(p)))
            if band:
                d.rounded_rectangle([40, 1560, W - 40, 1800], radius=36, fill=(0, 0, 0, 120))
            rich_text(d, W / 2, 1680, txt, size, fill=WHITE, maxw=940, stroke=8)
            break


def flash(img, t, t_start, dur=0.2, col=(255, 255, 255)):
    """Destello blanco de transición."""
    if t_start <= t < t_start + dur:
        a = int(255 * (1 - (t - t_start) / dur))
        ov = Image.new("RGB", img.size, col)
        return Image.blend(img, ov, a / 255)
    return img


# ==========================================================================
# ESCENA 1 (0 - 12 s): gancho + contexto
# ==========================================================================
CAR_X, CAR_GROUND = 40, 1350


def escena1(t):
    tt = min(t, 4.2) if t < 5.0 else t      # 4.2 - 5.0: congelado ("pausa")
    img = bg_road().copy()
    d = ImageDraw.Draw(img, "RGBA")

    ox, oy = paste_car(img, CAR_X, CAR_GROUND, hood=1.0)
    bay = (ox + 540, oy + 158)
    # resplandor del motor y humo
    pulse = 0.5 + 0.5 * math.sin(tt * 9)
    d.ellipse([bay[0] - 90, bay[1] - 30, bay[0] + 90, bay[1] + 30], fill=(255, 80, 20, int(120 + 80 * pulse)))
    draw_smoke(d, tt, bay[0], bay[1] - 10, 1.0, (225, 225, 225), n=24)

    if tt < 5.0:
        # ------ GANCHO: el cuñado vacía la hielera sobre el motor ------
        lift = ease_out(prog(tt, 0.0, 0.9))
        tilt = -70 * ease_in_out(prog(tt, 1.2, 2.2))
        arm = lerp(25, 192, lift)
        pos = draw_person(d, 860, 1420, 1.0, "cunado", arm_l=arm + 12, arm_r=arm - 12, expr="smug")
        hx = (pos["mano_izq"][0] + pos["mano_der"][0]) / 2
        hy = (pos["mano_izq"][1] + pos["mano_der"][1]) / 2
        mouth = draw_cooler(d, hx - 20, hy - 60, tilt, 1.0)
        if tt >= 2.0:
            imp = falling_ice(d, tt, 2.0, 4.2, mouth, bay[1], dt=0.05, vx=-110, spread=40, salt=11)
            draw_steam(d, imp)
            draw_smoke(d, tt, bay[0], bay[1] - 20, 1.0 * prog(tt, 2.1, 2.6), (255, 255, 255), n=18, salt=5)
        draw_person(d, 330, 1580, 1.0, "padrino", arm_l=-20, arm_r=150, expr="shock")
        draw_ringbox(d, 330 + 42 + 112 * math.sin(math.radians(150)),
                     1580 - 250 + 112 * math.cos(math.radians(150)) - 30, 1.0)
        headline(d, tt)
        if t >= 4.2:   # efecto "pausa": desaturar + icono
            gray = ImageOps.grayscale(img).convert("RGB")
            img = Image.blend(img, gray, 0.75)
            d = ImageDraw.Draw(img, "RGBA")
            d.rounded_rectangle([430, 760, 490, 960], radius=14, fill=(255, 255, 255, 230))
            d.rounded_rectangle([590, 760, 650, 960], radius=14, fill=(255, 255, 255, 230))
            pill(d, 540, 1040, "ESPERA... CONTEXTO", 54, (20, 20, 20, 230), YELLOW)
        return img

    # ------ CONTEXTO (5 - 12 s) ------
    draw_cooler(d, 960, 1370, 0, 0.75)
    draw_person(d, 840, 1420, 1.0, "cunado", arm_l=55, arm_r=-55, expr="smug")
    name_tag(d, 760, 980, "EL CUÑADO SABELOTODO", (230, 110, 0), prog(t, 5.5, 5.9))

    up = ease_out(prog(t, 7.3, 7.7))
    arm_r = lerp(40, 160, up)
    pos = draw_person(d, 430, 1580, 1.0, "padrino", arm_l=-15, arm_r=arm_r, expr="shock")
    hx, hy = pos["mano_der"]
    draw_ringbox(d, hx, hy - 30, 1.0 + 0.35 * up)
    if up > 0 and t < 9.6:
        name_tag(d, 430, 1130, "EL PADRINO (YO)", (60, 60, 160), prog(t, 7.5, 7.9))

    # Don Chuy entra caminando desde la izquierda
    wp = ease_out(prog(t, 9.6, 11.0))
    mx = lerp(-160, 150, wp)
    walking = 0 < wp < 1
    greet = prog(t, 11.0, 11.3)
    draw_person(d, mx, 1600, 1.0, "mecanico", arm_l=-14, arm_r=lerp(14, 135, greet),
                expr="calm", walk=math.sin(t * 12) if walking else 0)
    name_tag(d, 270, 1170, "DON CHUY · MECÁNICO", (40, 90, 180), prog(t, 10.6, 11.0))

    draw_gauge(d, 170, 520, 105, 0.95, t)
    pop = back_out(prog(t, 5.2, 5.6))
    if pop > 0:
        draw_timer(d, t, 7200 - (t - 5.0) * 60)
    headline(d, t)
    return img


# ==========================================================================
# ESCENA 2 (12 - 26 s): pantalla dividida cuñado vs. Don Chuy
# ==========================================================================
def escena2(t):
    img = bg_split().copy()
    d = ImageDraw.Draw(img, "RGBA")

    # ---------- MITAD SUPERIOR: el error ----------
    pill(d, W / 2, 150, "CUÑADO: HIELO DIRECTO", 46, (200, 30, 30), outline=WHITE)
    eng_top = (600, 600)
    crack = ease_out(prog(t, 19.5, 22.5))
    draw_engine(d, eng_top[0], eng_top[1], 1.0, 1.0, t, crack=crack)
    d.text((eng_top[0], eng_top[1] + 165), "110 °C", font=F(44), fill=WHITE, anchor="mm",
           stroke_width=5, stroke_fill=BLACK)
    mouth = draw_cooler(d, 760, 270, -60 - 6 * math.sin(t * 6), 0.85)
    imp = falling_ice(d, t, 12.3, 24.0, mouth, eng_top[1] - 160, dt=0.09, vx=-40, spread=180, size=16, salt=21)
    draw_steam(d, imp)
    draw_person(d, 150, 830, 0.72, "cunado", arm_l=160, arm_r=200, expr="smug")
    if t > 16.5:
        pill(d, 250, 330, "0 °C", 40, (40, 120, 220), outline=WHITE)
    draw_x(d, 920, 480, 0.9, prog(t, 22.8, 23.2))
    if crack > 0.95:
        pill(d, 600, 780, "¡CHOQUE TÉRMICO!", 44, (20, 20, 20), YELLOW)

    # ---------- divisor VS ----------
    d.rectangle([0, 852, W, 868], fill=WHITE)
    d.ellipse([480, 800, 600, 920], fill=(20, 20, 20), outline=WHITE, width=8)
    d.text((540, 860), "VS", font=F(50), fill=YELLOW, anchor="mm")

    # ---------- MITAD INFERIOR: lo correcto ----------
    pill(d, W / 2, 990, "DON CHUY: ESPERAR + AGUA TIBIA", 40, (20, 140, 70), outline=WHITE)
    cool = ease_in_out(prog(t, 13.0, 21.5))
    heat = lerp(1.0, 0.15, cool)
    eng_bot = (650, 1250)
    draw_engine(d, eng_bot[0], eng_bot[1], 0.78, heat, t)
    temp = int(lerp(110, 60, cool))
    d.text((eng_bot[0], eng_bot[1] + 135), f"{temp} °C", font=F(42), fill=WHITE, anchor="mm",
           stroke_width=5, stroke_fill=BLACK)
    draw_smoke(d, t, eng_bot[0], eng_bot[1] - 140, 0.9 * (1 - cool), (230, 230, 230), n=12, height=250, salt=9)
    draw_clock(d, 160, 1150, 62, t, speed=9.0 * (1 - prog(t, 21.5, 22)))
    d.text((160, 1250), "15-20 MIN", font=F(36), fill=WHITE, anchor="mm", stroke_width=4, stroke_fill=BLACK)
    draw_person(d, 160, 1490, 0.55, "mecanico", arm_l=-12, arm_r=95, expr="calm")

    # jarra de agua tibia vertiendo poco a poco
    pour = prog(t, 21.6, 22.2)
    if pour > 0:
        jx, jy = 860, 1110
        ang = -35 * ease_out(pour)
        jug = rot_pts(jx, jy, [(-45, -55), (45, -55), (55, 60), (-55, 60)], ang)
        d.polygon(jug, fill=(200, 230, 255, 220), outline=WHITE, width=4)
        d.polygon(rot_pts(jx, jy, [(-44, -5), (44, -5), (54, 58), (-54, 58)], ang), fill=(120, 190, 255, 200))
        spout = rot_pts(jx, jy, [(-50, -55)], ang)[0]
        if pour >= 1:
            wob = math.sin(t * 20) * 3
            d.line([spout, (spout[0] - 40 + wob, spout[1] + 40), (eng_bot[0] + 60, eng_bot[1] - 120)],
                   fill=(130, 200, 255, 220), width=10, joint="curve")
        d.text((jx + 120, jy), "TIBIA", font=F(32), fill=WHITE, anchor="mm", stroke_width=4, stroke_fill=BLACK)
    draw_check(d, 940, 1300, 0.8, prog(t, 24.3, 24.7))
    return img


# ==========================================================================
# ESCENA 3 (26 - 42 s): zoom microscópico al metal
# ==========================================================================
LENS_C = (540, 880)
LENS_R = 400
NR = NC = 11
BASE = 72
CRACK_COL = [5, 5, 6, 6, 5, 4, 4, 5, 5, 6, 5]   # columna por donde pasa la grieta en cada fila


@lru_cache(maxsize=64)
def lens_mask(r):
    m = Image.new("L", (2 * LENS_R, 2 * LENS_R), 0)
    ImageDraw.Draw(m).ellipse([LENS_R - r, LENS_R - r, LENS_R + r, LENS_R + r], fill=255)
    return m


def lattice(t):
    """
    Calcula las posiciones de los átomos.
    - 'frío' avanza desde la fila 0 (superficie) hacia adentro: los átomos
      fríos se acercan (contracción) y se ponen azules.
    - Los átomos calientes vibran más y están más separados (expansión).
    - Al final, una grieta separa las dos mitades.
    """
    front = 5.5 * ease_in_out(prog(t, 31.0, 35.0))
    cold = [clamp(front - r) for r in range(NR)]
    f = lambda c: lerp(1.12, 0.82, c)        # separación relativa caliente/frío
    ys = [0.0]
    for r in range(NR - 1):
        ys.append(ys[-1] + BASE * f((cold[r] + cold[r + 1]) / 2))
    mid = (ys[0] + ys[-1]) / 2
    crack_p = ease_in_out(prog(t, 36.3, 39.0))
    open_ = ease_out(prog(t, 36.5, 41.0))
    atoms = []
    for r in range(NR):
        fila = []
        h = 1 - cold[r]
        covered = r < crack_p * NR
        for i in range(NC):
            x = LENS_R + (i - (NC - 1) / 2) * BASE * f(cold[r])
            y = LENS_R + ys[r] - mid
            amp = 1.5 + 8 * h
            x += amp * math.sin(t * 23 + i * 1.7 + r * 2.3)
            y += amp * math.cos(t * 19 + i * 2.9 + r * 1.1)
            side = 0
            if covered:
                side = -1 if i <= CRACK_COL[r] else 1
                x += side * 30 * open_ * (1 - 0.45 * r / NR)
            fila.append((x, y, h, side, covered))
        atoms.append(fila)
    return atoms, cold, crack_p


def escena3(t):
    img = bg_lab().copy()
    d = ImageDraw.Draw(img, "RGBA")

    # ---- capa de la lente (átomos) ----
    layer = Image.new("RGB", (2 * LENS_R, 2 * LENS_R), (14, 20, 44))
    dl = ImageDraw.Draw(layer, "RGBA")
    atoms, cold, crack_p = lattice(t)
    stress = prog(t, 32.0, 33.0) * (1 - prog(t, 39.0, 40.0))

    # enlaces horizontales
    for r in range(NR):
        for i in range(NC - 1):
            a, b = atoms[r][i], atoms[r][i + 1]
            if a[4] and i == CRACK_COL[r]:
                continue   # enlace roto por la grieta
            col = lerp_col(COLD, HOT, a[2])
            dl.line([a[:2], b[:2]], fill=col + (150,), width=6)
    # enlaces verticales (en amarillo donde hay tensión entre capa fría y caliente)
    for r in range(NR - 1):
        tens = abs(cold[r] - cold[r + 1]) > 0.15 and stress > 0
        for i in range(NC):
            a, b = atoms[r][i], atoms[r + 1][i]
            if a[4] and b[4] and a[3] != b[3]:
                continue
            if tens:
                pul = 0.5 + 0.5 * math.sin(t * 18 + i)
                dl.line([a[:2], b[:2]], fill=(255, 230, 60, int(150 + 100 * pul * stress)), width=9)
            else:
                dl.line([a[:2], b[:2]], fill=lerp_col(COLD, HOT, a[2]) + (130,), width=6)
    # átomos
    for fila in atoms:
        for x, y, h, side, cov in fila:
            col = lerp_col(COLD, HOT, h)
            r = 16 + 6 * h
            if h > 0.3:
                g = r + 12 * h
                dl.ellipse([x - g, y - g, x + g, y + g], fill=(255, 90, 40, int(70 * h)))
            dl.ellipse([x - r, y - r, x + r, y + r], fill=col)
            dl.ellipse([x - r * 0.45, y - r * 0.55, x - r * 0.05, y - r * 0.15], fill=(255, 255, 255, 170))
    # grieta
    if crack_p > 0:
        path = []
        for r in range(NR):
            if atoms[r][0][4]:
                c = CRACK_COL[r]
                a, b = atoms[r][c], atoms[r][c + 1]
                path.append(((a[0] + b[0]) / 2, a[1]))
        if path:
            path = [(path[0][0], path[0][1] - 60)] + path
            dl.line(path, fill=(5, 5, 8), width=16, joint="curve")
            dl.line(path, fill=(255, 190, 70), width=4)
            tip = path[-1]
            if crack_p < 1:
                dl.ellipse([tip[0] - 22, tip[1] - 22, tip[0] + 22, tip[1] + 22], fill=(255, 240, 160, 200))
    # flechas: afuera se encoge / adentro empuja
    arr_p = prog(t, 32.5, 33.2) * (1 - prog(t, 39.5, 40.0))
    if arr_p > 0:
        y_top = atoms[1][0][1]
        y_bot = atoms[8][0][1]
        a = int(255 * arr_p)
        for sgn in (-1, 1):
            draw_arrow(dl, LENS_R + sgn * 340, y_top, LENS_R + sgn * 200, y_top, (120, 200, 255, a), 14)
            draw_arrow(dl, LENS_R + sgn * 120, y_bot, LENS_R + sgn * 300, y_bot, (255, 120, 60, a), 14)
        rich_text(dl, LENS_R, y_top - 70, "SE ENCOGE", 44, fill=(150, 215, 255), stroke=6)
        rich_text(dl, LENS_R, y_bot + 70, "SIGUE CALIENTE", 44, fill=(255, 150, 90), stroke=6)

    # apertura tipo iris de la lente
    r_now = int(LENS_R * ease_out(prog(t, 26.0, 26.8)))
    if r_now > 2:
        img.paste(layer, (LENS_C[0] - LENS_R, LENS_C[1] - LENS_R), lens_mask(r_now))
        d.ellipse([LENS_C[0] - r_now - 12, LENS_C[1] - r_now - 12, LENS_C[0] + r_now + 12, LENS_C[1] + r_now + 12],
                  outline=(170, 180, 200), width=22)
        d.ellipse([LENS_C[0] - r_now - 2, LENS_C[1] - r_now - 2, LENS_C[0] + r_now + 2, LENS_C[1] + r_now + 2],
                  outline=(230, 235, 245), width=4)
    pill(d, LENS_C[0], LENS_C[1] + LENS_R + 30, "ZOOM x 1.000.000", 34, (30, 40, 70), outline=(170, 180, 200))

    # etiqueta de temperatura de la superficie
    if t >= 31.0:
        pill(d, 170, 540, "AFUERA 0 °C", 32, (40, 110, 210), outline=WHITE)
        pill(d, 890, 1230, "ADENTRO 110 °C", 32, (200, 60, 30), outline=WHITE)
    elif t >= 26.8:
        pill(d, 890, 1230, "TODO A 110 °C", 32, (200, 60, 30), outline=WHITE)

    # recuadro: vaso caliente en agua fría
    vp = prog(t, 39.2, 39.6)
    if vp > 0:
        k = back_out(vp)
        gx, gy = 170, 1430
        d.rounded_rectangle([gx - 120 * k, gy - 110 * k, gx + 120 * k, gy + 110 * k], radius=int(30 * k) + 1,
                            fill=(20, 40, 80, 230), outline=WHITE, width=4)
        glass = [(gx - 50 * k, gy - 75 * k), (gx + 50 * k, gy - 75 * k), (gx + 38 * k, gy + 80 * k), (gx - 38 * k, gy + 80 * k)]
        d.rectangle([gx - 100 * k, gy + 20 * k, gx + 100 * k, gy + 100 * k], fill=(80, 160, 255, 150))
        d.polygon(glass, fill=(200, 240, 255, 90), outline=(230, 250, 255), width=5)
        draw_partial_path(d, [(gx - 8 * k, gy - 75 * k), (gx + 12 * k, gy - 30 * k), (gx - 10 * k, gy + 10 * k),
                              (gx + 14 * k, gy + 50 * k), (gx, gy + 80 * k)],
                          prog(t, 39.9, 40.6), (20, 20, 20), max(2, int(7 * k)))
        rich_text(d, 640, 1430, "= VASO CALIENTE\nEN AGUA FRÍA", 50, fill=WHITE, stroke=6, maxw=700)

    headline(d, t)
    return img


# ==========================================================================
# ESCENA 4 (42 - 55 s): CRACK + grúa + pregunta final
# ==========================================================================
def draw_tow_truck(img, d, x0, gy, s, t, swing):
    """Grúa amarilla (frente a la derecha) con el coche roto colgando atrás."""
    P = lambda px, py: (x0 + px * s, gy - py * s)
    # pluma y cadena
    d.line([P(60, 150), P(-40, 330)], fill=(70, 70, 75), width=int(26 * s))
    tip = P(-40, 330)
    hook = (tip[0] - 20 * s, tip[1] + 95 * s)
    d.line([tip, hook], fill=(40, 40, 40), width=int(8 * s))

    # coche colgando (frente arriba), con balanceo
    ang = 24 + swing
    sp = car_sprite(0.0, True)
    sc = 0.62 * s
    sp = sp.resize((int(sp.width * sc), int(sp.height * sc)), Image.LANCZOS)
    rot = sp.rotate(ang, resample=Image.BICUBIC, expand=True)
    # punto del frente del coche (defensa) dentro del sprite original, transformado
    px, py = 655 * sc, 230 * sc
    cx0, cy0 = sp.width / 2, sp.height / 2
    a = math.radians(ang)
    rx = rot.width / 2 + (px - cx0) * math.cos(a) + (py - cy0) * math.sin(a)
    ry = rot.height / 2 - (px - cx0) * math.sin(a) + (py - cy0) * math.cos(a)
    img.paste(rot, (int(hook[0] - rx), int(hook[1] - ry)), rot)
    draw_smoke(d, t, hook[0] - 40 * s, hook[1] + 20 * s, 0.6, (90, 90, 90), n=10, height=260, salt=33)

    # plataforma y cabina
    d.rectangle([*P(-10, 160), *P(450, 95)], fill=(235, 175, 20))
    d.text(P(220, 128), "GRÚAS DON CHUY", font=F(int(30 * s)), fill=(60, 40, 0), anchor="mm")
    d.rounded_rectangle([*P(430, 340), *P(650, 95)], radius=int(26 * s), fill=(250, 200, 30))
    d.rounded_rectangle([*P(470, 310), *P(625, 210)], radius=int(12 * s), fill=(170, 220, 255))
    d.rectangle([*P(-20, 100), *P(660, 70)], fill=(50, 50, 55))
    blink = int(t * 4) % 2 == 0
    d.rounded_rectangle([*P(520, 370), *P(580, 340)], radius=int(8 * s), fill=(255, 120, 0) if blink else (180, 70, 0))
    for wx in (100, 550):
        c = P(wx, 55)
        r = 55 * s
        d.ellipse([c[0] - r, c[1] - r, c[0] + r, c[1] + r], fill=(28, 28, 32))
        d.ellipse([c[0] - r / 2, c[1] - r / 2, c[0] + r / 2, c[1] + r / 2], fill=(170, 170, 180))
    # pasajeros: el padrino en la cabina con los anillos, el cuñado y Don Chuy en la plataforma
    wv = math.sin(t * 9) * 25
    draw_head(d, P(545, 0)[0], P(0, 250)[1], 0.62 * s, "padrino", "happy")
    draw_person(d, P(150, 0)[0], P(0, 160)[1], 0.6 * s, "mecanico", arm_l=-15, arm_r=150 + wv, expr="calm")
    draw_person(d, P(320, 0)[0], P(0, 160)[1], 0.6 * s, "cunado", arm_l=-160 - wv, arm_r=160 + wv, expr="smug")


def escena4(t):
    if t < T_GRUA:
        # ---------------- ¡CRACK! ----------------
        img = bg_road().copy()
        d = ImageDraw.Draw(img, "RGBA")
        broke = t >= T_CRACK
        ox, oy = paste_car(img, CAR_X, CAR_GROUND, hood=1.0, broken=broke)
        bay = (ox + 540, oy + 158)
        if not broke:
            d.ellipse([bay[0] - 90, bay[1] - 30, bay[0] + 90, bay[1] + 30], fill=(255, 80, 20, 190))
            draw_smoke(d, t, bay[0], bay[1] - 10, 1.0, (230, 230, 230), n=24)
            pos = draw_person(d, 860, 1420, 1.0, "cunado", arm_l=204, arm_r=180, expr="smug")
            hx = (pos["mano_izq"][0] + pos["mano_der"][0]) / 2
            hy = (pos["mano_izq"][1] + pos["mano_der"][1]) / 2
            mouth = draw_cooler(d, hx - 20, hy - 60, -70, 1.0)
            imp = falling_ice(d, t, 42.0, 43.0, mouth, bay[1], dt=0.04, vx=-110, spread=40, salt=41)
            draw_steam(d, imp)
            draw_person(d, 150, 1600, 1.0, "mecanico", arm_l=-14, arm_r=-150, expr="shock")
        else:
            k = prog(t, T_CRACK, T_CRACK + 1.2)
            draw_smoke(d, t, bay[0], bay[1] - 10, 1.0, (60, 60, 60), n=30, height=700, spread=140, salt=3)
            # pedazos que salen volando
            for i in range(10):
                vx = (hash01(i, 50) - 0.5) * 900
                vy = -500 - hash01(i, 51) * 700
                age = t - T_CRACK
                px = bay[0] + vx * age
                py = bay[1] + vy * age + 1300 * age * age
                if py < 1500:
                    sz = 10 + 12 * hash01(i, 52)
                    d.polygon(rot_pts(px, py, [(-sz, -sz * 0.6), (sz, -sz * 0.3), (sz * 0.4, sz)], age * 600 + i * 40),
                              fill=(70, 70, 75))
            draw_cooler(d, 960, 1395, 0, 0.75)
            draw_person(d, 860, 1420, 1.0, "cunado", arm_l=200, arm_r=160, expr="shock")
            draw_person(d, 150, 1600, 1.0, "mecanico", arm_l=-14, arm_r=172, expr="calm")   # facepalm
            s = back_out(prog(t, T_CRACK, T_CRACK + 0.3), 2.5)
            size = max(10, int(175 * s))
            d.text((540, 620), "¡CRACK!", font=F(size), fill=YELLOW, anchor="mm", stroke_width=16, stroke_fill=(200, 20, 20))
        draw_person(d, 430, 1580, 1.0, "padrino", arm_l=-160, arm_r=160, expr="shock")
        img = flash(img, t, T_CRACK, 0.35)
        return img

    # ---------------- LLEGADA EN GRÚA ----------------
    img = bg_wedding().copy()
    d = ImageDraw.Draw(img, "RGBA")
    # invitados saludando frente a la capilla
    invit = [(820, "invitado", (90, 140, 230)), (905, "novia", None), (985, "padrino", None),
             (1055, "invitado", (230, 90, 150))]
    arrived = prog(t, 47.3, 47.6)
    for k, (gx, kind, col) in enumerate(invit):
        wave = 150 + 25 * math.sin(t * 8 + k * 1.3) if arrived > 0 else 10
        expr = "shock" if arrived > 0 and t < T_CTA and kind != "novia" else "happy"
        draw_person(d, gx, 1250, 0.5, kind, arm_l=-12, arm_r=wave, expr=expr, shirt=col)
    # la grúa entra y se detiene
    x0 = lerp(-760, 290, ease_out(prog(t, T_GRUA, 47.4)))
    moving = t < 47.4
    swing = (math.sin(t * 7) * 6 if moving else math.sin(t * 4) * 4 * (1 - prog(t, 47.4, 50)))
    draw_tow_truck(img, d, x0, 1395, 0.85, t, swing)
    if moving:
        for i in range(4):   # líneas de velocidad
            y = 1180 + i * 50
            d.line([(x0 - 380 - i * 40, y), (x0 - 520 - i * 40, y)], fill=(255, 255, 255, 160), width=6)
    # confeti
    if arrived > 0:
        for i in range(70):
            cx = (i * 137.5) % W + 30 * math.sin(t * 2 + i)
            cy = ((t - 47.3) * (220 + (i % 7) * 40) + hash01(i, 60) * 300 - 300) % 1500
            col = [(255, 90, 120), YELLOW, (90, 200, 255), (120, 230, 120), WHITE][i % 5]
            d.polygon(rot_pts(cx, cy, [(-9, -5), (9, -5), (9, 5), (-9, 5)], t * 300 + i * 30), fill=col)
    headline(d, t)
    if t >= 45.3 and t < T_CTA:
        restante = int(125 - (t - T_GRUA) * 3)
        pill(d, 540, 690, f"BODA EN 0:{restante // 60:02d}:{restante % 60:02d}  ¡A TIEMPO!", 38, (20, 140, 70),
             outline=WHITE)
    if t >= 47.6 and t < T_CTA:
        p = back_out(prog(t, 47.6, 47.95))
        size = max(10, int(120 * p))
        d.text((540, 560), "¡EN GRÚA!", font=F(size), fill=YELLOW, anchor="mm", stroke_width=12, stroke_fill=BLACK)
    honk = 47.4 <= t < 48.2
    if honk:
        pill(d, x0 + 0.85 * 700, 980, "¡PIIIP!", 40, (20, 20, 20), YELLOW)

    # ---------------- PREGUNTA FINAL (CTA) ----------------
    if t >= T_CTA:
        a = prog(t, T_CTA, T_CTA + 0.3)
        ov = Image.new("RGB", img.size, (10, 10, 20))
        img = Image.blend(img, ov, 0.72 * a)
        d = ImageDraw.Draw(img, "RGBA")
        k = back_out(prog(t, T_CTA + 0.1, T_CTA + 0.5))
        if k > 0.05:
            cx, cy = 540, 860
            w2, h2 = 470 * k, 420 * k
            d.rounded_rectangle([cx - w2, cy - h2, cx + w2, cy + h2], radius=int(50 * k), fill=WHITE,
                                outline=YELLOW, width=max(1, int(10 * k)))
            if k > 0.8:
                rich_text(d, cx, cy - 170, "¿Y A TI QUÉ", 74, fill=(30, 30, 40), stroke=0)
                rich_text(d, cx, cy - 60, "\"REMEDIO CASERO\"", 74, fill=(230, 100, 0), stroke=0)
                rich_text(d, cx, cy + 90, "te han recomendado\ncuando se calienta el coche?", 50,
                          fill=(30, 30, 40), stroke=0, maxw=880)
                pul = 1 + 0.06 * math.sin(t * 9)
                pill(d, cx, cy + 300, "COMENTA ABAJO", int(52 * pul), RED, outline=WHITE)
        # flecha que rebota hacia los comentarios
        by = 1420 + 25 * abs(math.sin(t * 6))
        draw_arrow(d, 540, by - 90, 540, by + 20, YELLOW, 22)
        # el cuñado asomándose con su hielera
        draw_person(d, 900, 1560, 0.7, "cunado", arm_l=150, arm_r=200, expr="smug")
        draw_cooler(d, 905, 1240, 10, 0.55)
    return img


# ==========================================================================
# COMPOSICIÓN DE CADA FRAME
# ==========================================================================
def make_frame(t):
    t = min(t, DURACION - 1e-3)
    if t < S1[1]:
        img = escena1(t)
        band = False
    elif t < S2[1]:
        img = escena2(t)
        band = True
    elif t < S3[1]:
        img = escena3(t)
        band = True
    else:
        img = escena4(t)
        band = t < T_GRUA or t >= T_CTA

    # destellos de transición entre escenas
    for ts in (5.0, S2[0], S3[0], T_GRUA):
        img = flash(img, t, ts, 0.18)

    subtitles(img, t, band=band)
    arr = np.asarray(img, dtype=np.uint8)

    # temblor de cámara en el CRACK
    if T_CRACK <= t < T_CRACK + 0.7:
        amp = 30 * (1 - (t - T_CRACK) / 0.7)
        dx = int(amp * math.sin(t * 90))
        dy = int(amp * math.cos(t * 77))
        arr = np.roll(arr, (dy, dx), axis=(0, 1))
    return arr


# ==========================================================================
# EFECTOS DE SONIDO SINTETIZADOS (sin archivos externos)
# ==========================================================================
def build_sfx(dur=DURACION, sr=SR, seed=7):
    rng = np.random.default_rng(seed)
    n = int(dur * sr)
    out = np.zeros(n, np.float32)

    def tt(d_):
        return np.arange(int(d_ * sr)) / sr

    def add(t0, sig, gain=1.0):
        i = int(t0 * sr)
        if i >= n:
            return
        j = min(n, i + len(sig))
        out[i:j] += gain * sig[: j - i].astype(np.float32)

    def noise(d_):
        return rng.uniform(-1, 1, int(d_ * sr))

    def smooth(x, k):
        return np.convolve(x, np.ones(k) / k, mode="same")

    def whoosh(t0):
        d_ = 0.35
        sig = smooth(noise(d_), 20) * np.hanning(int(d_ * sr))
        add(t0 - 0.15, sig, 0.9)

    def sizzle(t0, d_, gain=0.10):
        x = noise(d_)
        x = x - smooth(x, 8)                                   # agudo (paso alto)
        env = np.minimum(1, tt(d_) / 0.1) * np.minimum(1, (d_ - tt(d_)) / 0.2)
        flutter = 0.7 + 0.3 * np.sin(2 * np.pi * 13 * tt(d_))
        add(t0, x * env * flutter, gain)

    def clink(t0, f):
        d_ = 0.12
        add(t0, np.sin(2 * np.pi * f * tt(d_)) * np.exp(-45 * tt(d_)), 0.12)

    def crack(t0, gain=1.0):
        d_ = 1.4
        x = noise(d_) * np.exp(-9 * tt(d_))
        thump = np.sin(2 * np.pi * 50 * tt(d_) * (1 - 0.3 * tt(d_))) * np.exp(-4 * tt(d_))
        add(t0, 0.8 * x + 0.9 * thump, gain)
        for k in range(5):   # chasquidos
            add(t0 + 0.02 * k + rng.uniform(0, 0.05), noise(0.015) * np.exp(-300 * tt(0.015)), 0.8 * gain)

    def ding(t0):
        d_ = 0.9
        x = np.sin(2 * np.pi * 1320 * tt(d_)) + 0.5 * np.sin(2 * np.pi * 1980 * tt(d_))
        add(t0, x * np.exp(-5 * tt(d_)), 0.22)

    def buzzer(t0):
        d_ = 0.4
        add(t0, np.sign(np.sin(2 * np.pi * 140 * tt(d_))) * np.exp(-2 * tt(d_)), 0.16)

    def pop(t0):
        d_ = 0.09
        f = 500 + 1500 * tt(d_) / d_
        add(t0, np.sin(2 * np.pi * np.cumsum(f) / sr) * np.exp(-30 * tt(d_)), 0.18)

    def honk(t0):
        for k in range(2):
            d_ = 0.22
            x = np.sign(np.sin(2 * np.pi * 330 * tt(d_))) + np.sign(np.sin(2 * np.pi * 415 * tt(d_)))
            add(t0 + k * 0.32, smooth(x, 6) * 0.5, 0.18)

    def tick(t0):
        add(t0, noise(0.01) * np.exp(-400 * tt(0.01)), 0.25)

    # --- línea de tiempo del sonido ---
    for ts in (5.0, S2[0], S3[0], T_GRUA):
        whoosh(ts)
    for t0, _, _, _ in TITULARES:
        pop(t0)
    sizzle(2.1, 2.1, 0.14)                  # hielo sobre el motor (gancho)
    for i in range(0, 44, 3):
        clink(2.0 + i * 0.05, 2400 + 900 * hash01(i, 90))
    sizzle(12.5, 11.0, 0.06)                # pantalla dividida
    for k in range(int((21.5 - 13.0) / 0.25)):
        tick(13.0 + k * 0.25)
    buzzer(22.8)
    ding(24.3)
    crack(36.3, 0.45)                       # grieta microscópica
    crack(40.0, 0.25)                       # vaso
    sizzle(42.0, 1.0, 0.14)
    crack(T_CRACK, 1.0)                     # ¡CRACK! final
    honk(47.4)
    pop(47.6)
    pop(T_CTA + 0.1)

    out = np.clip(out * 0.8, -1, 1)
    return np.stack([out, out], axis=1)


# ==========================================================================
# RENDER
# ==========================================================================
def _with_audio(clip, audio):
    return clip.with_audio(audio) if MOVIEPY2 else clip.set_audio(audio)


def _cut(clip, t1):
    return clip.subclipped(0, t1) if MOVIEPY2 else clip.subclip(0, t1)


def main():
    global FUENTE_USUARIO
    ap = argparse.ArgumentParser(description="Genera el short vertical del choque térmico.")
    ap.add_argument("--salida", default="choque_termico.mp4", help="archivo de salida (.mp4)")
    ap.add_argument("--fps", type=int, default=FPS, help="cuadros por segundo (30 por defecto)")
    ap.add_argument("--voz", default=None, help="archivo de audio con tu voz en off (mp3/wav)")
    ap.add_argument("--sin-sfx", action="store_true", help="no incluir efectos de sonido")
    ap.add_argument("--fuente", default=None, help="ruta a un .ttf para todos los textos")
    ap.add_argument("--frame", type=float, default=None, help="solo guarda un PNG del segundo indicado")
    args = ap.parse_args()

    if args.fuente:
        FUENTE_USUARIO = args.fuente
        F.cache_clear()

    if args.frame is not None:
        nombre = f"frame_{args.frame:05.2f}.png"
        Image.fromarray(make_frame(args.frame)).save(nombre)
        print("Guardado", nombre)
        return

    clip = VideoClip(make_frame, duration=DURACION)

    pistas = []
    if not args.sin_sfx:
        sfx = build_sfx()
        if args.voz:
            sfx = sfx * 0.55          # efectos más bajos para que se entienda la voz
        pistas.append(AudioArrayClip(sfx, fps=SR))
    if args.voz:
        if not os.path.exists(args.voz):
            sys.exit(f"No encuentro el archivo de voz: {args.voz}")
        voz = AudioFileClip(args.voz)
        if voz.duration > DURACION:
            voz = _cut(voz, DURACION)
        pistas.append(voz)
    if pistas:
        audio = pistas[0] if len(pistas) == 1 else CompositeAudioClip(pistas)
        clip = _with_audio(clip, audio)

    clip.write_videofile(
        args.salida,
        fps=args.fps,
        codec="libx264",
        audio_codec="aac",
        preset="medium",
        threads=os.cpu_count() or 4,
        ffmpeg_params=["-pix_fmt", "yuv420p", "-crf", "20"],
    )
    print("\nListo:", os.path.abspath(args.salida))


if __name__ == "__main__":
    main()
