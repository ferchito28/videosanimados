"""Videos explicativos estilo "¿Por qué...?" con narrador.

Un guion es una lista de frases. Cada frase tiene su texto, sus palabras clave
(que salen en amarillo en los subtítulos) y la función que dibuja la escena
mientras se dice. Los tiempos salen del audio de la voz (si lo hay) o se
estiman.
"""
import math
import random
import re

from PIL import Image, ImageDraw

from . import sincronizar
from . import stickman as sm
from .lienzo import ALTO, ANCHO, SS
from .video import Escena

# ------------------------------------------------------------------ colores
CONTORNO = (45, 30, 25)
PIEL = (255, 222, 186)
AMARILLO = (255, 214, 0)
CONCRETO = (196, 196, 190)
CONCRETO_OSCURO = (150, 150, 145)
TIERRA = (243, 160, 70)
TIERRA_OSCURA = (220, 125, 50)
MESA = (232, 104, 104)
MESA_OSCURA = (196, 76, 96)

CIELOS = {
    "dia": ((86, 168, 238), (190, 226, 255)),
    "calor": ((255, 120, 60), (255, 214, 120)),
    "noche": ((12, 16, 52), (64, 42, 112)),
    "estudio": ((255, 200, 90), (255, 140, 70)),
}

_cache_cielo = {}


def cielo(lz, tipo="dia", mezcla=None, k=0.0):
    """Pinta el cielo (degradado). Con `mezcla` y k (0-1) pasa de un cielo a otro."""
    def grad(nombre):
        if nombre not in _cache_cielo:
            (r1, g1, b1), (r2, g2, b2) = CIELOS[nombre]
            col = Image.new("RGB", (1, 256))
            px = col.load()
            for y in range(256):
                q = y / 255
                px[0, y] = (int(r1 + (r2 - r1) * q), int(g1 + (g2 - g1) * q), int(b1 + (b2 - b1) * q))
            _cache_cielo[nombre] = col.resize((ANCHO * SS, ALTO * SS))
        return _cache_cielo[nombre]
    img = grad(tipo)
    if mezcla and k > 0:
        img = Image.blend(img, grad(mezcla), min(1.0, k))
    lz.img.paste(img, (0, 0))


# ------------------------------------------------------------- primitivas
def rect(lz, x0, y0, x1, y1, relleno, borde=CONTORNO, grosor=6, radio=0):
    a, b = lz.p(x0, y0), lz.p(x1, y1)
    caja = [min(a[0], b[0]), min(a[1], b[1]), max(a[0], b[0]), max(a[1], b[1])]
    lz.d.rounded_rectangle(caja, radius=lz.l(radio), fill=relleno,
                           outline=borde if grosor else None,
                           width=max(1, int(lz.l(grosor))) if grosor else 0)


def arco(lz, c, r, ini, fin, color=CONTORNO, grosor=6):
    a, b = lz.p(c[0] - r, c[1] - r), lz.p(c[0] + r, c[1] + r)
    lz.d.arc([a, b], ini, fin, fill=color, width=max(1, int(lz.l(grosor))))


def flecha(lz, a, b, color=AMARILLO, grosor=22):
    """Flecha gruesa de a hacia b."""
    ang = math.atan2(b[1] - a[1], b[0] - a[0])
    punta = 2.2 * grosor
    base = (b[0] - math.cos(ang) * punta, b[1] - math.sin(ang) * punta)
    lz.linea(a, base, CONTORNO, grosor + 10)
    lz.linea(a, base, color, grosor)
    izq = (base[0] + math.cos(ang + math.pi / 2) * grosor * 1.4,
           base[1] + math.sin(ang + math.pi / 2) * grosor * 1.4)
    der = (base[0] + math.cos(ang - math.pi / 2) * grosor * 1.4,
           base[1] + math.sin(ang - math.pi / 2) * grosor * 1.4)
    lz.poligono([izq, b, der], relleno=color, borde=CONTORNO, grosor=6)


