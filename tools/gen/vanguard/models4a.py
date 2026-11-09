"""Stage 3 turret models (T1-T3). 1.0 = one tile (32 px). Turret heads face +Y.
Groups: base (static pad), body (rotating head), barrel (recoiling part, optional)."""
import numpy as np, math
from geom import *
from mats import Model, MID
from models import bolts, light, vent, chevrons, uef_base
from models2 import frame, octo
from models3 import hexa, add_rot

def P(pts): return ccw([tuple(p) for p in pts])

def cy_base(M, g, half, top=0.16):
    """Cybran foundation: dark chamfered plate, diagonal spikes, red edge strips."""
    h = half
    M.add(g, prism(cham_rect(h*0.985, h*0.985, h*0.34), 0, 0.08, 0.98), 'cy_dark')
    M.add(g, prism(cham_rect(h*0.86, h*0.86, h*0.30), 0.08, top, 0.95), 'cy_mid')
    M.add(g, prism(cham_rect(h*0.70, h*0.70, h*0.26), top, top+0.008), 'cy_dark')
    for k in range(4):
        R = rz(90*k)
        M.add(g, tf(cbox(0, -h*0.80, top+0.004, h*0.62, 0.035, 0.012), R), 'rglow')
        M.add(g, tf(cbox(0, -h*0.80, top+0.002, h*0.70, 0.075, 0.010), R), 'cy_dark')
        sp = P([(-0.07*h, 0.98*h), (0.07*h, 0.98*h), (0, 1.30*h)])
        M.add(g, tf(prism(sp, 0.06, 0.14, 0.55), rz(45+90*k)), 'red_armor')
        for s in (-1, 1):
            M.add(g, tf(cbox(s*h*0.45, -h*0.90, 0.085, 0.06, 0.05, 0.03), R), 'metal')

def ring(M, g, r, z0, z1, m='metal'):
    M.add(g, cyl((0, 0, z0), (0, 0, z1), r, n=28), m)
    M.add(g, cyl((0, 0, z1), (0, 0, z1+0.012), r*0.92, n=28), 'hull_dark')

