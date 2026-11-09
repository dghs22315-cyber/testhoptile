"""Stage 1 models part 2: crafters, defence, walls, items, ores."""
import numpy as np, math
from geom import *
from mats import Model, MID
from models import bolts, light, vent, chevrons, uef_base

def frame(M, g, outer, inner, z0, z1, m, top_scale=1.0):
    """annulus between two matching 8-vertex polygons"""
    o = np.asarray(outer); i = np.asarray(inner); n = len(o)
    for k in range(n):
        q = ccw([tuple(o[k]), tuple(o[(k+1) % n]), tuple(i[(k+1) % n]), tuple(i[k])])
        M.add(g, prism(q, z0, z1), m)

def octo(r, cx=0, cy=0, ph=22.5):
    return ccw([(cx+r*math.cos(math.radians(ph+45*k)), cy+r*math.sin(math.radians(ph+45*k))) for k in range(8)])

# ------------------------------------------------ Mass separator I (2x2)
def separator():
    M = Model()
    g = 'bottom'
    M.add(g, prism(cham_rect(0.985, 0.985, 0.28), 0, 0.08), 'hull_dark')
    M.add(g, cyl((0, 0, 0.08), (0, 0, 0.085), 0.56, n=28), 'vent')
    g = 'spinner'
    M.add(g, cyl((0, 0, 0.10), (0, 0, 0.20), 0.12, n=16), 'metal_light')
    M.add(g, cyl((0, 0, 0.20), (0, 0, 0.22), 0.07, n=12), 'yellow')
    for k in range(4):
        R = rz(45 + 90*k)
        M.add(g, tf(box(0.10, 0.47, -0.045, 0.045, 0.10, 0.17), R), 'metal')
        M.add(g, tf(box(0.40, 0.47, -0.05, 0.05, 0.17, 0.18), R), 'yellow')
        M.add(g, tf(box(0.14, 0.38, -0.02, 0.02, 0.17, 0.185), R), 'metal_light')
    for k in range(16):
        a0 = 2*math.pi*k/16; a1 = 2*math.pi*(k+1)/16
        q = ccw([(0.44*math.cos(a0), 0.44*math.sin(a0)), (0.44*math.cos(a1), 0.44*math.sin(a1)),
                 (0.49*math.cos(a1), 0.49*math.sin(a1)), (0.49*math.cos(a0), 0.49*math.sin(a0))])
        M.add(g, prism(q, 0.10, 0.15), 'metal')
    g = 'main'
    outer = cham_rect(0.985, 0.985, 0.28); inner = cham_rect(0.50, 0.50, 0.21)
    frame(M, g, outer, inner, 0.0, 0.10, 'hull_dark')
    o2 = cham_rect(0.86, 0.86, 0.26); i2 = cham_rect(0.56, 0.56, 0.23)
    frame(M, g, o2, i2, 0.10, 0.20, 'hull_mid')
    frame(M, g, cham_rect(0.585, 0.585, 0.24), cham_rect(0.53, 0.53, 0.22), 0.20, 0.23, 'metal')
    # corner hoppers (output bins) with ore
    for (sx, sy, ore) in ((1, 1, 'ore_fer'), (-1, 1, 'ore_salt'), (1, -1, 'ore_fer'), (-1, -1, 'ore_salt')):
        cx, cy = sx*0.73, sy*0.73
        p = ccw([(cx-0.13*sx, cy-0.02*sy), (cx+0.10*sx, cy-0.02*sy), (cx+0.10*sx, cy+0.10*sy), (cx-0.02*sx, cy+0.10*sy), (cx-0.13*sx, cy-0.0)])
        M.add(g, prism(cham_rect(0.13, 0.13, 0.04, cx, cy), 0.10, 0.27, 0.9), 'hull_light')
        M.add(g, prism(cham_rect(0.09, 0.09, 0.03, cx, cy), 0.27, 0.275), 'vent')
        for j in range(5):
            r = np.random.default_rng(abs(int(100*cx+10*cy))*10+j)
            ox, oy = r.uniform(-0.05, 0.05, 2)
            M.add(g, sphereish((cx+ox, cy+oy, 0.275), 0.03, 6), ore)
    # slag intake pipe
    M.add(g, tube_path([(0.98, 0.0, 0.14), (0.72, 0.0, 0.22), (0.60, 0.0, 0.22)], 0.05, n=10), 'metal')
    M.add(g, cyl((0.66, 0.0, 0.22), (0.70, 0.0, 0.22), 0.07, n=10), 'yellow')
    M.add(g, tube_path([(-0.98, 0.0, 0.14), (-0.72, 0.0, 0.22), (-0.60, 0.0, 0.22)], 0.035, n=8), 'cable')
    light(M, g, 0.0, 0.70, 0.20, 0.10, 0.04, 0.012)
    light(M, g, 0.0, -0.70, 0.20, 0.10, 0.04, 0.012)
    chevrons(M, g, 0.0, 0.82, 0.10, 0.36, 0.08, 4)
    chevrons(M, g, 0.0, -0.82, 0.10, 0.36, 0.08, 4)
    bolts(M, g, [(0.56*math.cos(math.radians(22.5+45*k)), 0.56*math.sin(math.radians(22.5+45*k))) for k in range(8)], 0.23, r=0.02)
    return M

