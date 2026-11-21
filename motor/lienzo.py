"""El lienzo donde se dibuja cada cuadro del video.

Todo se dibuja al doble de resolución y luego se reduce: así las líneas salen
suaves (sin escalones). Las escenas trabajan en coordenadas del "mundo"
(1080 de ancho, 1920 de alto) y la cámara decide qué parte se ve.
"""
import math
import os
import random

from PIL import Image, ImageDraw, ImageFont

from . import stickman as sm

ANCHO, ALTO = 1080, 1920
SS = 2  # superamuestreo

_AQUI = os.path.dirname(os.path.abspath(__file__))
FUENTE = os.path.join(_AQUI, "..", "fuentes", "Anton-Regular.ttf")

ESTILOS = {
    # Colores fuertes que resaltan en el feed
    "pop": {
        "fondo": ((255, 214, 64), (255, 120, 58)),
        "suelo": (43, 45, 66), "borde_suelo": (20, 20, 30),
        "figura": (17, 17, 17), "contorno": (255, 255, 255), "ojos": (255, 255, 255),
        "texto": (255, 255, 255), "texto_borde": (0, 0, 0),
        "acento": (255, 40, 90), "acento2": (40, 200, 255),
        "rayas": None,
    },
    # Fondo oscuro con el monito brillante
    "neon": {
        "fondo": ((10, 12, 40), (55, 10, 75)),
        "suelo": (18, 20, 52), "borde_suelo": (61, 245, 255),
        "figura": (61, 245, 255), "contorno": (120, 47, 247), "ojos": (10, 12, 40),
        "texto": (255, 255, 255), "texto_borde": (120, 47, 247),
        "acento": (255, 60, 200), "acento2": (255, 230, 70),
        "rayas": None,
    },
    # Como dibujado en una libreta
    "cuaderno": {
        "fondo": ((250, 248, 240), (240, 236, 222)),
        "suelo": (235, 230, 214), "borde_suelo": (30, 30, 30),
        "figura": (25, 25, 25), "contorno": (250, 248, 240), "ojos": (250, 248, 240),
        "texto": (25, 25, 25), "texto_borde": (250, 248, 240),
        "acento": (220, 40, 40), "acento2": (40, 90, 220),
        "rayas": (170, 200, 235),
    },
}


def _fuente(tam):
    try:
        return ImageFont.truetype(FUENTE, int(tam))
    except OSError:
        return ImageFont.truetype("DejaVuSans-Bold.ttf", int(tam))


