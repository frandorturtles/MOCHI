#!/usr/bin/env python3
"""Verificacion geometrica de MOCHI rev B (modulos ya hechos): lee 3d-models/source/params.scad (la misma fuente que
usan OpenSCAD y gen_stl.py) y comprueba que bateria, buzzer, SuperMini, TP4056, pantalla, botones y tornillos caben
sin colisionar.  Usa medidas PROVISIONALES: repetir con las reales (docs/manufacturing/measure_checklist.md)."""
import re, math, os, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
src = open(os.path.join(ROOT, "3d-models/source/params.scad"), encoding="utf-8").read()
P = {"true": True, "false": False}
for line in src.splitlines():
    line = line.split("//")[0].strip()
    m = re.match(r"^(\w+)\s*=\s*(.+);$", line)
    if m: P[m.group(1)] = eval(m.group(2), {"__builtins__": {}}, dict(P))
g = type("P", (), P)
fails = 0
def check(cond, msg, detail=""):
    global fails
    print(("  [ok]    " if cond else "  [FALLO] ") + msg + (f"   ({detail})" if detail else ""))
    if not cond: fails += 1

R = g.fillet - g.wall
def inset(z, h, r):
    if z < r: return r - math.sqrt(max(0, r*r - (r - z)**2))
    if z > h - r: return r - math.sqrt(max(0, r*r - (z - (h - r))**2))
    return 0.0
def cav(z):
    zz = z - g.wall; h = g.body_h - 2*g.wall
    ins = inset(min(max(zz, 0), h), h, R) if R > 0 else 0
    return ((g.body_w - 2*g.wall)/2 - ins, (g.body_l - 2*g.wall)/2 - ins)
def inside(x, y, ax, margin=0.0): return (x/(ax[0]-margin))**2 + (y/(ax[1]-margin))**2 <= 1.0
def box_corners(x0, y0, dx, dy): return [(x0, y0), (x0+dx, y0), (x0, y0+dy), (x0+dx, y0+dy)]
def overlap(a, b):  # cajas (x0,y0,x1,y1,z0,z1)
    return all(a[i] < b[i+2] and b[i] < a[i+2] for i in (0, 1)) and a[4] < b[5] and b[4] < a[5]

def plate_outline(n=24):
    pts = []; hw, hl, r = g.pcb_w/2, g.pcb_l/2, g.pcb_r
    for cx, cy, a0 in ((hw-r, hl-r, 0), (-hw+r, hl-r, 90), (-hw+r, -hl+r, 180), (hw-r, -hl+r, 270)):
        for i in range(n+1):
            a = math.radians(a0 + 90*i/n); pts.append((cx + r*math.cos(a), cy + r*math.sin(a)))
    return pts

print("== Pila vertical (Z) ==")
batt_top = g.batt_z0 + g.batt_t + g.batt_clear
check(batt_top <= g.pcb_z0 - 0.3, "bateria + holgura bajo la placa (deja sitio a patas soldadas)", f"{batt_top:.1f} <= {g.pcb_z0-0.3:.1f}")
check(g.batt_z0 + g.bz_h + 0.3 <= g.pcb_z0, "buzzer bajo la placa", f"{g.batt_z0+g.bz_h:.1f}")
tall = max(g.mcu_h, g.tp_h)
check(tall + 0.5 <= g.disp_gap, "modulos bajo la pantalla (holgura 0.5)", f"{tall}+0.5 <= {g.disp_gap}")
disp_bot = g.plate_top + g.disp_gap; disp_top = disp_bot + g.disp_t
check(disp_top + 0.4 <= g.ceiling_z, "pantalla bajo el techo (>=0.4 mm para espuma)", f"{disp_top:.1f}+0.4 <= {g.ceiling_z:.1f}")
check(g.usb_z - g.usb_h/2 >= g.mcu_z0 and g.usb_z + g.usb_h/2 <= g.split_z, "abertura USB completa dentro de la base", f"{g.usb_z-g.usb_h/2:.1f}..{g.usb_z+g.usb_h/2:.1f} (union en {g.split_z})")
check(g.usb_w >= 8.94 + 0.3 and g.usb_h >= g.usbc_h + 0.2, "abertura USB >= conector USB-C + holgura")
check(g.mcu_dy/2 >= g.usb_w/2 - 0.5, "la abertura queda centrada en el SuperMini")
check(g.wall >= 1.6, "pared >= 1.6 mm")
check(g.stem_len > 0.5, "vastago del boton con longitud util", f"{g.stem_len:.1f} mm")

