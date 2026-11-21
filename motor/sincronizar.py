"""Calcula en qué segundo se dice cada palabra del guion.

Sin audio: estima los tiempos con un ritmo de narrador normal.
Con audio (por ejemplo el MP3 de ElevenLabs): detecta las pausas de la voz y
las empareja con los puntos y comas del guion, así los subtítulos y los
cambios de escena caen justo cuando se dicen.
"""
import re
import subprocess

import numpy as np

RITMO = 19.0  # "unidades" por segundo (aprox. letras + 1.5 por palabra); ~2.9 palabras/s


def peso(palabra):
    return len(re.sub(r"[^\wáéíóúüñ]", "", palabra.lower())) + 1.5


def pausa_despues(palabra):
    """Qué tan larga es la pausa natural después de esta palabra (segundos)."""
    if palabra.endswith("..."):
        return 0.45
    if palabra[-1:] in ".?!":
        return 0.4
    if palabra[-1:] in ",;:":
        return 0.18
    return 0.0


def estimar(palabras, inicio=0.3):
    t, res = inicio, []
    for p in palabras:
        d = peso(p) / RITMO
        res.append((t, t + d))
        t += d + pausa_despues(p)
    return res


def _cargar_audio(ruta, sr=16000):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", ruta, "-ac", "1", "-ar", str(sr),
                          "-f", "f32le", "-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, dtype=np.float32), sr


def duracion_audio(ruta):
    x, sr = _cargar_audio(ruta)
    return len(x) / sr


def _silencios(ruta, min_silencio=0.14):
    x, sr = _cargar_audio(ruta)
    hop = int(sr * 0.01)
    n = len(x) // hop
    rms = np.sqrt(np.mean(x[: n * hop].reshape(n, hop) ** 2, axis=1) + 1e-12)
    umbral = max(np.percentile(rms, 95) * 0.06, 1e-4)
    voz = rms > umbral
    idx = np.nonzero(voz)[0]
    if len(idx) == 0:
        raise ValueError("No se detectó voz en el audio")
    ini_voz, fin_voz = idx[0] * 0.01, (idx[-1] + 1) * 0.01
    gaps, i = [], idx[0]
    while i <= idx[-1]:
        if not voz[i]:
            j = i
            while j <= idx[-1] and not voz[j]:
                j += 1
            if (j - i) * 0.01 >= min_silencio:
                gaps.append((i * 0.01, j * 0.01))
            i = j
        else:
            i += 1
    return ini_voz, fin_voz, gaps, len(x) / sr


def desde_audio(palabras, ruta):
    """Tiempos (inicio, fin) de cada palabra, alineados con la voz grabada."""
    ini, fin, gaps, total = _silencios(ruta)
    est = estimar(palabras, inicio=0.0)
    escala = (fin - ini) / max(1e-6, est[-1][1])
    # pausas del texto: (índice de palabra, tiempo esperado, importancia)
    cortes = []
    for i, p in enumerate(palabras[:-1]):
        pz = pausa_despues(p)
        if pz > 0:
            cortes.append((i, ini + est[i][1] * escala, 1.0 if pz >= 0.4 else 0.5))
    # emparejar pausas del texto con silencios del audio (programación dinámica)
    B, G = len(cortes), len(gaps)
    INF = 1e9
    costo = np.full((B + 1, G + 1), INF)
    paso = np.zeros((B + 1, G + 1), dtype=int)
    costo[0, :] = np.arange(G + 1) * 0.05
    for b in range(1, B + 1):
        costo[b, 0] = costo[b - 1, 0] + cortes[b - 1][2] * 0.6
        for g in range(1, G + 1):
            mid = (gaps[g - 1][0] + gaps[g - 1][1]) / 2
            opciones = (
                costo[b - 1, g - 1] + abs(cortes[b - 1][1] - mid),          # emparejar
                costo[b - 1, g] + cortes[b - 1][2] * 0.6,                    # pausa sin silencio
                costo[b, g - 1] + 0.05 + 0.3 * (gaps[g - 1][1] - gaps[g - 1][0]),  # silencio extra
            )
            k = int(np.argmin(opciones))
            costo[b, g], paso[b, g] = opciones[k], k
    pares, b, g = {}, B, G
    while b > 0 and g > 0:
        k = paso[b, g]
        if k == 0:
            pares[cortes[b - 1][0]] = gaps[g - 1]
            b, g = b - 1, g - 1
        elif k == 1:
            b -= 1
        else:
            g -= 1
    # anclas: tramos de palabras entre pausas emparejadas
    anclas = [(-1, None, ini)]
    for i in sorted(pares):
        anclas.append((i, pares[i][0], pares[i][1]))
    anclas.append((len(palabras) - 1, fin, None))
    res = [None] * len(palabras)
    for a in range(len(anclas) - 1):
        i0, t0 = anclas[a][0] + 1, anclas[a][2]
        i1, t1 = anclas[a + 1][0], anclas[a + 1][1]
        tramo = palabras[i0:i1 + 1]
        pesos = [peso(p) + pausa_despues(p) * RITMO * (k < len(tramo) - 1)
                 for k, p in enumerate(tramo)]
        total_p = sum(pesos) or 1
        t = t0
        for k, p in enumerate(tramo):
            d_hablada = peso(p) / total_p * (t1 - t0)
            res[i0 + k] = (t, t + d_hablada)
            t += pesos[k] / total_p * (t1 - t0)
    return res, total
