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


def _emparejar(cortes, gaps, pen_pausa=0.6, pen_silencio=0.5):
    """Empareja pausas del texto [(índice, tiempo esperado, peso)] con silencios
    [(inicio, fin)] respetando el orden (programación dinámica)."""
    B, G = len(cortes), len(gaps)
    costo = np.full((B + 1, G + 1), 1e9)
    paso = np.zeros((B + 1, G + 1), dtype=int)
    costo[0, :] = [sum(0.05 + pen_silencio * (g[1] - g[0]) for g in gaps[:j]) for j in range(G + 1)]
    for b in range(1, B + 1):
        costo[b, 0] = costo[b - 1, 0] + cortes[b - 1][2] * pen_pausa
        for g in range(1, G + 1):
            mid = (gaps[g - 1][0] + gaps[g - 1][1]) / 2
            opciones = (
                costo[b - 1, g - 1] + abs(cortes[b - 1][1] - mid),                 # emparejar
                costo[b - 1, g] + cortes[b - 1][2] * pen_pausa,                     # pausa sin silencio
                costo[b, g - 1] + 0.05 + pen_silencio * (gaps[g - 1][1] - gaps[g - 1][0]),  # silencio de más
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
    return pares


def desde_audio(palabras, ruta):
    """Tiempos (inicio, fin) de cada palabra, alineados con la voz grabada."""
    ini, fin, gaps, total = _silencios(ruta)
    est = estimar(palabras, inicio=0.0)
    fuertes = [i for i, p in enumerate(palabras[:-1]) if pausa_despues(p) >= 0.4]
    debiles = [i for i, p in enumerate(palabras[:-1]) if 0 < pausa_despues(p) < 0.4]

    def esperado(i, i0, t0, i1, t1):
        """Tiempo esperado del final de la palabra i, repartiendo [t0, t1] entre i0..i1."""
        base = est[i0][0]
        total_est = max(1e-6, est[i1][1] - base)
        return t0 + (est[i][1] - base) / total_est * (t1 - t0)

    # 1) pausas largas (fin de oración, "...", "¡crac!") ↔ silencios largos
    # el umbral se adapta a cada voz: tantas pausas largas como finales de oración (+15%)
    durs = sorted((g[1] - g[0] for g in gaps), reverse=True)
    k = min(len(durs), max(1, round(len(fuertes) * 1.15)))
    umbral = max(0.2, min(0.35, durs[k - 1])) if durs else 0.35
    largos = [g for g in gaps if g[1] - g[0] >= umbral]
    pares = _emparejar([(i, esperado(i, 0, ini, len(palabras) - 1, fin), 1.0) for i in fuertes], largos,
                        pen_pausa=2.5, pen_silencio=4.0)
    # 1b) un final de oración casi siempre es la pausa más larga de su zona: si junto a la
    #     pausa elegida hay otra libre más larga (p. ej. el narrador también se detuvo en una
    #     coma o en dos puntos), se queda con la más larga.
    orden = sorted(pares)
    for j, i in enumerate(orden):
        if palabras[i].endswith("..."):
            continue
        ant = pares[orden[j - 1]][1] if j > 0 else ini
        sig = pares[orden[j + 1]][0] if j + 1 < len(orden) else fin
        usados_ = set(pares.values())
        cand = [g for g in largos if g == pares[i] or (g not in usados_ and ant <= g[0] and g[1] <= sig)]
        exp = esperado(i, 0, ini, len(palabras) - 1, fin)
        pares[i] = max(cand, key=lambda g: (g[1] - g[0]) - 0.05 * abs((g[0] + g[1]) / 2 - exp))
    # 2) comas dentro de cada tramo ↔ los silencios que quedan en ese tramo
    anclas = [(-1, ini)] + [(i, pares[i][1]) for i in sorted(pares)] + [(len(palabras) - 1, fin)]
    usados = set(pares.values())
    for (a, ta), (b, tb) in zip(anclas, anclas[1:]):
        if b - a < 2:
            continue
        fin_b = pares[b][0] if b in pares else fin
        cortes = [(i, esperado(i, a + 1, ta, b, fin_b), 0.5) for i in debiles if a < i < b]
        libres = [g for g in gaps if g not in usados and ta <= g[0] and g[1] <= fin_b]
        if cortes and libres:
            pares.update(_emparejar(cortes, libres))
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
