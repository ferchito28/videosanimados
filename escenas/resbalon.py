"""El clásico: se resbala con una cáscara de plátano... y la cáscara regresa."""
from motor import stickman as sm
from motor.stickman import Pose, animar, animar_num, apoyar, caminando, acelera, frena, suave
from motor.video import Escena

SUELO = 1400
ESC = 1.25
X_PLATANO = 565
T_RESBALA = 2.6
T_PUM = 3.9
T_BONK = 8.5
T_PAF = 9.2

BASE = apoyar(Pose(escala=ESC, cara="feliz"), SUELO)


def caminar(t):
    return apoyar(caminando(BASE.con(x=120 + 135 * t), t * 1.6), SUELO)


ACOSTADO = apoyar(Pose(escala=ESC, x=520, rot=-90, cara="mareado",
                       brazo_f=170, ante_f=178, brazo_a=150, ante_a=160,
                       muslo_f=10, pierna_f=4, muslo_a=35, pierna_a=-5), SUELO)
SENTADO = apoyar(Pose(escala=ESC, x=520, torso=15, cara="mareado",
                      brazo_f=25, ante_f=35, brazo_a=-30, ante_a=-10,
                      muslo_f=85, pierna_f=80, muslo_a=75, pierna_a=70), SUELO)
AGACHADO = apoyar(Pose(escala=ESC, x=520, torso=28, cara="normal",
                       brazo_f=40, ante_f=60, brazo_a=-20, ante_a=0,
                       muslo_f=70, pierna_f=-20, muslo_a=45, pierna_a=-40), SUELO)
PULGAR_ARRIBA = apoyar(Pose(escala=ESC, x=520, cara="feliz",
                            brazo_f=95, ante_f=165), SUELO)
CARA_AL_PISO = apoyar(Pose(escala=ESC, x=560, rot=90, cara="mareado",
                           brazo_f=175, ante_f=180, brazo_a=150, ante_a=170,
                           muslo_f=-5, pierna_f=-10, muslo_a=-25, pierna_a=-40), SUELO)


def pose_en(t):
    if t < T_RESBALA:
        return caminar(t)
    inicio = caminar(T_RESBALA)
    claves = [
        (T_RESBALA, inicio),
        (2.75, Pose(escala=ESC, x=500, y=inicio.y - 60, rot=-25, cara="sorpresa",
                    brazo_f=150, ante_f=175, brazo_a=-150, ante_a=-175,
                    muslo_f=95, pierna_f=100, muslo_a=20, pierna_a=10), frena),
        (3.4, Pose(escala=ESC, x=515, y=inicio.y - 170, rot=-70, cara="miedo",
                   brazo_f=165, ante_f=210, brazo_a=-120, ante_a=-60,
                   muslo_f=110, pierna_f=135, muslo_a=80, pierna_a=100), frena),
        (T_PUM, ACOSTADO, acelera),
        (4.05, ACOSTADO.con(y=ACOSTADO.y - 28), frena),
        (4.2, ACOSTADO, acelera),
        (6.6, ACOSTADO),
        (7.1, SENTADO),
        (7.5, AGACHADO.con(cara="normal")),
        (7.9, PULGAR_ARRIBA, frena),
        (T_BONK, PULGAR_ARRIBA),
        (8.62, PULGAR_ARRIBA.con(cara="mareado", torso=-10, cabeza=-15, brazo_f=40, ante_f=60)),
        (T_PAF, CARA_AL_PISO, acelera),
        (9.32, CARA_AL_PISO.con(y=CARA_AL_PISO.y - 18), frena),
        (9.45, CARA_AL_PISO, acelera),
    ]
    return animar(claves, t)


def platano_en(t, cabeza_y):
    """Posición y giro de la cáscara: (x, y, giro)."""
    piso = (X_PLATANO, SUELO - 18, 0)
    if t < T_RESBALA:
        return piso
    if t < 3.6:  # sale volando
        return animar_num([(T_RESBALA, piso), (3.6, (980, -300, 720), frena)], t)
    if t < 7.9:
        return None
    sobre_cabeza = (520 + 15, cabeza_y, 540)
    if t < T_BONK:  # cae del cielo
        return animar_num([(7.9, (535, -250, 0)), (T_BONK, sobre_cabeza, acelera)], t)
    # rebota a un lado
    k = min(1.0, (t - T_BONK) / 0.6)
    x = 535 + 230 * k
    y = cabeza_y + (SUELO - 18 - cabeza_y) * k - 260 * 4 * k * (1 - k)
    return (x, y, 540 + 300 * k)