class Lienzo:
    def __init__(self, estilo="pop"):
        if estilo not in ESTILOS:
            raise ValueError(f"Estilo desconocido: {estilo}. Opciones: {', '.join(ESTILOS)}")
        self.nombre_estilo = estilo
        self.e = ESTILOS[estilo]
        self.fondo = self._crear_fondo()
        self._fuentes = {}
        self.t = 0.0

    # ----------------------------------------------------------- preparación
    def _crear_fondo(self):
        W, H = ANCHO * SS, ALTO * SS
        (r1, g1, b1), (r2, g2, b2) = self.e["fondo"]
        col = Image.new("RGB", (1, H))
        px = col.load()
        for y in range(H):
            k = y / (H - 1)
            px[0, y] = (int(r1 + (r2 - r1) * k), int(g1 + (g2 - g1) * k), int(b1 + (b2 - b1) * k))
        img = col.resize((W, H))
        if self.e["rayas"]:
            d = ImageDraw.Draw(img)
            for y in range(240 * SS, H, 64 * SS):
                d.line([(0, y), (W, y)], fill=self.e["rayas"], width=2 * SS)
            d.line([(110 * SS, 0), (110 * SS, H)], fill=(235, 150, 150), width=3 * SS)
        return img

    def fuente(self, tam):
        tam = int(tam)
        if tam not in self._fuentes:
            self._fuentes[tam] = _fuente(tam)
        return self._fuentes[tam]

    # ----------------------------------------------------------- cada cuadro
    def nuevo_cuadro(self, t):
        self.t = t
        self.img = self.fondo.copy()
        self.d = ImageDraw.Draw(self.img)
        self.cx, self.cy, self.zoom = ANCHO / 2, ALTO / 2, 1.0
        self.dx = self.dy = 0.0

    def camara(self, x=540, y=960, zoom=1.0, temblor=0.0):
        """Dónde mira la cámara (centro del mundo), acercamiento y temblor (0-1)."""
        self.cx, self.cy, self.zoom = x, y, zoom
        if temblor > 0:
            t = self.t
            fuerza = 38 * temblor
            self.dx = fuerza * (math.sin(t * 91) * 0.6 + math.sin(t * 57 + 1.3) * 0.4)
            self.dy = fuerza * (math.sin(t * 77 + 0.7) * 0.6 + math.sin(t * 43 + 2.1) * 0.4)
        else:
            self.dx = self.dy = 0.0

    def terminar(self):
        return self.img.reduce(SS)

    # --------------------------------------------------- conversión de puntos
    def p(self, x, y):
        """Mundo → píxel del lienzo grande."""
        sx = (x - self.cx) * self.zoom + ANCHO / 2 + self.dx
        sy = (y - self.cy) * self.zoom + ALTO / 2 + self.dy
        return (sx * SS, sy * SS)

    def l(self, largo):
        return largo * self.zoom * SS

    # ------------------------------------------------------------ primitivas
    def linea(self, a, b, color, grosor):
        w = max(1, int(self.l(grosor)))
        pa, pb = self.p(*a), self.p(*b)
        self.d.line([pa, pb], fill=color, width=w)
        r = w / 2
        for q in (pa, pb):
            self.d.ellipse([q[0] - r, q[1] - r, q[0] + r, q[1] + r], fill=color)

    def circulo(self, c, radio, relleno=None, borde=None, grosor=0):
        q = self.p(*c)
        r = self.l(radio)
        self.d.ellipse([q[0] - r, q[1] - r, q[0] + r, q[1] + r], fill=relleno,
                       outline=borde, width=max(0, int(self.l(grosor))) if borde else 0)

    def poligono(self, puntos, relleno=None, borde=None, grosor=0):
        pts = [self.p(*q) for q in puntos]
        self.d.polygon(pts, fill=relleno)
        if borde and grosor:
            w = max(1, int(self.l(grosor)))
            self.d.line(pts + [pts[0]], fill=borde, width=w, joint="curve")

    # --------------------------------------------------------------- escenario
    def suelo(self, y=1400):
        """Piso desde la altura y hacia abajo (se mueve con la cámara)."""
        _, sy = self.p(0, y)
        W, H = ANCHO * SS, ALTO * SS
        if sy < H:
            self.d.rectangle([0, sy, W, H], fill=self.e["suelo"])
            self.d.line([(0, sy), (W, sy)], fill=self.e["borde_suelo"], width=int(self.l(8)))

    def caja(self, x, y, ancho, alto, giro=0.0, pivote=None, color=(196, 128, 60)):
        """Caja con esquina inferior izquierda en (x, y). `giro` en grados
        alrededor de `pivote` (por defecto la esquina inferior derecha)."""
        esquinas = [(x, y), (x + ancho, y), (x + ancho, y - alto), (x, y - alto)]
        px, py = pivote if pivote else (x + ancho, y)
        a = math.radians(giro)
        ca, sa = math.cos(a), math.sin(a)
        rot = [(px + (qx - px) * ca - (qy - py) * sa, py + (qx - px) * sa + (qy - py) * ca)
               for qx, qy in esquinas]
        self.poligono(rot, relleno=color, borde=(40, 25, 10), grosor=8)
        # una cruz de cinta para que se lea como caja
        m1 = ((rot[0][0] + rot[1][0]) / 2, (rot[0][1] + rot[1][1]) / 2)
        m2 = ((rot[2][0] + rot[3][0]) / 2, (rot[2][1] + rot[3][1]) / 2)
        self.linea(m1, m2, (230, 190, 120), 14)

    def platano(self, x, y, giro=0.0, escala=1.0):
        """Cáscara de plátano centrada en (x, y)."""
        k = escala
        pts = []
        for i in range(13):  # borde de afuera
            a = math.radians(200 + i * 140 / 12)
            pts.append((math.cos(a) * 70 * k, math.sin(a) * 40 * k + 30 * k))
        for i in range(13):  # borde de adentro
            a = math.radians(340 - i * 140 / 12)
            pts.append((math.cos(a) * 55 * k, math.sin(a) * 22 * k + 30 * k))
        g = math.radians(giro)
        cg, sg = math.cos(g), math.sin(g)
        mundo = [(x + px * cg - py * sg, y + px * sg + py * cg) for px, py in pts]
        self.poligono(mundo, relleno=(255, 225, 40), borde=(110, 80, 10), grosor=6)
        punta = mundo[0]
        self.circulo(punta, 9 * k, relleno=(90, 60, 15))

    # --------------------------------------------------------------- monito
    def monito(self, pose: sm.Pose, color=None, contorno=None):
        j = sm.articulaciones(pose)
        col = color or self.e["figura"]
        borde = contorno or self.e["contorno"]
        g = sm.GROSOR * pose.escala
        segmentos_atras = [("hombro", "codo_a"), ("codo_a", "mano_a"),
                           ("cadera", "rodilla_a"), ("rodilla_a", "pie_a")]
        segmentos_frente = [("cadera", "cuello"),
                            ("cadera", "rodilla_f"), ("rodilla_f", "pie_f"),
                            ("hombro", "codo_f"), ("codo_f", "mano_f")]
        R = sm.CABEZA_R * pose.escala
        # contorno primero (más grueso) para que resalte sobre cualquier fondo
        for a, b in segmentos_atras + segmentos_frente:
            self.linea(j[a], j[b], borde, g + 10 * pose.escala)
        self.circulo(j["cabeza"], R + 5 * pose.escala, relleno=borde)
        for a, b in segmentos_atras + segmentos_frente:
            self.linea(j[a], j[b], col, g)
        self.circulo(j["cabeza"], R, relleno=col)
        self._cara(j, R, pose.cara)

    def _cara(self, j, R, cara):
        c, u, f = j["cabeza"], j["arriba"], j["adelante"]
        ojo = self.e["ojos"]

        def en(adel, arr):
            return (c[0] + f[0] * adel * R + u[0] * arr * R,
                    c[1] + f[1] * adel * R + u[1] * arr * R)

        ojos = [en(0.62, 0.12), en(0.18, 0.12)]
        if cara == "mareado":
            for o in ojos:
                s = 0.16
                self.linea(en_off(o, f, u, -s, -s, R), en_off(o, f, u, s, s, R), ojo, R * 0.09)
                self.linea(en_off(o, f, u, -s, s, R), en_off(o, f, u, s, -s, R), ojo, R * 0.09)
            self.linea(en(0.25, -0.45), en(0.6, -0.38), ojo, R * 0.08)
        elif cara in ("sorpresa", "miedo"):
            for o in ojos:
                self.circulo(o, R * 0.2, relleno=ojo)
            self.circulo(en(0.42, -0.45), R * 0.16, relleno=ojo)
        elif cara == "feliz":
            for o in ojos:
                self.linea(en_off(o, f, u, -0.14, -0.05, R), en_off(o, f, u, 0, 0.1, R), ojo, R * 0.09)
                self.linea(en_off(o, f, u, 0, 0.1, R), en_off(o, f, u, 0.14, -0.05, R), ojo, R * 0.09)
            self.linea(en(0.2, -0.35), en(0.45, -0.5), ojo, R * 0.09)
            self.linea(en(0.45, -0.5), en(0.72, -0.32), ojo, R * 0.09)
        elif cara == "enojado":
            for o in ojos:
                self.circulo(o, R * 0.12, relleno=ojo)
            self.linea(en(0.05, 0.42), en(0.75, 0.3), ojo, R * 0.1)
            self.linea(en(0.25, -0.45), en(0.62, -0.45), ojo, R * 0.08)
        else:  # normal
            for o in ojos:
                self.circulo(o, R * 0.13, relleno=ojo)

    # ------------------------------------------------------------- efectos
    def estrellitas(self, centro, radio=90, cantidad=3, velocidad=1.0):
        """Estrellas que giran alrededor de la cabeza (mareado)."""
        for i in range(cantidad):
            a = self.t * 4 * velocidad + i * 2 * math.pi / cantidad
            x = centro[0] + math.cos(a) * radio
            y = centro[1] - 40 + math.sin(a) * radio * 0.35
            self._estrella((x, y), 26, self.e["acento2"])

    def _estrella(self, c, r, color):
        pts = []
        for i in range(10):
            rr = r if i % 2 == 0 else r * 0.45
            a = -math.pi / 2 + i * math.pi / 5
            pts.append((c[0] + math.cos(a) * rr, c[1] + math.sin(a) * rr))
        self.poligono(pts, relleno=color, borde=(20, 20, 20), grosor=4)

    def polvo(self, centro, progreso, cantidad=7, color=None):
        """Nubecitas de polvo que salen hacia los lados (progreso 0→1)."""
        if not 0 <= progreso <= 1:
            return
        col = color or (230, 230, 230)
        rnd = random.Random(int(centro[0]) * 7 + int(centro[1]))
        for i in range(cantidad):
            lado = -1 if i % 2 else 1
            dist = (60 + rnd.random() * 160) * sm.frena(progreso)
            x = centro[0] + lado * dist
            y = centro[1] - rnd.random() * 50 * progreso
            r = (30 + rnd.random() * 25) * (1 - progreso)
            if r > 1:
                self.circulo((x, y), r, relleno=col)

    def lineas_velocidad(self, intensidad=1.0, color=(255, 255, 255)):
        """Rayas tipo anime desde los bordes hacia el centro de la pantalla."""
        if intensidad <= 0:
            return
        W, H = ANCHO * SS, ALTO * SS
        rnd = random.Random(int(self.t * 30))
        for _ in range(int(40 * intensidad)):
            a = rnd.random() * 2 * math.pi
            r1 = (0.55 + rnd.random() * 0.25) * H * 0.6
            r2 = H
            x1, y1 = W / 2 + math.cos(a) * r1, H / 2 + math.sin(a) * r1
            x2, y2 = W / 2 + math.cos(a) * r2, H / 2 + math.sin(a) * r2
            self.d.line([(x1, y1), (x2, y2)], fill=color, width=int((3 + rnd.random() * 6) * SS))

    def flash(self, fuerza, color=(255, 255, 255)):
        """Destello de toda la pantalla (fuerza 0-1)."""
        if fuerza <= 0:
            return
        capa = Image.new("RGB", self.img.size, color)
        self.img = Image.blend(self.img, capa, min(1.0, fuerza))
        self.d = ImageDraw.Draw(self.img)

    # ---------------------------------------------------------------- textos
    def texto(self, txt, y=260, tam=96, progreso=1.0, color=None, borde=None, ancho_max=940):
        """Texto en pantalla estilo TikTok (no se mueve con la cámara).
        `progreso` 0→1 hace que aparezca con un pequeño rebote."""
        if progreso <= 0:
            return
        k = sm.rebote(progreso) if progreso < 1 else 1.0
        tam_real = max(8, tam * (0.6 + 0.4 * k))
        f = self.fuente(tam_real * SS)
        lineas = _partir(txt.upper(), f, ancho_max * SS)
        alto_linea = tam_real * 1.12 * SS
        y0 = y * SS - alto_linea * (len(lineas) - 1) / 2
        for i, ln in enumerate(lineas):
            self.d.text((ANCHO * SS / 2, y0 + i * alto_linea), ln, font=f, anchor="mm",
                        fill=color or self.e["texto"],
                        stroke_width=int(tam_real * 0.11 * SS),
                        stroke_fill=borde or self.e["texto_borde"])

    def onomatopeya(self, txt, x, y, progreso, tam=170, giro=-8, color=None):
        """Texto de cómic (¡PUM!, ¡BONK!) que aparece de golpe en (x, y) del mundo."""
        if not 0 < progreso < 1.6:
            return
        k = sm.rebote(min(1.0, progreso * 2.2))
        if progreso > 1.2:  # se encoge al irse
            k *= max(0.0, 1 - (progreso - 1.2) / 0.4)
        if k <= 0.05:
            return
        tam_px = int(self.l(tam) * k)
        f = self.fuente(tam_px)
        caja = f.getbbox(txt, stroke_width=int(tam_px * 0.12))
        w, h = caja[2] - caja[0] + 40, caja[3] - caja[1] + 40
        capa = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        ImageDraw.Draw(capa).text((w / 2, h / 2), txt, font=f, anchor="mm",
                                  fill=color or self.e["acento"],
                                  stroke_width=int(tam_px * 0.12), stroke_fill=(255, 255, 255))
        capa = capa.rotate(giro, expand=True, resample=Image.BICUBIC)
        sx, sy = self.p(x, y)
        self.img.paste(capa, (int(sx - capa.width / 2), int(sy - capa.height / 2)), capa)


def en_off(o, f, u, adel, arr, R):
    return (o[0] + f[0] * adel * R + u[0] * arr * R, o[1] + f[1] * adel * R + u[1] * arr * R)


def _partir(txt, fuente, ancho):
    palabras, lineas, actual = txt.split(), [], ""
    for p in palabras:
        prueba = (actual + " " + p).strip()
        if fuente.getlength(prueba) <= ancho or not actual:
            actual = prueba
        else:
            lineas.append(actual)
            actual = p
    if actual:
        lineas.append(actual)
    return lineas
