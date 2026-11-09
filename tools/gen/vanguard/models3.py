"""Stage 2 models: ACUs (UEF / Cybran), engineer, BKM cores, engineering bay.
Units: 1.0 = one tile (32 px). Units face +Y. Mech layers: leg (right foot only), base, body, guns."""
import numpy as np, math
from geom import *
from mats import Model
from models import bolts, light, vent, chevrons, uef_base
from models2 import frame, octo

def hexa(r, cx=0, cy=0, ph=30):
    return ccw([(cx+r*math.cos(math.radians(ph+60*k)), cy+r*math.sin(math.radians(ph+60*k))) for k in range(6)])

def poly_x(P, s, cx=0, cy=0):
    return ccw([(cx+s*x, cy+y) for x, y in P])

def add_rot(M, g, sub, R, t=(0, 0, 0)):
    for gg, parts in sub.parts.items():
        for T, m in parts:
            M.add(g, tf(T, R, t), m)

# =============================================================== UEF ACU  "Страж"
def acu_uef():
    M = Model()
    # ---- leg (right foot, x=+0.40)
    g = 'leg'; X = 0.40
    M.add(g, prism(cham_rect(0.13, 0.29, 0.05, cx=X, cy=0.02), 0, 0.10, 0.9), 'hull_mid')
    M.add(g, prism(cham_rect(0.15, 0.075, 0.035, cx=X, cy=0.31), 0, 0.085, 0.85), 'hull_dark')
    M.add(g, prism(cham_rect(0.12, 0.05, 0.02, cx=X, cy=0.33), 0.085, 0.10), 'yellow')
    M.add(g, cbox(X, -0.27, 0.05, 0.19, 0.10, 0.10), 'hull_dark')
    M.add(g, prism(cham_rect(0.095, 0.17, 0.04, cx=X, cy=0.03), 0.10, 0.21, 0.82), 'hull_light')
    M.add(g, cbox(X, 0.15, 0.215, 0.13, 0.03, 0.012), 'yellow')
    M.add(g, cyl((X-0.10, -0.06, 0.23), (X+0.10, -0.06, 0.23), 0.055, n=12), 'metal')
    M.add(g, cyl((X, -0.22, 0.10), (X, -0.08, 0.22), 0.026, n=8), 'metal_light')
    bolts(M, g, [(X-0.07, 0.17), (X+0.07, 0.17), (X-0.07, -0.10), (X+0.07, -0.10)], 0.10, r=0.018)
    # ---- base (pelvis)
    g = 'base'
    M.add(g, prism(cham_rect(0.30, 0.17, 0.06), 0.18, 0.31, 0.9), 'hull_dark')
    for s in (-1, 1):
        M.add(g, cyl((s*0.24, 0, 0.26), (s*0.42, 0, 0.26), 0.085, n=14), 'metal')
        M.add(g, cyl((s*0.42, 0, 0.26), (s*0.46, 0, 0.26), 0.06, n=12), 'hull_mid')
    M.add(g, cyl((0, 0, 0.31), (0, 0, 0.34), 0.13, n=16), 'metal')
    # ---- body (torso)
    g = 'body'
    M.add(g, cyl((0, 0, 0.32), (0, 0, 0.40), 0.20, n=16), 'metal')
    M.add(g, prism(cham_rect(0.40, 0.29, 0.10, cy=0.02), 0.38, 0.57, 0.88), 'hull_mid')
    M.add(g, prism(cham_rect(0.32, 0.21, 0.08, cy=0.04), 0.57, 0.61, 0.93), 'hull_light')
    M.add(g, prism(cham_rect(0.065, 0.19, 0.02, cy=0.03), 0.61, 0.625), 'team')
    for s in (-1, 1):
        M.add(g, prism(cham_rect(0.05, 0.11, 0.015, cx=s*0.19, cy=0.06), 0.61, 0.62), 'hull_dark')
    # head / cockpit
    M.add(g, prism(cham_rect(0.13, 0.085, 0.04, cy=0.29), 0.46, 0.60, 0.84), 'hull_light')
    M.add(g, cbox(0, 0.365, 0.555, 0.17, 0.03, 0.03), 'glow')
    M.add(g, sphereish((0, 0.24, 0.62), 0.055, n=10), 'glass')
    # shoulders
    for s in (-1, 1):
        M.add(g, cyl((s*0.34, 0, 0.47), (s*0.46, 0, 0.47), 0.09, n=12), 'metal')
        M.add(g, prism(cham_rect(0.17, 0.22, 0.07, cx=s*0.51, cy=0.0), 0.50, 0.66, 0.82), 'hull_light')
        M.add(g, prism(cham_rect(0.105, 0.145, 0.045, cx=s*0.51, cy=-0.01), 0.66, 0.675), 'team')
        M.add(g, cbox(s*0.51, 0.205, 0.625, 0.25, 0.035, 0.04), 'yellow')
        light(M, g, s*0.62, 0.15, 0.62, 0.035, 0.035, 0.015)
        bolts(M, g, [(s*0.40, 0.17), (s*0.62, -0.17), (s*0.40, -0.17)], 0.66, r=0.016)
    # reactor backpack + jump jets
    M.add(g, prism(cham_rect(0.29, 0.13, 0.05, cy=-0.30), 0.42, 0.64, 0.9), 'hull_dark')
    vent(M, g, 0, -0.33, 0.64, 0.38, 0.11, slats=7)
    light(M, g, 0, -0.205, 0.635, 0.12, 0.025, 0.012)
    for s in (-1, 1):
        M.add(g, cyl((s*0.18, -0.38, 0.52), (s*0.18, -0.49, 0.47), 0.07, 0.085, n=12), 'metal')
        M.add(g, cyl((s*0.18, -0.485, 0.472), (s*0.18, -0.50, 0.466), 0.06, n=12), 'vent')
    M.add(g, cyl((-0.24, -0.20, 0.62), (-0.24, -0.20, 0.80), 0.012, n=6), 'metal_light')
    M.add(g, cbox(-0.24, -0.20, 0.805, 0.03, 0.03, 0.02), 'glow')
    bolts(M, g, [(-0.33, 0.25), (0.33, 0.25), (-0.33, -0.21), (0.33, -0.21)], 0.57, r=0.017)
    # ---- right arm: Zephyr plasma cannon
    g = 'gunR'
    M.add(g, cyl((0, -0.40, 0.40), (0, -0.22, 0.40), 0.09, n=12), 'metal')
    M.add(g, prism(cham_rect(0.12, 0.22, 0.045, cy=-0.06), 0.30, 0.50, 0.84), 'hull_mid')
    M.add(g, prism(cham_rect(0.088, 0.165, 0.03, cy=-0.07), 0.50, 0.53), 'hull_light')
    M.add(g, cbox(0, -0.12, 0.535, 0.05, 0.17, 0.012), 'team')
    M.add(g, cyl((0, 0.10, 0.42), (0, 0.36, 0.42), 0.078, n=14), 'hull_dark')
    M.add(g, cyl((0, 0.10, 0.42), (0, 0.60, 0.42), 0.048, n=14), 'metal')
    for yy in (0.40, 0.48):
        M.add(g, cyl((0, yy, 0.42), (0, yy+0.028, 0.42), 0.064, n=14), 'glow')
    M.add(g, cyl((0, 0.58, 0.42), (0, 0.64, 0.42), 0.062, 0.046, n=14), 'metal_light')
    bolts(M, g, [(-0.07, 0.10), (0.07, 0.10)], 0.50, r=0.015)
    # ---- left arm: tactical missile pod
    g = 'gunL'
    M.add(g, cyl((0, -0.40, 0.40), (0, -0.22, 0.40), 0.09, n=12), 'metal')
    M.add(g, prism(cham_rect(0.15, 0.25, 0.05, cy=0.0), 0.30, 0.54, 0.88), 'hull_mid')
    M.add(g, prism(cham_rect(0.115, 0.19, 0.035, cy=-0.02), 0.54, 0.565), 'hull_light')
    chevrons(M, g, 0, -0.13, 0.565, 0.20, 0.07, n=3)
    for dx in (-0.06, 0.06):
        M.add(g, cbox(dx, 0.07, 0.572, 0.075, 0.13, 0.012), 'hull_dark')
        M.add(g, cbox(dx, 0.07, 0.578, 0.05, 0.10, 0.008), 'red_armor')
        for dz in (0.38, 0.48):
            M.add(g, cyl((dx, 0.20, dz), (dx, 0.285, dz), 0.042, n=10), 'metal')
            M.add(g, cyl((dx, 0.284, dz), (dx, 0.29, dz), 0.03, n=10), 'bore')
    M.add(g, cbox(0.135, 0.0, 0.45, 0.04, 0.30, 0.08), 'team')
    return M

