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
  ninguno), `pelo` (lado, rizado, ninguno), `gafas`, colores `ropa`, `pantalon`, `corbata`,
  `sombrero_color`, `pelo_color`, `piel`.
- `escenas`: `fondo` (oficina, campo, noche, ciudad, o ruta a una imagen), `personajes` en escena
  (`id`, `x` 0–1, `escala`, `voltear`, `expresion`, `brazo`) y `lineas`.
- `lineas`: `personaje`, `texto`, opcionales `expresion` (normal, feliz, enojado, triste,
  sospechoso, sorprendido), `brazo` (abajo, arriba, señala), `audio` (archivo de voz; el tiempo se
  ajusta a su duración), `duracion`, `pausa`.
- `musica` y `volumen_musica`: música de fondo opcional.

Para otra fuente del título, copia un `.ttf` a `fuentes/titulo.ttf`.
