"""Convierte una historia (JSON) en un short vertical MP4."""
import json
import math
import subprocess
import tempfile
from pathlib import Path

import numpy as np
from PIL import Image

from . import audio, fondo, personaje, texto, voz

W, H = 1080, 1920
PISO_Y = 1800          # donde apoyan los pies
SUB_Y = 1480           # centro vertical de los subtítulos
TITULO_Y = 120


def _ease_back(x):
    x = min(max(x, 0.0), 1.0)
    c = 1.70158
    return 1 + (c + 1) * (x - 1) ** 3 + c * (x - 1) ** 2


def _ease_out(x):
    x = min(max(x, 0.0), 1.0)
    return 1 - (1 - x) ** 3


def _lineas_titulo(t):
    if isinstance(t, str):
        partes = [p.strip() for p in t.split("|")]
        colores = ["#ffffff"] * (len(partes) - 1) + ["#ff3b30"] if len(partes) > 1 else ["#ffffff"]
        t = [{"texto": p, "color": c} for p, c in zip(partes, colores)]
    return [(x["texto"], x.get("color", "#ffffff")) for x in t]


def _tiempos_palabras(palabras, inicio, dur_habla):
    pesos = [len(p) + 2 for p in palabras]
    tot = sum(pesos)
    t, out = inicio, []
    for p in pesos:
        d = dur_habla * p / tot
        out.append((t, t + d))
        t += d
    return out


def _envolvente(x, fps=60):
    """Volumen de la voz 60 veces por segundo, normalizado a 0..1 (para mover la boca)."""
    n = audio.SR // fps
    m = len(x) // n
    if m == 0:
        return np.zeros(1)
    rms = np.sqrt((x[:m * n].reshape(m, n) ** 2).mean(axis=1))
    return rms / (np.percentile(rms, 95) + 1e-6)


def _elegir_voz(h, ln, usar_voces):
    if not usar_voces:
        return None
    pid = ln.get("personaje")
    if ln.get("voz"):
        return ln["voz"]
    if pid and h["personajes"].get(pid, {}).get("voz"):
        return h["personajes"][pid]["voz"]
    return h.get("voz_narrador") if not pid else None


def construir_linea_de_tiempo(h, base, usar_voces=True):
    escenas, eventos, t = [], [], 0.0
    for ie, e in enumerate(h["escenas"]):
        ini = t
        eventos.append((max(0, t - 0.15), audio.whoosh(semilla=ie), 0.5))
        lineas = []
        for ln in e["lineas"]:
            palabras = ln["texto"].split()
            t_pal, env, nombre_voz = None, None, _elegir_voz(h, ln, usar_voces)
            if ln.get("audio") or nombre_voz:
                if ln.get("audio"):
                    ruta, alineado = base / ln["audio"], None
                else:
                    ruta, alineado = voz.generar(ln["texto"], nombre_voz, h.get("ajustes_voz"))
                x = audio.leer(ruta)
                habla = len(x) / audio.SR
                eventos.append((t, x, 1.0))
                env = _envolvente(x)
                if alineado and len(alineado) == len(palabras):
                    t_pal = [(t + a, t + b) for _, a, b in alineado]
            else:
                habla = ln.get("duracion") or max(1.0, 0.068 * len(ln["texto"]) + 0.3)
            fin = t + habla + ln.get("pausa", 0.25)
            lineas.append({**ln, "inicio": t, "fin_habla": t + habla, "fin": fin, "env": env,
                           "palabras": palabras, "t_pal": t_pal or _tiempos_palabras(palabras, t, habla)})
            t = fin
        escenas.append({**e, "inicio": ini, "fin": t, "lineas": lineas})
    return escenas, eventos, t


