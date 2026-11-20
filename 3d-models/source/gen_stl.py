#!/usr/bin/env python3
"""Generador de STL de MOCHI sin OpenSCAD: campos de distancia (SDF) + marching tetrahedra con numpy.
Lee 3d-models/source/params.scad (misma fuente que mochi.scad) y escribe STL binarios en ../STL.
Es una RE-IMPLEMENTACION de la geometria de mochi.scad (para poder entregar STL sin OpenSCAD). Para la mejor calidad
(superficies facetadas a 0.1 mm) compila mochi.scad con OpenSCAD; ambos usan los mismos parametros.
Uso:  python3 gen_stl.py [--res 0.4] [--parts base lid button plate] [--out ../STL]"""
import re, os, sys, math, argparse, numpy as np
from functools import reduce
def MX(l): return reduce(np.maximum, l)
def MN(l): return reduce(np.minimum, l)
HERE = os.path.dirname(os.path.abspath(__file__))

def load_params():
    P = {"true": True, "false": False}
    for line in open(os.path.join(HERE, "params.scad"), encoding="utf-8").read().splitlines():
        line = line.split("//")[0].strip(); m = re.match(r"^(\w+)\s*=\s*(.+);$", line)
        if m: P[m.group(1)] = eval(m.group(2), {"__builtins__": {}}, dict(P))
    return type("P", (), P)
g = load_params()

# ------------------------------------------------------------------ primitivas SDF (negativo = dentro)
F32 = np.float32
def ell(X, Y, ax, ay): return (np.sqrt((X/ax)**2 + (Y/ay)**2) - 1.0) * np.minimum(ax, ay)
def blob(X, Y, Z, W, L, H, r, z0=0.0):
    z = np.clip(Z - z0, 0, H)
    ins = np.where(z < r, r - np.sqrt(np.maximum(0, r*r - (r - z)**2)), np.where(z > H - r, r - np.sqrt(np.maximum(0, r*r - (z - (H - r))**2)), 0.0))
    ax = np.maximum(W/2 - ins, 1e-3); ay = np.maximum(L/2 - ins, 1e-3)
    return MX([ell(X, Y, ax, ay), (z0 - Z), (Z - z0 - H)])
def cyl(X, Y, Z, cx, cy, d, z0, z1): return MX([np.hypot(X - cx, Y - cy) - d/2, z0 - Z, Z - z1])
def box(X, Y, Z, x0, y0, z0, dx, dy, dz): return MX([np.abs(X - (x0 + dx/2)) - dx/2, np.abs(Y - (y0 + dy/2)) - dy/2, np.abs(Z - (z0 + dz/2)) - dz/2])
def U(*a): return MN(a)
def I(*a): return MX(a)
def D(a, *b): return MX([a] + [-x for x in b])
def poly_sdf(X, Y, pts):
    d = np.full(np.broadcast(X, Y).shape, 1e9, F32); ins = np.zeros(d.shape, bool)
    for i in range(len(pts)):
        ax, ay = pts[i]; bx, by = pts[(i+1) % len(pts)]; ex, ey = bx-ax, by-ay; wx, wy = X-ax, Y-ay
        t = np.clip((wx*ex + wy*ey)/(ex*ex + ey*ey), 0, 1)
        d = np.minimum(d, np.hypot(wx - ex*t, wy - ey*t))
        ins ^= ((ay > Y) != (by > Y)) & (X < (bx-ax)*(Y-ay)/(by-ay + 1e-30) + ax)
    return np.where(ins, -d, d)
def star_pts(R, r): return [((R if i % 2 == 0 else r)*math.cos(math.radians(90 + 36*i)), (R if i % 2 == 0 else r)*math.sin(math.radians(90 + 36*i))) for i in range(10)]
def star_prism(X, Y, Z, cx, cy, R, r, z0, z1, delta=0.0):
    return MX([poly_sdf(X - cx, Y - cy, star_pts(R, r)) - delta, z0 - Z, Z - z1])
def capsule2d(X, Y, a, b, ra, rb):
    ex, ey = b[0]-a[0], b[1]-a[1]; t = np.clip(((X-a[0])*ex + (Y-a[1])*ey)/(ex*ex + ey*ey), 0, 1)
    return np.hypot(X - a[0] - ex*t, Y - a[1] - ey*t) - (ra + (rb - ra)*t)
def wing(X, Y, Z, m):
    xx = -X if m else X; c, s = math.cos(math.radians(-12)), math.sin(math.radians(-12))
    px, py = xx - (g.body_w/2 - 3.2), Y - 7; lx, ly = c*px - s*py, s*px + c*py
    f = U(capsule2d(lx, ly, (0, 0), (8, 2.2), 3.4, 2.6), capsule2d(lx, ly, (1.5, -3), (9.5, -1.2), 2.8, 2.2), np.hypot(lx - 10.2, ly - 1.2) - 1.6)
    z0 = g.split_z + 1.5; return MX([f, z0 - Z, Z - (z0 + 3)])