# =============================================================== Cybran ACU  "Призрак"
def acu_cybran():
    M = Model()
    g = 'leg'; X = 0.40
    M.add(g, cyl((X, 0, 0.03), (X, 0, 0.15), 0.075, n=6), 'cy_mid')
    toe = ccw([(-0.04, 0), (0.04, 0), (0.018, 0.31), (-0.018, 0.31)])
    for a in (-22, 22):
        M.add(g, tf(prism(toe, 0, 0.075, 0.75), rz(a), (X, 0.02, 0)), 'cy_dark')
        tip = tf(np.array([[0, 0.30, 0.03]]), rz(a), (X, 0.02, 0))[0]
        M.add(g, cyl(tip, tip + np.array([0, 0, 0.05]), 0.022, n=6), 'red_armor')
    M.add(g, tf(prism(ccw([(-0.035, 0), (0.035, 0), (0.0, 0.20)]), 0, 0.06, 0.7), rz(180), (X, -0.03, 0)), 'cy_dark')
    M.add(g, prism(cham_rect(0.062, 0.17, 0.03, cx=X, cy=-0.03), 0.12, 0.25, 0.78), 'cy_mid')
    M.add(g, cbox(X, -0.03, 0.253, 0.022, 0.21, 0.01), 'rglow')
    M.add(g, cyl((X-0.09, -0.12, 0.24), (X+0.09, -0.12, 0.24), 0.045, n=6), 'metal')
    g = 'base'
    M.add(g, prism(hexa(0.24), 0.18, 0.31, 0.88), 'cy_dark')
    for s in (-1, 1):
        M.add(g, cyl((s*0.20, 0, 0.26), (s*0.42, 0, 0.26), 0.075, n=6), 'metal')
        M.add(g, cyl((s*0.42, 0, 0.26), (s*0.45, 0, 0.26), 0.05, n=6), 'red_armor')
    M.add(g, cyl((0, 0, 0.31), (0, 0, 0.34), 0.11, n=6), 'cy_mid')
    g = 'body'
    torso = ccw([(0, 0.42), (0.28, 0.20), (0.37, -0.08), (0.22, -0.34), (-0.22, -0.34), (-0.37, -0.08), (-0.28, 0.20)])
    M.add(g, prism(torso, 0.36, 0.55, 0.86), 'cy_mid')
    M.add(g, prism(scale_poly(torso, 0.70), 0.55, 0.60, 0.92), 'cy_dark')
    M.add(g, cbox(0, -0.04, 0.603, 0.03, 0.46, 0.01), 'rglow')
    for s in (-1, 1):
        M.add(g, tf(cbox(0, 0, 0.603, 0.022, 0.20, 0.01), rz(-s*40), (s*0.15, 0.10, 0)), 'rglow')
        M.add(g, tf(prism(ccw([(-0.05, -0.10), (0.05, -0.10), (0.035, 0.10), (-0.035, 0.10)]), 0.60, 0.615), rz(s*25), (s*0.17, -0.17, 0)), 'team')
    # head: wedge + single eye
    M.add(g, prism(ccw([(0, 0.48), (0.10, 0.30), (0.07, 0.20), (-0.07, 0.20), (-0.10, 0.30)]), 0.46, 0.62, 0.7), 'cy_dark')
    M.add(g, sphereish((0, 0.35, 0.60), 0.04, n=8), 'rglow')
    # shoulders with spikes
    sh = [(-0.12, -0.16), (0.15, -0.13), (0.19, 0.08), (0.03, 0.21), (-0.12, 0.10)]
    for s in (-1, 1):
        M.add(g, cyl((s*0.30, 0, 0.47), (s*0.44, 0, 0.47), 0.08, n=6), 'metal')
        M.add(g, prism(poly_x(sh, s, s*0.50, 0), 0.48, 0.64, 0.74), 'cy_mid')
        M.add(g, prism(poly_x([(x*0.6, y*0.6) for x, y in sh], s, s*0.51, 0), 0.64, 0.655), 'team')
        for k, (dx, dy) in enumerate(((0.06, -0.10), (0.13, -0.02))):
            p0 = (s*(0.50+dx*0.5), dy, 0.62); p1 = (s*(0.58+dx), dy-0.20, 0.72)
            M.add(g, cyl(p0, p1, 0.035, 0.004, n=6), 'cy_dark')
        M.add(g, cbox(s*0.60, 0.08, 0.60, 0.03, 0.03, 0.02), 'rglow')
    # stealth field generator
    M.add(g, cyl((0, -0.32, 0.40), (0, -0.32, 0.63), 0.13, 0.11, n=6), 'cy_dark')
    frame(M, g, hexa(0.10, 0, -0.32), hexa(0.065, 0, -0.32), 0.63, 0.645, 'red_armor')
    M.add(g, cyl((0, -0.32, 0.63), (0, -0.32, 0.64), 0.06, n=6), 'rglow')
    for s in (-1, 1):
        M.add(g, cyl((s*0.14, -0.40, 0.50), (s*0.14, -0.50, 0.46), 0.05, 0.06, n=6), 'metal')
        M.add(g, cyl((s*0.14, -0.495, 0.462), (s*0.14, -0.505, 0.458), 0.04, n=6), 'rglow')
    # right arm: microwave laser
    g = 'gunR'
    M.add(g, cyl((0, -0.40, 0.40), (0, -0.22, 0.40), 0.08, n=6), 'metal')
    M.add(g, prism(cham_rect(0.10, 0.21, 0.045, cy=-0.08), 0.30, 0.49, 0.82), 'cy_mid')
    M.add(g, cbox(0, -0.12, 0.495, 0.04, 0.20, 0.01), 'team')
    M.add(g, cyl((0, 0.06, 0.40), (0, 0.62, 0.40), 0.034, n=6), 'cy_dark')
    for yy in (0.16, 0.25, 0.34, 0.43):
        M.add(g, cyl((0, yy, 0.40), (0, yy+0.035, 0.40), 0.062, n=6), 'red_armor')
    M.add(g, cyl((0, 0.52, 0.40), (0, 0.60, 0.40), 0.05, 0.03, n=6), 'metal')
    M.add(g, cyl((0, 0.60, 0.40), (0, 0.65, 0.40), 0.035, n=6), 'rglow')
    # left arm: EMP prongs
    g = 'gunL'
    M.add(g, cyl((0, -0.40, 0.40), (0, -0.22, 0.40), 0.08, n=6), 'metal')
    M.add(g, prism(hexa(0.13, 0, -0.06), 0.30, 0.50, 0.8), 'cy_mid')
    M.add(g, cyl((0, -0.06, 0.50), (0, -0.06, 0.515), 0.06, n=6), 'rglow')
    for s in (-1, 1):
        M.add(g, cyl((s*0.05, 0.04, 0.40), (s*0.085, 0.42, 0.42), 0.035, 0.014, n=6), 'cy_dark')
        M.add(g, cyl((s*0.085, 0.40, 0.42), (s*0.075, 0.44, 0.42), 0.018, n=6), 'red_armor')
    M.add(g, sphereish((0, 0.30, 0.42), 0.035, n=8), 'rglow')
    M.add(g, cbox(-0.115, -0.06, 0.45, 0.03, 0.18, 0.06), 'team')
    return M

