"""Voces con ElevenLabs, con tiempos por palabra y caché en disco.

La clave NO va en el código: el proxy del entorno la inyecta en la cabecera xi-api-key.
Fuera de ese entorno, define la variable ELEVENLABS_API_KEY.
"""
import base64
import hashlib
import json
import os
import urllib.error
import urllib.request
from pathlib import Path

API = "https://api.elevenlabs.io/v1/text-to-speech/{voz}/with-timestamps?output_format=mp3_44100_128"
MODELO = "eleven_multilingual_v2"
CACHE = Path(__file__).resolve().parent.parent / "cache_voces"

# Voces prediseñadas que hablan español con el modelo multilingüe.
VOCES = {
    "george": "JBFqnCBsd6RMkjVDRZzb",   # hombre maduro, cálido (narrador)
    "adam": "pNInz6obpgDQGcFmaJgB",     # hombre, grave
    "daniel": "onwK4e9ZLuTAKqWW03F9",   # hombre, tono de noticiero
    "brian": "nPczCjzI2devNBz1zQrb",    # hombre, profundo
    "charlie": "IKne3meq5aSn9XLyUdCD",  # hombre joven, relajado
    "liam": "TX3LPaxmHKxFdv7VOQHJ",     # hombre joven
    "matilda": "XrExE9yKIg1WjnnlVkGX",  # mujer
}


def generar(texto, voz, ajustes=None):
    """Devuelve (ruta_mp3, [(palabra, inicio, fin), ...]). Usa caché si ya existe."""
    voz_id = VOCES.get(voz, voz)
    ajustes = ajustes or {"stability": 0.4, "similarity_boost": 0.8, "style": 0.35, "use_speaker_boost": True}
    clave = hashlib.sha1(json.dumps([texto, voz_id, MODELO, ajustes], sort_keys=True).encode()).hexdigest()[:16]
    mp3, meta = CACHE / f"{clave}.mp3", CACHE / f"{clave}.json"
    if mp3.exists() and meta.exists():
        return mp3, json.loads(meta.read_text())

    cuerpo = json.dumps({"text": texto, "model_id": MODELO, "voice_settings": ajustes}).encode()
    req = urllib.request.Request(API.format(voz=voz_id), data=cuerpo, method="POST", headers={
        "Content-Type": "application/json",
        "xi-api-key": os.environ.get("ELEVENLABS_API_KEY", "proxy-injected"),
    })
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            d = json.load(r)
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"ElevenLabs {e.code}: {e.read().decode(errors='replace')[:300]}") from None

    al = d.get("normalized_alignment") or d["alignment"]
    palabras = _palabras(al["characters"], al["character_start_times_seconds"], al["character_end_times_seconds"])
    CACHE.mkdir(exist_ok=True)
    mp3.write_bytes(base64.b64decode(d["audio_base64"]))
    meta.write_text(json.dumps(palabras, ensure_ascii=False))
    return mp3, palabras


def _palabras(chars, ini, fin):
    out, actual, t0, t1 = [], "", None, None
    for c, a, b in zip(chars, ini, fin):
        if c.isspace():
            if actual:
                out.append((actual, t0, t1))
            actual, t0 = "", None
            continue
        if t0 is None:
            t0 = a
        actual += c
        t1 = b
    if actual:
        out.append((actual, t0, t1))
    return out