def letrero(lz, txt, x, y, tam=90, color=AMARILLO, progreso=1.0, giro=0):
    """Texto grande dentro de la escena (se mueve con la cámara)."""
    if progreso > 0:
        borde = CONTORNO if color == (255, 255, 255) else (255, 255, 255)
        lz.onomatopeya(txt, x, y, min(progreso, 1.0), tam=tam, giro=giro, color=color, borde=borde)


def palomita(lz, c, tam=70, progreso=1.0):
    if progreso <= 0:
        return
    k = sm.rebote(min(1, progreso)) * tam
    lz.circulo(c, k, relleno=(60, 190, 90), borde=CONTORNO, grosor=6)
    lz.linea((c[0] - k * 0.45, c[1]), (c[0] - k * 0.1, c[1] + k * 0.35), (255, 255, 255), k * 0.2)
    lz.linea((c[0] - k * 0.1, c[1] + k * 0.35), (c[0] + k * 0.5, c[1] - k * 0.35), (255, 255, 255), k * 0.2)


def tache(lz, c, tam=70, progreso=1.0):
    if progreso <= 0:
        return
    k = sm.rebote(min(1, progreso)) * tam
    lz.circulo(c, k, relleno=(225, 60, 60), borde=CONTORNO, grosor=6)
    lz.linea((c[0] - k * 0.4, c[1] - k * 0.4), (c[0] + k * 0.4, c[1] + k * 0.4), (255, 255, 255), k * 0.2)
    lz.linea((c[0] - k * 0.4, c[1] + k * 0.4), (c[0] + k * 0.4, c[1] - k * 0.4), (255, 255, 255), k * 0.2)


# --------------------------------------------------------------- paisaje
def horizonte(lz, y=900, noche=False):
    """Mesetas del desierto y el piso a partir de la altura y."""
    oscuro = 0.45 if noche else 1.0

    def c(col):
        return tuple(int(v * oscuro) for v in col)
    mesetas = [(-120, 260, 190), (300, 640, 140), (700, 1250, 210)]
    for x0, x1, h in mesetas:
        lz.poligono([(x0, y), (x0 + 50, y - h), (x1 - 50, y - h), (x1, y)],
                    relleno=c(MESA), borde=c(MESA_OSCURA), grosor=6)
        lz.poligono([(x0 + 50, y - h), (x1 - 50, y - h), (x1 - 70, y - h + 28), (x0 + 70, y - h + 28)],
                    relleno=c(MESA_OSCURA))
    rect(lz, -2000, y, 3000, 4000, c(TIERRA), grosor=0)
    lz.linea((-2000, y), (3000, y), c(TIERRA_OSCURA), 8)


def sol(lz, c, r=120, t=0.0):
    for i in range(12):
        a = t * 0.6 + i * math.pi / 6
        p1 = (c[0] + math.cos(a) * r * 1.25, c[1] + math.sin(a) * r * 1.25)
        p2 = (c[0] + math.cos(a) * r * 1.75, c[1] + math.sin(a) * r * 1.75)
        lz.linea(p1, p2, (255, 200, 40), r * 0.16)
    lz.circulo(c, r, relleno=(255, 220, 60), borde=(255, 170, 30), grosor=10)


def luna_y_estrellas(lz, t=0.0):
    rnd = random.Random(7)
    for _ in range(40):
        x, y = rnd.uniform(0, 1080), rnd.uniform(60, 800)
        r = rnd.uniform(3, 7) * (0.7 + 0.3 * math.sin(t * 3 + x))
        lz.circulo((x, y), r, relleno=(255, 255, 230))
    lz.circulo((820, 330), 110, relleno=(250, 245, 215), borde=(200, 195, 170), grosor=8)
    lz.circulo((775, 300), 110, relleno=CIELOS["noche"][0])


def ondas_calor(lz, x0, x1, y, t, color=(255, 120, 40)):
    for i, x in enumerate(range(int(x0), int(x1), 150)):
        pts = [(x + 25 * math.sin(t * 6 + j * 0.9 + i), y - j * 22) for j in range(7)]
        for a, b in zip(pts, pts[1:]):
            lz.linea(a, b, color, 9)


