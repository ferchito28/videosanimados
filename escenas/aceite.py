"""¿Por qué nunca debes echarle agua a un sartén con aceite en llamas?

Solo existe en 3D: motor3d/escenas/aceite.html
  python generar3d.py aceite --voz salida/voces/aceite.mp3
"""
from motor.explicador import Explicador, Frase


def _nada(esc, lz, u, dur, n):
    pass


class Aceite(Explicador):
    nombre = "aceite"
    titulo = "¿Por qué no echarle agua al aceite en llamas?"
    duracion = 60.0
    una_palabra = True
    # segundos de silencio extra después de estas frases (para que se alcancen a ver las escenas)
    pausas = {0: 0.4, 2: 0.4, 3: 0.5, 4: 0.6, 5: 0.7, 7: 1.0, 8: 0.7, 9: 0.5, 10: 0.5, 11: 0.6}
    frases = [
        Frase("¿Por qué nunca debes echarle agua a un sartén con aceite en llamas?", "agua aceite llamas", _nada,
              [(0.05, "chisporroteo"), ("palabra:4", "whoosh_suave"), ("palabra:12", "golpecito")]),
        Frase("El aceite caliente puede pasar de los trescientos grados. El agua hierve a cien.",
              "trescientos cien", _nada, [("palabra:1", "chisporroteo"), ("palabra:7", "pop"), ("palabra:13", "pop")]),
        Frase("Y el agua pesa más que el aceite, así que se va directo al fondo... justo donde está más caliente.",
              "pesa fondo caliente", _nada, [("palabra:3", "tac"), ("palabra:11", "whoosh_suave"), ("palabra:14", "agua"),
                                             ("palabra:19", "chisporroteo")]),
        Frase("Ahí, en menos de un segundo, se convierte en vapor.", "segundo vapor", _nada,
              [("palabra:7", "fss"), ("palabra:9", "fss")]),
        Frase("Y el vapor ocupa como mil setecientas veces más espacio que el agua.", "mil setecientas", _nada,
              [("palabra:5", "whoosh"), ("palabra:7", "boing")]),
        Frase("Una sola taza de agua se vuelve más de cuatrocientos litros de vapor.", "taza cuatrocientos litros",
              _nada, [("palabra:2", "pop"), ("palabra:9", "whoosh"), ("palabra:11", "tada")]),
        Frase("Ese vapor sale disparado hacia arriba, y se lleva el aceite hecho gotitas.", "disparado gotitas", _nada,
              [("palabra:3", "fss"), ("palabra:3", "whoosh"), ("palabra:12", "chisporroteo")]),
        Frase("Y millones de gotitas de aceite ardiendo en el aire... son una bola de fuego.", "ardiendo bola fuego",
              _nada, [("palabra:6", "chisporroteo"), ("palabra:12", "fuego"), ("palabra:12", "golpe")]),
        Frase("Lo que era una llamita en el sartén, ahora llega hasta el techo.", "llamita techo", _nada,
              [("palabra:4", "chisporroteo"), ("palabra:9", "fuego"), ("palabra:12", "golpe")]),
        Frase("Entonces, ¿qué se hace? Apaga la estufa y tapa el sartén con una tapa o un trapo húmedo.",
              "apaga tapa trapo húmedo", _nada, [("palabra:4", "tac"), ("palabra:8", "golpecito"), ("palabra:13", "ding")]),
        Frase("Sin oxígeno, el fuego se ahoga solito.", "oxígeno ahoga", _nada,
              [("palabra:1", "whoosh_suave"), ("palabra:5", "fss")]),
        Frase("Y nunca, nunca cargues el sartén para sacarlo corriendo.", "nunca cargues", _nada,
              [("palabra:3", "whoosh"), ("palabra:8", "golpe")]),
        Frase("El agua apaga casi todo... menos esto. Aquí, el mejor bombero es una tapa.", "bombero tapa", _nada,
              [("palabra:5", "boing"), ("palabra:10", "pop"), (0.88, "tada")]),
    ]
