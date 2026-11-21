"""¿Por qué las carreteras de concreto tienen rayas? (juntas de control)

Video explicativo con narrador. Para sincronizarlo con la voz de ElevenLabs:
  python generar.py juntas_concreto --voz audio.mp3
"""
import math
import random

from motor import stickman as sm
from motor.explicador import (AMARILLO, CONCRETO, CONCRETO_OSCURO, CONTORNO, TIERRA,
                              Explicador, Frase, auto, auto_atras, cabezon, camino_grieta,
                              carretera, cielo, flecha, grieta, horizonte, letrero, losa,
                              luna_y_estrellas, ondas_calor, palomita, rect, sol, tache)

SUELO = 1350


def _p(u, dur):
    return max(0.0, min(1.0, u / max(1e-6, dur)))


# ------------------------------------------------------------- escenas
def e_rayas(esc, lz, u, dur, n):
    cielo(lz, "dia")
    esc.camara(lz, 540, 960, 1.0 + 0.08 * _p(u, dur))
    sol(lz, (880, 330), 90, lz.t)
    horizonte(lz, 820)
    carretera(lz, 820, avance=u * 0.5, resaltar=sm.suave((u - 0.7) / 0.4))
    cabezon(lz, 150, 1860, "obrero", k=0.95, cara="preocupado", brazos="senala")


def _mezcladora(lz, x, y, t):
    rect(lz, x - 230, y - 150, x + 170, y - 40, (230, 230, 235), radio=14)
    rect(lz, x + 170, y - 230, x + 330, y - 40, (240, 120, 40), radio=24)
    rect(lz, x + 200, y - 210, x + 300, y - 140, (180, 225, 255), grosor=5, radio=12)
    lz.circulo((x - 30, y - 230), 125, relleno=(250, 250, 250), borde=CONTORNO, grosor=7)
    for i in range(4):
        a = t * 3 + i * math.pi / 2
        lz.linea((x - 30 + math.cos(a) * 30, y - 230 + math.sin(a) * 110),
                 (x - 30 + math.cos(a + 0.5) * 110, y - 230 + math.sin(a + 0.5) * 30),
                 (240, 120, 40), 14)
    for wx in (x - 160, x + 30, x + 260):
        lz.circulo((wx, y - 30), 42, relleno=(40, 40, 45), borde=CONTORNO, grosor=6)
        lz.circulo((wx, y - 30), 16, relleno=(200, 200, 200))


def e_pieza(esc, lz, u, dur, n):
    p = _p(u, dur)
    cielo(lz, "dia")
    x1 = -100 + 1500 * sm.suave(p)
    esc.camara(lz, 300 + 650 * sm.suave(p), 1050, 1.0)
    horizonte(lz, 900)
    losa(lz, -600, x1, SUELO - 110)
    _mezcladora(lz, x1 + 260, SUELO + 10, lz.t)
    lz.linea((x1 + 60, SUELO - 200), (x1 + 10, SUELO - 110), (150, 150, 145), 26)
    cabezon(lz, x1 - 180, 1820, "obrero", k=1.0, cara="feliz", brazos="pulgar")


def e_perfecta(esc, lz, u, dur, n):
    p = _p(u, dur)
    cielo(lz, "dia")
    esc.camara(lz, 540, 1000, 1.0 + 0.06 * p)
    sol(lz, (870, 330), 90, lz.t)
    horizonte(lz, 900)
    losa(lz, -300, 1400, 1180, 120)
    rnd = random.Random(3)
    for i in range(7):
        x, y = rnd.uniform(80, 1000), rnd.uniform(1050, 1280)
        brillo = max(0.0, math.sin(lz.t * 6 + i * 1.7))
        if brillo > 0.1:
            lz._estrella((x, y), 30 * brillo, (255, 255, 255))
    cabezon(lz, 540, 1850, "jefe", k=1.3, cara="feliz", brazos="pulgar")