def losa(lz, x0, x1, y_arriba, grosor=110, grietas=None, color=CONCRETO):
    """Losa de concreto vista de lado."""
    rect(lz, x0, y_arriba, x1, y_arriba + grosor, color, grosor=7, radio=6)
    rnd = random.Random(int(x0) * 3 + 1)
    for _ in range(int((x1 - x0) / 60)):
        px, py = rnd.uniform(x0 + 15, x1 - 15), rnd.uniform(y_arriba + 15, y_arriba + grosor - 15)
        lz.circulo((px, py), rnd.uniform(4, 8), relleno=CONCRETO_OSCURO)


def grieta(lz, pts, progreso=1.0, grosor=12):
    """Dibuja una grieta (lista de puntos) hasta cierto progreso."""
    if progreso <= 0:
        return
    n = max(2, int(len(pts) * min(1.0, progreso)))
    for a, b in zip(pts[: n - 1], pts[1:n]):
        lz.linea(a, b, (40, 35, 35), grosor)


def camino_grieta(a, b, segmentos=12, desvio=40, semilla=1):
    rnd = random.Random(semilla)
    pts = []
    for i in range(segmentos + 1):
        k = i / segmentos
        x = a[0] + (b[0] - a[0]) * k
        y = a[1] + (b[1] - a[1]) * k
        if 0 < i < segmentos:
            dx, dy = b[1] - a[1], -(b[0] - a[0])
            n = math.hypot(dx, dy) or 1
            d = rnd.uniform(-desvio, desvio)
            x, y = x + dx / n * d, y + dy / n * d
        pts.append((x, y))
    return pts


def carretera(lz, y_horiz=820, avance=0.0, juntas=True, resaltar=0.0, ancho_abajo=1700):
    """Carretera de concreto en perspectiva, con sus juntas."""
    cx = 540
    abajo = 2100

    def borde(y):
        k = (y - y_horiz) / (abajo - y_horiz)
        return ancho_abajo / 2 * k

    lz.poligono([(cx - 6, y_horiz), (cx + 6, y_horiz), (cx + borde(abajo), abajo),
                 (cx - borde(abajo), abajo)], relleno=CONCRETO, borde=CONTORNO, grosor=6)
    if juntas:
        for i in range(30):
            z = 1 + i - (avance % 1.0)
            if z <= 0.15:
                continue
            y = y_horiz + (abajo - y_horiz) * (0.9 / z)
            if y > abajo or y - y_horiz < 6:
                continue
            w = borde(y)
            g = max(2, 14 / z)
            lz.linea((cx - w, y), (cx + w, y), (95, 95, 92), g)
            if resaltar > 0:
                pulso = 0.5 + 0.5 * math.sin(lz.t * 10)
                lz.linea((cx - w, y), (cx + w, y), AMARILLO, g * (1 + resaltar * (1.2 + pulso)))
        # línea central (también en perspectiva)
        lz.linea((cx, y_horiz + 4), (cx, abajo), (130, 130, 126), 5)


# ---------------------------------------------------------- personajes
ROPAS = {
    "obrero": ((40, 110, 210), "casco"),
    "jefe": ((110, 50, 160), "copa"),
    "ingeniero": ((245, 245, 245), "casco_blanco"),
    "chofer": ((60, 160, 90), None),
}


