"""El monito de palitos: su pose, cómo se mueve y cómo se dibuja.

Convención de ángulos (en grados), pensada para que sea fácil posar al monito:
  0   = apuntando hacia abajo
  90  = apuntando hacia adelante (hacia donde mira)
  180 = apuntando hacia arriba
  -90 = apuntando hacia atrás
Los brazos y piernas usan ángulos absolutos respecto al cuerpo, así que una pose
se lee sola: brazo_f=180 es "brazo de enfrente levantado".
`rot` gira todo el cuerpo alrededor de la cadera (positivo = cae de cara,
negativo = cae de espaldas).
"""
import math
from dataclasses import dataclass, fields, replace

# Medidas base del cuerpo (en píxeles del video 1080x1920, con escala=1)
TORSO = 170
CABEZA_R = 48
BRAZO = 100
ANTEBRAZO = 95
MUSLO = 120
PIERNA = 120
GROSOR = 18


@dataclass
class Pose:
    x: float = 540.0          # posición de la cadera
    y: float = 1160.0
    rot: float = 0.0          # giro de todo el cuerpo
    escala: float = 1.0
    mira: int = 1             # 1 = mira a la derecha, -1 = a la izquierda
    torso: float = 0.0        # inclinación del torso (positivo = hacia adelante)
    cabeza: float = 0.0       # inclinación extra de la cabeza
    brazo_a: float = -20.0    # brazo de atrás
    ante_a: float = -5.0
    brazo_f: float = 20.0     # brazo de enfrente
    ante_f: float = 35.0
    muslo_a: float = -8.0     # pierna de atrás
    pierna_a: float = -8.0
    muslo_f: float = 8.0      # pierna de enfrente
    pierna_f: float = 8.0
    cara: str = "normal"      # normal, sorpresa, mareado, feliz, enojado, miedo

    def con(self, **cambios):
        """Copia de la pose con algunos valores cambiados."""
        return replace(self, **cambios)


_NO_NUMERICOS = {"mira", "cara"}


def mezclar(a: Pose, b: Pose, t: float) -> Pose:
    """Interpola entre dos poses (t=0 → a, t=1 → b)."""
    t = max(0.0, min(1.0, t))
    valores = {}
    for f in fields(Pose):
        va, vb = getattr(a, f.name), getattr(b, f.name)
        if f.name in _NO_NUMERICOS:
            valores[f.name] = vb if t >= 0.5 else va
        else:
            valores[f.name] = va + (vb - va) * t
    return Pose(**valores)


# ---------------------------------------------------------------- suavizados
def suave(t):
    """Entrada y salida suaves (lo normal para casi todo)."""
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)


def acelera(t):
    t = max(0.0, min(1.0, t))
    return t * t


def frena(t):
    t = max(0.0, min(1.0, t))
    return 1 - (1 - t) * (1 - t)


def rebote(t):
    """Se pasa un poco y regresa: da sensación de golpe con resorte."""
    t = max(0.0, min(1.0, t))
    c1, c3 = 1.70158, 2.70158
    return 1 + c3 * (t - 1) ** 3 + c1 * (t - 1) ** 2


def animar(claves, t):
    """Anima una pose con fotogramas clave.

    claves = [(segundo, Pose), (segundo, Pose, funcion_suavizado), ...]
    Devuelve la pose que toca en el segundo t.
    """
    if t <= claves[0][0]:
        return claves[0][1]
    for i in range(len(claves) - 1):
        t0, p0 = claves[i][0], claves[i][1]
        t1, p1 = claves[i + 1][0], claves[i + 1][1]
        fn = claves[i + 1][2] if len(claves[i + 1]) > 2 else suave
        if t <= t1:
            return mezclar(p0, p1, fn((t - t0) / max(1e-6, t1 - t0)))
    return claves[-1][1]


# ------------------------------------------------------------- poses útiles
PARADO = Pose()


def caminando(base: Pose, fase: float, energia: float = 1.0) -> Pose:
    """Ciclo de caminata. `fase` avanza 1 por cada paso completo (dos pisadas)."""
    s = math.sin(fase * 2 * math.pi)
    c = math.cos(fase * 2 * math.pi)
    e = energia
    return base.con(
        y=base.y - abs(c) * 10 * e,
        torso=base.torso + 6 * e,
        muslo_f=28 * s * e,
        pierna_f=28 * s * e - max(0, -s) * 30 * e,
        muslo_a=-28 * s * e,
        pierna_a=-28 * s * e - max(0, s) * 30 * e,
        brazo_f=-30 * s * e,
        ante_f=-30 * s * e + 35,
        brazo_a=30 * s * e,
        ante_a=30 * s * e + 35,
    )