def shell(X, Y, Z):
    return D(blob(X, Y, Z, g.body_w, g.body_l, g.body_h, g.fillet), blob(X, Y, Z, g.body_w - 2*g.wall, g.body_l - 2*g.wall, g.body_h - 2*g.wall, g.fillet - g.wall, g.wall))

# ------------------------------------------------------------------ piezas
def part_base(X, Y, Z):
    s = I(shell(X, Y, Z), Z - g.split_z)
    parts = [s]
    for p in g.screw_pts: parts.append(cyl(X, Y, Z, p[0], p[1], g.col_od, g.wall - 0.01, g.split_z))
    for sx in (-1, 1):
        for sy in (-1, 1):
            parts.append(cyl(X, Y, Z, sx*g.post_x, sy*g.post_y, g.post_od, g.wall - 0.01, g.pcb_z0))
            parts.append(cyl(X, Y, Z, sx*g.post_x, sy*g.post_y, g.pin_d, g.wall - 0.01, g.pcb_z0 + g.pcb_t))
    for sx in (-1, 1): parts.append(box(X, Y, Z, sx*(g.batt_w/2 + g.batt_clear + 0.6) - 0.6, -g.batt_l/2, g.wall - 0.01, 1.2, g.batt_l, 2.2))
    ledge = box(X, Y, Z, -g.body_w/2, g.mcu_y - g.mcu_dy/2, g.wall - 0.01, g.body_w/2 - 21, g.mcu_dy, g.plate_top - g.wall + 0.01)
    parts.append(I(blob(X, Y, Z, g.body_w, g.body_l, g.body_h, g.fillet), ledge))
    parts.append(D(cyl(X, Y, Z, g.bz_x, g.bz_y, g.bz_d + 2.4, g.wall - 0.01, g.wall + 2.0), cyl(X, Y, Z, g.bz_x, g.bz_y, g.bz_d + 0.3, g.wall - 1, g.wall + 3)))
    solid = U(*parts); cuts = []
    for p in g.screw_pts:
        cuts += [cyl(X, Y, Z, p[0], p[1], g.clear_d, -1, g.split_z + 1), cyl(X, Y, Z, p[0], p[1], g.head_d, -1, g.head_h)]
    cuts.append(box(X, Y, Z, -g.body_w/2 - 1, g.mcu_y - g.usb_w/2, g.usb_z - g.usb_h/2, g.wall + 4, g.usb_w, g.usb_h))
    for i in range(-2, 3): cuts.append(cyl(X, Y, Z, g.bz_x, g.bz_y + i*2.2, 1.2, -1, g.wall + 1))
    return D(solid, *cuts)

def part_lid(X, Y, Z, decor=True):
    parts = [I(shell(X, Y, Z), g.split_z - Z)]
    parts.append(D(cyl(X, Y, Z, 0, g.disp_cy, g.bezel_od, g.body_h - 0.01, g.body_h + g.bezel_h), cyl(X, Y, Z, 0, g.disp_cy, g.window_d, g.body_h - 1, g.body_h + g.bezel_h + 3)))
    rd = g.disp_d/2 + g.disp_clear
    for a in (0, 180, 270):
        r2 = np.hypot(X, Y - g.disp_cy); ang = np.arctan2(Y - g.disp_cy, X); dd = np.abs((ang - math.radians(a) + math.pi) % (2*math.pi) - math.pi)
        ring = MX([rd - r2, r2 - (rd + g.cage_w), g.ceiling_z - g.cage_h - Z, Z - g.ceiling_z]); sec = (dd - math.radians(15))*r2
        parts.append(np.maximum(ring, sec))
    for p in g.screw_pts: parts.append(cyl(X, Y, Z, p[0], p[1], g.col_od, g.split_z - 0.01, g.ceiling_z + 0.02))
    if decor and g.decor_fuse: parts += decor_parts(X, Y, Z)
    solid = U(*parts); cuts = [cyl(X, Y, Z, 0, g.disp_cy, g.window_d, g.ceiling_z - 1, g.body_h + g.bezel_h + 2)]
    for p in g.screw_pts: cuts.append(cyl(X, Y, Z, p[0], p[1], g.pilot_d, g.split_z - 0.5, g.split_z - 0.5 + g.pilot_depth))
    for p in g.btn_pos: cuts.append(star_prism(X, Y, Z, p[0], p[1], g.star_R, g.star_r, g.ceiling_z - 1, g.ceiling_z + g.wall + 4, g.btn_clear))
    return D(solid, *cuts)

def decor_parts(X, Y, Z):
    return [decor_star(X, Y, Z), decor_loop(X, Y, Z), wing(X, Y, Z, 0), wing(X, Y, Z, 1)]
