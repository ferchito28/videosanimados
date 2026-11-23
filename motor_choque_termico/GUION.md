# El cuñado, la hielera y el motor — guion + guía

Short vertical 1080×1920 · 30 fps · 55 s · Mito vs. realidad: choque térmico en el motor.

## 1. Guion cronometrado

| Tiempo | Voz en off (rápida, sin pausas) | Acción visual | Texto en pantalla |
|---|---|---|---|
| 0:00–0:04 | "¡Mi cuñado le está echando una HIELERA ENTERA… a un motor hirviendo!" | Carro rojo humeando en la carretera. El cuñado (lentes oscuros, camisa floreada) levanta la hielera y la voltea: lluvia de hielo + vapor. El padrino, en shock, con la cajita de anillos. | **¿UNA HIELERA AL MOTOR?** |
| 0:04–0:05 | *(record scratch)* | Congelado en blanco y negro + icono de pausa. | **ESPERA… CONTEXTO** |
| 0:05–0:08.6 | "Contexto: faltan 2 horas para la boda de mi mejor amigo… y nosotros llevamos los anillos." | Aparece el cronómetro "BODA EN 1:59:xx" y el medidor de temperatura en H con "!" parpadeando. Etiqueta "EL CUÑADO SABELOTODO". El padrino levanta los anillos. | **FALTAN 2 HORAS PARA LA BODA** → **…Y LLEVAMOS LOS ANILLOS** |
| 0:08.6–0:12 | "A media carretera, el coche empezó a echar humo. Y llegó Don Chuy, mecánico de carretera de toda la vida." | Don Chuy (gorra roja, bigote canoso, overol) entra caminando y levanta la mano: "calma". | Etiqueta **DON CHUY · MECÁNICO** |
| 0:12–0:15.8 | "Mi cuñado: ¡Hielo! ¡Así se enfría más rápido!" | Pantalla dividida. Arriba (rojo): hielo cayendo sobre el bloque al rojo vivo, vapor. Abajo (verde): mismo motor, reloj girando. | **CUÑADO: HIELO DIRECTO** / **VS** / **DON CHUY: ESPERAR + AGUA TIBIA** |
| 0:15.8–0:22.6 | "Don Chuy: apágalo, abre el cofre y espera 15 a 20 minutos. Luego agua tibia, poquito a poco y con el motor encendido." | Arriba: "0 °C" contra "110 °C", la grieta empieza a crecer. Abajo: el motor pasa de rojo a gris (110 °C → 60 °C) y una jarra de agua tibia vierte despacio. | **15-20 MIN** · **TIBIA** |
| 0:22.6–0:26 | "Mi cuñado, obviamente… no esperó." | Arriba: ❌ + "¡CHOQUE TÉRMICO!". Abajo: ✅. | **¡CHOQUE TÉRMICO!** |
| 0:26–0:31 | "El metal caliente está expandido: sus átomos vibran y se separan." | La lente del microscopio se abre como un iris: red de átomos rojos, vibrando y separados. | **CALOR = METAL EXPANDIDO** · "ZOOM x 1.000.000" |
| 0:31–0:36 | "Con hielo, la parte de afuera se encoge de golpe… mientras por dentro sigue hirviendo." | Un frente azul baja desde la superficie: los átomos de arriba se juntan; los de abajo siguen rojos. Los enlaces de la frontera brillan en amarillo (tensión). Flechas: azules hacia adentro, rojas hacia afuera. | **HIELO: AFUERA SE ENCOGE DE GOLPE** · "AFUERA 0 °C" / "ADENTRO 110 °C" |
| 0:36–0:39.2 | "Afuera jala, adentro empuja… y el bloque se parte." | Una grieta en zigzag atraviesa la red de arriba abajo y las mitades se separan. | **AFUERA JALA, ADENTRO EMPUJA** |
| 0:39.2–0:42 | "Como un vaso caliente en agua fría." | Recuadro: vaso dentro de agua fría que se raja. | **= VASO CALIENTE EN AGUA FRÍA** |
| 0:42–0:44.5 | *¡CRACK!* (efecto de sonido) | Último cubetazo → destello blanco, temblor de cámara, humo negro, piezas volando. Don Chuy se lleva la mano a la cara. | **¡CRACK!** |
| 0:44.5–0:51 | "Y así llegamos a la boda: a tiempo… pero en grúa." | Llega una grúa amarilla ("GRÚAS DON CHUY") con el coche colgando y humeando. Claxon. Los invitados y la novia saludan, cae confeti. | **LLEGAMOS A TIEMPO…** → **¡EN GRÚA!** · "BODA EN 0:01:5x ¡A TIEMPO!" |
| 0:51–0:55 | "¿Y a ti qué remedio casero te han recomendado cuando se calienta el coche? Te leo en comentarios." | Se oscurece el fondo y salta una tarjeta. El cuñado se asoma con su hielera y una flecha rebota hacia abajo. | **¿Y A TI QUÉ "REMEDIO CASERO" te han recomendado cuando se calienta el coche?** · botón **COMENTA ABAJO** |

