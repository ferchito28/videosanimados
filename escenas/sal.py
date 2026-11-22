"""¿Por qué le echan sal a las calles cuando va a nevar?

Formato historia: Beto (el listo) contra el vecino presumido.
Solo existe en 3D: motor3d/escenas/sal.html
  python generar3d.py sal --voz salida/voces/sal.mp3
"""
from motor.explicador import Explicador, Frase


def _nada(esc, lz, u, dur, n):
    pass


class Sal(Explicador):
    nombre = "sal"
    titulo = "¿Por qué le echan sal a las calles?"
    duracion = 56.0
    una_palabra = True
    frases = [
        Frase("¿Por qué le echan sal a las calles cuando va a nevar?", "sal nevar", _nada,
              [("palabra:4", "pop")]),
        Frase("Es de noche, viene una tormenta, y Beto sale a echarle sal a su calle.", "tormenta Beto sal", _nada,
              [(0.25, "whoosh"), ("palabra:11", "agua")]),
        Frase("El vecino se ríe: ¿Qué, vas a cocinar la banqueta?", "cocinar", _nada,
              [(0.15, "boing")]),
        Frase("A la mañana siguiente, todo está congelado.", "congelado", _nada,
              [(0.7, "crac")]),
        Frase("El vecino arranca su camioneta, acelera… y se va patinando hasta el bote de basura.",
              "patinando basura", _nada,
              [("palabra:4", "whoosh"), ("palabra:8", "resbalon"), ("palabra:13", "golpe"), ("palabra:14", "estrellas")]),
        Frase("Mientras, Beto sale tranquilo, sin resbalarse ni una vez.", "tranquilo", _nada,
              [(0.3, "paso"), (0.5, "paso"), (0.85, "ding")]),
        Frase("¿Por qué?", "", _nada, [(0.2, "pop")]),
        Frase("El agua se congela a cero grados, cuando sus moléculas se agarran de la mano y forman hielo.",
              "cero moléculas mano hielo", _nada,
              [("palabra:5", "ding"), ("palabra:10", "pop"), ("palabra:16", "crac")]),
        Frase("Pero la sal se mete en medio y no las deja agarrarse.", "sal medio", _nada,
              [("palabra:2", "tac"), ("palabra:5", "tac"), (0.7, "boing")]),
        Frase("Con sal, el agua aguanta hasta unos nueve grados bajo cero sin congelarse.",
              "nueve bajo cero", _nada, [("palabra:7", "whoosh_suave"), (0.85, "ding")]),
        Frase("Por eso las ciudades rocían agua con sal antes de la tormenta: así el hielo no se pega al piso.",
              "rocían antes pega", _nada, [(0.15, "agua"), (0.75, "whoosh")]),
        Frase("Al otro día, el vecino compró diez bultos de sal.", "diez bultos", _nada,
              [("palabra:6", "tac"), (0.75, "tac"), (0.85, "tac")]),
        Frase("Pero esa noche bajó a quince bajo cero.", "quince", _nada, [(0.4, "whoosh_suave"), (0.75, "crac")]),
        Frase("Y ahí la sal ya no sirve: se usa arena.", "arena", _nada, [(0.4, "boing"), (0.8, "agua")]),
        Frase("Beto ya tenía arena.", "arena", _nada, [(0.5, "resbalon"), (0.75, "golpe"), (0.9, "tada")]),
    ]