# =============================================================== UEF engineer
def engineer():
    M = Model()
    # hover drone: two side hover pods with lift fans (flying low-altitude builder)
    g = 'body'
    for s in (-1, 1):
        X = s*0.255
        M.add(g, prism(cham_rect(0.065, 0.20, 0.03, cx=X, cy=-0.01), 0.06, 0.17, 0.86), 'hull_dark')
        M.add(g, cbox(X, 0.185, 0.12, 0.11, 0.04, 0.07), 'yellow')
        for fy in (0.07, -0.11):
            M.add(g, cyl((X, fy, 0.17), (X, fy, 0.185), 0.052, n=14), 'metal')
            M.add(g, cyl((X, fy, 0.185), (X, fy, 0.19), 0.034, n=12), 'glow')
            M.add(g, cbox(X, fy, 0.192, 0.075, 0.012, 0.004), 'metal_light')
        M.add(g, cyl((s*0.16, -0.01, 0.12), (s*0.20, -0.01, 0.12), 0.04, n=10), 'metal_light')
    M.add(g, prism(cham_rect(0.20, 0.19, 0.05), 0.13, 0.26, 0.88), 'hull_mid')
    M.add(g, prism(cham_rect(0.165, 0.10, 0.03, cy=-0.07), 0.26, 0.27), 'hull_dark')
    chevrons(M, g, 0.0, -0.12, 0.27, 0.26, 0.07, n=4)
    M.add(g, cbox(0.0, -0.035, 0.30, 0.18, 0.07, 0.06), 'steel')
    M.add(g, prism(cham_rect(0.075, 0.065, 0.02, cx=-0.09, cy=0.09), 0.26, 0.34, 0.85), 'hull_light')
    M.add(g, cbox(-0.09, 0.145, 0.315, 0.10, 0.015, 0.03), 'glow')
    M.add(g, prism(cham_rect(0.04, 0.05, 0.01, cx=-0.09, cy=0.08), 0.34, 0.347), 'team')
    M.add(g, prism(cham_rect(0.03, 0.15, 0.01, cx=0.165, cy=0.0), 0.26, 0.268), 'team')
    M.add(g, cyl((0.08, 0.04, 0.26), (0.08, 0.04, 0.31), 0.05, n=12), 'metal')
    M.add(g, tube_path([(0.08, 0.04, 0.31), (0.08, 0.20, 0.38), (0.035, 0.33, 0.35)], 0.022, n=8), 'yellow')
    M.add(g, cyl((0.035, 0.33, 0.35), (0.03, 0.40, 0.33), 0.03, 0.02, n=10), 'metal_light')
    M.add(g, cyl((0.03, 0.40, 0.33), (0.03, 0.415, 0.325), 0.016, n=8), 'glow')
    M.add(g, cyl((-0.15, -0.14, 0.26), (-0.15, -0.14, 0.33), 0.022, n=8), 'metal')
    M.add(g, cyl((-0.15, -0.14, 0.33), (-0.15, -0.14, 0.355), 0.026, n=8), 'flame')
    M.add(g, cyl((0.15, -0.16, 0.26), (0.15, -0.16, 0.40), 0.007, n=5), 'metal_light')
    for s in (-1, 1):
        M.add(g, cyl((s*0.10, -0.19, 0.20), (s*0.10, -0.24, 0.18), 0.04, 0.05, n=10), 'metal')
    bolts(M, g, [(-0.17, 0.16), (0.17, 0.16), (-0.17, -0.16), (0.17, -0.16)], 0.26, r=0.012, h=0.01)
    return M