def _termometro(lz, x, y, nivel):
    rect(lz, x - 34, y - 520, x + 34, y, (255, 255, 255), radio=34)
    alto = 40 + 440 * nivel
    rect(lz, x - 18, y - alto, x + 18, y - 10, (230, 40, 40), grosor=0, radio=18)
    lz.circulo((x, y + 30), 62, relleno=(230, 40, 40), borde=CONTORNO, grosor=7)
    for i in range(6):
        lz.linea((x + 34, y - 80 - i * 75), (x + 60, y - 80 - i * 75), CONTORNO, 6)


def e_verano(esc, lz, u, dur, n):
    p = _p(u, dur)
    cielo(lz, "dia", mezcla="calor", k=sm.suave(p * 1.3))
    esc.camara(lz, 540, 960, 1.0 + 0.05 * p)
    sol(lz, (500, 1150 - 620 * sm.frena(p * 1.2)), 150, lz.t)
    horizonte(lz, 1000)
    _termometro(lz, 880, 1500, sm.suave(p))
    cabezon(lz, 330, 1850, "obrero", k=1.15, cara="calor")


def _losa_estirable(lz, largo, y=1150, flechas=0, color_flecha=AMARILLO, adentro=False):
    x0, x1 = 540 - largo / 2, 540 + largo / 2
    losa(lz, x0, x1, y, 130)
    if flechas > 0:
        d = 150 * flechas
        mov = 15 * math.sin(lz.t * 9)
        if adentro:
            flecha(lz, (x0 - d - 40 + mov, y + 65), (x0 - 25, y + 65), color_flecha)
            flecha(lz, (x1 + d + 40 - mov, y + 65), (x1 + 25, y + 65), color_flecha)
        else:
            flecha(lz, (x0 - 20, y + 65), (x0 - d - 40 - mov, y + 65), color_flecha)
            flecha(lz, (x1 + 20, y + 65), (x1 + d + 40 + mov, y + 65), color_flecha)
    return x0, x1


def e_estira(esc, lz, u, dur, n):
    p = _p(u, dur)
    cielo(lz, "calor")
    esc.camara(lz, 540, 1000, 1.0)
    sol(lz, (870, 330), 110, lz.t)
    horizonte(lz, 900)
    ondas_calor(lz, 220, 900, 1110, lz.t)
    _losa_estirable(lz, 640 + 140 * sm.frena(p), flechas=min(1.0, p * 3))


def e_centimetros(esc, lz, u, dur, n):
    p = _p(u, dur)
    cielo(lz, "calor")
    esc.camara(lz, 540, 1000, 1.0 + 0.08 * p)
    sol(lz, (870, 330), 110, lz.t)
    horizonte(lz, 900)
    x0, x1 = _losa_estirable(lz, 780)
    # parte que "creció"
    crece = 50 * sm.frena(min(1.0, p * 1.5))
    rect(lz, x1 - 4, 1150, x1 + crece, 1280, AMARILLO, radio=6)
    # cota de 100 m
    y = 1340
    lz.linea((x0, y), (x1, y), (255, 255, 255), 8)
    for xx in (x0, x1):
        lz.linea((xx, y - 25), (xx, y + 25), (255, 255, 255), 8)
    letrero(lz, "100 m", 540, y + 70, tam=80, color=(255, 255, 255), progreso=(u - 0.1) / 0.5, giro=0)
    letrero(lz, "+4 cm", 540, 640, tam=190, progreso=(u - dur * 0.45) / 0.6, giro=-6)


def e_encoge(esc, lz, u, dur, n):
    p = _p(u, dur)
    cielo(lz, "noche")
    luna_y_estrellas(lz, lz.t)
    esc.camara(lz, 540, 1000, 1.0)
    horizonte(lz, 900, noche=True)
    _losa_estirable(lz, 780 - 140 * sm.frena(p), flechas=min(1.0, p * 3),
                    color_flecha=(120, 190, 255), adentro=True)
    cabezon(lz, 220, 1850, "obrero", k=1.05, cara="frio", tiembla=1.0)


def _yunque(lz, x, y):
    lz.poligono([(x - 160, y), (x + 160, y), (x + 120, y - 60), (x + 60, y - 70), (x + 60, y - 150),
                 (x + 200, y - 160), (x + 180, y - 230), (x - 150, y - 230), (x - 200, y - 190),
                 (x - 70, y - 150), (x - 70, y - 70), (x - 120, y - 60)],
                relleno=(70, 70, 80), borde=CONTORNO, grosor=7)
    letrero(lz, "10 t", x, y - 190, tam=70, color=(255, 255, 255), progreso=1, giro=0)


