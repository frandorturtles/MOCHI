#!/usr/bin/env python3
"""Dibuja el diagrama de cableado de MOCHI (modulos ya hechos) a partir de mochi_netlist.json -> hardware/schematics/*.png"""
import os
from PIL import Image, ImageDraw, ImageFont
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUT = os.path.join(ROOT, "hardware/schematics")
def F(sz, bold=True):
    for p in ("/usr/share/fonts/truetype/dejavu/DejaVuSans%s.ttf" % ("-Bold" if bold else ""),):
        if os.path.exists(p): return ImageFont.truetype(p, sz)
    return ImageFont.load_default()
BG, INK = (250, 247, 240), (40, 36, 70)
C = {"pwr": (214, 60, 60), "gnd": (60, 60, 60), "sig": (40, 110, 200), "spi": (30, 150, 110), "btn": (200, 120, 20), "buz": (150, 60, 190)}

def box(d, x, y, w, h, title, sub="", fill=(200, 235, 228)):
    d.rounded_rectangle([x, y, x+w, y+h], 14, fill=fill, outline=INK, width=3)
    d.text((x+w/2, y+22), title, font=F(22), fill=INK, anchor="mm")
    if sub: d.text((x+w/2, y+48), sub, font=F(14, False), fill=INK, anchor="mm")
def pin(d, x, y, label, side, col, dx=0):
    d.ellipse([x-6, y-6, x+6, y+6], fill=col, outline=INK)
    ax = "rm" if side == "L" else "lm"
    d.text((x + (-14 if side == "L" else 14) + dx, y), label, font=F(16), fill=INK, anchor=ax)
def wire(d, pts, col, w=5): d.line(pts, fill=col, width=w, joint="curve")
def junction(d, x, y, col): d.ellipse([x-6, y-6, x+6, y+6], fill=col)