print("== Planta (XY) ==")
pts = plate_outline(); ax = cav(g.pcb_z0); axt = cav(g.plate_top + g.tp_h)
check(all(inside(x, y, ax) and inside(x, y, axt) for x, y in pts), "placa soporte dentro de la cavidad")
axb = cav(g.batt_z0)
bc = box_corners(-g.batt_w/2 - g.batt_clear, -g.batt_l/2, g.batt_w + 2*g.batt_clear, g.batt_l)
check(all(inside(x, y, axb) for x, y in bc), "bateria (con topes) dentro de la cavidad al nivel del suelo")
bz = [(g.bz_x + g.bz_d/2*math.cos(math.radians(a)) + 0, g.bz_y + g.bz_d/2*math.sin(math.radians(a))) for a in range(0, 360, 15)]
bzn = [(g.bz_x + (g.bz_d/2+1.2)*math.cos(math.radians(a)), g.bz_y + (g.bz_d/2+1.2)*math.sin(math.radians(a))) for a in range(0, 360, 15)]
check(all(inside(x, y, axb) for x, y in bzn), "buzzer con su nido dentro de la cavidad al nivel del suelo")
check(g.bz_x - g.bz_d/2 - 1.2 >= g.batt_w/2 + g.batt_clear, "buzzer no choca con la bateria", f"{g.bz_x-g.bz_d/2-1.2:.1f} >= {g.batt_w/2+g.batt_clear:.1f}")
flat_bottom = (g.body_w/2 - g.fillet, g.body_l/2 - g.fillet)
check(all(inside(g.bz_x + 0.6*math.cos(math.radians(a)), g.bz_y + 2*2.2*math.sin(math.radians(a)), flat_bottom) for a in range(0, 360, 45)), "orificios de sonido sobre el fondo plano")

mcu_box = (g.mcu_x0, g.mcu_y - g.mcu_dy/2, g.mcu_x0 + g.mcu_dx, g.mcu_y + g.mcu_dy/2, g.mcu_z0, g.mcu_z0 + g.mcu_h)
tp_box  = (g.tp_x0, g.tp_y0, g.tp_x0 + g.tp_dx, g.tp_y0 + g.tp_dy, g.plate_top, g.plate_top + g.tp_h)
axm = cav(g.mcu_z0 + g.mcu_h); axtp = cav(g.plate_top + g.tp_h)
check(all(inside(x, y, axm) for x, y in box_corners(mcu_box[0], mcu_box[1], g.mcu_dx, g.mcu_dy)), "SuperMini dentro de la cavidad (USB junto a la pared)")
check(all(inside(x, y, axtp) for x, y in box_corners(*tp_box[:2], g.tp_dx, g.tp_dy)), "TP4056 dentro de la cavidad")
check(not overlap(mcu_box, tp_box), "SuperMini y TP4056 no se solapan", f"holgura X {tp_box[0]-mcu_box[2]:.1f} mm")
on_plate = lambda x, y: inside(x, y, (g.pcb_w/2, g.pcb_l/2)) or (abs(x) <= g.pcb_w/2 and abs(y) <= g.pcb_l/2)
tp_over = max(0, tp_box[2] - g.pcb_w/2); mcu_over = max(0, -g.pcb_w/2 - mcu_box[0])
print(f"          voladizos fuera de la placa: TP4056 {tp_over:.1f} mm (apoyado en la placa), SuperMini {mcu_over:.1f} mm (apoyado en la repisa de la base)")
check(tp_over <= 4 and mcu_over <= 6, "voladizos aceptables (<= 4 / 6 mm)")
ledge = (-g.body_w/2, g.mcu_y - g.mcu_dy/2, -21, g.mcu_y + g.mcu_dy/2)
check(ledge[2] >= -g.pcb_w/2 and ledge[0] <= mcu_box[0], "la repisa de la base soporta el extremo USB del SuperMini")