def e_aplastar(esc, lz, u, dur, n):
    p = _p(u, dur)
    cielo(lz, "estudio")
    rect(lz, -500, SUELO, 1600, 3000, (235, 180, 110), grosor=0)
    lz.linea((-500, SUELO), (1600, SUELO), (200, 140, 80), 8)
    golpe = 0.22
    temblor = 0.6 * (1 - (p - golpe) / 0.06) if golpe <= p < golpe + 0.06 else 0
    esc.camara(lz, 540, 1000, 1.0, temblor=temblor)
    bx0, bx1, by = 330, 750, SUELO - 220
    if p < 0.5:
        losa(lz, bx0, bx1, by, 220)
        q = min(1.0, p / golpe)
        _yunque(lz, 540, -250 + (by + 250) * sm.acelera(q))
        palomita(lz, (540, 560), progreso=(p - golpe - 0.03) / 0.12)
    else:
        q = (p - 0.5) / 0.5
        separa = 45 * sm.frena((q - 0.6) / 0.3) if q > 0.6 else 0
        losa(lz, bx0 - separa, 540 - separa, by, 220)
        losa(lz, 540 + separa, bx1 + separa, by, 220)
        if q <= 0.6:
            losa(lz, bx0, bx1, by, 220)
            grieta(lz, camino_grieta((540, by), (540, SUELO), 6, 14, 4), progreso=(q - 0.45) / 0.15)
        for lado in (-1, 1):
            xm = 540 + lado * 420 + lado * separa
            lz.linea((540 + lado * (210 + separa), by + 110), (xm, 1640), (150, 100, 50), 12)
            cabezon(lz, xm + lado * 40, 1850, "obrero", k=0.95, cara="enojado" if q < 0.6 else "sorpresa",
                    brazos="jalar", mira=-lado, tiembla=0.4 if q < 0.6 else 0)
        tache(lz, (540, 560), progreso=(q - 0.62) / 0.15)


def _losa_arriba(lz, grietas_mostradas, u):
    rect(lz, -300, -300, 1400, 2400, TIERRA, grosor=0)
    rect(lz, 70, 380, 1010, 1560, CONCRETO, radio=10)
    rnd = random.Random(11)
    for _ in range(80):
        lz.circulo((rnd.uniform(90, 990), rnd.uniform(400, 1540)), rnd.uniform(4, 9), relleno=CONCRETO_OSCURO)


GRIETA_GRANDE = camino_grieta((70, 900), (1010, 1010), 14, 60, 21)
GRIETAS_CHUECAS = [camino_grieta(a, b, 10, 45, s) for s, (a, b) in enumerate([
    ((70, 520), (640, 380)), ((1010, 620), (420, 1100)), ((250, 1560), (520, 1050)),
    ((1010, 1350), (650, 1560)), ((70, 1250), (400, 1500)), ((700, 380), (900, 800)),
    ((420, 700), (700, 760)),
])]


def e_crac(esc, lz, u, dur, n):
    t_crac = esc.momento_palabra(n, 4)
    temblor = 1 - (u - t_crac) / 0.4 if t_crac <= u < t_crac + 0.4 else 0
    esc.camara(lz, 540, 960, 1.0 + 0.05 * _p(u, dur), temblor=temblor)
    _losa_arriba(lz, 0, u)
    grieta(lz, GRIETA_GRANDE, progreso=(u - t_crac) / 0.5, grosor=16)
    for i, rama in enumerate((camino_grieta(GRIETA_GRANDE[5], (420, 1200), 6, 30, 5),
                              camino_grieta(GRIETA_GRANDE[9], (760, 700), 6, 30, 6))):
        grieta(lz, rama, progreso=(u - t_crac - 0.25 - i * 0.15) / 0.4, grosor=11)
    letrero(lz, "¡CRAC!", 540, 650, tam=200, progreso=(u - t_crac) / 0.25, giro=-7)


