# videosanimados

Generador de shorts animados verticales (1080x1920) con personajes de cabeza redonda,
título grande y subtítulos palabra por palabra. Todo se dibuja por código a partir de
una historia en JSON.

```bash
python3 generar.py historias/ejemplo.json                  # crea salida/ejemplo.mp4
python3 generar.py historias/ejemplo.json --captura 2 6.5  # solo fotogramas PNG para revisar
```

## Historia (JSON)
- `titulo`: texto; separa líneas con `|` (la última sale en rojo).
- `personajes`: `sombrero` (bombin, copa, gorra, casco, boina, ninguno), `bigote` (grueso, manubrio,
  ninguno), `pelo` (lado, rizado, largo, ninguno), `gafas`, colores `ropa`, `pantalon`, `corbata`,
  `sombrero_color`, `pelo_color`, `piel`.
- `escenas`: `fondo` (oficina, campo, noche, ciudad, calor, cocina, o ruta a una imagen), `personajes` en escena
  (`id`, `x` 0–1, `escala`, `voltear`, `expresion`, `brazo`, y para esa escena `piel`, `ropa`, `sudor`) y `lineas`.
- `lineas`: `personaje`, `texto`, opcionales `expresion` (normal, feliz, enojado, triste,
  sospechoso, sorprendido), `brazo` (abajo, arriba, señala), `audio` (archivo de voz; el tiempo se
  ajusta a su duración), `duracion`, `pausa`.
- `musica` y `volumen_musica`: música de fondo opcional.

## Estilo "fino" (como los shorts de cocina)
Pon `"estilo": "fino"` en un personaje: cabeza blanca grande, ojos con pupila y cejas gruesas.
- `cuerpo`: pantalon | vestido (con `falda`, `delantal`, `delantal_color`)
- `pelo`: moño | corto | ninguno · `objeto`: vaso (con `"brazo": "sostiene"`)
- `mirada`: -1 izquierda, 0 al frente, 1 derecha
- expresiones: normal, picara, preocupado, sorprendido, feliz, enojado, triste
- En la escena, `"asomado": [x0, y0, x1, y1]` y `"y"` muestran al personaje solo dentro de ese
  rectángulo (por ejemplo, una ventana). Ver `historias/cocina.json`.

## Voces (ElevenLabs)
- Pon `"voz"` en cada personaje y `"voz_narrador"` para líneas sin personaje. También se puede
  cambiar por línea con `"voz"`.
- Nombres disponibles: george, adam, daniel, brian, charlie, liam, matilda (ver `animador/voz.py`),
  o cualquier ID de voz de tu cuenta o de la Voice Library.
- Los subtítulos usan los tiempos exactos de cada palabra y la boca se mueve con el volumen.
- Las voces se guardan en `cache_voces/`: volver a generar el mismo texto no gasta créditos.
- La clave la inyecta el entorno en la nube. En otro equipo, define `ELEVENLABS_API_KEY`.
- `--sin-voz` genera sin llamar a ElevenLabs (para pruebas rápidas).

Para otra fuente del título, copia un `.ttf` a `fuentes/titulo.ttf`.
