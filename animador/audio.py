"""Mezcla de audio: voces por línea (opcional), música de fondo y efectos generados."""
import subprocess
import wave

import numpy as np

SR = 44100


def leer(ruta):
    """Decodifica cualquier audio (mp3, wav, m4a...) a float32 mono con ffmpeg."""
    raw = subprocess.run(
        ["ffmpeg", "-v", "error", "-i", str(ruta), "-f", "f32le", "-ac", "1", "-ar", str(SR), "-"],
        check=True, capture_output=True).stdout
    return np.frombuffer(raw, dtype=np.float32).copy()


def whoosh(dur=0.4, semilla=0):
    n = int(SR * dur)
    ruido = np.random.default_rng(semilla).standard_normal(n).astype(np.float32)
    # filtro paso bajo con corte que sube y baja: suena a "barrido"
    t = np.linspace(0, 1, n)
    k = 0.02 + 0.25 * np.sin(np.pi * t) ** 2
    out = np.empty_like(ruido)
    y = 0.0
    for i in range(n):
        y += k[i] * (ruido[i] - y)
        out[i] = y
    return out * np.sin(np.pi * t) ** 1.5 * 0.9


def pop(dur=0.14):
    t = np.arange(int(SR * dur)) / SR
    f = 900 * np.exp(-t * 25) + 180
    return (np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 30) * 0.6).astype(np.float32)


def mezclar(total, eventos, musica=None, vol_musica=0.15):
    """eventos: lista de (segundo_inicio, muestras, volumen)."""
    pista = np.zeros(int(total * SR) + SR, dtype=np.float32)
    if musica is not None and len(musica):
        rep = np.tile(musica, int(np.ceil(len(pista) / len(musica))))[:len(pista)]
        pista += rep * vol_musica
    for t0, x, vol in eventos:
        i = int(t0 * SR)
        x = x[:max(0, len(pista) - i)]
        pista[i:i + len(x)] += x * vol
    pico = np.abs(pista).max()
    if pico > 0.98:
        pista *= 0.98 / pico
    return pista[:int(total * SR)]


def guardar_wav(ruta, pista):
    with wave.open(str(ruta), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((pista * 32767).astype(np.int16).tobytes())
