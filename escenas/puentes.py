"""¿Por qué algunos puentes de acero están parados sobre rodillos? (dilatación del acero)

Solo existe en 3D: motor3d/escenas/puentes.html
  python generar3d.py puentes --voz salida/voces/puentes.mp3
"""
from motor.explicador import Explicador, Frase


def _nada(esc, lz, u, dur, n):
    pass


class Puentes(Explicador):
    nombre = "puentes"
    titulo = "¿Por qué los puentes están sobre rodillos?"
    duracion = 60.0
    una_palabra = True
    # segundos de silencio extra después de estas frases (para que se alcancen a ver las escenas)
    pausas = {0: 0.4, 3: 0.4, 4: 0.8, 6: 0.9, 7: 0.4, 8: 0.6, 9: 0.9, 10: 0.7, 11: 0.6}
    frases = [
        Frase("¿Por qué algunos puentes de acero están parados sobre rodillos?", "rodillos", _nada,
              [("palabra:9", "pop")]),
        Frase("Imagina un puente de acero de doscientos metros, bien amarrado a la tierra en los dos extremos.",
              "doscientos amarrado extremos", _nada, [("palabra:6", "pop"), ("palabra:9", "tac"), ("palabra:15", "tac")]),
        Frase("Fuerte, rígido, perfecto.", "perfecto", _nada, [(0.75, "ding")]),
        Frase("Pero el acero tiene un secreto: con el calor, crece.", "secreto calor crece", _nada,
              [("palabra:5", "whoosh_suave"), ("palabra:9", "boing")]),
        Frase("Entre una mañana de invierno y una tarde de verano, ese puente puede estirarse casi diez centímetros.",
              "invierno verano diez centímetros", _nada, [("palabra:7", "whoosh"), ("palabra:15", "pop")]),
        Frase("Y si está amarrado de los dos lados, no tiene para dónde crecer.", "amarrado dónde", _nada,
              [("palabra:3", "tac"), ("palabra:7", "tac")]),
        Frase("Así que empuja... y empuja... hasta que se tuerce o revienta sus apoyos.", "empuja tuerce revienta",
              _nada, [("palabra:2", "golpecito"), ("palabra:4", "golpecito"), ("palabra:8", "crac"),
                      ("palabra:10", "golpe"), ("palabra:10", "crac")]),
        Frase("La solución parece trampa: dejar un lado suelto.", "trampa suelto", _nada,
              [("palabra:3", "ding"), ("palabra:7", "boing")]),
        Frase("Un extremo se fija bien a la tierra, y el otro se apoya sobre rodillos de acero.",
              "fija rodillos", _nada, [("palabra:3", "tac"), ("palabra:8", "whoosh_suave"), ("palabra:14", "pop")]),
        Frase("Con el calor, el puente rueda hacia afuera. Con el frío, rueda de regreso.",
              "calor afuera frío regreso", _nada, [("palabra:5", "whoosh_suave"), ("palabra:11", "whoosh_suave")]),
        Frase("Y en la orilla ponen una junta con dientes, como dos peines, para que los autos pasen sin brincar.",
              "dientes peines brincar", _nada, [("palabra:8", "pop"), ("palabra:16", "whoosh"), (0.92, "ding")]),
        Frase("Hoy muchos puentes usan almohadillas de hule gigantes en lugar de rodillos, pero la idea es la misma.",
              "almohadillas hule misma", _nada, [("palabra:4", "boing"), (0.9, "ding")]),
        Frase("Así que la próxima vez que cruces un puente... recuerda que se está moviendo debajo de ti.",
              "moviendo ti", _nada, [("palabra:8", "whoosh"), (0.85, "tada")]),
    ]