> Los subtítulos de esta tabla ya están en el script (`SUBTITULOS` y `TITULARES`). Si grabas tu voz con otro ritmo, cambia ahí los tiempos.

## 2. Código

Script completo: [`video_choque_termico.py`](video_choque_termico.py) (PIL + NumPy + MoviePy, sin imágenes externas).

- El lienzo es de 1080×1920 a 30 fps y dura 55 s.
- Escena 1 (0–12 s): carretera, humo, hielera, cronómetro de la boda y medidor de temperatura.
- Escena 2 (12–26 s): pantalla dividida, hielo + grieta contra esperar + agua tibia.
- Escena 3 (26–42 s): zoom microscópico. Los átomos rojos están expandidos, la contracción azul llega desde la superficie y se abre una grieta animada.
- Escena 4 (42–55 s): ¡CRACK!, llegada en grúa con los invitados saludando y la pregunta final.
- Los subtítulos son grandes, con contorno, y resaltan en amarillo las palabras clave. Quedan dentro de la zona segura de TikTok y Shorts.
- Los efectos de sonido se generan por código: hielo, chisporroteo, tic-tac, buzzer, ding, ¡CRACK!, claxon y whooshes.

## 3. Cómo ejecutarlo

Necesitas Python 3.9+ y **ffmpeg**. MoviePy lo trae a través de `imageio-ffmpeg`, así que normalmente no tienes que instalar nada más.

```bash
# (opcional) entorno virtual
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

pip install moviepy pillow numpy

# Render completo (~1-3 min) -> choque_termico.mp4
python video_choque_termico.py

# Con tu voz en off grabada (mp3/wav de ~55 s):
python video_choque_termico.py --voz narracion.mp3

# Revisar un momento concreto sin renderizar todo (guarda un PNG):
python video_choque_termico.py --frame 37.5

# Vista previa rápida a 15 fps:
python video_choque_termico.py --fps 15 --salida preview.mp4

# Usar tu propia tipografía (p. ej. Montserrat ExtraBold):
python video_choque_termico.py --fuente "C:/ruta/Montserrat-ExtraBold.ttf"
```

### Mejoras rápidas

1. **Voz:** grábala al 1.1–1.2× de velocidad y ajusta los tiempos de `SUBTITULOS` a tu toma.
2. **Música:** agrega en TikTok o CapCut un audio en tendencia a volumen bajo (10–15 %). Así sumas el alcance del sonido viral.
3. **Gancho:** sube los primeros 0.5 s directamente con el hielo cayendo. Para eso cambia el inicio de `falling_ice` en la escena 1 de `2.0` a `0.5`.
4. **Loop:** termina la CTA con la hielera del cuñado. Así el final enlaza con el inicio y sube la retención.

## 4. Aclaraciones técnicas (para la descripción del video)

> ⚠️ **Nota:** El video es humor. **No le eches agua fría ni hielo a un motor caliente.** El cambio brusco de temperatura (choque térmico) puede deformar la cabeza del motor, quemar el empaque o rajar el bloque.
>
> **Qué hacer si tu auto se sobrecalienta:**
> 1. Orilla el auto en un lugar seguro y **apaga el motor**. Si puedes, antes enciende la calefacción al máximo unos segundos para sacar calor.
> 2. Abre el cofre (con cuidado, puede salir vapor) y **espera 15–20 minutos**.
> 3. **Nunca abras el tapón del radiador con el motor caliente.** El refrigerante está a presión y puede causar quemaduras graves. Ábrelo con el motor frío y con un trapo, girando poco a poco.
> 4. Rellena con **anticongelante/refrigerante** o, en emergencia, **agua a temperatura ambiente**. Si el manual lo indica, hazlo **con el motor encendido en ralentí** para que el líquido circule y no llegue de golpe a metal caliente.
> 5. Revisa si hay fugas (mangueras, radiador, bomba de agua). Si la aguja vuelve a subir, **no sigas manejando**: llévalo al mecánico o pide una grúa.
>
> *Si usaste solo agua, cámbiala por refrigerante en cuanto puedas: el agua sola hierve antes, se congela y oxida el sistema.*
