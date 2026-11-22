"""¿Por qué te despiertas a las 3 a.m.? (ciclos de sueño y el "primer y segundo sueño")

Solo existe en 3D: motor3d/escenas/sueno.html
  python generar3d.py sueno --voz salida/voces/sueno.mp3
"""
from motor.explicador import Explicador, Frase


def _nada(esc, lz, u, dur, n):
    pass


class Sueno(Explicador):
    nombre = "sueno"
    titulo = "¿Por qué te despiertas a las 3 a.m.?"
    duracion = 62.0
    frases = [
        Frase("¿Por qué te despiertas a las tres de la mañana, si querías dormir ocho horas seguidas?",
              "tres mañana", _nada, [(0.35, "ding")]),
        Frase("Todos creemos que dormir bien es caer como piedra y no abrir los ojos hasta que suene la alarma.",
              "piedra alarma", _nada, [(0.3, "golpe"), (0.85, "estrellas")]),
        Frase("Pero tu cerebro no duerme en línea recta. Duerme en ciclos.", "ciclos", _nada,
              [(0.3, "boing"), (0.65, "whoosh")]),
        Frase("Cada ciclo dura más o menos noventa minutos.", "noventa minutos", _nada, [(0.55, "ding")]),
        Frase("Primero sueño ligero, luego sueño profundo, y al final el sueño REM, donde tienes los sueños más locos.",
              "ligero profundo REM locos", _nada,
              [("palabra:1", "whoosh_suave"), ("palabra:4", "whoosh"), ("palabra:10", "pop"), ("palabra:16", "boing")]),
        Frase("En una noche das de cuatro a seis vueltas a ese ciclo.", "cuatro seis", _nada, [(0.4, "whoosh")]),
        Frase("Y entre un ciclo y otro, es normal despertar unos segundos... aunque casi nunca lo recuerdes.",
              "normal despertar", _nada, [(0.4, "pop")]),
        Frase("¿Y lo más raro? Hace siglos, en Europa, mucha gente dormía en dos partes.", "dos partes", _nada,
              [(0.1, "whoosh")]),
        Frase("Un primer sueño, luego una hora despiertos platicando, rezando o hasta visitando a los vecinos...",
              "primer hora despiertos vecinos", _nada, [(0.85, "tac"), (0.9, "tac")]),
        Frase("y después, el segundo sueño.", "segundo", _nada, [(0.5, "pop")]),
        Frase("Eso cambió cuando llegó la luz artificial y todos empezamos a desvelarnos.", "luz artificial desvelarnos",
              _nada, [(0.25, "ding"), (0.4, "pop"), (0.55, "pop")]),
        Frase("Así que si te despiertas a mitad de la noche, no te asustes.", "asustes", _nada, [(0.2, "boing")]),
        Frase("Tal vez no duermes mal... solo terminaste un ciclo.", "ciclo", _nada, [(0.7, "ding")]),
        Frase("Eso sí: si te cuesta volver a dormir y amaneces agotado, vale la pena ir al médico.", "médico", _nada,
              [(0.75, "tada")]),
    ]
