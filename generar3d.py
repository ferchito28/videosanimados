#!/usr/bin/env python3
"""Genera los videos explicativos en 3D (personajes 2D de cabeza blanca en escenarios 3D).

Ejemplos:
  python generar3d.py juntas_concreto                      # vista previa con tiempos estimados
  python generar3d.py juntas_concreto --voz concreto.mp3   # sincronizado con la voz de ElevenLabs
  python generar3d.py juntas_concreto --voz concreto.mp3 --cuadros 2,10.5,30

Necesita Node (con three.js instalado en motor3d/: `cd motor3d && npm install`),
Playwright con Chromium, Python 3 con NumPy y ffmpeg.
"""
import argparse
import json
import os
import subprocess
import sys
import tempfile

RAIZ = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, RAIZ)

from escenas.juntas_concreto import JuntasConcreto  # noqa: E402
from escenas.titanic import Titanic  # noqa: E402
from escenas.sueno import Sueno  # noqa: E402
from escenas.sal import Sal  # noqa: E402
from escenas.puentes import Puentes  # noqa: E402
from motor.sonidos import crear_pista  # noqa: E402

# nombre → (clase con el guion y tiempos, página 3D)
VIDEOS = {
    "juntas_concreto": (JuntasConcreto, "motor3d/escenas/juntas_concreto.html"),
    "titanic": (Titanic, "motor3d/escenas/titanic.html"),
    "sueno": (Sueno, "motor3d/escenas/sueno.html"),
    "sal": (Sal, "motor3d/escenas/sal.html"),
    "puentes": (Puentes, "motor3d/escenas/puentes.html"),
}


def datos_de(esc):
    frases = []
    for n, (ini, fin, i0) in enumerate(esc.tramos):
        k = len(esc.frases[n].palabras)
        frases.append({"ini": ini, "fin": fin,
                       "palabras": [esc.tiempos[i0 + j][0] - ini for j in range(k)]})
    return {"duracion": esc.duracion, "frases": frases,
            "subs": [[t, txt, am] for t, txt, am in esc.subs]}


def con_pausas(esc, voz, pausas, salida):
    """Copia la voz metiendo silencio justo antes de la frase n+1 (pausas = {n: segundos})."""
    os.makedirs(os.path.dirname(salida), exist_ok=True)
    cortes = sorted((float(esc.tramos[n + 1][0]) + 0.02, seg) for n, seg in pausas.items() if n + 1 < len(esc.tramos))
    partes, filtros, ant = [], [], 0.0
    for i, (t, seg) in enumerate(cortes):
        filtros.append(f"[0:a]atrim={ant:.3f}:{t:.3f},asetpts=PTS-STARTPTS[p{i}]")
        filtros.append(f"aevalsrc=0:d={seg:.3f}:s=44100:c=mono,aformat=channel_layouts=mono[s{i}]")
        partes += [f"[p{i}]", f"[s{i}]"]
        ant = t
    filtros.append(f"[0:a]atrim=start={ant:.3f},asetpts=PTS-STARTPTS[pf]")
    partes.append("[pf]")
    filtros.append("".join(partes) + f"concat=n={len(partes)}:v=0:a=1[a]")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", voz, "-filter_complex",
                    ";".join(filtros),
                    "-map", "[a]", "-ac", "1", "-ar", "44100", salida], check=True)
    return salida


def main():
    ap = argparse.ArgumentParser(description="Videos explicativos en 3D")
    ap.add_argument("video", choices=list(VIDEOS))
    ap.add_argument("--voz", help="MP3 del narrador (ElevenLabs)")
    ap.add_argument("--fps", type=int, default=30)
    ap.add_argument("--salida", default="salida")
    ap.add_argument("--cuadros", help="solo guarda estos segundos como imágenes, ej. 2,10.5")
    ap.add_argument("--sin-subs", action="store_true", help="sin subtítulos (para portadas)")
    a = ap.parse_args()

    clase, pagina = VIDEOS[a.video]
    esc = clase(voz=os.path.abspath(a.voz)) if a.voz else clase()
    if a.voz and getattr(clase, "pausas", None):
        # respiro extra después de las frases importantes: se mete silencio en la voz
        a.voz = con_pausas(esc, a.voz, clase.pausas, os.path.join(a.salida, "voces", f"{a.video}_pausas.wav"))
        esc = clase(voz=os.path.abspath(a.voz))
    os.makedirs(os.path.join(RAIZ, "motor3d", "tmp"), exist_ok=True)
    ruta_json = os.path.join("motor3d", "tmp", f"{a.video}.json")
    with open(os.path.join(RAIZ, ruta_json), "w") as f:
        datos = datos_de(esc)
        if a.sin_subs:
            datos["subs"] = []
        json.dump(datos, f)
    url = f"{pagina}?datos=/{ruta_json}"
    render = ["node", os.path.join(RAIZ, "motor3d", "render.js"), url]

    if a.cuadros:
        carpeta = os.path.join(a.salida, f"{a.video}_cuadros")
        subprocess.run(render + [carpeta, str(a.fps), f"--cuadros={a.cuadros}"], check=True, cwd=RAIZ)
        return

    os.makedirs(a.salida, exist_ok=True)
    final = os.path.join(a.salida, f"{a.video}_3d.mp4")
    print(f"Generando '{a.video}' en 3D ({esc.duracion:.1f} s)...")
    with tempfile.TemporaryDirectory() as tmp:
        mudo = os.path.join(tmp, "mudo.mp4")
        subprocess.run(render + [mudo, str(a.fps)], check=True, cwd=RAIZ)
        wav = os.path.join(tmp, "efectos.wav")
        crear_pista(esc.sonidos, esc.duracion, wav)
        cmd = ["ffmpeg", "-y", "-loglevel", "error", "-i", mudo]
        if a.voz:
            cmd += ["-i", a.voz, "-i", wav, "-filter_complex",
                    "[1:a]volume=1.0[v];[2:a]volume=0.35[e];[v][e]amix=inputs=2:normalize=0:duration=longest[a]"]
        else:
            cmd += ["-i", wav, "-filter_complex", "[1:a]volume=1.0[a]"]
        cmd += ["-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
                "-t", f"{esc.duracion:.3f}", final]
        subprocess.run(cmd, check=True)
    print("Listo →", final)


if __name__ == "__main__":
    main()