# ------------------------------------------------ Steel smelter (2x2)
def smelter():
    M = Model(); g = 'main'
    uef_base(M, g, 1.0, vents=False)
    body = octo(0.62)
    M.add(g, prism(body, 0.17, 0.40, 0.93), 'hull_mid')
    M.add(g, prism(scale_poly(body, 0.86), 0.40, 0.43, 0.97), 'hull_light')
    frame(M, g, scale_poly(octo(0.62), 0.80), octo(0.27), 0.43, 0.46, 'metal')
    M.add(g, cyl((0, 0, 0.36), (0, 0, 0.44), 0.27, n=24), 'vent')
    M.add(g, cyl((0, 0, 0.44), (0, 0, 0.447), 0.22, n=24), 'flame')
    for k in range(5):
        r = np.random.default_rng(k)
        x, y = r.uniform(-0.12, 0.12, 2)
        M.add(g, cyl((x, y, 0.447), (x, y, 0.452), 0.03+0.02*r.random(), n=8), 'flame')
    # chimneys
    for s in (-1, 1):
        cx, cy = s*0.62, 0.62
        M.add(g, cyl((cx, cy, 0.17), (cx, cy, 0.62), 0.12, n=14), 'metal')
        M.add(g, cyl((cx, cy, 0.50), (cx, cy, 0.54), 0.135, n=14), 'yellow')
        M.add(g, cyl((cx, cy, 0.62), (cx, cy, 0.64), 0.135, n=14), 'hull_dark')
        M.add(g, cyl((cx, cy, 0.63), (cx, cy, 0.645), 0.085, n=12), 'heat')
    # hoppers: ferrolite left-front, coal right-front
    for s, ore in ((-1, 'ore_fer'), (1, 'bore')):
        cx, cy = s*0.60, -0.62
        M.add(g, prism(rect(cx, cy, 0.20, 0.17), 0.17, 0.36, 0.9), 'hull_light')
        M.add(g, prism(rect(cx, cy, 0.15, 0.12), 0.36, 0.365), 'vent')
        for j in range(7):
            r = np.random.default_rng(31*j + (s+2))
            ox, oy = r.uniform(-0.11, 0.11), r.uniform(-0.08, 0.08)
            M.add(g, sphereish((cx+ox, cy+oy, 0.365), 0.035, 6), ore)
        M.add(g, box(cx-0.20, cx+0.20, cy+0.16, cy+0.19, 0.30, 0.37), 'yellow')
    # heat-exchange fins on the sides
    for s in (-1, 1):
        for j in range(5):
            y = -0.20 + j*0.10
            M.add(g, box(s*0.62, s*0.80, y-0.02, y+0.02, 0.17, 0.33) if s > 0 else box(-0.80, -0.62, y-0.02, y+0.02, 0.17, 0.33), 'metal_light')
    light(M, g, 0, -0.50, 0.40, 0.08, 0.03, 0.012)
    return M

