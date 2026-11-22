#!/usr/bin/env python3
"""Genera un short animado vertical a partir de una historia en JSON.

  python3 generar.py historias/ejemplo.json                 # vídeo en salida/
  python3 generar.py historias/ejemplo.json --captura 2.5   # solo un fotograma PNG
"""
import argparse
from pathlib import Path

from animador.render import Animador


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("historia")
    ap.add_argument("-o", "--salida")
    ap.add_argument("--fps", type=int, default=30)
    ap.add_argument("--captura", type=float, nargs="*", help="segundos a exportar como PNG")
    a = ap.parse_args()

    anim = Animador(a.historia)
    nombre = Path(a.historia).stem
    if a.captura is not None:
        for t in a.captura or [1.0]:
            ruta = Path("salida") / f"{nombre}_{t:.1f}s.png"
            ruta.parent.mkdir(exist_ok=True)
            anim.fotograma(t).save(ruta)
            print(ruta)
        return
    anim.render(a.salida or Path("salida") / f"{nombre}.mp4", fps=a.fps)


if __name__ == "__main__":
    main()