# =========================================================== Redoubt (T2, UEF fortified artillery, 3x3)
def redoubt():
    M = Model(); g = 'base'
    uef_base(M, g, 1.5)
    ring(M, g, 1.08, 0.17, 0.21)
    g = 'body'
    M.add(g, prism(octo(1.10), 0.22, 0.34, 0.96), 'hull_dark')
    hull = P([(-0.98, -0.92), (0.98, -0.92), (1.06, 0.12), (0.74, 0.88), (-0.74, 0.88), (-1.06, 0.12)])
    M.add(g, prism(hull, 0.34, 0.60, top_poly=scale_poly(hull, 0.80)), 'hull_mid')
    deck = scale_poly(hull, 0.80)
    M.add(g, prism(deck, 0.60, 0.63, 0.96), 'hull_light')
    # side armour skirts with yellow trim
    for s in (-1, 1):
        sk = P([(s*1.02, -0.80), (s*1.16, -0.62), (s*1.16, 0.10), (s*1.02, 0.30)])
        M.add(g, prism(sk, 0.28, 0.50, 0.92), 'hull_light')
        M.add(g, prism(P([(s*1.10, -0.58), (s*1.15, -0.52), (s*1.15, 0.02), (s*1.10, 0.10)]), 0.50, 0.515), 'yellow')
        bolts(M, g, [(s*1.09, y) for y in (-0.62, -0.36, -0.10, 0.14)], 0.50, r=0.022)
    # rear engine/ammo deck
    vent(M, g, 0, -0.62, 0.63, 0.92, 0.22, slats=8)
    for x in (-0.52, 0.52):
        M.add(g, cyl((x, -0.70, 0.63), (x, -0.70, 0.76), 0.10, n=12), 'metal')
        M.add(g, cyl((x, -0.70, 0.76), (x, -0.70, 0.78), 0.075, n=12), 'vent')
    # commander cupola
    M.add(g, cyl((0.42, -0.12, 0.63), (0.42, -0.12, 0.76), 0.17, n=10), 'hull_mid')
    M.add(g, cyl((0.42, -0.12, 0.76), (0.42, -0.12, 0.80), 0.12, n=10), 'glass')
    M.add(g, cbox(0.42, 0.02, 0.79, 0.12, 0.03, 0.02), 'glow')
    # ammo hatch + hazard plate
    M.add(g, prism(cham_rect(0.22, 0.17, 0.05, cx=-0.38, cy=-0.12), 0.63, 0.67, 0.9), 'hull_dark')
    bolts(M, g, [(-0.55, -0.26), (-0.21, -0.26), (-0.55, 0.02), (-0.21, 0.02)], 0.67, r=0.02)
    chevrons(M, g, 0, 0.30, 0.63, 0.90, 0.16, n=5)
    light(M, g, -0.80, 0.40, 0.55, 0.06, 0.06)
    light(M, g, 0.80, 0.40, 0.55, 0.06, 0.06)
    g = 'barrel'
    M.add(g, prism(cham_rect(0.64, 0.20, 0.07, cy=0.84), 0.40, 0.70, 0.88), 'hull_light')
    M.add(g, prism(cham_rect(0.50, 0.06, 0.02, cy=0.98), 0.70, 0.705), 'yellow')
    for x in (-0.36, 0.0, 0.36):
        M.add(g, cyl((x, 0.88, 0.56), (x, 1.18, 0.56), 0.115, n=14), 'hull_mid')
        M.add(g, cyl((x, 1.18, 0.56), (x, 1.66, 0.56), 0.082, n=14), 'metal')
        M.add(g, cyl((x, 1.30, 0.56), (x, 1.36, 0.56), 0.095, n=14), 'metal_light')
        M.add(g, cyl((x, 1.66, 0.56), (x, 1.84, 0.56), 0.12, n=10), 'hull_dark')
        for yy in (1.71, 1.78): M.add(g, cbox(x, yy, 0.56, 0.26, 0.022, 0.07), 'vent')
        M.add(g, cyl((x, 1.84, 0.56), (x, 1.85, 0.56), 0.07, n=10), 'bore')
    return M

def heat_redoubt(mp, X, Y, g):
    return np.clip((Y-1.25)/0.55, 0, 1)*np.isin(mp, [MID['metal'], MID['metal_light'], MID['hull_dark']])