# ------------------------------------------------ Propellant press (2x2)
def press():
    M = Model()
    g = 'bottom'
    M.add(g, prism(cham_rect(0.985, 0.985, 0.28), 0, 0.08), 'hull_dark')
    M.add(g, prism(rect(0, 0, 0.55, 0.55), 0.08, 0.085), 'vent')
    r = np.random.default_rng(5)
    for j in range(40):
        x, y = r.uniform(-0.45, 0.45, 2)
        M.add(g, cyl((x, y, 0.085), (x, y, 0.09), 0.02+0.02*r.random(), n=6), 'ore_salt')
    g = 'piston'
    M.add(g, box(-0.42, 0.10, -0.10, 0.10, 0.10, 0.22), 'metal')
    M.add(g, cyl((-0.42, 0, 0.16), (0.08, 0, 0.16), 0.07, n=12), 'metal_light')
    M.add(g, box(-0.48, -0.36, -0.15, 0.15, 0.10, 0.25), 'hull_dark')
    M.add(g, box(-0.47, -0.37, -0.12, 0.12, 0.25, 0.26), 'yellow')
    g = 'main'
    outer = cham_rect(0.985, 0.985, 0.28); inner = cham_rect(0.55, 0.55, 0.12)
    frame(M, g, outer, inner, 0.0, 0.10, 'hull_dark')
    frame(M, g, cham_rect(0.87, 0.87, 0.26), cham_rect(0.60, 0.60, 0.14), 0.10, 0.22, 'hull_mid')
    frame(M, g, cham_rect(0.64, 0.64, 0.15), cham_rect(0.57, 0.57, 0.13), 0.22, 0.25, 'metal')
    for k in range(4):
        R = rz(90*k)
        sub = Model()
        chevrons(sub, 'c', 0.0, -0.76, 0.22, 0.42, 0.09, 4)
        light(sub, 'c', 0.42, -0.74, 0.22, 0.04, 0.04, 0.012)
        sub.add('c', box(-0.62, -0.48, -0.86, -0.70, 0.22, 0.30), 'hull_light')
        for T, m in sub.parts['c']:
            M.add(g, tf(T, R), m)
    bolts(M, g, [(sx*0.80, sy*0.80) for sx in (-1, 1) for sy in (-1, 1)], 0.22, r=0.03)
    g = 'top'
    M.add(g, cyl((0, 0, 0.26), (0, 0, 0.40), 0.20, n=20), 'hull_light')
    M.add(g, cyl((0, 0, 0.40), (0, 0, 0.42), 0.15, n=20), 'metal')
    M.add(g, cyl((0, 0, 0.42), (0, 0, 0.43), 0.07, n=12), 'glow')
    for k in range(4):
        a = math.radians(45+90*k)
        M.add(g, cyl((0.17*math.cos(a), 0.17*math.sin(a), 0.40), (0.17*math.cos(a), 0.17*math.sin(a), 0.415), 0.025, n=8), 'yellow')
    return M

# ------------------------------------------------ Point-defence interceptor (2x2)
def interceptor():
    M = Model(); g = 'base'
    uef_base(M, g, 1.0)
    M.add(g, cyl((0, 0, 0.17), (0, 0, 0.20), 0.55, n=24), 'metal')
    g = 'head'
    hull = mirror_half([(0.0, 0.42), (0.24, 0.38), (0.40, 0.18), (0.40, -0.26), (0.26, -0.42), (0.0, -0.44)])
    M.add(g, prism(hull, 0.20, 0.40, 0.88), 'hull_mid')
    M.add(g, prism(scale_poly(hull, 0.84), 0.40, 0.42, 0.95), 'hull_light')
    for s in (-1, 1):
        M.add(g, cyl((s*0.17, 0.10, 0.36), (s*0.17, 0.66, 0.36), 0.055, n=12), 'metal')
        M.add(g, cyl((s*0.17, 0.30, 0.36), (s*0.17, 0.36, 0.36), 0.07, n=12), 'yellow')
        M.add(g, cyl((s*0.17, 0.62, 0.36), (s*0.17, 0.68, 0.36), 0.065, n=12), 'hull_dark')
        M.add(g, cyl((s*0.17, 0.68, 0.36), (s*0.17, 0.695, 0.36), 0.04, n=10), 'glow')
        vent(M, g, s*0.44, -0.05, 0.20, 0.08, 0.36, 5, along='y')
        M.add(g, box(s*0.40, s*0.48, -0.25, 0.15, 0.20, 0.33) if s > 0 else box(-0.48, -0.40, -0.25, 0.15, 0.20, 0.33), 'hull_dark')
    M.add(g, sphereish((0, -0.15, 0.42), 0.17, 12), 'glass')
    M.add(g, cyl((0, -0.15, 0.40), (0, -0.15, 0.44), 0.19, n=16), 'metal')
    M.add(g, cyl((0, -0.15, 0.555), (0, -0.15, 0.575), 0.04, n=8), 'glow')
    chevrons(M, g, 0, -0.36, 0.40, 0.30, 0.07, 3)
    bolts(M, g, [(-0.28, 0.22), (0.28, 0.22), (-0.28, -0.30), (0.28, -0.30)], 0.42, r=0.016)
    return M

