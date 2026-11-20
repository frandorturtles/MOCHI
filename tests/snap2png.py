#!/usr/bin/env python3
"""Convierte las capturas PPM+textos de ui_snapshot en PNG redondos (mascara de la pantalla GC9A01) con texto real."""
import sys, glob, os
from PIL import Image, ImageDraw, ImageFont
d = sys.argv[1]; out = sys.argv[2]; os.makedirs(out, exist_ok=True)
FONTS = {}
def font(n):
    size = {1: 8, 2: 14, 4: 24, 6: 40}.get(n, 14)
    if size not in FONTS:
        for p in ("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"):
            if os.path.exists(p): FONTS[size] = ImageFont.truetype(p, size); break
        else: FONTS[size] = ImageFont.load_default()
    return FONTS[size]
for ppm in sorted(glob.glob(os.path.join(d, "*.ppm"))):
    im = Image.open(ppm).convert("RGB"); dr = ImageDraw.Draw(im)
    for line in open(ppm[:-4] + ".txt", encoding="utf-8"):
        x, y, f, dat, col, s = line.rstrip("\n").split("|", 5); x, y, f, dat, col = map(int, (x, y, f, dat, col))
        c = ((col >> 8) & 0xF8, (col >> 3) & 0xFC, (col << 3) & 0xF8)
        anchor = {0: "la", 1: "ma", 3: "lm", 4: "mm"}.get(dat, "mm")
        dr.text((x, y), s, font=font(f), fill=c, anchor=anchor)
    big = im.resize((480, 480), Image.NEAREST)
    mask = Image.new("L", (480, 480), 0); ImageDraw.Draw(mask).ellipse((0, 0, 479, 479), fill=255)
    res = Image.new("RGBA", (480, 480), (0, 0, 0, 0)); res.paste(big, (0, 0), mask)
    res.save(os.path.join(out, os.path.basename(ppm)[:-4] + ".png"))
print("PNG listos en", out)
