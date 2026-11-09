"""Cybran Long Range Artillery (SupCom 2 inspired) - procedural model.
Units: 1.0 = one Mindustry tile. Z up. Turret faces +Y.
Groups: base (static), body / wingl / wingr (rotate with turret), barrel (recoils, elevated).
"""
import numpy as np, math
from geom import *

ELEV = 16.0
PIVOT = np.array([0.0, 0.55, 0.98])

MATS = ['hull_dark','hull_mid','hull_light','red_armor','metal','metal_light',
        'cable','vent','bore','coil','heat','glow','ground']
MID = {m:i for i, m in enumerate(MATS)}

class Model:
    def __init__(self):
        self.parts = {}
    def add(self, g, T, m):
        T = clean(T)
        if len(T): self.parts.setdefault(g, []).append((T, m))
    def arrays(self, groups, xforms=None):
        tris, mats, grp = [], [], []
        for g in groups:
            for T, m in self.parts.get(g, []):
                TT = T if not xforms or g not in xforms else xforms[g](T)
                tris.append(TT); mats += [MID[m]]*len(TT); grp += [g]*len(TT)
        return np.concatenate(tris), np.array(mats), np.array(grp)

def build_base(M):
    g = 'base'
    slab = cham_rect(1.47, 1.47, 0.42)
    M.add(g, prism(slab, 0.0, 0.12, 0.985), 'hull_dark')
    tier = cham_rect(1.27, 1.27, 0.52)
    M.add(g, prism(tier, 0.12, 0.27, 0.93), 'hull_mid')
    M.add(g, prism(cham_rect(1.08, 1.08, 0.46), 0.27, 0.30, 0.97), 'hull_dark')
    for k in range(4):
        R = rz(45 + 90*k)
        u0, u1 = 0.80, 1.74
        def zt(u): return 0.50 - (u-u0)/(u1-u0)*0.32
        bot = [(u0,-0.22),(1.20,-0.17),(1.52,-0.09),(u1,0.0),(1.52,0.09),(1.20,0.17),(u0,0.22)]
        top = [(u0+0.02,-0.15),(1.20,-0.11),(1.50,-0.05),(u1-0.03,0.0),(1.50,0.05),(1.20,0.11),(u0+0.02,0.15)]
        b3 = ring(ccw(bot), 0.12)
        tp = ccw(top)
        t3 = np.column_stack([tp, [zt(u) for u, _ in tp]])
        M.add(g, tf(loft(b3, t3), R), 'hull_dark')
        cp = ccw([(0.90,-0.10),(1.25,-0.075),(1.48,-0.035),(1.48,0.035),(1.25,0.075),(0.90,0.10)])
        cb = np.column_stack([cp, [zt(u)+0.004 for u, _ in cp]])
        cps = scale_poly(cp, (0.97, 0.75))
        ct = np.column_stack([cps, [zt(u)+0.04 for u, _ in cps]])
        M.add(g, tf(loft(cb, ct), R), 'red_armor')
        M.add(g, tf(cbox(1.60, 0, zt(1.60)+0.02, 0.07, 0.05, 0.05), R), 'glow')
        for v in (-0.12, 0.12):
            M.add(g, tf(cyl((0.86, v, zt(0.86)-0.02), (0.86, v, zt(0.86)+0.025), 0.035, n=8), R), 'metal_light')
        for s in (-1, 1):
            sp_b = ccw([(1.10, s*0.15), (1.24, s*0.15), (1.17, s*0.27)])
            M.add(g, tf(loft(ring(sp_b, 0.12), ring(scale_poly(sp_b, 0.4), 0.26)), R), 'hull_light')
        S = rz(90*k)
        M.add(g, tf(box(-0.34, 0.34, 0.86, 1.10, 0.27, 0.278), S), 'vent')
        M.add(g, tf(box(-0.29, 0.29, 0.90, 1.06, 0.27, 0.283), S), 'glow')
        for i in range(6):
            x = -0.25 + i*0.1
            M.add(g, tf(box(x-0.022, x+0.022, 0.88, 1.08, 0.283, 0.31), S), 'metal')
        M.add(g, tf(box(-0.38, 0.38, 1.10, 1.15, 0.27, 0.32), S), 'hull_light')
        M.add(g, tf(box(-0.38, 0.38, 0.81, 0.86, 0.27, 0.32), S), 'hull_light')
        for sx in (-0.55, 0.55):
            pts = [(sx, 1.40, 0.15), (sx*0.93, 1.18, 0.30), (sx*0.80, 1.00, 0.38)]
            M.add(g, tf(tube_path(pts, 0.045, n=10), S), 'cable')
            M.add(g, tf(cyl((sx, 1.42, 0.15), (sx, 1.34, 0.19), 0.065, n=10), S), 'red_armor')
        for x in (-1.0, -0.8, 0.8, 1.0):
            M.add(g, tf(cyl((x, 1.36, 0.11), (x, 1.36, 0.145), 0.032, n=8), S), 'metal_light')
    M.add(g, cyl((0,0,0.30), (0,0,0.42), 0.99, n=40), 'hull_mid')
    M.add(g, cyl((0,0,0.42), (0,0,0.46), 0.99, 0.93, n=40), 'metal')
    M.add(g, cyl((0,0,0.46), (0,0,0.47), 0.86, n=40), 'hull_dark')
    M.add(g, cyl((0,0,0.47), (0,0,0.475), 0.62, n=36), 'vent')
    M.add(g, cyl((0,0,0.475), (0,0,0.49), 0.30, n=24), 'hull_mid')
    for i in range(12):
        a = math.radians(360*i/12+15)
        M.add(g, cyl((0.74*math.cos(a), 0.74*math.sin(a), 0.47), (0.74*math.cos(a), 0.74*math.sin(a), 0.49), 0.03, n=8), 'metal_light')
    for i in range(32):
        M.add(g, tf(cbox(1.025, 0, 0.36, 0.06, 0.07, 0.10), rz(360*i/32)), 'metal')
    M.add(g, cyl((0,0,0.415), (0,0,0.425), 1.0, n=40), 'glow')