def cabezon(lz, x, y, tipo="obrero", k=1.0, cara="normal", brazos="abajo", mira=1,
            tiembla=0.0, salto=0.0):
    """Personaje cabezón parado con los pies en (x, y)."""
    ropa, sombrero = ROPAS[tipo]
    t = lz.t
    rebote = abs(math.sin(t * 5 + x)) * 6 * k
    if tiembla:
        x += math.sin(t * 70) * 7 * tiembla
    y -= salto
    cadera = y - 70 * k
    oscuro = tuple(int(v * 0.6) for v in ropa)
    # piernas y zapatos
    for lado in (-1, 1):
        lz.linea((x + lado * 20 * k, cadera), (x + lado * 24 * k, y - 10 * k), CONTORNO, 22 * k)
        lz.linea((x + lado * 20 * k, cadera), (x + lado * 24 * k, y - 10 * k), (60, 60, 75), 14 * k)
        lz.circulo((x + lado * 24 * k + mira * 8 * k, y - 8 * k), 16 * k, relleno=(50, 35, 30))
    # brazos (detrás del cuerpo si van abajo)
    hombro_y = y - 165 * k - rebote

    def brazo(lado, ang_hombro, ang_codo):
        h = (x + lado * 46 * k, hombro_y + 10 * k)
        c = (h[0] + math.sin(math.radians(ang_hombro)) * 50 * k * lado,
             h[1] + math.cos(math.radians(ang_hombro)) * 50 * k)
        m = (c[0] + math.sin(math.radians(ang_codo)) * 45 * k * lado,
             c[1] + math.cos(math.radians(ang_codo)) * 45 * k)
        lz.linea(h, c, CONTORNO, 26 * k)
        lz.linea(c, m, CONTORNO, 26 * k)
        lz.linea(h, c, ropa, 16 * k)
        lz.linea(c, m, ropa, 16 * k)
        lz.circulo(m, 15 * k, relleno=PIEL, borde=CONTORNO, grosor=5 * k)
        return m

    poses = {
        "abajo": ((20, 10), (20, 10)),
        "arriba": ((150, 170), (150, 170)),
        "pulgar": ((20, 10), (95, 175)),
        "senala": ((20, 10), (80, 90)),
        "jalar": ((75, 85), (75, 85)),
        "festejo": ((130, 160), (130, 160)),
    }
    izq, der = poses.get(brazos, poses["abajo"])
    if brazos == "festejo":
        mov = math.sin(t * 10) * 20
        izq, der = (izq[0] + mov, izq[1] + mov), (der[0] - mov, der[1] - mov)
    # cuerpo
    rect(lz, x - 48 * k, y - 175 * k - rebote, x + 48 * k, cadera + 6 * k, ropa, grosor=6 * k, radio=26 * k)
    rect(lz, x - 48 * k, cadera - 14 * k, x + 48 * k, cadera + 6 * k, oscuro, grosor=6 * k, radio=8 * k)
    brazo(-1, *izq)
    mano = brazo(1, *der)
    if brazos == "pulgar":
        lz.linea(mano, (mano[0], mano[1] - 26 * k), CONTORNO, 15 * k)
        lz.linea(mano, (mano[0], mano[1] - 26 * k), PIEL, 8 * k)
    # cabeza
    hc = (x, y - 250 * k - rebote)
    R = 82 * k
    lz.circulo(hc, R, relleno=PIEL, borde=CONTORNO, grosor=7 * k)
    _cara(lz, hc, R, cara, mira)
    _sombrero(lz, hc, R, sombrero)
    return hc