def corriendo(base: Pose, fase: float) -> Pose:
    s = math.sin(fase * 2 * math.pi)
    c = math.cos(fase * 2 * math.pi)
    return base.con(
        y=base.y - abs(c) * 28,
        torso=base.torso + 18,
        muslo_f=50 * s + 15,
        pierna_f=50 * s - 25 - max(0, -s) * 55,
        muslo_a=-50 * s + 15,
        pierna_a=-50 * s - 25 - max(0, s) * 55,
        brazo_f=-55 * s + 10,
        ante_f=-55 * s + 95,
        brazo_a=55 * s + 10,
        ante_a=55 * s + 95,
    )


# --------------------------------------------------------------- geometría
def _dir(angulo, mira):
    r = math.radians(angulo)
    return (mira * math.sin(r), math.cos(r))


def articulaciones(p: Pose):
    """Calcula dónde queda cada articulación (en coordenadas del mundo)."""
    k = p.escala
    m = p.mira

    def mover(origen, largo, angulo):
        d = _dir(angulo - p.rot, m)
        return (origen[0] + d[0] * largo * k, origen[1] + d[1] * largo * k)

    cadera = (p.x, p.y)
    ang_torso = 180 - p.torso
    cuello = mover(cadera, TORSO, ang_torso)
    hombro = mover(cadera, TORSO * 0.82, ang_torso)
    ang_cabeza = 180 - p.torso - p.cabeza
    cabeza = mover(cuello, CABEZA_R + 6, ang_cabeza)
    codo_a = mover(hombro, BRAZO, p.brazo_a)
    mano_a = mover(codo_a, ANTEBRAZO, p.ante_a)
    codo_f = mover(hombro, BRAZO, p.brazo_f)
    mano_f = mover(codo_f, ANTEBRAZO, p.ante_f)
    rodilla_a = mover(cadera, MUSLO, p.muslo_a)
    pie_a = mover(rodilla_a, PIERNA, p.pierna_a)
    rodilla_f = mover(cadera, MUSLO, p.muslo_f)
    pie_f = mover(rodilla_f, PIERNA, p.pierna_f)
    # vectores de la cara: "arriba" y "adelante" de la cabeza
    arriba = _dir(ang_cabeza - p.rot, m)
    adelante = _dir(ang_cabeza - 90 - p.rot, m)
    return {
        "cadera": cadera, "cuello": cuello, "hombro": hombro, "cabeza": cabeza,
        "codo_a": codo_a, "mano_a": mano_a, "codo_f": codo_f, "mano_f": mano_f,
        "rodilla_a": rodilla_a, "pie_a": pie_a, "rodilla_f": rodilla_f, "pie_f": pie_f,
        "arriba": arriba, "adelante": adelante,
    }


def animar_num(claves, t):
    """Igual que `animar`, pero para números o tuplas (cámara, objetos...).

    claves = [(segundo, valor), (segundo, valor, suavizado), ...]
    """
    if t <= claves[0][0]:
        return claves[0][1]
    for i in range(len(claves) - 1):
        t0, v0 = claves[i][0], claves[i][1]
        t1, v1 = claves[i + 1][0], claves[i + 1][1]
        fn = claves[i + 1][2] if len(claves[i + 1]) > 2 else suave
        if t <= t1:
            k = fn((t - t0) / max(1e-6, t1 - t0))
            if isinstance(v0, tuple):
                return tuple(a + (b - a) * k for a, b in zip(v0, v1))
            return v0 + (v1 - v0) * k
    return claves[-1][1]


def apoyar(p: Pose, suelo: float) -> Pose:
    """Sube o baja la pose para que su punto más bajo toque el suelo."""
    return p.con(y=p.y + (suelo - punto_mas_bajo(p)))


def punto_mas_bajo(p: Pose):
    """La Y más baja del cuerpo (útil para apoyarlo en el suelo)."""
    j = articulaciones(p)
    ys = [j[k][1] for k in ("pie_a", "pie_f", "mano_a", "mano_f", "rodilla_a",
                            "rodilla_f", "cadera", "cuello")]
    ys.append(j["cabeza"][1] + CABEZA_R * p.escala)
    return max(ys)