def e_chuecas(esc, lz, u, dur, n):
    p = _p(u, dur)
    esc.camara(lz, 540, 960, 1.04 - 0.04 * p)
    _losa_arriba(lz, 0, u)
    grieta(lz, GRIETA_GRANDE, grosor=16)
    for i, g in enumerate(GRIETAS_CHUECAS):
        grieta(lz, g, progreso=(p - i * 0.09) / 0.18, grosor=12)
    cabezon(lz, 830, 2010, "jefe", k=1.2, cara="sorpresa", mira=-1)


def _losa_inclinada(lz, pivote_x, y_top, largo, ang, lado):
    """Losa que gira sobre su extremo exterior (lado=-1 izquierda, 1 derecha)."""
    a = math.radians(ang)
    h = 110
    d = (-lado * math.cos(a), -math.sin(a))      # hacia el centro, inclinada hacia arriba
    nrm = (-lado * math.sin(a) * -1, math.cos(a))  # perpendicular hacia abajo
    nrm = (math.sin(a) * -lado, math.cos(a))
    p0 = (pivote_x, y_top)
    p1 = (p0[0] + d[0] * largo, p0[1] + d[1] * largo)
    pts = [p0, p1, (p1[0] + nrm[0] * h, p1[1] + nrm[1] * h), (p0[0] + nrm[0] * h, p0[1] + nrm[1] * h)]
    lz.poligono(pts, relleno=CONCRETO, borde=CONTORNO, grosor=7)


def e_golpe(esc, lz, u, dur, n):
    t_pop = esc.momento_palabra(n, 12)
    q = (u - t_pop) / 0.25
    temblor = 1 - (u - t_pop) / 0.5 if t_pop <= u < t_pop + 0.5 else (
        0.15 if u < t_pop and u > t_pop - 1.2 else 0)
    cielo(lz, "calor")
    esc.camara(lz, 540, 1000, 1.0 + 0.1 * sm.frena(min(1.0, max(0.0, q))), temblor=temblor)
    sol(lz, (880, 320), 110, lz.t)
    horizonte(lz, 900)
    ang = 14 * sm.rebote(min(1.0, max(0.0, q)))
    _losa_inclinada(lz, -260, 1180, 800, ang, -1)
    _losa_inclinada(lz, 1340, 1180, 800, ang, 1)
    if u < t_pop:
        k = min(1.0, u / 0.5)
        flecha(lz, (60, 1080), (300 + 30 * math.sin(lz.t * 9), 1080), AMARILLO, 20 * k + 1)
        flecha(lz, (1020, 1080), (780 - 30 * math.sin(lz.t * 9), 1080), AMARILLO, 20 * k + 1)
    lz.polvo((540, 1190), (u - t_pop) / 0.7)
    x_auto = animar_auto(u, t_pop)
    auto(lz, x_auto, 1700, k=1.0)
    letrero(lz, "!", x_auto + 40, 1420, tam=150, color=(255, 60, 60), progreso=(u - t_pop - 0.15) / 0.3, giro=0)
    letrero(lz, "¡PUM!", 540, 800, tam=190, progreso=(u - t_pop) / 0.3, giro=8)


def animar_auto(u, t_pop):
    if u < t_pop:
        return -300 + 380 * u / max(0.1, t_pop)
    return 80 + 60 * sm.frena(min(1.0, (u - t_pop) / 0.4))


def _foco(lz, c, k):
    if k <= 0:
        return
    k = sm.rebote(min(1.0, k))
    for i in range(8):
        a = i * math.pi / 4 + lz.t
        lz.linea((c[0] + math.cos(a) * 95 * k, c[1] + math.sin(a) * 95 * k),
                 (c[0] + math.cos(a) * 130 * k, c[1] + math.sin(a) * 130 * k), AMARILLO, 12)
    lz.circulo(c, 70 * k, relleno=(255, 240, 120), borde=CONTORNO, grosor=7)
    rect(lz, c[0] - 32 * k, c[1] + 55 * k, c[0] + 32 * k, c[1] + 100 * k, (150, 150, 160), radio=8)