# ------------------------------------------------------------------ 1) GPIO
def gpio():
    im = Image.new("RGB", (1700, 1000), BG); d = ImageDraw.Draw(im)
    d.text((850, 36), "MOCHI - cableado de senales (ESP32-C3 SuperMini)", font=F(32), fill=INK, anchor="mm")
    mx, my, mw, mh = 700, 100, 300, 820
    box(d, mx, my, mw, mh, "ESP32-C3 SuperMini", "USB-C = programacion + carga", fill=(255, 233, 160))
    left = [("5V", "pwr"), ("G", "gnd"), ("3V3", "pwr"), ("IO4", "sig"), ("IO3", "btn"), ("IO2", "sig"), ("IO1", "btn"), ("IO0", "btn")]
    right = [("IO20", "buz"), ("IO21", "sig"), ("IO10", "spi"), ("IO9 (BOOT)", None), ("IO8 (LED)", None), ("IO7", "spi"), ("IO6", "spi"), ("IO5", "spi")]
    ly = {n: 190 + i*90 for i, (n, _) in enumerate(left)}; ry = {n: 190 + i*90 for i, (n, _) in enumerate(right)}
    for n, k in left: pin(d, mx, ly[n], n, "R", C[k]) if False else None
    for n, k in left:
        d.ellipse([mx-6, ly[n]-6, mx+6, ly[n]+6], fill=C[k]); d.text((mx+14, ly[n]), n, font=F(18), fill=INK, anchor="lm")
    for n, k in right:
        col = C[k] if k else (170, 170, 170)
        d.ellipse([mx+mw-6, ry[n]-6, mx+mw+6, ry[n]+6], fill=col); d.text((mx+mw-14, ry[n]), n, font=F(18), fill=col if k else (150, 150, 150), anchor="rm")
    # izquierda: botones, divisor, 3V3/5V/G
    def sw(y, name, net):
        x = 330; d.rounded_rectangle([x, y-24, x+150, y+24], 10, fill=(255, 240, 210), outline=INK, width=3)
        d.text((x+75, y), name, font=F(18), fill=INK, anchor="mm"); wire(d, [(x+150, y), (mx, y)], C["btn"])
        wire(d, [(x, y), (200, y)], C["gnd"]); d.text((190, y), "a GND", font=F(16), fill=INK, anchor="rm")
    sw(ly["IO0"], "Estrella A", "BTN_A"); sw(ly["IO1"], "Estrella B", "BTN_B"); sw(ly["IO3"], "Estrella C", "BTN_C")
    # divisor VBAT
    y = ly["IO2"]; wire(d, [(mx, y), (520, y)], C["sig"]); junction(d, 520, y, C["sig"])
    for dy, name, note, col in ((-40, "R3 100k", "a VBAT (OUT+ del TP4056)", C["pwr"]), (40, "R4 100k", "a GND", C["gnd"])):
        wire(d, [(520, y), (520, y+dy), (400, y+dy)], C["sig"])
        d.rounded_rectangle([250, y+dy-18, 400, y+dy+18], 8, fill=(240, 240, 240), outline=INK, width=3)
        d.text((325, y+dy), name, font=F(17), fill=INK, anchor="mm"); d.text((240, y+dy), note, font=F(15), fill=col, anchor="rm")
    d.text((545, y+60), "(+ C1 100nF a GND, opcional)", font=F(13, False), fill=INK, anchor="lm")
    for n, txt, col in (("5V", "TP4056 IN+  y  D1 (K)", C["pwr"]), ("G", "GND comun", C["gnd"]), ("3V3", "LCD VCC/RST, BZ+, D2 K", C["pwr"])):
        wire(d, [(mx, ly[n]), (230, ly[n])], col); d.text((220, ly[n]), txt, font=F(16), fill=col, anchor="rm")
    y = ly["IO4"]; wire(d, [(mx, y), (480, y)], C["sig"]); d.rounded_rectangle([330, y-24, 480, y+24], 8, fill=(240, 240, 240), outline=INK, width=3); d.text((405, y), "R1 100", font=F(17), fill=INK, anchor="mm")
    wire(d, [(330, y), (200, y)], C["sig"]); d.text((190, y), "-> pantalla BL", font=F(16), fill=C["sig"], anchor="rm")
    # derecha: pantalla
    lx = 1250; box(d, lx, 330, 340, 470, "Pantalla GC9A01", "redonda 1.28in", fill=(215, 205, 245))
    pins = [("SCL", "IO6", "spi"), ("SDA", "IO7", "spi"), ("DC", "IO5", "spi"), ("CS", "IO10", "spi")]
    for i, (pn, io, k) in enumerate(pins):
        yy = 410 + i*60; d.ellipse([lx-6, yy-6, lx+6, yy+6], fill=C[k]); d.text((lx+14, yy), pn, font=F(18), fill=INK, anchor="lm")
        wire(d, [(mx+mw, ry[io]), (1100 + (i*20), ry[io]), (1100 + (i*20), yy), (lx, yy)], C[k])
    for i, (pn, note) in enumerate((("VCC", "a 3V3"), ("RST", "a 3V3"), ("GND", "a GND"), ("BL", "a IO4 via R1"))):
        yy = 650 + i*38; d.ellipse([lx-6, yy-6, lx+6, yy+6], fill=(90, 90, 90)); d.text((lx+14, yy), pn, font=F(18), fill=INK, anchor="lm"); d.text((lx+110, yy), note, font=F(15, False), fill=INK, anchor="lm")
    # buzzer
    y = ry["IO20"]; wire(d, [(mx+mw, y), (1060, y)], C["buz"]); d.rounded_rectangle([1060, y-24, 1210, y+24], 8, fill=(240, 240, 240), outline=INK, width=3); d.text((1135, y), "R2 1k", font=F(17), fill=INK, anchor="mm")
    wire(d, [(1210, y), (1300, y)], C["buz"]); d.polygon([(1300, y-30), (1300, y+30), (1360, y+30), (1360, y-30)], fill=(235, 225, 250), outline=INK)
    d.text((1330, y), "Q1\nBC547", font=F(15), fill=INK, anchor="mm", align="center")
    d.text((1375, y-26), "C -> buzzer (-) y 1N4148 (A)", font=F(14, False), fill=INK, anchor="lm"); d.text((1375, y), "E -> GND   B <- R2", font=F(14, False), fill=INK, anchor="lm")
    d.text((1375, y+26), "buzzer (+) y 1N4148 (K) a 3V3", font=F(14, False), fill=INK, anchor="lm")
    wire(d, [(mx+mw, ry["IO21"]), (1000, ry["IO21"])], C["sig"]); d.text((1010, ry["IO21"]), "IO21 <- CHRG del TP4056 (opcional)", font=F(15), fill=C["sig"], anchor="lm")
    d.text((850, 975), "IO8 (LED) e IO9 (BOOT) no se usan. Todas las lineas de GND van al mismo punto comun.", font=F(15, False), fill=INK, anchor="mm")
    im.save(os.path.join(OUT, "wiring_signals.png"))