def _cara(lz, c, R, cara, mira):
    ox = mira * R * 0.12
    ojos = [(c[0] - R * 0.32 + ox, c[1] - R * 0.05), (c[0] + R * 0.32 + ox, c[1] - R * 0.05)]
    boca = (c[0] + ox, c[1] + R * 0.38)
    if cara in ("sorpresa", "miedo"):
        for o in ojos:
            lz.circulo(o, R * 0.2, relleno=(255, 255, 255), borde=CONTORNO, grosor=R * 0.06)
            lz.circulo(o, R * 0.08, relleno=CONTORNO)
        lz.circulo(boca, R * 0.16, relleno=(120, 30, 30), borde=CONTORNO, grosor=R * 0.05)
    elif cara == "feliz":
        for o in ojos:
            arco(lz, (o[0], o[1] + R * 0.06), R * 0.13, 200, 340, CONTORNO, R * 0.07)
        arco(lz, (boca[0], boca[1] - R * 0.2), R * 0.32, 20, 160, CONTORNO, R * 0.08)
        lz.circulo((c[0] - R * 0.55, c[1] + R * 0.2), R * 0.12, relleno=(255, 170, 160))
        lz.circulo((c[0] + R * 0.55, c[1] + R * 0.2), R * 0.12, relleno=(255, 170, 160))
    elif cara == "preocupado":
        for o in ojos:
            lz.circulo(o, R * 0.09, relleno=CONTORNO)
        lz.linea((ojos[0][0] - R * 0.15, ojos[0][1] - R * 0.18), (ojos[0][0] + R * 0.12, ojos[0][1] - R * 0.25), CONTORNO, R * 0.06)
        lz.linea((ojos[1][0] - R * 0.12, ojos[1][1] - R * 0.25), (ojos[1][0] + R * 0.15, ojos[1][1] - R * 0.18), CONTORNO, R * 0.06)
        arco(lz, (boca[0], boca[1] + R * 0.15), R * 0.2, 210, 330, CONTORNO, R * 0.07)
    elif cara == "frio":
        for o in ojos:
            lz.circulo(o, R * 0.09, relleno=CONTORNO)
        pts = [(boca[0] - R * 0.3 + i * R * 0.1, boca[1] + (R * 0.05 if i % 2 else -R * 0.05)) for i in range(7)]
        for a, b in zip(pts, pts[1:]):
            lz.linea(a, b, CONTORNO, R * 0.06)
        lz.circulo((c[0] - R * 0.55, c[1] + R * 0.2), R * 0.12, relleno=(140, 190, 255))
        lz.circulo((c[0] + R * 0.55, c[1] + R * 0.2), R * 0.12, relleno=(140, 190, 255))
    elif cara == "calor":
        for o in ojos:
            lz.linea((o[0] - R * 0.12, o[1]), (o[0] + R * 0.12, o[1]), CONTORNO, R * 0.07)
        lz.circulo(boca, R * 0.13, relleno=(120, 30, 30), borde=CONTORNO, grosor=R * 0.05)
        gota = (c[0] + R * 0.85, c[1] - R * 0.2 + (lz.t * 120) % (R * 0.6))
        lz.poligono([(gota[0], gota[1] - R * 0.2), (gota[0] - R * 0.1, gota[1]), (gota[0] + R * 0.1, gota[1])],
                    relleno=(120, 190, 255))
        lz.circulo(gota, R * 0.1, relleno=(120, 190, 255))
    else:
        for o in ojos:
            lz.circulo(o, R * 0.1, relleno=CONTORNO)
        arco(lz, (boca[0], boca[1] - R * 0.12), R * 0.2, 30, 150, CONTORNO, R * 0.07)


def _sombrero(lz, c, R, tipo):
    if tipo in ("casco", "casco_blanco"):
        color = AMARILLO if tipo == "casco" else (250, 250, 250)
        pts = [(c[0] + math.cos(math.radians(a)) * R * 1.03, c[1] - R * 0.25 + math.sin(math.radians(a)) * R * 0.85)
               for a in range(180, 361, 12)]
        lz.poligono(pts, relleno=color, borde=CONTORNO, grosor=R * 0.08)
        rect(lz, c[0] - R * 1.2, c[1] - R * 0.32, c[0] + R * 1.2, c[1] - R * 0.16, color,
             grosor=R * 0.08, radio=R * 0.08)
        lz.linea((c[0], c[1] - R * 1.05), (c[0], c[1] - R * 0.35), CONTORNO, R * 0.07)
    elif tipo == "copa":
        rect(lz, c[0] - R * 0.6, c[1] - R * 1.75, c[0] + R * 0.6, c[1] - R * 0.65, (30, 25, 35),
             grosor=R * 0.07, radio=R * 0.06)
        rect(lz, c[0] - R * 0.6, c[1] - R * 0.95, c[0] + R * 0.6, c[1] - R * 0.78, (200, 40, 50), grosor=0)
        rect(lz, c[0] - R * 1.0, c[1] - R * 0.75, c[0] + R * 1.0, c[1] - R * 0.6, (30, 25, 35),
             grosor=R * 0.07, radio=R * 0.07)


