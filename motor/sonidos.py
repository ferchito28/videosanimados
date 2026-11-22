"""Efectos de sonido sintetizados (no hace falta descargar nada).

Cada escena pone una lista de (segundo, "nombre") y aquí se arma la pista.
Nombres disponibles: golpe, golpecito, whoosh, boing, paso, resbalon, pop,
estrellas, tada.
"""
import wave

import numpy as np

SR = 44100


def _t(dur):
    return np.arange(int(SR * dur)) / SR


def _ruido(n, seed=0):
    return np.random.default_rng(seed).uniform(-1, 1, n)


def _paso_bajo(x, k=8):
    return np.convolve(x, np.ones(k) / k, mode="same")


def golpe():
    t = _t(0.45)
    frec = 90 * np.exp(-t * 6) + 38
    tono = np.sin(2 * np.pi * np.cumsum(frec) / SR) * np.exp(-t * 7)
    ruido = _paso_bajo(_ruido(len(t), 1), 6) * np.exp(-t * 30)
    return 1.0 * tono + 0.6 * ruido


def golpecito():
    return golpe()[: int(SR * 0.25)] * 0.55


def whoosh():
    t = _t(0.5)
    env = np.sin(np.pi * t / 0.5) ** 2
    r = _ruido(len(t), 2)
    r = r - _paso_bajo(r, 3) * 0.5
    return _paso_bajo(r, 4) * env * 0.5


def boing():
    t = _t(0.6)
    frec = 260 + 120 * np.sin(2 * np.pi * 9 * t) * np.exp(-t * 3) + 140 * np.exp(-t * 4)
    return np.sin(2 * np.pi * np.cumsum(frec) / SR) * np.exp(-t * 4) * 0.7


def paso():
    t = _t(0.06)
    return _paso_bajo(_ruido(len(t), 3), 10) * np.exp(-t * 80) * 0.5


def resbalon():
    t = _t(0.35)
    frec = 700 + 2200 * (t / 0.35)
    return np.sin(2 * np.pi * np.cumsum(frec) / SR) * np.exp(-t * 3) * 0.35


def pop():
    t = _t(0.12)
    frec = 400 + 1600 * t / 0.12
    return np.sin(2 * np.pi * np.cumsum(frec) / SR) * np.exp(-t * 25) * 0.6


def estrellas():
    partes = []
    for f in (2400, 2900, 2400, 2900):
        t = _t(0.09)
        partes.append(np.sin(2 * np.pi * f * t) * np.exp(-t * 30) * 0.25)
        partes.append(np.zeros(int(SR * 0.05)))
    return np.concatenate(partes)


def tada():
    t = _t(0.7)
    s = sum(np.sin(2 * np.pi * f * t) for f in (523, 659, 784)) / 3
    return s * np.minimum(1, t * 40) * np.exp(-t * 3) * 0.6


def whoosh_suave():
    return whoosh()[: int(SR * 0.35)] * 0.35


def tac():
    t = _t(0.12)
    tono = np.sin(2 * np.pi * 180 * t) * np.exp(-t * 45)
    return (tono + _paso_bajo(_ruido(len(t), 5), 3) * np.exp(-t * 90) * 0.5) * 0.8


def crac():
    partes = []
    rng = np.random.default_rng(9)
    for i in range(6):
        t = _t(0.04 + rng.random() * 0.03)
        partes.append(_ruido(len(t), 10 + i) * np.exp(-t * 60) * (0.9 - i * 0.1))
    return np.concatenate(partes)


def ding():
    t = _t(0.6)
    return (np.sin(2 * np.pi * 1320 * t) + 0.5 * np.sin(2 * np.pi * 1980 * t)) * np.exp(-t * 6) * 0.35


def agua():
    """Chapoteo / agua entrando."""
    t = _t(0.7)
    r = _paso_bajo(_ruido(len(t), 12), 12)
    burbujas = 0.6 + 0.4 * np.sin(2 * np.pi * 14 * t) * np.sin(2 * np.pi * 3 * t)
    return r * burbujas * np.minimum(1, t * 20) * np.exp(-t * 3) * 1.2


SONIDOS = {f.__name__: f for f in (golpe, golpecito, whoosh, boing, paso, resbalon,
                                    pop, estrellas, tada, whoosh_suave, tac, crac, ding, agua)}


def crear_pista(eventos, duracion, ruta):
    """Mezcla los sonidos en un .wav. eventos = [(segundo, nombre), ...]"""
    pista = np.zeros(int(SR * (duracion + 1)))
    for seg, nombre in eventos:
        if nombre not in SONIDOS:
            raise ValueError(f"Sonido desconocido: {nombre}. Opciones: {', '.join(SONIDOS)}")
        s = SONIDOS[nombre]()
        i = int(seg * SR)
        fin = min(len(pista), i + len(s))
        pista[i:fin] += s[: fin - i]
    pista = pista[: int(SR * duracion)]
    pico = np.max(np.abs(pista)) or 1
    pista = np.int16(pista / max(pico, 1.0) * 0.9 * 32767)
    with wave.open(ruta, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pista.tobytes())