# =========================================================== Mantis (T3, Cybran heavy artillery + Scathis, 4x4)
def mantis():
    M = Model(); g = 'base'
    cy_base(M, g, 2.0)
    ring(M, g, 1.36, 0.16, 0.21, 'cy_mid')
    g = 'body'
    hull = P([(-1.22, -1.10), (1.22, -1.10), (1.50, -0.05), (0.95, 1.05), (-0.95, 1.05), (-1.50, -0.05)])
    M.add(g, prism(hull, 0.21, 0.38, 0.96), 'cy_dark')
    M.add(g, prism(scale_poly(hull, 0.88), 0.38, 0.62, 0.86), 'cy_mid')
    # shoulder plates with spikes
    for s in (-1, 1):
        pl = P([(s*0.70, -0.92), (s*1.32, -0.62), (s*1.36, 0.22), (s*0.86, 0.70)])
        M.add(g, prism(pl, 0.60, 0.74, 0.86), 'red_armor')
        M.add(g, prism(P([(s*0.80, -0.70), (s*1.20, -0.50), (s*1.22, 0.12), (s*0.90, 0.46)]), 0.74, 0.76, 0.9), 'cy_dark')
        for k, y in enumerate((-0.55, -0.20, 0.15)):
            sp = P([(s*1.30, y-0.07), (s*1.30, y+0.07), (s*1.62, y+0.12)])
            M.add(g, prism(sp, 0.42, 0.52, 0.6), 'cy_dark')
        M.add(g, cbox(s*1.05, -0.20, 0.765, 0.035, 0.70, 0.01), 'rglow')
        for y in (-0.62, -0.30, 0.02):
            M.add(g, cbox(s*0.80, y, 0.66, 0.06, 0.16, 0.03), 'metal')
    # rear nanite reactor (hex) with red core
    M.add(g, prism(hexa(0.44, 0, -0.62), 0.62, 0.80, 0.82), 'cy_dark')
    M.add(g, prism(hexa(0.30, 0, -0.62), 0.80, 0.84, 0.9), 'cy_mid')
    M.add(g, prism(hexa(0.17, 0, -0.62), 0.84, 0.90, 0.7), 'rglow')
    for k in range(6):
        a = math.radians(30+60*k)
        M.add(g, cyl((0.36*math.cos(a), -0.62+0.36*math.sin(a), 0.80), (0.36*math.cos(a), -0.62+0.36*math.sin(a), 0.86), 0.035, n=6), 'metal')
    # cable bundles
    for s in (-1, 1):
        M.add(g, tube_path([(s*0.30, -0.40, 0.66), (s*0.40, -0.05, 0.70), (s*0.38, 0.30, 0.68)], 0.035, n=6), 'cable')
    g = 'barrel'
    # Scathis drum + fan of six barrels
    M.add(g, prism(hexa(0.50, 0, 0.42, ph=0), 0.58, 0.86, 0.85), 'cy_mid')
    M.add(g, prism(hexa(0.36, 0, 0.42, ph=0), 0.86, 0.90, 0.9), 'cy_dark')
    M.add(g, prism(hexa(0.14, 0, 0.42, ph=0), 0.90, 0.95, 0.7), 'rglow')
    for k in range(6):
        ang = -13.75 + 5.5*k; z = 0.72 if k in (0, 2, 4) else 0.66
        sub = Model()
        sub.add('b', cyl((0, 0.30, z), (0, 0.80, z), 0.085, n=12), 'cy_mid')
        sub.add('b', cyl((0, 0.80, z), (0, 1.62, z), 0.062, n=12), 'metal')
        sub.add('b', cyl((0, 1.10, z), (0, 1.16, z), 0.075, n=12), 'red_armor')
        sub.add('b', cyl((0, 1.62, z), (0, 1.74, z), 0.085, n=8), 'cy_dark')
        sub.add('b', cyl((0, 1.74, z), (0, 1.75, z), 0.05, n=8), 'bore')
        sub.add('b', cbox(0, 1.55, z+0.06, 0.03, 0.10, 0.01), 'rglow')
        add_rot(M, g, sub, rz(ang), (0, 0.42, 0))
    return M

def heat_mantis(mp, X, Y, g):
    return np.clip((Y-1.35)/0.6, 0, 1)*np.isin(mp, [MID['metal'], MID['cy_dark']])

# =========================================================== Lash (T2, Cybran pulse laser, 2x2)
def lash():
    M = Model(); g = 'base'
    cy_base(M, g, 1.0)
    ring(M, g, 0.66, 0.16, 0.20, 'cy_mid')
    g = 'body'
    head = P([(-0.52, -0.56), (0.52, -0.56), (0.64, 0.04), (0.34, 0.56), (-0.34, 0.56), (-0.64, 0.04)])
    M.add(g, prism(head, 0.20, 0.36, 0.92), 'cy_dark')
    M.add(g, prism(scale_poly(head, 0.80), 0.36, 0.48, 0.85), 'cy_mid')
    for s in (-1, 1):
        prong = P([(s*0.12, 0.26), (s*0.32, 0.26), (s*0.27, 1.06), (s*0.17, 1.14)])
        M.add(g, prism(prong, 0.30, 0.44, 0.88), 'red_armor')
        M.add(g, cbox(s*0.22, 0.68, 0.442, 0.035, 0.56, 0.01), 'rglow')
        M.add(g, cyl((s*0.22, 0.98, 0.37), (s*0.22, 1.18, 0.37), 0.048, n=8), 'metal')
        M.add(g, sphereish((s*0.22, 1.18, 0.37), 0.045, n=8), 'rglow')
        M.add(g, prism(P([(s*0.50, -0.40), (s*0.70, -0.30), (s*0.66, -0.05), (s*0.50, -0.10)]), 0.30, 0.40, 0.8), 'cy_dark')
    M.add(g, prism(hexa(0.17, 0, -0.14), 0.48, 0.58, 0.6), 'rglow')
    M.add(g, cyl((0, -0.14, 0.48), (0, -0.14, 0.50), 0.24, n=6), 'metal')
    vent(M, g, 0, -0.42, 0.48, 0.42, 0.10, slats=5)
    return M