class Resbalon(Escena):
    nombre = "resbalon"
    titulo = "Cáscara de plátano (con venganza)"
    duracion = 11.0
    sonidos = (
        [(i * 0.3125, "paso") for i in range(1, 9)]
        + [(T_RESBALA, "resbalon"), (2.8, "whoosh"), (T_PUM, "golpe"),
           (4.5, "estrellas"), (5.6, "estrellas"), (7.9, "pop"), (8.0, "whoosh"),
           (T_BONK, "boing"), (T_PAF, "golpecito"), (9.7, "tada")]
    )

    def dibujar(self, lz, t):
        # ---- cámara
        cam = animar_num([
            (0.0, (540, 1080, 1.1)),
            (T_RESBALA, (540, 1080, 1.1)),
            (3.0, (520, 1110, 1.45), frena),
            (T_PUM, (480, 1230, 1.3)),
            (6.6, (480, 1230, 1.3)),
            (7.9, (540, 1080, 1.1)),
            (T_BONK, (540, 1080, 1.1)),
            (8.6, (540, 1050, 1.3), frena),
            (T_PAF, (560, 1220, 1.25)),
        ], t)
        temblor = 0.0
        if T_PUM <= t < T_PUM + 0.5:
            temblor = 1 - (t - T_PUM) / 0.5
        if T_PAF <= t < T_PAF + 0.35:
            temblor = 0.6 * (1 - (t - T_PAF) / 0.35)
        lz.camara(*cam, temblor=temblor)

        # ---- escenario y personajes
        if 2.75 < t < T_PUM:
            lz.lineas_velocidad(min(1.0, (t - 2.75) / 0.2) * min(1.0, (T_PUM - t) / 0.2))
        lz.suelo(SUELO)
        lz.polvo((520, SUELO), (t - T_PUM) / 0.6)
        lz.polvo((620, SUELO), (t - T_PAF) / 0.5, cantidad=5)

        pose = pose_en(t)
        lz.monito(pose)
        cabeza = sm.articulaciones(pose)["cabeza"]

        cabeza_arriba = sm.articulaciones(PULGAR_ARRIBA)["cabeza"][1] - sm.CABEZA_R * ESC - 25
        pl = platano_en(t, cabeza_arriba)
        if pl:
            lz.platano(pl[0], pl[1], pl[2], escala=1.2)

        if T_PUM + 0.3 < t < 6.7:
            lz.estrellitas(cabeza, radio=95)
        if T_BONK + 0.1 < t:
            lz.estrellitas(cabeza, radio=90, velocidad=1.3)

        lz.onomatopeya("¡PUM!", 520, SUELO - 300, (t - T_PUM) / 0.9)
        lz.onomatopeya("¡BONK!", 600, cabeza_arriba - 120, (t - T_BONK) / 0.8, giro=10,
                       color=lz.e["acento2"])

        # ---- efectos de pantalla y textos
        if T_PUM <= t < T_PUM + 0.12:
            lz.flash(0.7 * (1 - (t - T_PUM) / 0.12))
        if T_BONK <= t < T_BONK + 0.08:
            lz.flash(0.5)

        if t < T_RESBALA + 0.1:
            lz.texto("Cuando vas tarde al trabajo...", progreso=t / 0.4)
        elif 4.3 < t < 7.6:
            lz.texto("...y el universo dice: NO", progreso=(t - 4.3) / 0.4)
        elif 7.7 < t < T_BONK:
            lz.texto("Estoy bien", progreso=(t - 7.7) / 0.3)
        elif t >= T_BONK + 0.2:
            lz.texto("El universo: ¿seguro?", progreso=(t - T_BONK - 0.2) / 0.3)
        if t >= 9.7:
            lz.texto("Sígueme para la parte 2", y=1700, tam=78, progreso=(t - 9.7) / 0.35)
