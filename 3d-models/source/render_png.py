#!/usr/bin/env python3
"""Renders de MOCHI sin OpenSCAD: genera mallas gruesas con gen_stl.py y las dibuja con un rasterizador propio (painter's algorithm).
Salida: ../renders/*.png.  Uso: python3 render_png.py [--res 0.9]"""
import os, sys, math, argparse, numpy as np
from PIL import Image, ImageDraw
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gen_stl as G
g = G.g
OUT = os.path.join(G.HERE, "..", "renders")

# piezas extra solo para render (decoracion por separado para colorearla)
G.PARTS["lid_plain"] = (lambda X, Y, Z: G.part_lid(X, Y, Z, decor=False), G.PARTS["lid"][1], 1.0)
G.PARTS["d_star"] = (G.decor_star, G.PARTS["lid"][1], 0.5)
G.PARTS["d_loop"] = (G.decor_loop, G.PARTS["lid"][1], 0.5)
G.PARTS["d_wings"] = (lambda X, Y, Z: G.U(G.wing(X, Y, Z, 0), G.wing(X, Y, Z, 1)), G.PARTS["lid"][1], 0.5)

def box_mesh(x0, y0, z0, dx, dy, dz):
    v = np.array([[x0+a*dx, y0+b*dy, z0+c*dz] for c in (0,1) for b in (0,1) for a in (0,1)], float)
    f = [(0,2,1),(1,2,3),(4,5,6),(5,7,6),(0,1,4),(1,5,4),(2,6,3),(3,6,7),(0,4,2),(2,4,6),(1,3,5),(3,7,5)]
    return np.array([[v[i] for i in t] for t in f])
def cyl_mesh(cx, cy, z0, d, h, n=40):
    T = []; r = d/2
    for i in range(n):
        a, b = 2*math.pi*i/n, 2*math.pi*(i+1)/n; p = [(cx+r*math.cos(a), cy+r*math.sin(a)), (cx+r*math.cos(b), cy+r*math.sin(b))]
        T += [[(*p[0], z0), (*p[1], z0), (*p[1], z0+h)], [(*p[0], z0), (*p[1], z0+h), (*p[0], z0+h)],
              [(cx, cy, z0+h), (*p[0], z0+h), (*p[1], z0+h)], [(cx, cy, z0), (*p[1], z0), (*p[0], z0)]]
    return np.array(T, float)
def shift(T, dx, dy, dz): return T + np.array([dx, dy, dz])

def render(items, az, el, path, size=(1400, 1100), scale=None):
    S = 2; W, H = size[0]*S, size[1]*S
    az_r, el_r = math.radians(az), math.radians(el)
    ca, sa, ce, se = math.cos(az_r), math.sin(az_r), math.cos(el_r), math.sin(el_r)
    allx = []; polys = []
    for T, col in items:
        T = np.asarray(T, float); x1 = ca*T[...,0] - sa*T[...,1]; y1 = sa*T[...,0] + ca*T[...,1]; z1 = T[...,2]
        xs, ys, dp = x1, y1*se + z1*ce, -y1*ce + z1*se
        P = np.stack([xs, ys, dp], -1)
        a = P[:,1] - P[:,0]; b = P[:,2] - P[:,0]; n = np.cross(a, b); nn = np.linalg.norm(n, axis=1, keepdims=True) + 1e-12; n = n / nn
        # el vector n esta en (right, up, depth); la camara mira hacia -depth: visible si n_depth > 0
        vis = n[:,2] > 0
        light = np.array([-0.35, 0.55, 0.75]); sh = 0.38 + 0.62*np.clip((n*light).sum(1), 0, 1)
        for i in np.nonzero(vis)[0]: polys.append((P[i,:,2].mean(), P[i], np.array(col)*sh[i]))
        allx.append(P[...,:2].reshape(-1, 2))
    allp = np.concatenate(allx); mn, mx = allp.min(0), allp.max(0)
    sc = scale or min((W*0.9)/(mx[0]-mn[0]), (H*0.9)/(mx[1]-mn[1])); cx, cy = (mn+mx)/2
    im = Image.new("RGB", (W, H), (250, 247, 240)); d = ImageDraw.Draw(im)
    polys.sort(key=lambda t: t[0])
    for _, P, c in polys:
        pts = [(W/2 + (p[0]-cx)*sc, H/2 - (p[1]-cy)*sc) for p in P]
        d.polygon(pts, fill=tuple(int(v) for v in c))
    im.resize(size, Image.LANCZOS).save(path)

if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--res", type=float, default=0.9); a = ap.parse_args(); os.makedirs(OUT, exist_ok=True)
    M = {n: G.build(n, a.res) for n in ("base", "lid_plain", "button", "d_star", "d_loop", "d_wings", "plate")}
    AQ, YE, WH, LA = (143, 227, 208), (255, 233, 138), (253, 253, 245), (201, 184, 240)
    caps = [(shift(M["button"], p[0], p[1], g.ceiling_z - g.flange_t), YE) for p in g.btn_pos]
    disp = cyl_mesh(0, g.disp_cy, g.plate_top + g.disp_gap, g.disp_d, g.disp_t)
    closed = [(M["base"], AQ), (M["lid_plain"], AQ), (M["d_star"], YE), (M["d_loop"], LA), (M["d_wings"], WH), (disp, (70, 50, 130))] + caps
    render(closed, 35, 38, os.path.join(OUT, "mochi_iso.png"))
    render(closed, 0, 90, os.path.join(OUT, "mochi_top.png"), (1100, 1100))
    render(closed, 0, 8, os.path.join(OUT, "mochi_front.png"), (1400, 700))
    render(closed, 210, 30, os.path.join(OUT, "mochi_back.png"))
    inner = [(M["base"], AQ), (M["plate"].copy() + np.array([0, 0, g.pcb_z0]), (60, 170, 120)),
             (box_mesh(g.mcu_x0, g.mcu_y - g.mcu_dy/2, g.mcu_z0, g.mcu_dx, g.mcu_dy, g.mcu_h), (200, 60, 60)),
             (box_mesh(g.tp_x0, g.tp_y0, g.plate_top, g.tp_dx, g.tp_dy, g.tp_h), (60, 120, 200)),
             (box_mesh(-g.batt_w/2, -g.batt_l/2, g.batt_z0, g.batt_w, g.batt_l, g.batt_t), (50, 50, 60)),
             (cyl_mesh(g.bz_x, g.bz_y, g.wall, g.bz_d, g.bz_h), (110, 110, 120))]
    for p in g.btn_pos: inner.append((box_mesh(p[0]-g.sw_w/2, p[1]-g.sw_w/2, g.plate_top, g.sw_w, g.sw_w, g.sw_h), (230, 150, 40)))
    render(inner, 20, 52, os.path.join(OUT, "mochi_internal_iso.png"))
    render(inner, 0, 90, os.path.join(OUT, "mochi_internal_top.png"), (1100, 1100))
    print("renders en", OUT)