# =========================================================== Hydra (T3, Cybran missile salvo, 3x3)
def hydra():
    M = Model(); g = 'base'
    cy_base(M, g, 1.5)
    ring(M, g, 0.98, 0.16, 0.20, 'cy_mid')
    g = 'body'
    M.add(g, prism(hexa(0.82, ph=0), 0.20, 0.40, 0.9), 'cy_dark')
    M.add(g, prism(cham_rect(0.36, 0.60, 0.12), 0.40, 0.66, 0.85), 'cy_mid')
    M.add(g, prism(hexa(0.16, 0, -0.25), 0.66, 0.74, 0.7), 'rglow')
    M.add(g, cbox(0, 0.22, 0.665, 0.05, 0.50, 0.01), 'rglow')
    for s in (-1, 1):
        cx = s*0.74
        pod = cham_rect(0.36, 0.78, 0.10, cx=cx, cy=0.12)
        M.add(g, prism(pod, 0.36, 0.70, 0.94), 'red_armor')
        M.add(g, prism(cham_rect(0.32, 0.72, 0.09, cx=cx, cy=0.12), 0.70, 0.73), 'cy_dark')
        for i in range(4):
            x = cx + (-0.24 + 0.16*i)
            M.add(g, cyl((x, -0.40, 0.66), (x, 0.92, 0.66), 0.065, n=10), 'cy_mid')
            M.add(g, cyl((x, 0.92, 0.66), (x, 0.94, 0.66), 0.045, n=10), 'bore')
            M.add(g, cyl((x, 0.80, 0.66), (x, 0.92, 0.66), 0.04, n=8, r1=0.01), 'rglow')
        M.add(g, tube_path([(s*0.30, -0.10, 0.60), (s*0.42, -0.30, 0.62), (cx, -0.62, 0.60)], 0.04, n=6), 'cable')
        for sp in (-0.45, 0.10):
            M.add(g, prism(P([(cx+s*0.36, sp-0.08), (cx+s*0.36, sp+0.08), (cx+s*0.60, sp+0.14)]), 0.44, 0.54, 0.6), 'cy_dark')
    return M

def heat_front(y0, y1):
    def f(mp, X, Y, g): return np.clip((Y-y0)/(y1-y0), 0, 1)*np.isin(mp, [MID['metal'], MID['cy_mid'], MID['cy_dark'], MID['hull_dark']])
    return f

# =========================================================== Wasp (T3, Cybran AA missiles, 3x3)
def wasp():
    M = Model(); g = 'base'
    cy_base(M, g, 1.5)
    ring(M, g, 0.96, 0.16, 0.20, 'cy_mid')
    g = 'body'
    M.add(g, prism(octo(0.80), 0.20, 0.42, 0.88), 'cy_dark')
    M.add(g, prism(octo(0.58), 0.42, 0.58, 0.88), 'cy_mid')
    # radar dish (rear)
    M.add(g, cyl((0, -0.30, 0.58), (0, -0.30, 0.70), 0.06, n=8), 'metal')
    dish = [(0.34*math.cos(a), -0.30+0.20*math.sin(a)) for a in np.linspace(0, 2*math.pi, 16, endpoint=False)]
    M.add(g, prism(P(dish), 0.70, 0.76, 0.75), 'metal_light')
    M.add(g, cbox(0, -0.30, 0.77, 0.04, 0.04, 0.02), 'rglow')
    for s in (-1, 1):
        cx = s*0.66
        M.add(g, prism(cham_rect(0.30, 0.56, 0.12, cx=cx, cy=0.18), 0.44, 0.80, 0.9), 'red_armor')
        for i in range(2):
            for j in range(2):
                x = cx + (-0.12 + 0.24*i); z = 0.66 + 0.10*j
                M.add(g, cyl((x, -0.20, z), (x, 0.86, z), 0.085, n=10), 'cy_mid')
                M.add(g, cyl((x, 0.86, z), (x, 0.88, z), 0.06, n=10), 'bore')
                M.add(g, cyl((x, 0.74, z), (x, 0.86, z), 0.055, n=8, r1=0.012), 'rglow')
        M.add(g, cbox(cx, -0.30, 0.805, 0.36, 0.05, 0.01), 'rglow')
        M.add(g, cyl((s*0.28, 0.18, 0.62), (s*0.40, 0.18, 0.62), 0.10, n=10), 'metal')
    return M

