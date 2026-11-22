"""¿Por qué se hundió el Titanic, si era insumergible? (mamparos que no llegaban arriba)

Solo existe en 3D. Guion y tiempos aquí; las escenas están en
motor3d/escenas/titanic.html. Para generarlo:
  python generar3d.py titanic --voz salida/voces/titanic.mp3
"""
from motor.explicador import Explicador, Frase


def _nada(esc, lz, u, dur, n):
    pass


class Titanic(Explicador):
    nombre = "titanic"
    titulo = "¿Por qué se hundió el Titanic?"
    duracion = 62.0
    frases = [
        Frase("¿Por qué se hundió el Titanic, si era insumergible?", "insumergible", _nada),
        Frase("En 1912, todos decían que el Titanic prácticamente no se podía hundir.", "hundir", _nada,
              [(0.05, "tada")]),
        Frase("¿Su secreto? Dieciséis compartimentos separados por paredes de acero, llamadas mamparos.",
              "dieciséis mamparos", _nada, [(0.3, "pop")]),
        Frase("Si entraba agua en uno, las puertas se cerraban y el agua se quedaba atrapada ahí.",
              "atrapada", _nada, [(0.15, "agua"), (0.5, "golpecito"), (0.85, "ding")]),
        Frase("Podía flotar hasta con cuatro compartimentos inundados.", "cuatro", _nada,
              [(0.2, "agua"), (0.7, "ding")]),
        Frase("Pero la noche del catorce de abril... ¡pum! Un iceberg.", "iceberg", _nada,
              [("palabra:7", "golpe"), ("palabra:7", "crac")]),
        Frase("El golpe abrió cinco compartimentos.", "cinco", _nada, [(0.15, "crac"), (0.4, "agua")]),
        Frase("Uno más de lo que aguantaba.", "uno más", _nada, [(0.35, "boing")]),
        Frase("Y aquí viene lo peor: los mamparos no llegaban hasta arriba.", "hasta arriba", _nada,
              [(0.6, "pop")]),
        Frase("Eran como una charola de hielos.", "charola hielos", _nada, [(0.3, "agua")]),
        Frase("La proa se fue hundiendo, el agua llenó el primer compartimento... y se desbordó al "
              "siguiente. Y al siguiente. Y al siguiente.", "siguiente", _nada,
              [("palabra:13", "agua"), ("palabra:16", "agua"), ("palabra:19", "agua")]),
        Frase("Dos horas y cuarenta minutos después, el barco insumergible estaba en el fondo del mar.",
              "insumergible fondo", _nada, [(0.5, "whoosh")]),
        Frase("Y lo peor: solo llevaba botes salvavidas para la mitad de la gente.", "mitad", _nada,
              [(0.6, "golpecito")]),
        Frase("Desde entonces, la ley obliga a que todos los barcos lleven botes para todos.",
              "botes todos", _nada, [(0.7, "tada")]),
    ]