dc = (0, g.disp_cy); rd = g.disp_d/2 + g.disp_clear; axd = cav(disp_bot)
check(all(inside(dc[0]+(rd+g.cage_w)*math.cos(math.radians(a)), dc[1]+(rd+g.cage_w)*math.sin(math.radians(a)), axd) for a in range(0, 360, 5)), "pantalla + lenguetas dentro de la cavidad")
top_flat = (g.body_w/2 - g.fillet, g.body_l/2 - g.fillet)
check(all(inside(dc[0]+g.bezel_od/2*math.cos(math.radians(a)), dc[1]+g.bezel_od/2*math.sin(math.radians(a)), top_flat) for a in range(0, 360, 5)), "aro del bisel sobre la zona plana del techo")
for p in g.screw_pts:
    d = math.hypot(p[0]-dc[0], p[1]-dc[1]) - g.col_od/2 - rd
    check(d >= 1.0, f"columna de tornillo {p} libre de la pantalla", f"{d:.2f} mm")
    check(inside(p[0], p[1], cav(g.ceiling_z - 0.5)), f"columna {p} dentro de la cavidad bajo el techo")
    col = (p[0]-g.col_od/2, p[1]-g.col_od/2, p[0]+g.col_od/2, p[1]+g.col_od/2, g.wall, g.split_z)
    for nm, bx in (("SuperMini", mcu_box), ("TP4056", tp_box)):
        check(not overlap(col, bx), f"columna {p} no toca {nm}")
for p in g.btn_pos:
    star = [(p[0]+(g.star_R+g.btn_clear)*math.cos(math.radians(90+72*k)), p[1]+(g.star_R+g.btn_clear)*math.sin(math.radians(90+72*k))) for k in range(5)]
    check(all(inside(x, y, top_flat) for x, y in star), f"boton estrella {p} sobre la zona plana del techo")
    d = math.hypot(p[0]-dc[0], p[1]-dc[1]) - (g.star_R+1.2) - rd
    check(d >= 1.5, f"brida del boton {p} libre de la pantalla", f"{d:.1f} mm")
    sw = (p[0]-g.sw_w/2, p[1]-g.sw_w/2, p[0]+g.sw_w/2, p[1]+g.sw_w/2, g.plate_top, g.plate_top + g.sw_h)
    check(all(abs(x) <= g.pcb_w/2 and abs(y) <= g.pcb_l/2 for x, y in box_corners(sw[0], sw[1], g.sw_w, g.sw_w)) and all(inside(x, y, (g.pcb_w/2, g.pcb_l/2)) or True for x, y in []), f"pulsador bajo {p} cabe en la placa")
    check(not overlap(sw, mcu_box) and not overlap(sw, tp_box), f"pulsador {p} no choca con los modulos")
    # que el contorno redondeado de la placa lo contenga
    check(all(any(math.hypot(x-cx, y-cy) <= g.pcb_r or (abs(x) <= g.pcb_w/2-g.pcb_r) or (abs(y) <= g.pcb_l/2-g.pcb_r) for cx, cy in ((math.copysign(g.pcb_w/2-g.pcb_r, x), math.copysign(g.pcb_l/2-g.pcb_r, y)),)) for x, y in box_corners(sw[0], sw[1], g.sw_w, g.sw_w)), f"pulsador {p} dentro del contorno redondeado")
for i in range(3):
    for j in range(i+1, 3):
        a, b = g.btn_pos[i], g.btn_pos[j]
        check(math.hypot(a[0]-b[0], a[1]-b[1]) >= 2*(g.star_R+1.2)+0.5, f"bridas de botones {i}-{j} no se tocan")

print("== Tornillos M2 ==")
tip = g.head_h + g.screw_len; pilot_start = g.split_z - 0.5; pilot_end = pilot_start + g.pilot_depth
check(tip <= pilot_end - 0.3, "punta del tornillo no llega al fondo del piloto", f"punta z={tip:.1f}, piloto hasta {pilot_end:.1f}")
check(tip - pilot_start >= 2.5, "enganche >= 2.5 mm", f"{tip-pilot_start:.1f} mm")
check(pilot_end <= g.body_h - 1.0, "el piloto no atraviesa la cara superior (queda >= 1 mm)", f"{pilot_end:.1f} <= {g.body_h-1.0:.1f}")
print("\nRESULTADO:", "TODO OK" if fails == 0 else f"{fails} FALLO(S)"); sys.exit(1 if fails else 0)
