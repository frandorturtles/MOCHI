#!/usr/bin/env python3
"""Genera los sprites pixel-art originales de MOCHI de forma procedural.

Salidas:
  assets/sprites/*.png        hojas de sprites ampliadas (para revisar y para el README)
  assets/icons/*.png          iconos 16x16 ampliados
  firmware/src/sprites.h      datos indexados (paleta de 16 colores RGB565) para el firmware

Uso:  python3 firmware/tools/gen_sprites.py      (requiere Pillow)
"""
import math, os
from PIL import Image, ImageDraw

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
W = H = 32

PAL = [  # indice 0 = transparente
    None,        # 0
    "#3b3b73",   # 1 contorno
    "#8fe3d0",   # 2 cuerpo
    "#6fc3b8",   # 3 sombra
    "#c8f4ec",   # 4 brillo
    "#ff9fb5",   # 5 mejillas
    "#ffffff",   # 6 blanco ojos
    "#ffe98a",   # 7 estrella
    "#f2c94c",   # 8 sombra estrella
    "#fdfdf5",   # 9 ala
    "#d9d6e8",   # 10 sombra ala
    "#c9b8f0",   # 11 lavanda
    "#e0607e",   # 12 boca
    "#7a5cc0",   # 13 morado
    "#ffb26b",   # 14 naranja
    "#7fc4ff",   # 15 azul lagrima
]
def rgb(h): h = h.lstrip("#"); return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))
def rgb565(h): r, g, b = rgb(h); return ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)

class Canvas:
    def __init__(self, w=W, h=H): self.w, self.h = w, h; self.p = [[0]*w for _ in range(h)]
    def set(self, x, y, c):
        x, y = int(x), int(y)
        if 0 <= x < self.w and 0 <= y < self.h: self.p[y][x] = c
    def get(self, x, y): return self.p[y][x] if 0 <= x < self.w and 0 <= y < self.h else 0
    def ellipse(self, cx, cy, rx, ry, c):
        for y in range(self.h):
            for x in range(self.w):
                if ((x-cx)/rx)**2 + ((y-cy)/ry)**2 <= 1.0: self.p[y][x] = c
    def outline(self, c=1):
        out = [row[:] for row in self.p]
        for y in range(self.h):
            for x in range(self.w):
                if self.p[y][x] == 0 and any(self.get(x+dx, y+dy) not in (0, c) for dx, dy in ((1,0),(-1,0),(0,1),(0,-1))):
                    out[y][x] = c
        self.p = out
    def star(self, cx, cy, r, c, c2=None):
        pts = [(cx + (r if i % 2 == 0 else r*0.45) * math.sin(i*math.pi/5),
                cy - (r if i % 2 == 0 else r*0.45) * math.cos(i*math.pi/5)) for i in range(10)]
        im = Image.new("P", (self.w, self.h), 0); ImageDraw.Draw(im).polygon(pts, fill=1)
        for y in range(self.h):
            for x in range(self.w):
                if im.getpixel((x, y)): self.set(x, y, c)
    def image(self):
        im = Image.new("RGBA", (self.w, self.h), (0, 0, 0, 0))
        for y in range(self.h):
            for x in range(self.w):
                i = self.p[y][x]
                if i: im.putpixel((x, y), rgb(PAL[i]) + (255,))
        return im

# (rx, ry, cy) por etapa
BODY = {"baby": (7, 6, 20), "child": (9, 8, 18), "teen": (10, 9, 18), "adult": (11, 10, 17)}

def wing(c, cx, cy, side, size):
    """Ala tipo nube (como la de la referencia): dos lobulos + rizo, sale del borde del cuerpo."""
    ex, ey = cx + side * size * 0.5, cy - size * 0.6
    c.ellipse(ex, ey, size * 1.0, size * 0.75, 9)
    c.ellipse(ex + side * size * 0.45, ey + size * 0.55, size * 0.8, size * 0.5, 9)
    for y in range(c.h):
        for x in range(c.w):
            if c.p[y][x] == 9 and y >= ey + size * 0.55: c.p[y][x] = 10
    c.set(ex + side * size * 0.3, ey - size * 0.1, 10)