def auto(lz, x, y, k=1.0, color=(220, 60, 60), mira=1):
    """Auto de caricatura visto de lado, con las llantas apoyadas en y."""
    rect(lz, x - 160 * k, y - 120 * k, x + 160 * k, y - 40 * k, color, grosor=7 * k, radio=30 * k)
    rect(lz, x - 90 * k + mira * 10 * k, y - 190 * k, x + 70 * k + mira * 10 * k, y - 110 * k, color,
         grosor=7 * k, radio=30 * k)
    rect(lz, x - 70 * k + mira * 10 * k, y - 175 * k, x + 50 * k + mira * 10 * k, y - 120 * k,
         (180, 225, 255), grosor=5 * k, radio=18 * k)
    for lado in (-1, 1):
        lz.circulo((x + lado * 95 * k, y - 38 * k), 38 * k, relleno=(40, 40, 45), borde=CONTORNO, grosor=6 * k)
        lz.circulo((x + lado * 95 * k, y - 38 * k), 15 * k, relleno=(200, 200, 200))
    lz.circulo((x + mira * 150 * k, y - 95 * k), 12 * k, relleno=(255, 240, 150))


def auto_atras(lz, x, y, k=1.0, color=(220, 60, 60)):
    """Auto visto desde atrás."""
    rect(lz, x - 170 * k, y - 150 * k, x + 170 * k, y - 30 * k, color, grosor=7 * k, radio=34 * k)
    rect(lz, x - 120 * k, y - 250 * k, x + 120 * k, y - 140 * k, color, grosor=7 * k, radio=34 * k)
    rect(lz, x - 100 * k, y - 235 * k, x + 100 * k, y - 155 * k, (150, 200, 240), grosor=5 * k, radio=20 * k)
    for lado in (-1, 1):
        rect(lz, x + lado * 150 * k - 25 * k, y - 120 * k, x + lado * 150 * k + 25 * k, y - 90 * k,
             (255, 70, 70), grosor=4 * k, radio=8 * k)
        rect(lz, x + lado * 120 * k - 30 * k, y - 35 * k, x + lado * 120 * k + 30 * k, y + 5 * k,
             (40, 40, 45), grosor=5 * k, radio=8 * k)
    rect(lz, x - 50 * k, y - 80 * k, x + 50 * k, y - 50 * k, (250, 250, 250), grosor=4 * k, radio=4 * k)


# ------------------------------------------------------------- subtítulos
def _limpiar(p):
    return re.sub(r"[.,;:…]+$", "", p).replace("...", "")


def _normal(p):
    return re.sub(r"[^\wáéíóúüñ]", "", p.lower())


def subtitulo(lz, txt, amarillo, progreso, y=880, tam=118):
    """Subtítulo grande al centro, estilo shorts (1-2 palabras)."""
    k = 0.72 + 0.28 * sm.rebote(min(1.0, progreso)) if progreso < 1 else 1.0
    f = lz.fuente(tam * k * SS)
    x, yy = ANCHO * SS / 2, y * SS
    sombra = int(7 * SS)
    lz.d.text((x + sombra, yy + sombra), txt, font=f, anchor="mm", fill=(0, 0, 0),
              stroke_width=int(tam * 0.1 * SS * k), stroke_fill=(0, 0, 0))
    lz.d.text((x, yy), txt, font=f, anchor="mm",
              fill=AMARILLO if amarillo else (255, 255, 255),
              stroke_width=int(tam * 0.1 * SS * k), stroke_fill=(0, 0, 0))


# ----------------------------------------------------------------- escena
class Frase:
    def __init__(self, texto, clave, dibujar, sonidos=(), voltear_en=None):
        self.texto = texto
        self.palabras = texto.split()
        self.clave = {_normal(c) for c in clave.split()}
        self.dibujar = dibujar
        self.sonidos = list(sonidos)  # [(fracción 0-1 o "palabra:N", nombre)]