# ------------------------------------------------ Spotter beacon (1x1 radar)
def beacon():
    M = Model(); g = 'base'
    M.add(g, prism(cham_rect(0.49, 0.49, 0.14), 0, 0.08, 0.97), 'hull_dark')
    M.add(g, prism(cham_rect(0.42, 0.42, 0.12), 0.08, 0.14, 0.95), 'hull_mid')
    for sx in (-1, 1):
        for sy in (-1, 1):
            M.add(g, box(sx*0.30-0.05, sx*0.30+0.05, sy*0.30-0.05, sy*0.30+0.05, 0.14, 0.16), 'yellow')
    M.add(g, cyl((0, 0, 0.14), (0, 0, 0.17), 0.22, n=16), 'metal')
    g = 'head'
    M.add(g, cyl((0, 0, 0.17), (0, 0, 0.42), 0.06, n=10), 'metal_light')
    dish = [(0.34*math.cos(a), 0.14*math.sin(a)) for a in np.linspace(0, 2*math.pi, 16, endpoint=False)]
    D = prism(ccw(dish), -0.02, 0.02)
    M.add(g, tf(D, rx(-62), (0, 0.04, 0.44)), 'hull_light')
    D2 = prism(ccw([(x*0.82, y*0.82) for x, y in dish]), 0.02, 0.03)
    M.add(g, tf(D2, rx(-62), (0, 0.04, 0.44)), 'metal')
    M.add(g, cyl((0, 0.04, 0.44), (0, 0.22, 0.54), 0.012, n=6), 'metal_light')
    M.add(g, sphereish((0, 0.22, 0.54), 0.035, 8), 'glow')
    M.add(g, box(-0.08, 0.08, -0.22, -0.10, 0.20, 0.30), 'hull_dark')
    M.add(g, box(-0.06, 0.06, -0.225, -0.215, 0.23, 0.28), 'glow')
    return M

# ------------------------------------------------ Shield emitter T1 (2x2)
def emitter():
    M = Model(); g = 'main'
    uef_base(M, g, 1.0, vents=True)
    body = octo(0.58)
    M.add(g, prism(body, 0.17, 0.33, 0.92), 'hull_mid')
    M.add(g, prism(scale_poly(body, 0.84), 0.33, 0.35), 'hull_light')
    for sx in (-1, 1):
        for sy in (-1, 1):
            cx, cy = sx*0.58, sy*0.58
            M.add(g, cyl((cx, cy, 0.17), (cx, cy, 0.46), 0.12, n=14), 'metal')
            M.add(g, cyl((cx, cy, 0.30), (cx, cy, 0.35), 0.13, n=14), 'yellow')
            M.add(g, cyl((cx, cy, 0.46), (cx, cy, 0.48), 0.09, n=12), 'hull_dark')
            M.add(g, cyl((cx, cy, 0.48), (cx, cy, 0.49), 0.05, n=10), 'glow')
            M.add(g, tube_path([(cx*0.8, cy*0.8, 0.40), (cx*0.55, cy*0.55, 0.42), (cx*0.35, cy*0.35, 0.44)], 0.02, n=6), 'cable')
    for i, (r0, z) in enumerate(((0.34, 0.35), (0.28, 0.42), (0.22, 0.49))):
        M.add(g, cyl((0, 0, z), (0, 0, z+0.05), r0, r0*0.95, n=22), 'metal' if i % 2 == 0 else 'metal_light')
        M.add(g, cyl((0, 0, z+0.05), (0, 0, z+0.065), r0*0.9, n=22), 'glow')
    M.add(g, sphereish((0, 0, 0.55), 0.15, 12), 'glass')
    M.add(g, cyl((0, 0, 0.66), (0, 0, 0.70), 0.05, n=10), 'glow')
    return M