def decor_star(X, Y, Z): return star_prism(X, Y, Z, g.top_star_pos[0], g.top_star_pos[1], 6.2, 2.9, g.body_h - 2.2, g.body_h + 1.6)
def decor_loop(X, Y, Z): return D(cyl(X, Y, Z, g.loop_pos[0], g.loop_pos[1], 9, g.split_z + 1, g.split_z + 3.4), cyl(X, Y, Z, g.loop_pos[0], g.loop_pos[1], 4.8, g.split_z, g.split_z + 5))

def part_button(X, Y, Z):
    ft = g.flange_t
    return U(star_prism(X, Y, Z, 0, 0, g.star_R + 1.2, g.star_r + 0.6, 0, ft), star_prism(X, Y, Z, 0, 0, g.star_R, g.star_r, 0, ft + g.wall + g.cap_proud), cyl(X, Y, Z, 0, 0, g.stem_d, -g.stem_len, 0.01))

def part_plate(X, Y, Z):
    hw, hl, r = g.pcb_w/2, g.pcb_l/2, g.pcb_r; qx, qy = np.abs(X) - (hw - r), np.abs(Y) - (hl - r)
    rr = np.hypot(np.maximum(qx, 0), np.maximum(qy, 0)) + np.minimum(np.maximum(qx, qy), 0) - r
    f = MX([rr, -Z, Z - g.pcb_t]); cuts = []
    for sx in (-1, 1):
        for sy in (-1, 1): cuts.append(cyl(X, Y, Z, sx*g.post_x, sy*g.post_y, g.pin_d + 0.3, -1, g.pcb_t + 1))
    for p in g.screw_pts: cuts.append(cyl(X, Y, Z, p[0], p[1], g.col_od + 1.2, -1, g.pcb_t + 1))
    return D(f, *cuts)

PARTS = {  # nombre: (funcion, caja (x0,x1,y0,y1,z0,z1), resolucion relativa)
    "base":   (part_base,   (-g.body_w/2 - 1, g.body_w/2 + 1, -g.body_l/2 - 1, g.body_l/2 + 1, -1, g.split_z + 1), 1.0),
    "lid":    (part_lid,    (-g.body_w/2 - 14, g.body_w/2 + 14, -g.body_l/2 - 1, g.body_l/2 + 8, g.split_z - 1, g.body_h + g.bezel_h + 3), 1.0),
    "button": (part_button, (-g.star_R - 3, g.star_R + 3, -g.star_R - 3, g.star_R + 3, -g.stem_len - 1, g.flange_t + g.wall + g.cap_proud + 1), 0.5),
    "plate":  (part_plate,  (-g.pcb_w/2 - 1, g.pcb_w/2 + 1, -g.pcb_l/2 - 1, g.pcb_l/2 + 1, -1, g.pcb_t + 1), 0.75),
}

# ------------------------------------------------------------------ marching tetrahedra
CORN = np.array([[0,0,0],[1,0,0],[1,1,0],[0,1,0],[0,0,1],[1,0,1],[1,1,1],[0,1,1]])
TETS = [(0,5,1,6),(0,1,2,6),(0,2,3,6),(0,3,7,6),(0,7,4,6),(0,4,5,6)]
def march(F, xs, ys, zs):
    inside = F < 0
    cnt = (inside[:-1,:-1,:-1].astype(np.int8) + inside[1:,:-1,:-1] + inside[1:,1:,:-1] + inside[:-1,1:,:-1] +
           inside[:-1,:-1,1:] + inside[1:,:-1,1:] + inside[1:,1:,1:] + inside[:-1,1:,1:])
    idx = np.argwhere((cnt > 0) & (cnt < 8)); tris = []
    h = np.array([xs[1]-xs[0], ys[1]-ys[0], zs[1]-zs[0]])
    org = np.array([xs[0], ys[0], zs[0]])
    cidx = idx[:, None, :] + CORN[None, :, :]                       # (n,8,3)
    val = F[cidx[...,0], cidx[...,1], cidx[...,2]]                   # (n,8)
    pos = org + cidx * h                                             # (n,8,3)
    gid = (cidx[...,0]*F.shape[1] + cidx[...,1])*F.shape[2] + cidx[...,2]   # id global para orden canonico
    def interp(a, b, va, vb, pa, pb, ga, gb):                       # punto en la arista, orden canonico por id
        sw = ga > gb; pa2 = np.where(sw[:,None], pb, pa); pb2 = np.where(sw[:,None], pa, pb)
        va2 = np.where(sw, vb, va); vb2 = np.where(sw, va, vb)
        t = va2 / (va2 - vb2 + 1e-30); return pa2 + (pb2 - pa2)*t[:,None]
    for tet in TETS:
        v = val[:, tet]; p = pos[:, tet]; gi = gid[:, tet]; ins = v < 0; code = ins[:,0]*1 + ins[:,1]*2 + ins[:,2]*4 + ins[:,3]*8
        for c in range(1, 15):
            m = code == c
            if not m.any(): continue
            iv = [k for k in range(4) if (c >> k) & 1]; ov = [k for k in range(4) if not (c >> k) & 1]
            vv, pp, gg = v[m], p[m], gi[m]
            E = lambda a, b: interp(a, b, vv[:,a], vv[:,b], pp[:,a], pp[:,b], gg[:,a], gg[:,b])
            if len(iv) == 1:
                a = iv[0]; T = [(E(a, ov[0]), E(a, ov[1]), E(a, ov[2]))]; ref = pp[:, ov].mean(1) - pp[:, a]
            elif len(iv) == 3:
                d = ov[0]; T = [(E(iv[0], d), E(iv[1], d), E(iv[2], d))]; ref = pp[:, d] - pp[:, iv].mean(1)
            else:
                a, b = iv; c1, d1 = ov; q = [E(a, c1), E(a, d1), E(b, d1), E(b, c1)]
                T = [(q[0], q[1], q[2]), (q[0], q[2], q[3])]; ref = pp[:, ov].mean(1) - pp[:, iv].mean(1)
            for t in T:
                n = np.cross(t[1] - t[0], t[2] - t[0]); flip = (n*ref).sum(1) < 0
                t1 = np.where(flip[:,None], t[2], t[1]); t2 = np.where(flip[:,None], t[1], t[2])
                tris.append(np.stack([t[0], t1, t2], 1))
    return np.concatenate(tris, 0) if tris else np.zeros((0,3,3))