class Explicador(Escena):
    """Video explicativo armado a partir de un guion (lista de Frase)."""
    frases = []
    final_extra = 1.3  # segundos después de la última palabra

    def __init__(self, voz=None):
        self.voz = voz
        palabras = [p for fr in self.frases for p in fr.palabras]
        if voz:
            tiempos, total = sincronizar.desde_audio(palabras, voz)
            self.duracion = max(total, tiempos[-1][1] + 0.4)
        else:
            tiempos = sincronizar.estimar(palabras)
            self.duracion = tiempos[-1][1] + self.final_extra
        self.tiempos = tiempos
        # inicio y fin de cada frase (la escena cambia un poquito antes de la frase)
        i = 0
        self.tramos = []
        for n, fr in enumerate(self.frases):
            ini = 0.0 if n == 0 else tiempos[i][0] - 0.08
            i += len(fr.palabras)
            self.tramos.append([ini, None, i - len(fr.palabras)])
        for n in range(len(self.tramos)):
            self.tramos[n][1] = self.tramos[n + 1][0] if n + 1 < len(self.tramos) else self.duracion
        self._armar_subtitulos(palabras)
        self._armar_sonidos()

    def _armar_subtitulos(self, palabras):
        self.subs = []
        idx = 0
        for fr in self.frases:
            grupo = []
            for p in fr.palabras:
                if grupo and len(" ".join(_limpiar(palabras[g]) for g in grupo + [idx])) > 15:
                    self._agregar_sub(grupo, palabras, fr)  # no juntar dos palabras largas
                    grupo = []
                grupo.append(idx)
                idx += 1
                texto = " ".join(_limpiar(palabras[g]) for g in grupo)
                corta = re.search(r"[.,;:?!…]$", p) or p.endswith("...")
                if len(grupo) == 2 or corta or len(texto) > 11:
                    self._agregar_sub(grupo, palabras, fr)
                    grupo = []
            if grupo:
                self._agregar_sub(grupo, palabras, fr)

    def _agregar_sub(self, grupo, palabras, fr):
        texto = " ".join(_limpiar(palabras[g]) for g in grupo).upper()
        amarillo = any(_normal(palabras[g]) in fr.clave for g in grupo)
        self.subs.append((self.tiempos[grupo[0]][0], texto, amarillo))

    def _armar_sonidos(self):
        sonidos = []
        for n, fr in enumerate(self.frases):
            ini, fin, i0 = self.tramos[n]
            if n > 0:
                sonidos.append((max(0, ini), "whoosh_suave"))
            for cuando, nombre in fr.sonidos:
                if isinstance(cuando, str) and cuando.startswith("palabra:"):
                    t = self.tiempos[i0 + int(cuando.split(":")[1])][0]
                else:
                    t = ini + (fin - ini) * cuando
                sonidos.append((t, nombre))
        self.sonidos = sonidos

    def momento_palabra(self, n_frase, k):
        """Segundo (relativo a la escena) en que se dice la palabra k de la frase."""
        ini, _, i0 = self.tramos[n_frase]
        return self.tiempos[i0 + k][0] - ini

    def dibujar(self, lz, t):
        n = 0
        while n + 1 < len(self.tramos) and t >= self.tramos[n + 1][0]:
            n += 1
        ini, fin, _ = self.tramos[n]
        u, dur = t - ini, fin - ini
        # empujón de cámara al entrar a cada escena + acercamiento lento
        self._zoom_extra = 1.0 + 0.07 * (1 - sm.frena(min(1.0, u / 0.3)))
        lz.camara(540, 960, self._zoom_extra)
        self.frases[n].dibujar(self, lz, u, dur, n)
        # subtítulo actual
        actual = None
        for s in self.subs:
            if s[0] <= t + 0.03:
                actual = s
            else:
                break
        if actual and t < self.tiempos[-1][1] + 0.6:
            subtitulo(lz, actual[1], actual[2], (t - actual[0]) / 0.14)

    def camara(self, lz, x=540, y=960, zoom=1.0, temblor=0.0):
        """Para usar dentro de las escenas: respeta el empujón de entrada."""
        lz.camara(x, y, zoom * self._zoom_extra, temblor)