def e_locura(esc, lz, u, dur, n):
    p = _p(u, dur)
    cielo(lz, "estudio")
    esc.camara(lz, 540, 1000, 1.0 + 0.06 * p)
    rect(lz, -500, 1500, 1600, 3000, (235, 180, 110), grosor=0)
    hc = cabezon(lz, 330, 1850, "ingeniero", k=1.25, cara="feliz", brazos="arriba")
    _foco(lz, (hc[0], hc[1] - 300), (u - 0.15) / 0.3)
    jefe_k = (p - 0.5) / 0.15
    if jefe_k > 0:
        cabezon(lz, 820, 1880, "jefe", k=1.15, cara="sorpresa", mira=-1, salto=30 * max(0, math.sin(min(1, jefe_k) * math.pi)))
        letrero(lz, "¿¡QUÉ!?", 820, 1060, tam=120, color=(255, 80, 80), progreso=jefe_k, giro=8)


def _cortadora(lz, x, y, t):
    rect(lz, x - 70, y - 60, x + 70, y + 60, (250, 190, 30), radio=14)
    lz.circulo((x, y), 48, relleno=(210, 210, 220), borde=CONTORNO, grosor=6)
    for i in range(8):
        a = t * 25 + i * math.pi / 4
        lz.linea((x, y), (x + math.cos(a) * 44, y + math.sin(a) * 44), CONTORNO, 5)


def e_ranuras(esc, lz, u, dur, n):
    p = _p(u, dur)
    esc.camara(lz, 540, 960, 1.0)
    rect(lz, -300, -300, 1400, 2400, TIERRA, grosor=0)
    rect(lz, 90, -100, 850, 2100, CONCRETO, radio=0)
    for y in (480,):
        lz.linea((90, y), (850, y), (80, 80, 78), 12)
    y_corte = 960
    avance = 90 + 760 * sm.suave((p - 0.1) / 0.75)
    if avance > 90:
        lz.linea((90, y_corte), (avance, y_corte), (80, 80, 78), 12)
    _cortadora(lz, avance, y_corte, lz.t)
    lz.polvo((avance, y_corte), (lz.t * 3) % 1.0, cantidad=4, color=(235, 235, 230))
    # cota de 4-5 m
    lz.linea((950, 480), (950, 960), (255, 255, 255), 8)
    for yy in (480, 960):
        lz.linea((925, yy), (975, yy), (255, 255, 255), 8)
    letrero(lz, "4-5 m", 965, 1060, tam=64, color=(255, 255, 255), progreso=(p - 0.3) / 0.3, giro=0)
    cabezon(lz, 470, 1850, "obrero", k=1.1, cara="feliz", brazos="pulgar")


def e_derechita(esc, lz, u, dur, n):
    p = _p(u, dur)
    cielo(lz, "estudio")
    esc.camara(lz, 540, 1050, 1.0 + 0.07 * p)
    rect(lz, -500, 1300, 1600, 3000, (205, 150, 95), grosor=0)
    rnd = random.Random(2)
    for _ in range(60):
        lz.circulo((rnd.uniform(-100, 1180), rnd.uniform(1320, 1700)), rnd.uniform(8, 18), relleno=(170, 120, 75))
    x0, x1, top, bot = 110, 970, 880, 1300
    abre = 18 * sm.frena((p - 0.62) / 0.2) if p > 0.62 else 0
    rect(lz, x0 - abre, top, 540 - abre, bot, CONCRETO, radio=8)
    rect(lz, 540 + abre, top, x1 + abre, bot, CONCRETO, radio=8)
    lz.poligono([(515, top), (565, top), (540, top + 120)], relleno=(80, 80, 78))
    if p < 0.62:
        lz.linea((540, top + 120), (540, bot), CONCRETO, 26)
    grieta(lz, camino_grieta((540, top + 120), (540, bot), 8, 10, 8), progreso=(p - 0.12) / 0.4, grosor=12)
    if p > 0.8:
        rect(lz, 515, top - 10, 565, top + 40, (30, 30, 30), radio=6)
    flecha(lz, (300, 700), (505, 860), AMARILLO, 18)
    letrero(lz, "corte", 280, 650, tam=80, color=(255, 255, 255), progreso=(p - 0.02) / 0.2, giro=-5)
    palomita(lz, (800, 650), tam=80, progreso=(p - 0.6) / 0.15)


