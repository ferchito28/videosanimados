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

## Videos explicativos "¿Por qué...?" con narrador (~55-60 s)

Es el formato favorito del usuario (estilo curiosidades: pregunta gancho,
problema, solución rara, dato final que sorprende). Ejemplo: `escenas/juntas_concreto.py`.

1. Escribe el guion: frases cortas, tono de narrador con humor, datos correctos,
   ~150 palabras. Dáselo al usuario para que genere la voz en **ElevenLabs**
   (modelo Multilingual v2) y te mande el MP3.
2. Crea la escena como subclase de `Explicador` con una `Frase` por oración:
   `Frase(texto, "palabras clave en amarillo", funcion_escena, [(fraccion | "palabra:N", sonido)])`.
   El texto debe ser **idéntico** al que se grabó.
3. Cada función de escena recibe `(esc, lz, u, dur, n)`: `u` = segundos desde
   que empezó la frase, `dur` = duración de la frase. Usa `esc.camara(...)` y
   `esc.momento_palabra(n, k)` para sincronizar un efecto con una palabra.
   Personajes: `cabezon(lz, x, y_pies, "obrero"|"jefe"|"ingeniero"|"chofer", cara=..., brazos=...)`.
   Los subtítulos (1-2 palabras, clave en amarillo) salen solos en y=880:
   deja libre esa franja de caras y letreros.
4. Vista previa sin voz: `python generar.py juntas_concreto`.
   Con la voz: `python generar.py juntas_concreto --voz audio.mp3`
   (detecta las pausas de la voz y acomoda subtítulos y escenas).

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