def draw_pet(stage, form, mood):
    c = Canvas(); rx, ry, cy = BODY[stage]; cx = 16
    if stage == "teen" or (stage == "adult" and form == "angel"): rx -= 2   # deja sitio a las alas
    if stage == "teen":  wing(c, cx - rx, cy, -1, 4); wing(c, cx + rx, cy, 1, 4)
    if stage == "adult" and form == "angel": wing(c, cx - rx, cy, -1, 5); wing(c, cx + rx, cy, 1, 5)
    for y in range(c.h):
        for x in range(c.w):
            if ((x-cx)/rx)**2 + ((y-cy)/ry)**2 <= 1.0: c.p[y][x] = 2
    # sombra inferior y brillo
    for y in range(c.h):
        for x in range(c.w):
            if c.p[y][x] == 2 and y > cy + ry*0.45: c.p[y][x] = 3
    for dx, dy in ((-rx*0.5, -ry*0.55), (-rx*0.3, -ry*0.7), (-rx*0.55, -ry*0.3)):
        c.set(cx + dx, cy + dy, 4)
    # extras por forma/etapa (detras del contorno)
    if stage == "child": c.star(cx, cy - ry - 1, 3, 7)
    if stage == "adult":
        if form == "star":  c.star(cx, cy - ry - 1, 4, 7)
        if form == "dreamer":
            for i in range(5): c.ellipse(cx - 2 + i//2, cy - ry - 1 - i, max(1, 5 - i)*0.9, 0.7, 13)
            c.set(cx + 3, cy - ry - 6, 7)
    c.outline(1)
    if stage == "child": c.star(cx, cy - ry - 1, 3, 7)
    # cara
    ex = max(2, int(rx * 0.45)); ey = cy - max(1, int(ry * 0.15))
    L, R = cx - ex - 1, cx + ex
    def eyes_open():
        for x in (L, R):
            c.set(x, ey, 1); c.set(x, ey + 1, 1); c.set(x + 1, ey, 1); c.set(x + 1, ey + 1, 1); c.set(x, ey - 1, 1); c.set(x + 1, ey - 1, 1)
            c.set(x, ey - 1, 6)
    def eyes_happy():
        for x in (L, R): c.set(x - 1, ey + 1, 1); c.set(x, ey, 1); c.set(x + 1, ey, 1); c.set(x + 2, ey + 1, 1)
    def eyes_closed():
        for x in (L, R): c.set(x - 1, ey, 1); c.set(x, ey + 1, 1); c.set(x + 1, ey + 1, 1); c.set(x + 2, ey, 1)
    def eyes_tired():
        for x in (L, R):
            for k in range(-1, 3): c.set(x + k, ey, 1)
        c.set(L + 1, ey - 1, 13); c.set(R + 1, ey - 1, 13)
    def eyes_x():
        for x in (L, R):
            for k in range(3): c.set(x - 1 + k, ey - 1 + k, 1); c.set(x + 1 - k, ey - 1 + k, 1)
    my = ey + 3 + (1 if stage in ("adult", "teen") else 0)
    if mood in ("neutral", "hungry"): eyes_open()
    elif mood in ("happy", "eating"): eyes_happy()
    elif mood == "sad": eyes_open(); c.set(L - 1, ey - 2, 1); c.set(L, ey - 2, 1); c.set(R + 1, ey - 2, 1); c.set(R + 2, ey - 2, 1); c.set(L, ey + 2, 15); c.set(L, ey + 3, 15)
    elif mood == "tired": eyes_tired()
    elif mood == "sleeping": eyes_closed()
    elif mood == "sick": eyes_x(); c.set(R + 3, ey + 2, 15); c.set(R + 3, ey + 3, 15)
    # boca y mejillas
    if mood in ("neutral",): c.set(cx - 1, my, 1); c.set(cx, my + 1, 1); c.set(cx + 1, my, 1)
    if mood == "happy":
        for k in range(-1, 2): c.set(cx + k, my, 1)
        c.set(cx, my + 1, 12)
    if mood == "hungry": c.set(cx, my, 1); c.set(cx - 1, my + 1, 1); c.set(cx + 1, my + 1, 1); c.set(cx, my + 1, 12); c.set(cx, my + 2, 1)
    if mood == "sad": c.set(cx - 1, my + 1, 1); c.set(cx, my, 1); c.set(cx + 1, my + 1, 1)
    if mood == "tired": c.set(cx, my, 1); c.set(cx + 1, my, 1)
    if mood == "sleeping": c.set(cx, my, 1); c.set(cx + 1, my, 1); c.set(cx + 8 if rx < 10 else cx + 9, cy - ry - 2, 13); c.set(cx + 9 if rx < 10 else cx + 10, cy - ry - 4, 13)
    if mood == "eating":
        for k in range(-1, 2): c.set(cx + k, my, 12); c.set(cx + k, my + 1, 12)
        c.set(cx, my + 2, 12); c.set(cx + 4, my + 3, 14); c.set(cx - 5, my + 2, 14)
    if mood == "sick": c.set(cx - 1, my + 1, 1); c.set(cx, my, 1); c.set(cx + 1, my + 1, 1)
    if mood not in ("sick", "tired", "sleeping"):
        c.set(L - 2, ey + 3, 5); c.set(L - 1, ey + 3, 5); c.set(R + 2, ey + 3, 5); c.set(R + 3, ey + 3, 5)
    return c

def draw_egg(frame):
    c = Canvas(); cx, cy = 16, 18
    c.ellipse(cx, cy, 9, 11, 9)
    for y in range(c.h):
        for x in range(c.w):
            if c.p[y][x] == 9 and (x - cx) + (y - cy) > 6: c.p[y][x] = 10
    for (x, y, col) in ((13, 13, 11), (14, 13, 11), (19, 17, 2), (20, 17, 2), (15, 22, 7), (16, 22, 7), (13, 18, 5), (12, 18, 5)):
        c.set(x, y, col)
    c.set(16, 8, 4); c.set(15, 9, 4)
    if frame: c.set(11, 12, 4); c.set(12, 11, 4)
    c.outline(1)
    return c

def icon(name):
    im = Image.new("P", (16, 16), 0); d = ImageDraw.Draw(im)
    if name == "food":   d.polygon([(8, 2), (14, 13), (2, 13)], fill=9); d.rectangle([3, 9, 13, 13], fill=1); d.rectangle([5, 10, 11, 12], fill=6)
    elif name == "heart": d.polygon([(8, 14), (1, 7), (1, 4), (3, 2), (6, 2), (8, 4), (10, 2), (13, 2), (15, 4), (15, 7)], fill=12)
    elif name == "bolt":  d.polygon([(9, 1), (3, 9), (7, 9), (6, 15), (13, 6), (9, 6)], fill=7)
    elif name == "moon":  d.ellipse([2, 2, 14, 14], fill=11); d.ellipse([6, 0, 17, 11], fill=0)
    elif name == "game":  d.rounded_rectangle([1, 4, 14, 12], 3, fill=13); d.rectangle([3, 7, 7, 8], fill=6); d.rectangle([5, 5, 5, 10], fill=6); d.ellipse([10, 6, 11, 7], fill=14); d.ellipse([12, 8, 13, 9], fill=7)
    elif name == "clock": d.ellipse([1, 1, 14, 14], fill=6, outline=1); d.line([8, 8, 8, 4], fill=1); d.line([8, 8, 11, 9], fill=1)
    elif name == "gear":  d.ellipse([3, 3, 12, 12], fill=11, outline=13); d.ellipse([6, 6, 9, 9], fill=0); [d.rectangle(r, fill=13) for r in ([7, 0, 8, 2], [7, 13, 8, 15], [0, 7, 2, 8], [13, 7, 15, 8])]
    elif name == "pill":  d.rounded_rectangle([1, 5, 14, 10], 2, fill=6, outline=1); d.rectangle([8, 6, 13, 9], fill=5)
    elif name == "star":  c = Canvas(16, 16); c.star(8, 8.5, 7, 7); c.outline(8); return c
    elif name == "check": d.line([3, 8, 6, 12], fill=1, width=2); d.line([6, 12, 13, 3], fill=1, width=2)
    c = Canvas(16, 16)
    for y in range(16):
        for x in range(16):
            v = im.getpixel((x, y)); c.p[y][x] = v
    return c

MOODS = ["neutral", "happy", "hungry", "sad", "tired", "sleeping", "eating", "sick"]
SPRITES = [("baby", "none"), ("child", "none"), ("teen", "none"), ("adult", "angel"), ("adult", "star"), ("adult", "dreamer")]
ICONS = ["food", "heart", "bolt", "moon", "game", "clock", "gear", "pill", "star", "check"]

def sheet(canvases, cols, scale, path, bg="#2b2350"):
    rows = (len(canvases) + cols - 1) // cols
    cw = canvases[0].w; ch = canvases[0].h
    im = Image.new("RGB", (cols*cw*scale, rows*ch*scale), rgb(bg))
    for i, cv in enumerate(canvases):
        s = cv.image().resize((cw*scale, ch*scale), Image.NEAREST)
        im.paste(s, ((i % cols)*cw*scale, (i // cols)*ch*scale), s)
    im.save(path)

def c_array(name, cv):
    flat = [v for row in cv.p for v in row]
    body = ",".join(str(v) for v in flat)
    return f"static const uint8_t {name}[{cv.w*cv.h}] PROGMEM_IF = {{{body}}};\n"

def main():
    os.makedirs(os.path.join(ROOT, "assets/sprites"), exist_ok=True); os.makedirs(os.path.join(ROOT, "assets/icons"), exist_ok=True)
    out = ["// GENERADO por firmware/tools/gen_sprites.py - no editar a mano.\n#pragma once\n#include <stdint.h>\n",
           "#ifdef ARDUINO\n#include <pgmspace.h>\n#define PROGMEM_IF PROGMEM\n#else\n#define PROGMEM_IF\n#endif\n\nnamespace mochi {\n",
           f"constexpr int kSpriteW = {W}, kSpriteH = {H}, kIconW = 16, kIconH = 16;\n",
           "// Paleta de 16 entradas RGB565; indice 0 = transparente.\nstatic const uint16_t kPalette[16] PROGMEM_IF = {" + ",".join("0x%04X" % (0 if h is None else rgb565(h)) for h in PAL) + "};\n"]
    all_pets = []; names = {}
    for si, (stage, form) in enumerate(SPRITES):
        row = []
        for mi, mood in enumerate(MOODS):
            cv = draw_pet(stage, form, mood); row.append(cv)
            nm = f"pet_{si}_{mi}"; out.append(c_array(nm, cv)); names[(si, mi)] = nm
        all_pets += row
        sheet(row, 8, 6, os.path.join(ROOT, f"assets/sprites/pet_{stage}{'_'+form if form!='none' else ''}.png"))
    eggs = [draw_egg(0), draw_egg(1)]
    for i, e in enumerate(eggs): out.append(c_array(f"egg_{i}", e))
    sheet(eggs, 2, 8, os.path.join(ROOT, "assets/sprites/egg.png"))
    sheet(all_pets, 8, 3, os.path.join(ROOT, "assets/sprites/ALL_pets_preview.png"))
    ics = [icon(n) for n in ICONS]
    for n, cv in zip(ICONS, ics): out.append(c_array(f"icon_{n}", cv))
    sheet(ics, 10, 6, os.path.join(ROOT, "assets/icons/icons.png"))
    # tablas de acceso: [sprite(0..5)][mood(0..7)]
    out.append("static const uint8_t* const kPetSprites[6][8] = {\n" + ",\n".join("  {" + ",".join(names[(s, m)] for m in range(8)) + "}" for s in range(6)) + "\n};\n")
    out.append("static const uint8_t* const kEggSprites[2] = {egg_0, egg_1};\n")
    out.append("enum IconId { ICON_FOOD, ICON_HEART, ICON_BOLT, ICON_MOON, ICON_GAME, ICON_CLOCK, ICON_GEAR, ICON_PILL, ICON_STAR, ICON_CHECK };\n")
    out.append("static const uint8_t* const kIcons[10] = {" + ",".join(f"icon_{n}" for n in ICONS) + "};\n}  // namespace mochi\n")
    with open(os.path.join(ROOT, "firmware/src/sprites.h"), "w") as f: f.write("".join(out))
    print("OK:", len(all_pets), "sprites de mascota,", len(eggs), "huevos,", len(ics), "iconos")

if __name__ == "__main__": main()
