# Videos animados de stickman

Plantilla para crear videos cortos de stickman (monito de palitos) en formato
vertical 1080x1920, listos para TikTok, Reels y Shorts. El dueño habla español:
responde siempre en español, en palabras sencillas (no es programador).

## Cómo generar videos

```bash
python generar.py --lista                      # escenas y estilos disponibles
python generar.py resbalon                     # → salida/resbalon_pop.mp4
python generar.py parkour --estilo neon
python generar.py resbalon --captura 3.9       # un solo cuadro en PNG para revisar
```

Un video de ~10 s tarda unos 15 s en generarse. Los videos quedan en `salida/`
(no se suben al repo). Al terminar, **manda el MP4 al usuario** para que lo vea
en su celular.

## Cuando el usuario pida un video nuevo ("haz uno de un stickman que...")

1. Crea `escenas/<nombre>.py` copiando la estructura de `escenas/resbalon.py`
   y regístrala en `escenas/__init__.py`.
2. Estructura que funciona para que sea viral (10–15 s):
   - 0–0.5 s: texto gancho arriba ("Cuando...", "POV:", "Yo intentando...").
   - Preparación corta (2–3 s), el accidente con **cámara lenta, zoom y rayas de
     velocidad**, luego el **golpe** con temblor, destello, polvo, onomatopeya
     (¡PUM!, ¡CRASH!) y sonido `golpe`.
   - Un segundo giro chistoso al final (lo que parecía resuelto sale peor).
   - Cierre con texto abajo ("¿Parte 2?", "Sígueme para la parte 2").
3. Antes de generar el video completo, revisa 4–6 cuadros clave con
   `--captura` y míralos (posturas raras, cosas fuera de cuadro, textos tapados).
4. Genera el MP4 y mándalo.

## Piezas del motor (`motor/`)

- `stickman.py`: `Pose` (ángulos: 0 = abajo, 90 = adelante, 180 = arriba;
  `rot` gira todo el cuerpo: +90 cae de cara, -90 cae de espaldas),
  `animar(claves, t)`, `animar_num`, `apoyar(pose, suelo)`, `caminando`,
  `corriendo`, suavizados `suave`, `acelera`, `frena`, `rebote`.
  Caras: normal, feliz, sorpresa, miedo, enojado, mareado.
- `lienzo.py`: `camara`, `suelo`, `monito`, `caja`, `platano`, `circulo`,
  `linea`, `poligono`, `estrellitas`, `polvo`, `lineas_velocidad`, `flash`,
  `texto`, `onomatopeya`. Estilos: pop, neon, cuaderno.
- `sonidos.py`: golpe, golpecito, whoosh, boing, paso, resbalon, pop,
  estrellas, tada (sintetizados, sin descargas).

Solo necesita Python 3, Pillow, NumPy y ffmpeg (ver `requirements.txt`).