# ------------------------------------------------ Steel walls
def wall(half):
    M = Model(); g = 'main'; h = half
    M.add(g, prism(cham_rect(h*0.99, h*0.99, h*0.10), 0, 0.10, 0.99), 'hull_dark')
    M.add(g, prism(cham_rect(h*0.92, h*0.92, h*0.14), 0.10, 0.24, 0.90), 'steel')
    M.add(g, prism(cham_rect(h*0.66, h*0.66, h*0.12), 0.24, 0.28, 0.92), 'hull_light')
    st = ccw([(-h*0.92, h*0.30), (-h*0.30, h*0.92), (-h*0.10, h*0.92), (-h*0.92, h*0.10)])
    M.add(g, prism(st, 0.24, 0.245), 'yellow')
    st = ccw([(h*0.92, -h*0.30), (h*0.30, -h*0.92), (h*0.10, -h*0.92), (h*0.92, -h*0.10)])
    M.add(g, prism(st, 0.24, 0.245), 'yellow')
    bolts(M, g, [(sx*h*0.78, sy*h*0.78) for sx in (-1, 1) for sy in (-1, 1)], 0.24, r=0.02+0.01*h)
    if h > 0.6:
        bolts(M, g, [(0, h*0.78), (0, -h*0.78), (h*0.78, 0), (-h*0.78, 0)], 0.24, r=0.025)
        M.add(g, prism(rect(0, 0, h*0.30, h*0.04), 0.28, 0.285), 'vent')
    return M

# ------------------------------------------------ items (rendered at 1 tile scale; canvas 32)
def chunks(mat, seed, n=5, s=0.16, crystal=False):
    M = Model(); r = np.random.default_rng(seed)
    pos = [(-0.12, -0.08), (0.12, -0.10), (0.0, 0.12), (-0.18, 0.12), (0.18, 0.12)][:n]
    for k, (x, y) in enumerate(pos):
        sz = s*(0.8+0.4*r.random())
        if crystal:
            p = [(sz*0.45*math.cos(a), sz*0.45*math.sin(a)) for a in np.linspace(0, 2*math.pi, 6, endpoint=False)]
            T = prism(ccw(p), 0, sz*1.6, 0.25)
            M.add('main', tf(T, rx(50)@rz(r.uniform(0, 360)), (x, y, 0.1)), mat)
        else:
            nv = 7
            p = [(sz*(0.7+0.4*r.random())*math.cos(a), sz*(0.7+0.4*r.random())*math.sin(a)) for a in np.linspace(0, 2*math.pi, nv, endpoint=False)]
            M.add('main', prism(ccw(p), 0, sz*0.9, 0.6), mat)
    return M

def ingot():
    M = Model()
    T = prism(rect(0, 0, 0.36, 0.20), 0, 0.16, top_poly=rect(0, 0, 0.29, 0.14))
    M.add('main', tf(T, rz(-25)), 'steel')
    M.add('main', tf(prism(rect(0, 0, 0.12, 0.05), 0.16, 0.168), rz(-25)), 'hull_light')
    return M

def cartridge():
    M = Model()
    for (x, y) in ((-0.12, -0.04), (0.12, 0.04)):
        M.add('main', cyl((x, y-0.34, 0.14), (x, y+0.22, 0.14), 0.13, n=14), 'charge')
        M.add('main', cyl((x, y+0.02, 0.14), (x, y+0.08, 0.14), 0.135, n=14), 'yellow')
        M.add('main', cyl((x, y+0.22, 0.14), (x, y+0.34, 0.14), 0.13, 0.05, n=14), 'copper')
    return M
