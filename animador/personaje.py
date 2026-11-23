"""Dibuja personajes de cabeza redonda con contorno grueso, todo por código.

Cada personaje se describe con un diccionario (ver historias/ejemplo.json):
  sombrero: bombin | copa | gorra | casco | boina | ninguno
  bigote:   grueso | manubrio | ninguno
  pelo:     lado | rizado | ninguno
  gafas:    true/false
  ropa, pantalon, corbata, sombrero_color, pelo_color, piel: colores "#rrggbb"
"""
from PIL import Image, ImageDraw

S = 2               # supermuestreo: se dibuja al doble y se reduce (bordes suaves)
ANCHO, ALTO = 600, 1000
TINTA = (32, 28, 34, 255)
LW = 9              # grosor del contorno a 1x


def _hex(c, a=255):
    c = c.lstrip("#")
    return (int(c[0:2], 16), int(c[2:4], 16), int(c[4:6], 16), a)


def _oscurecer(rgba, f=0.82):
    return tuple(int(v * f) for v in rgba[:3]) + (rgba[3],)


def dibujar(cfg, boca=False, ojos_cerrados=False, expresion="normal", brazo="abajo"):
    if cfg.get("estilo") == "fino":
        return dibujar_fino(cfg, boca, ojos_cerrados, expresion, brazo)
    im = Image.new("RGBA", (ANCHO * S, ALTO * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)

    def s(*v):
        return [int(x * S) for x in v]

    lw = LW * S
    piel = _hex(cfg.get("piel", "#f8f5ee"))
    ropa = _hex(cfg.get("ropa", "#3f6b4a"))
    pelo = _hex(cfg.get("pelo_color", "#3a2a22"))
    som = _hex(cfg.get("sombrero_color", "#2b2b30"))

    # --- piernas (palitos) y zapatos ---
    for x0, x1 in ((265, 250), (335, 350)):
        d.line(s(x0, 790, x1, 935), fill=TINTA, width=int(11 * S))
    for x in (238, 362):
        d.ellipse(s(x - 40, 918, x + 40, 962), fill=(30, 30, 34, 255), outline=TINTA, width=lw)

    # --- brazos (palitos detrás del torso) ---
    hombro_i, hombro_d = (200, 590), (400, 590)
    mano_i = {"arriba": (40, 450), "señala": (130, 760)}.get(brazo, (140, 770))
    mano_d = {"señala": (560, 560)}.get(brazo, (460, 770))
    d.line(s(*hombro_i, *mano_i), fill=TINTA, width=int(11 * S))
    d.line(s(*hombro_d, *mano_d), fill=TINTA, width=int(11 * S))

    # --- torso (abrigo) ---
    d.rounded_rectangle(s(168, 520, 432, 815), radius=70 * S, fill=ropa, outline=TINTA, width=lw)
    d.rounded_rectangle(s(185, 540, 236, 800), radius=40 * S, fill=_oscurecer(ropa, 0.88))
    d.line(s(300, 600, 300, 812), fill=TINTA, width=int(5 * S))
    d.polygon(s(248, 522, 352, 522, 300, 610), fill=(250, 250, 250, 255), outline=TINTA, width=int(5 * S))
    if cfg.get("corbata"):
        d.polygon(s(288, 545, 312, 545, 318, 640, 300, 660, 282, 640), fill=_hex(cfg["corbata"]),
                  outline=TINTA, width=int(4 * S))
    for y in (660, 720):
        d.ellipse(s(312, y - 10, 332, y + 10), fill=(226, 180, 60, 255), outline=TINTA, width=int(4 * S))

    # --- manos ---
    for mx, my in (mano_i, mano_d):
        d.ellipse(s(mx - 30, my - 30, mx + 30, my + 30), fill=(252, 252, 252, 255), outline=TINTA, width=lw)

    # --- pelo (detrás de la cabeza) ---
    estilo_pelo = cfg.get("pelo", "lado")
    if estilo_pelo == "lado":
        d.ellipse(s(62, 220, 150, 400), fill=pelo, outline=TINTA, width=lw)
        d.ellipse(s(450, 220, 538, 400), fill=pelo, outline=TINTA, width=lw)
    elif estilo_pelo == "largo":
        d.rounded_rectangle(s(70, 200, 530, 640), radius=150 * S, fill=pelo, outline=TINTA, width=lw)
    elif estilo_pelo == "rizado":
        for cx, cy in ((80, 250), (65, 320), (85, 390), (520, 250), (535, 320), (515, 390)):
            d.ellipse(s(cx - 45, cy - 45, cx + 45, cy + 45), fill=pelo, outline=TINTA, width=lw)

    # --- cabeza con sombreado ---
    caja = (85, 135, 515, 525)
    d.ellipse(s(*caja), fill=_oscurecer(piel, 0.9))
    d.ellipse(s(caja[0] + 4, caja[1] + 2, caja[2] - 28, caja[3] - 26), fill=piel)
    d.ellipse(s(*caja), outline=TINTA, width=lw)
    if cfg.get("mejillas", True):
        for cx in (195, 405):
            rubor = tuple(int(a * 0.55 + b * 0.45) for a, b in zip(piel[:3], (255, 120, 120))) + (255,)
            d.ellipse(s(cx - 32, 395, cx + 32, 425), fill=rubor)

    if estilo_pelo == "largo":  # flequillo
        d.chord(s(88, 138, 512, 430), 188, 352, fill=pelo, outline=TINTA, width=lw)

    # --- ojos ---
    ojos = ((232, 330), (368, 330))
    for i, (ex, ey) in enumerate(ojos):
        if ojos_cerrados:
            d.line(s(ex - 22, ey, ex + 22, ey), fill=TINTA, width=int(8 * S))
        elif expresion == "feliz":
            d.arc(s(ex - 26, ey - 20, ex + 26, ey + 28), 200, 340, fill=TINTA, width=int(9 * S))
        elif expresion == "sorprendido":
            d.ellipse(s(ex - 30, ey - 34, ex + 30, ey + 34), fill=(255, 255, 255, 255), outline=TINTA, width=lw)
            d.ellipse(s(ex - 12, ey - 12, ex + 12, ey + 12), fill=TINTA)
        else:
            d.ellipse(s(ex - 16, ey - 24, ex + 16, ey + 24), fill=TINTA)
            d.ellipse(s(ex - 7, ey - 16, ex + 3, ey - 6), fill=(255, 255, 255, 255))
            if expresion == "sospechoso":
                d.rectangle(s(ex - 22, ey - 30, ex + 22, ey - 2), fill=piel)
                d.line(s(ex - 26, ey - 2, ex + 26, ey - 2), fill=TINTA, width=int(7 * S))

    # --- cejas ---
    cejas = {
        "enojado": ((195, 268, 262, 298), (338, 298, 405, 268)),
        "triste": ((198, 296, 260, 276), (340, 276, 402, 296)),
        "sospechoso": ((198, 284, 262, 284), (338, 266, 402, 276)),
        "sorprendido": ((200, 262, 262, 254), (338, 254, 400, 262)),
    }.get(expresion, ((200, 280, 262, 276), (338, 276, 400, 280)))
    if expresion != "feliz":
        for c in cejas:
            d.line(s(*c), fill=pelo if estilo_pelo != "ninguno" else TINTA, width=int(13 * S))

    # --- gafas ---
    if cfg.get("gafas"):
        for ex, ey in ojos:
            d.ellipse(s(ex - 44, ey - 42, ex + 44, ey + 42), outline=TINTA, width=int(7 * S))
        d.line(s(276, 326, 324, 326), fill=TINTA, width=int(7 * S))

    # --- boca ---
    bigote = cfg.get("bigote", "ninguno")
    by = 470 if bigote != "ninguno" else 430
    if boca:
        if expresion == "feliz":
            d.chord(s(240, by - 40, 360, by + 50), 0, 180, fill=(90, 20, 30, 255), outline=TINTA, width=lw)
            d.rectangle(s(258, by + 4, 342, by + 16), fill=(255, 255, 255, 255))
        else:
            d.ellipse(s(270, by - 22, 330, by + 34), fill=(90, 20, 30, 255), outline=TINTA, width=lw)
            d.ellipse(s(282, by + 8, 318, by + 30), fill=(235, 95, 105, 255))
    else:
        if expresion in ("enojado", "triste"):
            d.arc(s(262, by, 338, by + 40), 200, 340, fill=TINTA, width=int(8 * S))
        elif expresion == "sospechoso":
            d.line(s(270, by + 8, 330, by + 2), fill=TINTA, width=int(8 * S))
        else:
            d.arc(s(262, by - 30, 338, by + 14), 20, 160, fill=TINTA, width=int(8 * S))

    # --- bigote ---
    if bigote == "grueso":
        d.ellipse(s(228, 398, 302, 444), fill=pelo, outline=TINTA, width=int(6 * S))
        d.ellipse(s(298, 398, 372, 444), fill=pelo, outline=TINTA, width=int(6 * S))
    elif bigote == "manubrio":
        d.chord(s(220, 390, 300, 450), 0, 180, fill=pelo, outline=TINTA, width=int(6 * S))
        d.chord(s(300, 390, 380, 450), 0, 180, fill=pelo, outline=TINTA, width=int(6 * S))
        d.arc(s(188, 380, 236, 428), 270, 90, fill=TINTA, width=int(9 * S))
        d.arc(s(364, 380, 412, 428), 90, 270, fill=TINTA, width=int(9 * S))

    # --- sombrero ---
    tipo = cfg.get("sombrero", "ninguno")
    if tipo == "bombin":
        d.chord(s(150, 40, 450, 300), 180, 360, fill=som, outline=TINTA, width=lw)
        d.rectangle(s(156, 150, 444, 172), fill=_oscurecer(som, 0.6))
        d.ellipse(s(96, 158, 504, 222), fill=som, outline=TINTA, width=lw)
    elif tipo == "copa":
        d.rectangle(s(180, 0, 420, 180), fill=som, outline=TINTA, width=lw)
        d.rectangle(s(184, 130, 416, 160), fill=(170, 30, 40, 255))
        d.ellipse(s(110, 160, 490, 222), fill=som, outline=TINTA, width=lw)
    elif tipo == "gorra":
        d.chord(s(112, 70, 488, 330), 180, 360, fill=som, outline=TINTA, width=lw)
        d.ellipse(s(250, 175, 560, 240), fill=_oscurecer(som, 0.7), outline=TINTA, width=lw)
        d.ellipse(s(275, 110, 325, 160), fill=(240, 240, 240, 255), outline=TINTA, width=int(6 * S))
    elif tipo == "casco":
        d.chord(s(78, 50, 522, 360), 180, 360, fill=som, outline=TINTA, width=lw)
        d.ellipse(s(56, 178, 544, 234), fill=_oscurecer(som, 0.8), outline=TINTA, width=lw)
    elif tipo == "boina":
        d.ellipse(s(100, 100, 470, 230), fill=som, outline=TINTA, width=lw)
        d.line(s(290, 100, 300, 76), fill=TINTA, width=int(10 * S))

    # --- gotas de sudor ---
    if cfg.get("sudor"):
        for gx, gy, r in ((120, 300, 22), (490, 260, 26), (455, 400, 18), (160, 200, 16)):
            d.polygon(s(gx - r * 0.9, gy, gx + r * 0.9, gy, gx, gy - r * 2.4), fill=(120, 200, 255, 255))
            d.ellipse(s(gx - r, gy - r, gx + r, gy + r), fill=(120, 200, 255, 255), outline=TINTA, width=int(5 * S))
            d.ellipse(s(gx - r * 0.5, gy - r * 0.5, gx - r * 0.1, gy - r * 0.1), fill=(255, 255, 255, 255))

    im = im.resize((ANCHO, ALTO), Image.LANCZOS)
    if cfg.get("voltear"):
        im = im.transpose(Image.FLIP_LEFT_RIGHT)
    return im


# ======================================================================
# Estilo "fino": cabeza blanca grande, ojos con blanco y pupila, párpados,
# brazos finos, vestido con delantal y objetos en la mano.
#   cuerpo: pantalon | vestido      mirada: -1 (izq) | 0 | 1 (der)
#   pelo:   moño | corto | ninguno   objeto: vaso | ninguno
#   expresiones: normal, picara, preocupado, sorprendido, feliz, enojado, triste
# ======================================================================
def dibujar_fino(cfg, boca=False, ojos_cerrados=False, expresion="normal", brazo="abajo"):
    im = Image.new("RGBA", (ANCHO * S, ALTO * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)

    def s(*v):
        return [int(x * S) for x in v]

    lw = int(7 * S)
    piel = _hex(cfg.get("piel", "#ffffff"))
    ropa = _hex(cfg.get("ropa", "#8fb3d9"))
    pelo = _hex(cfg.get("pelo_color", "#141414"))
    cuerpo = cfg.get("cuerpo", "pantalon")
    mirada = cfg.get("mirada", 0) * 16

    # --- piernas y zapatos ---
    y_cad = 870 if cuerpo == "vestido" else 760
    for x0, x1 in ((262, 248), (338, 352)):
        d.line(s(x0, y_cad, x1, 945), fill=TINTA, width=int(8 * S))
    for x in (232, 368):
        d.ellipse(s(x - 42, 928, x + 42, 966), fill=(20, 20, 22, 255))

    # --- brazos ---
    hi, hd = (215, 545), (385, 545)
    mano_i = {"arriba": (60, 420), "sostiene": (300, 690), "señala": (150, 720)}.get(brazo, (165, 730))
    mano_d = {"sostiene": (515, 500), "señala": (560, 520)}.get(brazo, (435, 730))
    d.line(s(*hi, *mano_i), fill=TINTA, width=int(8 * S))
    d.line(s(*hd, *mano_d), fill=TINTA, width=int(8 * S))

    # --- torso ---
    if cuerpo == "vestido":
        falda = _hex(cfg.get("falda", "#c8735a"))
        d.polygon(s(205, 640, 395, 640, 455, 880, 145, 880), fill=falda, outline=TINTA, width=lw)
        d.rounded_rectangle(s(200, 495, 400, 665), radius=55 * S, fill=ropa, outline=TINTA, width=lw)
        for cx in (200, 400):  # mangas cortas
            d.ellipse(s(cx - 42, 505, cx + 42, 590), fill=ropa, outline=TINTA, width=lw)
        if cfg.get("delantal", True):
            dl = _hex(cfg.get("delantal_color", "#f3e2c2"))
            d.rounded_rectangle(s(232, 545, 368, 640), radius=12 * S, fill=dl, outline=TINTA, width=int(5 * S))
            d.polygon(s(210, 630, 390, 630, 420, 860, 180, 860), fill=dl, outline=TINTA, width=int(5 * S))
            d.line(s(205, 640, 395, 640), fill=TINTA, width=int(5 * S))
            colores = [(214, 120, 96), (110, 160, 190), (230, 170, 80)]
            k = 0
            for yy in range(572, 850, 44):
                for xx in range(200, 420, 44):
                    m = (yy - 630) * 0.13
                    if (yy < 625 and 250 < xx < 350) or (yy > 650 and 222 - m < xx < 378 + m):
                        d.ellipse(s(xx - 9, yy - 9, xx + 9, yy + 9), fill=colores[k % 3] + (255,))
                        k += 1
    else:
        d.rounded_rectangle(s(200, 495, 400, 775), radius=60 * S, fill=ropa, outline=TINTA, width=lw)
        d.line(s(300, 560, 300, 770), fill=TINTA, width=int(4 * S))
        d.polygon(s(258, 497, 342, 497, 300, 560), fill=(250, 250, 250, 255), outline=TINTA, width=int(4 * S))

    # --- pelo detrás (moño) ---
    est_pelo = cfg.get("pelo", "ninguno")
    if est_pelo == "moño":
        d.ellipse(s(450, 230, 560, 340), fill=pelo, outline=TINTA, width=lw)

    # --- cabeza ---
    d.ellipse(s(92, 92, 508, 508), fill=piel)
    if est_pelo in ("moño", "corto"):
        # pelo en una capa recortada con la forma de la cabeza; la frente hace una curva
        capa = Image.new("RGBA", im.size, (0, 0, 0, 0))
        dc = ImageDraw.Draw(capa)
        dc.ellipse(s(92, 92, 508, 508), fill=pelo)
        frente = (60, 205, 540, 700) if est_pelo == "moño" else (50, 185, 550, 700)
        dc.ellipse(s(*frente), fill=piel, outline=TINTA, width=lw)
        if est_pelo == "moño":
            dc.line(s(300, 92, 290, 200), fill=(70, 70, 70, 255), width=int(4 * S))
        mascara = Image.new("L", im.size, 0)
        ImageDraw.Draw(mascara).ellipse(s(92, 92, 508, 508), fill=255)
        im.paste(capa, (0, 0), mascara)
    d.ellipse(s(92, 92, 508, 508), outline=TINTA, width=lw)

    # --- ojos ---
    ojos = ((222, 315), (378, 315))
    for i, (ex, ey) in enumerate(ojos):
        if ojos_cerrados or expresion == "feliz":
            if expresion == "feliz" and not ojos_cerrados:
                d.arc(s(ex - 32, ey - 20, ex + 32, ey + 30), 200, 340, fill=TINTA, width=int(9 * S))
            else:
                d.arc(s(ex - 32, ey - 30, ex + 32, ey + 10), 20, 160, fill=TINTA, width=int(7 * S))
            continue
        rx, ry = (40, 34) if expresion in ("sorprendido", "preocupado") else (38, 30)
        d.ellipse(s(ex - rx, ey - ry, ex + rx, ey + ry), fill=(255, 255, 255, 255), outline=TINTA, width=int(6 * S))
        pr = 11 if expresion in ("sorprendido", "preocupado") else 15
        px = ex + mirada
        d.ellipse(s(px - pr, ey - pr + 4, px + pr, ey + pr + 4), fill=TINTA)
        d.ellipse(s(px - pr * 0.5, ey - pr * 0.4, px - pr * 0.1, ey), fill=(255, 255, 255, 255))
        if expresion in ("picara", "sospechoso"):  # párpado pesado
            d.chord(s(ex - rx - 2, ey - ry - 2, ex + rx + 2, ey + ry + 2), 180, 360, fill=piel)
            d.line(s(ex - rx - 4, ey, ex + rx + 4, ey - 4), fill=TINTA, width=int(8 * S))
        elif expresion == "enojado":
            lado = 1 if i == 0 else -1
            d.polygon(s(ex - rx - 4, ey - ry - 6, ex + rx + 4, ey - ry - 6,
                        ex + lado * rx, ey - (4 if lado == 1 else ry), ex - lado * rx, ey - (ry if lado == 1 else 4)),
                      fill=piel)

    # --- cejas gruesas ---
    cejas = {
        "picara": ((180, 262, 262, 280), (338, 250, 420, 238)),
        "sospechoso": ((180, 262, 262, 280), (338, 250, 420, 238)),
        "enojado": ((182, 252, 262, 282), (338, 282, 418, 252)),
        "preocupado": ((185, 268, 258, 246), (342, 246, 415, 268)),
        "triste": ((185, 270, 258, 250), (342, 250, 415, 270)),
        "sorprendido": ((185, 250, 262, 238), (338, 238, 415, 250)),
        "feliz": ((185, 258, 260, 250), (340, 250, 415, 258)),
    }.get(expresion, ((185, 262, 260, 256), (340, 256, 415, 262)))
    for c in cejas:
        d.line(s(*c), fill=TINTA, width=int(13 * S))

    # --- boca ---
    by = 420
    if boca:
        if expresion == "feliz":
            d.chord(s(240, by - 30, 360, by + 50), 0, 180, fill=(90, 20, 30, 255), outline=TINTA, width=lw)
            d.rectangle(s(258, by + 12, 342, by + 22), fill=(255, 255, 255, 255))
        else:
            d.ellipse(s(272, by - 14, 328, by + 40), fill=(90, 20, 30, 255), outline=TINTA, width=lw)
            d.ellipse(s(284, by + 16, 316, by + 36), fill=(235, 95, 105, 255))
    elif expresion in ("picara", "sospechoso"):
        d.arc(s(235, by - 50, 365, by + 20), 25, 150, fill=TINTA, width=int(7 * S))
        d.line(s(352, by + 8, 372, by - 6), fill=TINTA, width=int(7 * S))
    elif expresion in ("preocupado", "triste", "enojado"):
        d.arc(s(262, by + 4, 338, by + 44), 200, 340, fill=TINTA, width=int(7 * S))
    elif expresion == "sorprendido":
        d.ellipse(s(285, by - 6, 315, by + 30), fill=(90, 20, 30, 255), outline=TINTA, width=lw)
    else:
        d.arc(s(255, by - 40, 345, by + 10), 25, 155, fill=TINTA, width=int(7 * S))

    # --- objeto en la mano ---
    if cfg.get("objeto") == "vaso" and brazo == "sostiene":
        mx, my = mano_d
        d.polygon(s(mx - 40, my - 120, mx + 40, my - 120, mx + 32, my + 10, mx - 32, my + 10),
                  fill=(205, 232, 248, 150), outline=TINTA, width=int(5 * S))
        d.polygon(s(mx - 36, my - 70, mx + 36, my - 70, mx + 32, my + 6, mx - 32, my + 6), fill=(120, 185, 230, 200))
        d.line(s(mx - 24, my - 105, mx - 20, my - 10), fill=(255, 255, 255, 220), width=int(6 * S))

    # --- manos (pequeñas, contorno) ---
    for mx, my in (mano_i, mano_d):
        d.ellipse(s(mx - 22, my - 22, mx + 22, my + 22), fill=(255, 255, 255, 255), outline=TINTA, width=lw)

    im = im.resize((ANCHO, ALTO), Image.LANCZOS)
    if cfg.get("voltear"):
        im = im.transpose(Image.FLIP_LEFT_RIGHT)
    return im
