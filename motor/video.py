"""Convierte una escena en un video MP4 vertical (1080x1920) con sonido."""
import os
import subprocess
import tempfile
import time

from .lienzo import ALTO, ANCHO, Lienzo
from .sonidos import crear_pista


class Escena:
    """Base para todas las escenas. Una escena nueva solo necesita:
    - nombre, titulo y duracion (segundos)
    - sonidos: lista de (segundo, "nombre")
    - dibujar(lz, t): dibuja el cuadro del segundo t usando el lienzo `lz`
    """
    nombre = "escena"
    titulo = ""
    duracion = 10.0
    sonidos = []

    def dibujar(self, lz: Lienzo, t: float):
        raise NotImplementedError


def renderizar(escena: Escena, salida: str, estilo="pop", fps=30, sonido=True,
               calidad="normal"):
    lz = Lienzo(estilo)
    n = int(round(escena.duracion * fps))
    os.makedirs(os.path.dirname(os.path.abspath(salida)), exist_ok=True)

    with tempfile.TemporaryDirectory() as tmp:
        cmd = ["ffmpeg", "-y", "-loglevel", "error",
               "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{ANCHO}x{ALTO}",
               "-r", str(fps), "-i", "-"]
        voz = getattr(escena, "voz", None)
        if sonido and (escena.sonidos or voz):
            entradas = []
            if voz:
                cmd += ["-i", voz]
                entradas.append("[1:a]volume=1.0[a1]")
            if escena.sonidos:
                wav = os.path.join(tmp, "audio.wav")
                crear_pista(escena.sonidos, escena.duracion, wav)
                cmd += ["-i", wav]
                n_in = 2 if voz else 1
                vol = 0.35 if voz else 1.0
                entradas.append(f"[{n_in}:a]volume={vol}[a{n_in}]")
            if voz and escena.sonidos:
                filtro = ";".join(entradas) + ";[a1][a2]amix=inputs=2:normalize=0:duration=longest[a]"
            else:
                filtro = entradas[0].rsplit("[", 1)[0] + "[a]"
            cmd += ["-filter_complex", filtro, "-map", "0:v", "-map", "[a]",
                    "-c:a", "aac", "-b:a", "192k"]
        preset = "slow" if calidad == "alta" else "veryfast"
        cmd += ["-c:v", "libx264", "-preset", preset, "-crf", "20",
                "-pix_fmt", "yuv420p", "-movflags", "+faststart",
                "-t", f"{escena.duracion:.3f}", salida]

        inicio = time.time()
        proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
        try:
            for i in range(n):
                t = i / fps
                lz.nuevo_cuadro(t)
                escena.dibujar(lz, t)
                proc.stdin.write(lz.terminar().tobytes())
                if i % fps == 0:
                    print(f"\r  cuadro {i}/{n}", end="", flush=True)
        finally:
            proc.stdin.close()
            proc.wait()
        if proc.returncode != 0:
            raise RuntimeError("ffmpeg no pudo crear el video")
        print(f"\r  listo: {n} cuadros en {time.time() - inicio:.1f} s → {salida}")
    return salida


def captura(escena: Escena, t: float, salida: str, estilo="pop"):
    """Guarda un solo cuadro como PNG (para revisar rápido una pose)."""
    lz = Lienzo(estilo)
    lz.nuevo_cuadro(t)
    escena.dibujar(lz, t)
    lz.terminar().save(salida)
    return salida