def e_tac(esc, lz, u, dur, n):
    tacs = [esc.momento_palabra(n, k) for k in (7, 8, 9)]
    cielo(lz, "dia")
    esc.camara(lz, 540, 960, 1.0)
    sol(lz, (870, 330), 90, lz.t)
    horizonte(lz, 820)
    carretera(lz, 820, avance=u * 1.6)
    brinco = 0
    for i, tk in enumerate(tacs):
        if u >= tk:
            brinco = 22 * math.exp(-(u - tk) * 12)
        letrero(lz, "TAC", 300 + i * 240, 1250 - i * 60, tam=130, progreso=(u - tk) / 0.35, giro=-8 + i * 8)
    auto_atras(lz, 540, 1780 - brinco, k=1.35)


def e_planearon(esc, lz, u, dur, n):
    p = _p(u, dur)
    cielo(lz, "dia")
    esc.camara(lz, 540, 1000, 1.15 - 0.15 * sm.frena(p))
    sol(lz, (870, 330), 90, lz.t)
    horizonte(lz, 820)
    carretera(lz, 820, avance=u * 0.3)
    cabezon(lz, 200, 1830, "obrero", k=1.0, cara="feliz", brazos="festejo")
    cabezon(lz, 880, 1830, "ingeniero", k=1.0, cara="feliz", brazos="festejo", mira=-1)
    cabezon(lz, 540, 1870, "jefe", k=1.2, cara="feliz", brazos="pulgar")


# ---------------------------------------------------------------- guion
class JuntasConcreto(Explicador):
    nombre = "juntas_concreto"
    titulo = "¿Por qué las carreteras de concreto tienen rayas?"
    duracion = 58.0
    frases = [
        Frase("¿Por qué las carreteras de concreto tienen estas rayas?", "rayas", e_rayas),
        Frase("Imagina que construyes una carretera de concreto de una sola pieza larguísima.",
              "pieza larguísima", e_pieza),
        Frase("Lisa, bonita, perfecta.", "perfecta", e_perfecta, [(0.55, "ding")]),
        Frase("Pero llegó el verano.", "verano", e_verano),
        Frase("Con el calor, el concreto se estira.", "estira", e_estira),
        Frase("Un tramo de cien metros puede crecer casi cuatro centímetros.",
              "cuatro centímetros", e_centimetros, [(0.45, "pop")]),
        Frase("Y en las noches frías, se encoge otra vez.", "encoge", e_encoge),
        Frase("El concreto aguanta que lo aplasten, pero no que lo jalen.", "aplasten jalen",
              e_aplastar, [(0.22, "golpe"), (0.5 + 0.5 * 0.45, "crac")]),
        Frase("Así que, al encogerse... ¡crac! Se agrieta por donde quiere.", "crac agrieta",
              e_crac, [("palabra:4", "crac"), ("palabra:4", "golpecito")]),
        Frase("Grietas chuecas, por todos lados.", "chuecas", e_chuecas, [(0.1, "crac"), (0.45, "crac")]),
        Frase("Y en olas de calor, algunas losas se empujan tanto que se levantan de golpe.",
              "golpe", e_golpe, [("palabra:12", "golpe"), ("palabra:12", "boing")]),
        Frase("La solución parece una locura: romper el concreto a propósito.", "romper propósito",
              e_locura, [(0.15, "ding"), (0.5, "pop")]),
        Frase("Pocas horas después de echarlo, cortan ranuras cada cuatro o cinco metros.",
              "ranuras", e_ranuras),
        Frase("Así, la grieta aparece justo ahí, derechita y escondida.", "derechita escondida",
              e_derechita, [(0.14, "crac"), (0.62, "ding")]),
        Frase("Por eso, cuando manejas y escuchas ese tac... tac... tac...", "tac",
              e_tac, [("palabra:7", "tac"), ("palabra:8", "tac"), ("palabra:9", "tac")]),
        Frase("son las grietas que los ingenieros planearon desde el principio.", "planearon",
              e_planearon, [(0.6, "tada")]),
    ]
