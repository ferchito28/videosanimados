#!/usr/bin/env python3
"""Genera videos de stickman listos para TikTok, Reels o Shorts.

Ejemplos:
  python generar.py --lista
  python generar.py resbalon
  python generar.py parkour --estilo neon
  python generar.py todas --estilo cuaderno
  python generar.py resbalon --captura 3.9     (un solo cuadro en PNG)
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from escenas import ESCENAS  # noqa: E402
from motor.lienzo import ESTILOS  # noqa: E402
from motor.video import captura, renderizar  # noqa: E402


def main():
    ap = argparse.ArgumentParser(description="Generador de videos de stickman")
    ap.add_argument("escena", nargs="?", help="nombre de la escena o 'todas'")
    ap.add_argument("--estilo", default="pop", choices=list(ESTILOS))
    ap.add_argument("--fps", type=int, default=30)
    ap.add_argument("--sin-sonido", action="store_true")
    ap.add_argument("--alta-calidad", action="store_true", help="archivo más ligero, tarda más")
    ap.add_argument("--salida", default="salida", help="carpeta donde se guardan")
    ap.add_argument("--voz", metavar="AUDIO",
                    help="audio del narrador (MP3 de ElevenLabs) para videos explicativos")
    ap.add_argument("--captura", type=float, metavar="SEGUNDO",
                    help="guarda solo el cuadro de ese segundo como PNG")
    a = ap.parse_args()

    if a.escena is None or a.escena == "--lista":
        print("Escenas disponibles:")
        for n, e in ESCENAS.items():
            print(f"  {n:<12} {e.duracion:>4.1f} s  {e.titulo}")
        print("Estilos:", ", ".join(ESTILOS))
        return

    nombres = list(ESCENAS) if a.escena == "todas" else [a.escena]
    for n in nombres:
        if n not in ESCENAS:
            sys.exit(f"No existe la escena '{n}'. Usa --lista para ver las opciones.")
        clase = ESCENAS[n]
        if a.voz and getattr(clase, "frases", None):
            escena = clase(voz=a.voz)
        else:
            escena = clase()
        if a.captura is not None:
            ruta = os.path.join(a.salida, f"{n}_{a.estilo}_{a.captura:.2f}s.png")
            os.makedirs(a.salida, exist_ok=True)
            print("Captura:", captura(escena, a.captura, ruta, a.estilo))
            continue
        ruta = os.path.join(a.salida, f"{n}_{a.estilo}.mp4")
        print(f"Generando '{n}' ({escena.duracion:.0f} s, estilo {a.estilo})...")
        renderizar(escena, ruta, estilo=a.estilo, fps=a.fps, sonido=not a.sin_sonido,
                   calidad="alta" if a.alta_calidad else "normal")


if __name__ == "__main__":
    main()