# =============================================================== UEF command complex (core, 4x4)
def core_uef():
    M = Model(); g = 'main'
    uef_base(M, g, 2.0, top=0.17)
    M.add(g, prism(cham_rect(1.45, 1.45, 0.40), 0.17, 0.30, 0.95), 'hull_mid')
    M.add(g, prism(cham_rect(1.36, 1.36, 0.37), 0.30, 0.33, 0.97), 'hull_light')
    for k in range(4):
        R = rz(90*k)
        M.add(g, tf(prism(cham_rect(0.44, 0.065, 0.03, cy=-1.21), 0.33, 0.345), R), 'team')
        sub = Model()
        vent(sub, 'v', 0.0, -0.98, 0.33, 0.62, 0.12, slats=8)
        chevrons(sub, 'v', 0.0, -1.30, 0.30, 0.60, 0.07, n=5)
        add_rot(M, g, sub, R)
    # bridges to pylons
    for k in range(4):
        R = rz(45+90*k)
        M.add(g, tf(box(-0.07, 0.07, 0.58, 1.30, 0.33, 0.40), R), 'metal')
        M.add(g, tf(box(-0.025, 0.025, 0.62, 1.26, 0.40, 0.41), R), 'cable')
    # central command tower
    M.add(g, prism(octo(0.66), 0.33, 0.70, 0.82), 'hull_mid')
    M.add(g, prism(octo(0.53), 0.70, 0.74, 0.97), 'hull_light')
    frame(M, g, octo(0.50), octo(0.38), 0.74, 0.78, 'metal')
    M.add(g, cyl((0, 0, 0.74), (0, 0, 0.755), 0.37, n=32), 'hull_dark')
    frame(M, g, octo(0.31), octo(0.25), 0.755, 0.77, 'team')
    M.add(g, cyl((0, 0, 0.755), (0, 0, 0.775), 0.10, n=16), 'glow')
    for k in range(8):
        a = math.radians(22.5+45*k)
        light(M, g, 0.44*math.cos(a), 0.44*math.sin(a), 0.78, 0.04, 0.04, 0.012)
    # pylons: 3 defence pylons + 1 comm dish
    for i, (sx, sy) in enumerate(((-1, -1), (1, -1), (-1, 1), (1, 1))):
        x, y = sx*1.06, sy*1.06
        M.add(g, prism(octo(0.24, x, y), 0.33, 0.50, 0.86), 'hull_dark')
        if i == 3:
            M.add(g, cyl((x, y, 0.50), (x, y, 0.62), 0.06, n=10), 'metal')
            M.add(g, cyl((x, y, 0.62), (x, y, 0.69), 0.15, 0.30, n=24), 'metal_light')
            M.add(g, cyl((x, y, 0.69), (x, y, 0.695), 0.22, n=24), 'metal')
            M.add(g, cyl((x, y, 0.69), (x, y, 0.80), 0.02, n=6), 'metal_light')
            M.add(g, cbox(x, y, 0.81, 0.04, 0.04, 0.02), 'glow')
        else:
            M.add(g, cyl((x, y, 0.50), (x, y, 0.62), 0.16, 0.13, n=16), 'metal')
            M.add(g, cyl((x, y, 0.62), (x, y, 0.635), 0.15, n=16), 'yellow')
            M.add(g, cyl((x, y, 0.635), (x, y, 0.66), 0.08, n=12), 'glow')
    pts = [(sx*0.45, sy*1.33) for sx in (-1, 1) for sy in (-1, 1)] + [(sx*1.33, sy*0.45) for sx in (-1, 1) for sy in (-1, 1)]
    bolts(M, g, pts, 0.33, r=0.03)
    return M