def build(name, res):
    fn, (x0, x1, y0, y1, z0, z1), k = PARTS[name]; h = res * k
    xs = np.arange(x0 + 0.0173, x1 + h, h, dtype=F32); ys = np.arange(y0 + 0.0291, y1 + h, h, dtype=F32); zs = np.arange(z0 + 0.0113, z1 + h, h, dtype=F32)   # desfase: evita que planos de corte coincidan con la malla
    X, Y, Z = xs[:, None, None], ys[None, :, None], zs[None, None, :]
    F = np.broadcast_to(fn(X, Y, Z), (len(xs), len(ys), len(zs))).astype(F32)
    T = march(F, xs, ys, zs); T = np.round(T, 4)
    q = np.round(T * 1e4).astype(np.int64)            # descarta solo triangulos colapsados tras cuantizar (mantiene la topologia)
    keep = ~((q[:,0] == q[:,1]).all(1) | (q[:,1] == q[:,2]).all(1) | (q[:,0] == q[:,2]).all(1))
    return T[keep]

def stats(T):
    vol = np.einsum("ij,ij->i", T[:,0], np.cross(T[:,1], T[:,2])).sum() / 6.0
    q = np.round(T.reshape(-1,3) * 1e4).astype(np.int64); _, inv = np.unique(q, axis=0, return_inverse=True); f = inv.reshape(-1,3)
    e = np.sort(np.concatenate([f[:,[0,1]], f[:,[1,2]], f[:,[2,0]]]), axis=1); _, cnts = np.unique(e, axis=0, return_counts=True)
    return vol, int((cnts != 2).sum())

def write_stl(path, T, name):
    n = np.cross(T[:,1] - T[:,0], T[:,2] - T[:,0]); n /= (np.linalg.norm(n, axis=1, keepdims=True) + 1e-30)
    rec = np.zeros(len(T), dtype=[("n", "<f4", 3), ("v", "<f4", (3, 3)), ("a", "<u2")]); rec["n"] = n; rec["v"] = T
    with open(path, "wb") as f: f.write(name.encode()[:79].ljust(80, b" ")); f.write(np.uint32(len(T)).tobytes()); f.write(rec.tobytes())

if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--res", type=float, default=0.4); ap.add_argument("--parts", nargs="+", default=list(PARTS)); ap.add_argument("--out", default=os.path.join(HERE, "..", "STL"))
    a = ap.parse_args(); os.makedirs(a.out, exist_ok=True)
    for nm in a.parts:
        T = build(nm, a.res); vol, bad = stats(T); path = os.path.join(a.out, f"mochi_{nm}.stl"); write_stl(path, T, f"MOCHI {nm}")
        bb = T.reshape(-1, 3); print(f"{nm:7s} {len(T):8d} triangulos  volumen {vol/1000:6.2f} cm3  caja {np.ptp(bb[:,0]):.1f}x{np.ptp(bb[:,1]):.1f}x{np.ptp(bb[:,2]):.1f} mm  aristas no-manifold: {bad}  -> {os.path.getsize(path)/1e6:.1f} MB")