HULL_HALF = [(0,1.0),(0.36,0.90),(0.60,0.58),(0.74,0.12),(0.70,-0.42),(0.56,-0.86),(0.28,-1.08),(0,-1.14)]

def build_body(M):
    g = 'body'
    hull = mirror_half(HULL_HALF)
    M.add(g, prism(hull, 0.46, 0.80, 0.86), 'hull_dark')
    deck = scale_poly(hull, 0.80, (0, 0))
    M.add(g, prism(deck, 0.79, 0.90, 0.84), 'hull_mid')
    sh = ccw([(0.17,0.32),(0.40,0.22),(0.45,-0.30),(0.34,-0.58),(0.17,-0.48)])
    for s in (1, -1):
        P = sh if s == 1 else ccw(sh*np.array([-1,1.0]))
        M.add(g, prism(P, 0.90, 0.96, 0.86), 'red_armor')
        for (x, y) in ((0.36, 0.12), (0.36, -0.36), (0.22, -0.40)):
            M.add(g, cyl((s*x, y, 0.955), (s*x, y, 0.975), 0.025, n=8), 'metal_light')
    for i, y in enumerate((0.18, -0.04, -0.26, -0.48)):
        b = rect(0, y, 0.075, 0.075)
        t = rect(0, y-0.07, 0.022, 0.03)
        M.add(g, loft(ring(b, 0.90), ring(t, 1.06 - i*0.012)), 'hull_light')
        M.add(g, box(-0.03, 0.03, y-0.115, y-0.095, 0.90, 0.925), 'glow')
    M.add(g, box(-0.36, 0.36, -0.70, -0.52, 0.895, 0.905), 'vent')
    M.add(g, box(-0.32, 0.32, -0.68, -0.54, 0.895, 0.912), 'heat')
    for i in range(7):
        x = -0.27 + i*0.09
        M.add(g, box(x-0.018, x+0.018, -0.69, -0.53, 0.912, 0.94), 'metal')
    M.add(g, cyl((-0.42,-0.92,0.80), (0.42,-0.92,0.80), 0.27, n=22), 'metal')
    for x in (-0.30, -0.10, 0.10, 0.30):
        M.add(g, cyl((x-0.025,-0.92,0.80), (x+0.025,-0.92,0.80), 0.295, n=22), 'red_armor')
    for s in (-1, 1):
        M.add(g, cyl((s*0.42,-0.92,0.80), (s*0.48,-0.92,0.80), 0.19, n=16), 'hull_dark')
        M.add(g, cyl((s*0.48,-0.92,0.80), (s*0.51,-0.92,0.80), 0.08, n=12), 'glow')
    for s in (-1, 1):
        M.add(g, cyl((s*0.46,-0.80,0.62), (s*0.50,-1.12,0.62), 0.085, n=12), 'hull_dark')
        M.add(g, cyl((s*0.50,-1.11,0.62), (s*0.505,-1.135,0.62), 0.055, n=10), 'heat')
    M.add(g, cbox(-0.42, 0.52, 0.86, 0.26, 0.32, 0.17), 'hull_mid')
    M.add(g, cbox(-0.42, 0.50, 0.955, 0.18, 0.20, 0.03), 'hull_light')
    M.add(g, cyl((-0.42,0.67,0.87), (-0.42,0.72,0.87), 0.09, n=14), 'metal')
    M.add(g, cyl((-0.42,0.70,0.87), (-0.42,0.735,0.87), 0.062, n=14), 'glow')
    M.add(g, cbox(0.42, 0.56, 0.84, 0.16, 0.22, 0.12), 'hull_light')
    M.add(g, cyl((0.42,0.66,0.85), (0.42,0.70,0.85), 0.045, n=10), 'glow')
    M.add(g, cyl((0.34,-0.52,0.93), (0.62,-1.30,1.30), 0.032, 0.02, n=8), 'metal')
    M.add(g, cyl((0.62,-1.30,1.30), (0.64,-1.36,1.33), 0.045, n=8), 'glow')
    M.add(g, cyl((-0.30,-0.56,0.93), (-0.46,-1.12,1.18), 0.03, 0.02, n=8), 'metal')
    M.add(g, cyl((-0.46,-1.12,1.18), (-0.47,-1.16,1.20), 0.04, n=8), 'glow')
    M.add(g, cbox(0, 0.55, 0.92, 0.46, 0.44, 0.26), 'hull_mid')
    M.add(g, cbox(0, 0.55, 1.055, 0.30, 0.30, 0.03), 'hull_light')
    for s in (-1, 1):
        M.add(g, cyl((s*0.22,0.55,0.98), (s*0.33,0.55,0.98), 0.12, n=16), 'metal')
        M.add(g, cyl((s*0.33,0.55,0.98), (s*0.35,0.55,0.98), 0.06, n=10), 'red_armor')
        a = np.array([s*0.17,-0.16,0.92]); b = np.array([s*0.17,0.40,1.05])
        m = a + (b-a)*0.55
        M.add(g, cyl(a, m, 0.058, n=12), 'hull_dark')
        M.add(g, cyl(m, b, 0.034, n=10), 'metal_light')
    for s in (-1, 1):
        pts = [(s*0.12,-0.74,1.06), (s*0.14,-0.34,0.98), (s*0.14,0.20,1.00), (s*0.11,0.38,1.07)]
        M.add(g, tube_path(pts, 0.034, n=10), 'cable')
    for s in (-1, 1):
        for y in (0.30, 0.10, -0.10):
            M.add(g, cbox(s*0.66, y, 0.70, 0.05, 0.12, 0.05), 'heat')