# =============================================================== Cybran nexus (core, 4x4)
def core_cybran():
    M = Model(); g = 'main'
    M.add(g, prism(cham_rect(1.97, 1.97, 0.62), 0, 0.10, 0.985), 'cy_dark')
    M.add(g, prism(cham_rect(1.76, 1.76, 0.56), 0.10, 0.20, 0.96), 'cy_mid')
    for k in range(4):
        R = rz(45+90*k)
        M.add(g, tf(box(-0.09, 0.09, 1.02, 1.95, 0.20, 0.26), R), 'cy_dark')
        M.add(g, tf(box(-0.025, 0.025, 1.05, 1.90, 0.26, 0.272), R), 'rglow')
    for k in range(4):
        R = rz(90*k)
        # cardinal spikes
        M.add(g, tf(cyl((0, -1.36, 0.20), (0, -1.36, 0.30), 0.24, 0.21, n=6), R), 'cy_dark')
        M.add(g, tf(cyl((0, -1.36, 0.30), (0, -1.36, 0.86), 0.19, 0.03, n=6), R), 'cy_mid')
        M.add(g, tf(cyl((0, -1.36, 0.30), (0, -1.36, 0.315), 0.21, n=6), R), 'rglow')
        M.add(g, tf(prism(ccw([(-0.30, -1.80), (0.30, -1.80), (0.18, -1.60), (-0.18, -1.60)]), 0.20, 0.235), R), 'team')
        M.add(g, tf(cbox(0.0, -1.02, 0.21, 0.22, 0.05, 0.02), R), 'red_armor')
    # quantum gate
    frame(M, g, octo(1.02), octo(0.80), 0.20, 0.50, 'cy_mid')
    frame(M, g, octo(0.94), octo(0.86), 0.50, 0.52, 'cy_dark')
    frame(M, g, octo(0.80), octo(0.67), 0.20, 0.44, 'red_armor')
    M.add(g, cyl((0, 0, 0.20), (0, 0, 0.24), 0.68, n=8, phase=math.radians(22.5)), 'cy_dark')
    M.add(g, cyl((0, 0, 0.24), (0, 0, 0.25), 0.46, n=24), 'rglow')
    M.add(g, cyl((0, 0, 0.25), (0, 0, 0.26), 0.36, n=24), 'cy_dark')
    for k in range(6):
        a = math.radians(60*k)
        M.add(g, tf(box(-0.02, 0.02, 0.10, 0.34, 0.255, 0.265), rz(60*k+15)), 'rglow')
    M.add(g, cyl((0, 0, 0.26), (0, 0, 0.60), 0.13, 0.06, n=6), 'cy_mid')
    M.add(g, sphereish((0, 0, 0.62), 0.06, n=8), 'rglow')
    for k in range(8):
        a = math.radians(22.5+45*k)
        M.add(g, cbox(0.97*math.cos(a), 0.97*math.sin(a), 0.525, 0.05, 0.05, 0.02), 'rglow')
    for sx in (-1, 1):
        for sy in (-1, 1):
            M.add(g, prism(hexa(0.20, sx*1.42, sy*1.42), 0.20, 0.40, 0.8), 'cy_mid')
            M.add(g, prism(hexa(0.12, sx*1.42, sy*1.42), 0.40, 0.42), 'team')
            M.add(g, cyl((sx*1.42, sy*1.42, 0.42), (sx*1.42, sy*1.42, 0.44), 0.05, n=6), 'rglow')
    return M