# =========================================================== Rivet (T1, UEF twin machine gun, 2x2)
def rivet():
    M = Model(); g = 'base'
    uef_base(M, g, 1.0)
    ring(M, g, 0.66, 0.17, 0.20)
    g = 'body'
    M.add(g, prism(octo(0.56), 0.20, 0.36, 0.9), 'hull_mid')
    M.add(g, prism(cham_rect(0.36, 0.40, 0.10, cy=0.02), 0.36, 0.52, 0.86), 'hull_light')
    M.add(g, cbox(0, -0.30, 0.525, 0.40, 0.06, 0.01), 'yellow')
    M.add(g, cbox(0.50, -0.06, 0.40, 0.20, 0.36, 0.20), 'hull_dark')   # ammo box
    M.add(g, cbox(0.50, -0.06, 0.505, 0.16, 0.30, 0.01), 'copper')
    M.add(g, tube_path([(0.42, 0.10, 0.44), (0.24, 0.22, 0.46)], 0.03, n=6), 'metal')
    for x in (-0.11, 0.11):
        M.add(g, cyl((x, 0.30, 0.44), (x, 0.62, 0.44), 0.07, n=12), 'hull_mid')
        M.add(g, cyl((x, 0.62, 0.44), (x, 1.10, 0.44), 0.042, n=10), 'metal')
        M.add(g, cyl((x, 1.04, 0.44), (x, 1.14, 0.44), 0.058, n=10), 'hull_dark')
        M.add(g, cyl((x, 1.14, 0.44), (x, 1.15, 0.44), 0.03, n=8), 'bore')
    light(M, g, -0.24, -0.16, 0.52, 0.06, 0.06)
    bolts(M, g, [(-0.28, 0.32), (0.28, 0.32), (-0.28, -0.24), (0.28, -0.24)], 0.52, r=0.02)
    return M

# =========================================================== Sparrow (T1, UEF quad flak, 2x2)
def sparrow():
    M = Model(); g = 'base'
    uef_base(M, g, 1.0)
    ring(M, g, 0.66, 0.17, 0.20)
    g = 'body'
    M.add(g, cyl((0, 0, 0.20), (0, 0, 0.36), 0.58, n=16), 'hull_mid')
    M.add(g, cyl((0, 0, 0.36), (0, 0, 0.40), 0.50, n=16), 'hull_dark')
    for s in (-1, 1):
        M.add(g, prism(cham_rect(0.20, 0.40, 0.06, cx=s*0.30, cy=0.10), 0.36, 0.60, 0.88), 'hull_light')
        M.add(g, cbox(s*0.30, -0.22, 0.605, 0.30, 0.05, 0.01), 'yellow')
        for j, z in enumerate((0.50, 0.58)):
            x = s*(0.22 if j == 0 else 0.38)
            M.add(g, cyl((x, 0.30, z), (x, 0.92, z), 0.05, n=10), 'metal')
            M.add(g, cyl((x, 0.84, z), (x, 0.96, z), 0.068, n=10), 'hull_dark')
            M.add(g, cyl((x, 0.96, z), (x, 0.97, z), 0.035, n=8), 'bore')
    M.add(g, cyl((0, -0.12, 0.40), (0, -0.12, 0.52), 0.14, n=10), 'hull_mid')
    M.add(g, cyl((0, -0.12, 0.52), (0, -0.12, 0.55), 0.10, n=10), 'glass')
    light(M, g, 0, 0.30, 0.40, 0.08, 0.05)
    return M