def wing_tris():
    W = ccw([(0.56,0.58),(0.94,0.26),(1.12,-0.30),(1.03,-0.80),(1.20,-1.32),(0.66,-1.00),(0.62,-0.40),(0.64,0.14)])
    def zt(x): return 0.82 - (x-0.56)*0.40
    top = scale_poly(W, 0.95)
    out = [(loft(ring(W, 0.50), np.column_stack([top, [zt(x) for x, _ in top]])), 'hull_light')]
    st = ccw([(0.74,0.30),(0.93,0.12),(1.02,-0.32),(0.95,-0.72),(0.84,-0.44),(0.78,0.04)])
    sb = np.column_stack([st, [zt(x)+0.003 for x, _ in st]])
    s2 = scale_poly(st, 0.9)
    stp = np.column_stack([s2, [zt(x)+0.035 for x, _ in s2]])
    out.append((loft(sb, stp), 'red_armor'))
    for (x, y) in ((1.04, 0.0), (1.07, -0.30), (1.02, -0.62)):
        out.append((cbox(x, y, zt(x)+0.02, 0.06, 0.10, 0.04), 'glow'))
    for (x, y) in ((0.72, 0.30), (0.70, -0.20), (0.74, -0.70)):
        out.append((cyl((x, y, zt(x)-0.01), (x, y, zt(x)+0.03), 0.03, n=8), 'metal_light'))
    out.append((cyl((0.92,-1.0,zt(0.92)-0.02), (1.10,-1.26,zt(1.10)-0.04), 0.035, 0.015, n=8), 'metal'))
    return out