class Animador:
    def __init__(self, ruta_historia, usar_voces=True):
        self.ruta = Path(ruta_historia)
        self.base = self.ruta.parent
        self.h = json.loads(self.ruta.read_text(encoding="utf-8"))
        self.reparto = self.h["personajes"]
        self.escenas, self.eventos, self.total = construir_linea_de_tiempo(self.h, self.base, usar_voces)
        self.fondos = {}
        self.sprites = {}
        self.titulo = texto.titulo(_lineas_titulo(self.h["titulo"])) if self.h.get("titulo") else None
        if self.titulo:
            self.eventos.append((0.05, audio.pop(), 0.8))
        sombra = Image.new("RGBA", (400, 60), (0, 0, 0, 0))
        from PIL import ImageDraw
        ImageDraw.Draw(sombra).ellipse([0, 0, 400, 60], fill=(0, 0, 0, 90))
        self.sombra = sombra

    # ---------- piezas cacheadas ----------
    def _fondo(self, nombre):
        if nombre not in self.fondos:
            self.fondos[nombre] = fondo.crear(nombre, self.base).convert("RGBA")
        return self.fondos[nombre]

    def _sprite(self, pid, boca, cerrados, expresion, brazo, voltear):
        k = (pid, boca, cerrados, expresion, brazo, voltear)
        if k not in self.sprites:
            cfg = dict(self.reparto[pid], voltear=voltear)
            self.sprites[k] = personaje.dibujar(cfg, boca, cerrados, expresion, brazo)
        return self.sprites[k]

    # ---------- un fotograma ----------
    def fotograma(self, t):
        esc = next((e for e in self.escenas if e["inicio"] <= t < e["fin"]), self.escenas[-1])
        local = t - esc["inicio"]
        linea = next((l for l in esc["lineas"] if l["inicio"] <= t < l["fin"]), None)
        cuadro = self._fondo(esc.get("fondo", "oficina")).copy()

        for i, pc in enumerate(esc.get("personajes", [])):
            pid = pc["id"]
            habla = bool(linea and linea.get("personaje") == pid and t < linea["fin_habla"])
            if habla and linea["env"] is not None:
                env = linea["env"]
                boca = env[min(len(env) - 1, int((t - linea["inicio"]) * 60))] > 0.35
            else:
                boca = habla and (math.sin(t * 29 + i) + 0.6 * math.sin(t * 13)) > -0.2
            cerrados = ((t + i * 1.37) % 3.2) < 0.12
            expresion = pc.get("expresion", "normal")
            brazo = pc.get("brazo", "abajo")
            if linea and linea.get("personaje") == pid:
                expresion = linea.get("expresion", expresion)
                brazo = linea.get("brazo", brazo)
            spr = self._sprite(pid, boca, cerrados, expresion, brazo, pc.get("voltear", False))

            esc_k = pc.get("escala", 1.25)
            entrada = _ease_back(local / 0.4) if pc.get("entra", True) else 1.0
            rebote = math.sin(t * 2 * math.pi * 4.5) * 10 if habla else math.sin(t * 2 * math.pi * 0.7 + i) * 4
            aplasta = 1 + (0.02 * math.sin(t * 2 * math.pi * 4.5) if habla else 0.008 * math.sin(t * 4 + i))
            w = int(spr.width * esc_k / aplasta ** 0.5)
            h = int(spr.height * esc_k * aplasta * max(entrada, 0.05))
            img = spr.resize((w, h), Image.BILINEAR)
            cx = int(pc.get("x", 0.5) * W)
            pie = PISO_Y + int((1 - min(entrada, 1)) * 80)
            sw = int(w * 0.7)
            cuadro.alpha_composite(self.sombra.resize((sw, int(sw * 0.15))), (cx - sw // 2, PISO_Y - int(sw * 0.07)))
            cuadro.alpha_composite(img, (cx - w // 2, int(pie - h * 0.96 + rebote)))

        # cámara: acercamiento lento + "golpe" al empezar cada escena
        dur = esc["fin"] - esc["inicio"]
        z = 1.0 + 0.06 * local / dur + 0.10 * (1 - _ease_out(local / 0.3))
        if z > 1.001:
            cw, ch = W / z, H / z
            fx, fy = W / 2, H * 0.6
            cuadro = cuadro.resize((W, H), Image.BILINEAR, box=(fx - cw / 2, fy - ch * 0.6, fx + cw / 2, fy + ch * 0.4))

        if self.titulo:
            k = _ease_back(t / 0.45)
            tit = self.titulo
            if k < 0.999 or k > 1.001:
                tit = tit.resize((max(1, int(tit.width * k)), max(1, int(tit.height * k))), Image.BILINEAR)
            cuadro.alpha_composite(tit, ((W - tit.width) // 2, TITULO_Y + (self.titulo.height - tit.height) // 2))

        if linea and t < linea["fin_habla"] + 0.15:
            self._subtitulos(cuadro, linea, t)
        return cuadro.convert("RGB")

    def _subtitulos(self, cuadro, linea, t):
        pal, tp = linea["palabras"], linea["t_pal"]
        idx = next((j for j, (a, b) in enumerate(tp) if a <= t < b), len(pal) - 1)
        g = 3
        grupo0 = (idx // g) * g
        grupo = tuple(pal[grupo0:grupo0 + g])
        img = texto.subtitulo(grupo, idx - grupo0)
        salto = _ease_back((t - tp[idx][0]) / 0.18)
        if salto < 0.999:
            k = 0.85 + 0.15 * salto
            img = img.resize((int(img.width * k), int(img.height * k)), Image.BILINEAR)
        cuadro.alpha_composite(img, ((W - img.width) // 2, SUB_Y - img.height // 2))

    # ---------- vídeo completo ----------
    def render(self, salida, fps=30, crf=20):
        salida = Path(salida)
        salida.parent.mkdir(parents=True, exist_ok=True)
        musica = None
        if self.h.get("musica"):
            musica = audio.leer(self.base / self.h["musica"])
        pista = audio.mezclar(self.total, self.eventos, musica, self.h.get("volumen_musica", 0.15))
        with tempfile.TemporaryDirectory() as tmp:
            wav = Path(tmp) / "audio.wav"
            audio.guardar_wav(wav, pista)
            cmd = ["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                   "-r", str(fps), "-i", "-", "-i", str(wav), "-c:v", "libx264", "-preset", "medium",
                   "-crf", str(crf), "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k",
                   "-movflags", "+faststart", "-shortest", str(salida)]
            ff = subprocess.Popen(cmd, stdin=subprocess.PIPE)
            n = int(self.total * fps)
            for i in range(n):
                ff.stdin.write(self.fotograma(i / fps).tobytes())
                if i % fps == 0:
                    print(f"\r{i / fps:5.1f}s / {self.total:.1f}s", end="", flush=True)
            ff.stdin.close()
            if ff.wait() != 0:
                raise RuntimeError("ffmpeg falló")
        print(f"\nListo: {salida} ({self.total:.1f}s)")
        return salida