# ------------------------------------------------------------------ 2) Potencia
def power():
    im = Image.new("RGB", (1700, 760), BG); d = ImageDraw.Draw(im)
    d.text((850, 34), "MOCHI - cableado de potencia y carga", font=F(32), fill=INK, anchor="mm")
    box(d, 80, 230, 260, 230, "LiPo 3.7 V", "~300 mAh (503035)", fill=(225, 225, 235))
    box(d, 520, 130, 420, 450, "Modulo TP4056", "con proteccion (DW01 + 8205)", fill=(200, 235, 228))
    box(d, 1250, 120, 330, 520, "ESP32-C3 SuperMini", "(solo pines de potencia)", fill=(255, 233, 160))
    # bateria -> B+ / B-
    for yy, lab, col in ((300, "+ (rojo)", C["pwr"]), (400, "- (negro)", C["gnd"])):
        d.ellipse([334, yy-6, 346, yy+6], fill=col); d.text((322, yy), lab, font=F(16), fill=INK, anchor="rm")
    wire(d, [(340, 300), (520, 300)], C["pwr"]); wire(d, [(340, 400), (520, 400)], C["gnd"])
    d.text((530, 300), "B+", font=F(20), fill=INK, anchor="lm"); d.text((530, 400), "B-", font=F(20), fill=INK, anchor="lm")
    d.text((940-14, 200), "IN+  <- 5V del SuperMini", font=F(18), fill=INK, anchor="rm"); d.text((940-14, 260), "IN-  <- GND", font=F(18), fill=INK, anchor="rm")
    wire(d, [(940, 200), (1250, 200)], C["pwr"]); d.text((1010, 180), "VBUS 5 V (USB del SuperMini)", font=F(15, False), fill=C["pwr"], anchor="lm")
    wire(d, [(940, 260), (1100, 260), (1100, 600), (1250, 600)], C["gnd"]); d.text((1250+14, 600), "G", font=F(18), fill=INK, anchor="lm")
    d.text((940-14, 470), "OUT+ -> anodo 1N5819", font=F(18), fill=INK, anchor="rm"); d.text((940-14, 530), "OUT- -> GND", font=F(18), fill=INK, anchor="rm")
    wire(d, [(940, 530), (1100, 530)], C["gnd"])
    # diodo
    wire(d, [(940, 470), (1010, 470)], C["pwr"]); d.polygon([(1010, 440), (1010, 500), (1070, 470)], fill=(245, 200, 200), outline=INK); d.line([(1075, 440), (1075, 500)], fill=INK, width=5)
    wire(d, [(1075, 470), (1150, 470), (1150, 200)], C["pwr"]); junction(d, 1150, 200, C["pwr"])
    d.text((1040, 418), "D1 1N5819 (franja = K hacia 5V)", font=F(15), fill=INK, anchor="mm")
    d.text((1250+14, 200), "5V", font=F(18), fill=INK, anchor="lm")
    d.text((700, 650), "Pasos: 1) cambiar R_PROG del TP4056 a 10k (120 mA)  2) NO conectar su USB propio  3) la bateria se carga por el USB-C del SuperMini", font=F(16, False), fill=INK, anchor="mm")
    d.text((700, 690), "Tambien: OUT+ -> R3 (divisor 100k/100k) -> IO2.   ATENCION: verifica polaridad del conector de la bateria con multimetro.", font=F(16), fill=C["pwr"], anchor="mm")
    im.save(os.path.join(OUT, "wiring_power.png"))

if __name__ == "__main__": gpio(); power(); print("diagramas escritos en", OUT)