def build_wings(M):
    for T, m in wing_tris():
        M.add('wingr', T, m)
        M.add('wingl', mirror_x(T), m)

def build_barrel(M, g='barrel_local'):
    # breech + accelerator jacket (Cybran coil rings)
    M.add(g, box(-0.19, 0.19, -0.42, 0.24, -0.16, 0.16), 'hull_mid')
    M.add(g, box(-0.13, 0.13, -0.34, 0.12, 0.16, 0.20), 'red_armor')
    M.add(g, box(-0.14, 0.14, -0.50, -0.42, -0.12, 0.12), 'metal')
    M.add(g, cyl((0,-0.50,0), (0,-0.55,0), 0.07, n=12), 'glow')
    M.add(g, cyl((0,0.22,0), (0,1.16,0), 0.165, n=24), 'hull_dark')
    for k in range(5):
        y = 0.30 + k*0.165
        M.add(g, cyl((0,y,0), (0,y+0.055,0), 0.20, n=24), 'red_armor')
        M.add(g, cyl((0,y+0.055,0), (0,y+0.165,0), 0.175, n=24), 'coil')
    # hydraulic recoil cylinders on both sides + rods + clamp
    for s in (-1, 1):
        M.add(g, cyl((s*0.27,-0.30,0), (s*0.27,0.95,0), 0.062, n=14), 'metal_light')
        M.add(g, cyl((s*0.27,0.95,0), (s*0.27,1.34,0), 0.034, n=12), 'metal')
        for y in (-0.22, 0.45):
            M.add(g, cyl((s*0.27,y,0), (s*0.27,y+0.06,0), 0.078, n=14), 'hull_mid')
        x0, x1 = sorted((s*0.17, s*0.22))
        M.add(g, box(x0, x1, 0.24, 1.12, 0.02, 0.10), 'metal_light')
        x0, x1 = sorted((s*0.185, s*0.205))
        M.add(g, box(x0, x1, 0.30, 1.06, 0.10, 0.115), 'coil')
    M.add(g, box(-0.31, 0.31, 1.30, 1.40, -0.06, 0.06), 'hull_mid')
    M.add(g, cyl((0,1.28,0), (0,1.42,0), 0.14, n=22), 'hull_mid')
    # long gun tube (two tapered sections + bands)
    M.add(g, cyl((0,1.16,0), (0,1.95,0), 0.142, n=24), 'metal')
    M.add(g, cyl((0,1.95,0), (0,2.58,0), 0.122, n=22), 'metal')
    for y in (1.62, 1.95, 2.28):
        M.add(g, cyl((0,y-0.03,0), (0,y+0.03,0), 0.158, n=22), 'hull_mid')
    # big muzzle brake with baffles
    M.add(g, box(-0.155, 0.155, 2.56, 2.92, -0.13, 0.13), 'hull_dark')
    M.add(g, box(-0.085, 0.085, 2.58, 2.90, 0.11, 0.14), 'red_armor')
    for s in (-1, 1):
        for y0 in (2.60, 2.715, 2.83):
            x0, x1 = sorted((s*0.155, s*0.31))
            M.add(g, box(x0, x1, y0, y0+0.075, -0.11, 0.11), 'metal_light')
    M.add(g, cyl((0,2.92,0), (0,2.935,0), 0.08, n=16), 'bore')
    M.add(g, cyl((0,2.92,0), (0,2.94,0), 0.05, n=14), 'coil')

def barrel_world(T, elev=None):
    return tf(T, rx(ELEV if elev is None else elev), PIVOT)

def build():
    M = Model()
    build_base(M); build_body(M); build_wings(M); build_barrel(M)
    M.parts['barrel'] = [(barrel_world(T), m) for T, m in M.parts['barrel_local']]
    return M

if __name__ == '__main__':
    M = build()
    for g, L in M.parts.items():
        print(g, sum(len(T) for T, _ in L), 'tris')
