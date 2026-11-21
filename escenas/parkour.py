"""Intenta saltar una caja estilo parkour, se atora, cae de cara... y la caja le cae encima."""
from motor import stickman as sm
from motor.stickman import Pose, animar, animar_num, apoyar, corriendo, acelera, frena
from motor.video import Escena

SUELO = 1400
ESC = 1.2
CAJA_X, CAJA_W, CAJA_H = 620, 200, 230
T_SALTO = 1.75
T_ATORA = 2.3
T_CRASH = 3.3
T_CAJA = 3.75
T_PULGAR = 6.3

CARA_AL_PISO = apoyar(Pose(escala=ESC, x=880, rot=90, cara="mareado",
                           brazo_f=175, ante_f=185, brazo_a=150, ante_a=170,
                           muslo_f=-5, pierna_f=-10, muslo_a=-25, pierna_a=-40), SUELO)


def correr(t):
    return apoyar(corriendo(Pose(escala=ESC, x=-60 + 260 * t, cara="enojado"), t * 2.2), SUELO)


def pose_en(t):
    if t < 1.7:
        return correr(t)
    claves = [
        (1.7, correr(1.7)),
        (T_SALTO, apoyar(Pose(escala=ESC, x=420, torso=30, cara="enojado",
                              brazo_f=-60, ante_f=-40, brazo_a=-75, ante_a=-50,
                              muslo_f=75, pierna_f=-15, muslo_a=30, pierna_a=-50), SUELO)),
        (T_ATORA, Pose(escala=ESC, x=600, y=950, torso=25, cara="enojado",
                       brazo_f=150, ante_f=160, brazo_a=-100, ante_a=-60,
                       muslo_f=110, pierna_f=30, muslo_a=-35, pierna_a=-45), frena),
        (2.8, Pose(escala=ESC, x=740, y=880, rot=70, cara="miedo",
                   brazo_f=200, ante_f=240, brazo_a=120, ante_a=60,
                   muslo_f=40, pierna_f=-20, muslo_a=-60, pierna_a=-100), frena),
        (T_CRASH, CARA_AL_PISO, acelera),
        (3.42, CARA_AL_PISO.con(y=CARA_AL_PISO.y - 22), frena),
        (3.55, CARA_AL_PISO, acelera),
        (6.0, CARA_AL_PISO),
        (T_PULGAR + 0.25, CARA_AL_PISO.con(brazo_f=270, ante_f=300, cara="feliz"), frena),
    ]
    return animar(claves, t)


class Parkour(Escena):
    nombre = "parkour"
    titulo = "Parkour fallido (y la caja también)"
    duracion = 8.5
    sonidos = (
        [(i * 0.227, "paso") for i in range(1, 8)]
        + [(T_SALTO, "whoosh"), (T_ATORA, "golpecito"), (2.4, "whoosh"),
           (T_CRASH, "golpe"), (3.45, "whoosh"), (T_CAJA, "golpe"),
           (4.2, "estrellas"), (5.2, "estrellas"), (T_PULGAR, "pop"), (7.0, "tada")]
    )

    def dibujar(self, lz, t):
        cam = animar_num([
            (0.0, (540, 1080, 1.05)),
            (1.6, (540, 1080, 1.05)),
            (T_ATORA, (640, 1050, 1.25)),
            (2.6, (740, 1030, 1.4), frena),
            (T_CRASH, (880, 1230, 1.15)),
        ], t)
        temblor = 0.0
        if T_CRASH <= t < T_CRASH + 0.45:
            temblor = 1 - (t - T_CRASH) / 0.45
        if T_CAJA <= t < T_CAJA + 0.45:
            temblor = 0.8 * (1 - (t - T_CAJA) / 0.45)
        lz.camara(*cam, temblor=temblor)

        if T_ATORA + 0.05 < t < T_CRASH:
            lz.lineas_velocidad(min(1.0, (t - T_ATORA) / 0.2) * min(1.0, (T_CRASH - t) / 0.2))
        lz.suelo(SUELO)
        lz.polvo((900, SUELO), (t - T_CRASH) / 0.6)
        lz.polvo((960, SUELO), (t - T_CAJA) / 0.6, cantidad=6)

        pose = pose_en(t)
        giro_caja = animar_num([(3.45, 0.0), (T_CAJA, 90.0, acelera)], t)
        if giro_caja > 0:  # la caja ya va cayendo: el monito queda abajo
            lz.monito(pose)
            lz.caja(CAJA_X, SUELO, CAJA_W, CAJA_H, giro=giro_caja)
        else:
            lz.caja(CAJA_X, SUELO, CAJA_W, CAJA_H)
            lz.monito(pose)

        cabeza = sm.articulaciones(pose)["cabeza"]
        if T_CAJA + 0.3 < t < T_PULGAR:
            lz.estrellitas(cabeza, radio=90)

        lz.onomatopeya("¡CRASH!", 960, 1120, (t - T_CRASH) / 0.8)
        lz.onomatopeya("¡PAF!", 1000, 1050, (t - T_CAJA) / 0.8, giro=9, color=lz.e["acento2"])

        if T_CRASH <= t < T_CRASH + 0.12:
            lz.flash(0.7 * (1 - (t - T_CRASH) / 0.12))
        if T_CAJA <= t < T_CAJA + 0.1:
            lz.flash(0.5)

        if t < T_ATORA + 0.2:
            lz.texto("Yo intentando hacer parkour", progreso=t / 0.4)
        elif 3.9 < t < T_PULGAR - 0.1:
            lz.texto("Los jueces: 0/10", progreso=(t - 3.9) / 0.35)
        elif t >= T_PULGAR:
            lz.texto("Pero lo logré", progreso=(t - T_PULGAR) / 0.3)
        if t >= 7.0:
            lz.texto("¿Parte 2?", y=1700, tam=90, progreso=(t - 7.0) / 0.35)