# =============================================================== Engineering bay (UnitFactory 3x3)
def bay():
    M = Model()
    g = 'main'
    M.add(g, prism(cham_rect(1.48, 1.48, 0.26), 0, 0.08), 'hull_dark')
    M.add(g, prism(cham_rect(1.16, 1.16, 0.18), 0.08, 0.10), 'ground')
    for i in range(-3, 4):
        M.add(g, cbox(i*0.32, 0, 0.102, 0.012, 2.1, 0.004), 'hull_dark')
        M.add(g, cbox(0, i*0.32, 0.102, 2.1, 0.012, 0.004), 'hull_dark')
    frame(M, g, octo(0.785), octo(0.755), 0.10, 0.108, 'yellow')
    for k in range(8):
        a = math.radians(45*k)
        M.add(g, cbox(0.77*math.cos(a), 0.77*math.sin(a), 0.115, 0.05, 0.05, 0.012), 'glow')
    g = 'out'
    for i in range(3):
        x = 0.80 + i*0.12
        p = ccw([(x-0.05, -0.12), (x, -0.12), (x+0.07, 0.0), (x, 0.12), (x-0.05, 0.12), (x+0.02, 0.0)])
        M.add(g, prism(p, 0.10, 0.115), 'yellow')
    g = 'top'
    frame(M, g, cham_rect(1.48, 1.48, 0.26), cham_rect(1.10, 1.10, 0.18), 0.08, 0.26, 'hull_mid')
    frame(M, g, cham_rect(1.40, 1.40, 0.245), cham_rect(1.17, 1.17, 0.19), 0.26, 0.29, 'hull_light')
    for k in range(4):
        R = rz(90*k)
        sub = Model()
        chevrons(sub, 'v', 0.0, -1.29, 0.29, 0.80, 0.09, n=6)
        add_rot(M, g, sub, R)
    for s in (-1, 1):
        M.add(g, box(s*1.18, s*1.26, -1.05, 1.05, 0.29, 0.37) if s > 0 else box(-1.26, -1.18, -1.05, 1.05, 0.29, 0.37), 'metal')
        M.add(g, cbox(s*1.22, 0.45, 0.40, 0.20, 0.22, 0.08), 'yellow')
        M.add(g, cbox(s*1.22, 0.45, 0.445, 0.12, 0.14, 0.012), 'hull_dark')
        M.add(g, tube_path([(s*1.15, 0.45, 0.40), (s*1.02, 0.40, 0.42), (s*0.93, 0.36, 0.36)], 0.024, n=8), 'metal_light')
        M.add(g, cyl((s*0.93, 0.36, 0.36), (s*0.90, 0.34, 0.33), 0.02, n=8), 'flame')
    for sx in (-1, 1):
        for sy in (-1, 1):
            x, y = sx*1.27, sy*1.27
            M.add(g, prism(cham_rect(0.16, 0.16, 0.05, cx=x, cy=y), 0.08, 0.46, 0.85), 'hull_dark')
            M.add(g, prism(cham_rect(0.12, 0.12, 0.04, cx=x, cy=y), 0.46, 0.48), 'yellow')
            light(M, g, x, y, 0.48, 0.05, 0.05, 0.015)
    bolts(M, g, [(sx*0.6, sy*1.33) for sx in (-1, 1) for sy in (-1, 1)], 0.29, r=0.02)
    return M
