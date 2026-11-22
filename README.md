# videosanimados

Generador de videos de stickman para TikTok, Reels y Shorts: formato vertical
1080x1920, con cámara lenta, zoom, temblor, textos grandes y efectos de sonido.

## Uso rápido (desde Claude en el celular)

Abre una sesión de Code con este repositorio y pide, por ejemplo:

> Hazme un video de un stickman que se cae de la bici

Claude crea la escena, revisa los cuadros y te manda el MP4.

## Uso manual

```bash
pip install -r requirements.txt     # también necesita ffmpeg
python generar.py --lista
python generar.py resbalon --estilo pop
python generar.py parkour --estilo neon
python generar.py todas --estilo cuaderno
```

Los videos quedan en la carpeta `salida/`.

| Escena    | Duración | De qué trata |
|-----------|----------|--------------|
| resbalon  | 11 s     | Se resbala con una cáscara de plátano... y la cáscara regresa |
| parkour   | 8.5 s    | Intenta saltar una caja, cae de cara y la caja le cae encima |

Estilos: `pop` (colores fuertes), `neon` (fondo oscuro), `cuaderno` (libreta).

Consejo: en CapCut puedes ponerle encima un sonido que esté de moda; los
efectos de sonido del video se escuchan por debajo.

La fuente Anton se incluye bajo la licencia SIL Open Font License
(`fuentes/OFL-Anton.txt`).
