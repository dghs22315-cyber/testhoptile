"""Stage 3 non-turret models: T2-T3 industry, heat, defence, items. 1.0 = one tile."""
import numpy as np, math
from geom import *
from mats import Model, MID
from models import bolts, light, vent, chevrons, uef_base
from models2 import frame, octo, chunks
from models3 import hexa, add_rot
from models4a import P, cy_base

def pad(M, g, h, top=0.10, m='hull_dark'):
    M.add(g, prism(cham_rect(h*0.985, h*0.985, h*0.22), 0, top, 0.98), m)

# ---------------------------------------------------------------- Electrolyzer (2x2): bauxite -> aluminium + chlorine
def electrolyzer():
    M = Model(); g = 'bottom'
    pad(M, g, 1.0, 0.08)
    M.add(g, prism(cham_rect(0.46, 0.46, 0.08), 0.08, 0.10), 'vent')
    g = 'main'
    frame(M, g, cham_rect(0.97, 0.97, 0.26), cham_rect(0.42, 0.42, 0.07), 0.08, 0.30, 'hull_mid')
    frame(M, g, cham_rect(0.90, 0.90, 0.24), cham_rect(0.46, 0.46, 0.08), 0.30, 0.32, 'hull_light')
    for x in (-0.17, 0.17):
        M.add(g, cbox(x, 0, 0.27, 0.06, 0.92, 0.05), 'copper')
        for y in (-0.52, 0.52):
            M.add(g, cyl((x, y, 0.30), (x, y, 0.40), 0.065, n=10), 'metal_light')
            M.add(g, cyl((x, y, 0.40), (x, y, 0.43), 0.045, n=10), 'glow')
    # transformer (right band)
    M.add(g, cbox(0.70, 0.0, 0.40, 0.30, 0.56, 0.16), 'hull_dark')
    for y in (-0.18, 0.0, 0.18): M.add(g, cyl((0.58, y, 0.48), (0.82, y, 0.48), 0.06, n=10), 'coil')
    # chlorine outlet (left band)
    M.add(g, cyl((-0.70, -0.50, 0.40), (-0.70, 0.50, 0.40), 0.10, n=12), 'metal')
    M.add(g, cyl((-0.70, -0.25, 0.40), (-0.70, 0.25, 0.40), 0.11, n=12), 'glass')
    M.add(g, cyl((-0.70, -0.20, 0.40), (-0.70, 0.20, 0.40), 0.085, n=12), 'gglow')
    chevrons(M, g, 0, -0.72, 0.32, 0.70, 0.12, n=4)
    bolts(M, g, [(-0.84, -0.84), (0.84, -0.84), (-0.84, 0.84), (0.84, 0.84)], 0.30)
    light(M, g, 0.0, 0.74, 0.32, 0.10, 0.05)
    return M

# ---------------------------------------------------------------- Alloy furnace (3x3): cobaltite + steel + titanium + slag -> cobalt alloy
def alloy_furnace():
    M = Model(); g = 'main'
    uef_base(M, g, 1.5, top=0.14, vents=False)
    M.add(g, prism(octo(1.12), 0.14, 0.42, 0.92), 'hull_mid')
    M.add(g, prism(octo(0.98), 0.42, 0.46, 0.96), 'hull_light')
    M.add(g, cyl((0, 0, 0.46), (0, 0, 0.60), 0.54, n=20), 'metal')
    M.add(g, cyl((0, 0, 0.60), (0, 0, 0.62), 0.46, n=20), 'hull_dark')
    M.add(g, cyl((0, 0, 0.55), (0, 0, 0.625), 0.38, n=20), 'flame')
    for k in range(8):
        a = math.radians(22.5+45*k)
        M.add(g, cbox(0.50*math.cos(a), 0.50*math.sin(a), 0.62, 0.08, 0.08, 0.04), 'metal_light')
    # three hoppers
    for k, mat in enumerate(('ore_cob', 'steel', 'metal_light')):
        a = math.radians(90+120*k); cx, cy = 0.95*math.cos(a), 0.95*math.sin(a)
        M.add(g, tf(prism(cham_rect(0.24, 0.20, 0.05), 0.30, 0.62, top_poly=cham_rect(0.30, 0.26, 0.06)), rz(math.degrees(a)-90), (cx, cy, 0)), 'hull_dark')
        M.add(g, tf(prism(cham_rect(0.22, 0.18, 0.05), 0.62, 0.64), rz(math.degrees(a)-90), (cx, cy, 0)), mat)
    # chimneys
    for x in (-1.0, 1.0):
        M.add(g, cyl((x, -0.95, 0.14), (x, -0.95, 0.86), 0.15, n=12), 'hull_dark')
        M.add(g, cyl((x, -0.95, 0.86), (x, -0.95, 0.88), 0.11, n=12), 'vent')
        M.add(g, cyl((x, -0.95, 0.70), (x, -0.95, 0.74), 0.17, n=12), 'yellow')
    for k in range(4):
        a = math.radians(45+90*k)
        M.add(g, cyl((0.80*math.cos(a), 0.80*math.sin(a), 0.46), (0.62*math.cos(a), 0.62*math.sin(a), 0.52), 0.05, n=8), 'coil')
    light(M, g, 0, -1.25, 0.14, 0.12, 0.05)
    return M

# ---------------------------------------------------------------- Tungsten forge (3x3, heat consumer)
def tungsten_forge():
    M = Model(); g = 'main'
    pad(M, g, 1.5, 0.12)
    M.add(g, prism(cham_rect(1.30, 1.30, 0.30), 0.12, 0.40, 0.92), 'tung')
    M.add(g, prism(cham_rect(1.10, 1.10, 0.26), 0.40, 0.44), 'hull_dark')
    # heat intake ports (all 4 sides)
    for k in range(4):
        R = rz(90*k)
        M.add(g, tf(cbox(1.30, 0, 0.26, 0.36, 0.62, 0.22), R), 'hull_mid')
        M.add(g, tf(cbox(1.40, 0, 0.30, 0.16, 0.46, 0.18), R), 'heat')
        for y in (-0.26, 0.26): M.add(g, tf(cbox(1.30, y, 0.38, 0.40, 0.06, 0.04), R), 'metal')
    # crucible + press head
    M.add(g, prism(octo(0.62), 0.44, 0.58, 0.9), 'hull_mid')
    M.add(g, cyl((0, 0, 0.56), (0, 0, 0.60), 0.44, n=16), 'flame')
    for s in (-1, 1):
        M.add(g, cbox(s*0.58, 0, 0.72, 0.16, 1.30, 0.20), 'hull_light')
        M.add(g, cbox(s*0.58, 0, 0.825, 0.10, 1.10, 0.01), 'yellow')
    M.add(g, cbox(0, 0, 0.74, 1.00, 0.34, 0.14), 'tung')
    M.add(g, cyl((0, 0, 0.62), (0, 0, 0.86), 0.12, n=10), 'metal_light')
    bolts(M, g, [(sx*1.05, sy*1.05) for sx in (-1, 1) for sy in (-1, 1)], 0.44, r=0.04)
    return M

def heat_right_port(mp, X, Y, g):
    return ((mp == MID['heat']) & (X > 1.2)).astype(float)

# ---------------------------------------------------------------- Magnet factory (2x2): neodymite + silicon + chlorine -> magnet
def magnet_factory():
    M = Model(); g = 'bottom'
    pad(M, g, 1.0, 0.08)
    M.add(g, cyl((0, 0, 0.08), (0, 0, 0.10), 0.46, n=20), 'vent')
    g = 'spinner'
    for k in range(6):
        a = math.radians(60*k)
        M.add(g, tf(cbox(0.30, 0, 0.16, 0.16, 0.08, 0.06), rz(60*k)), 'magnet')
        M.add(g, cyl((0.30*math.cos(a), 0.30*math.sin(a), 0.19), (0.30*math.cos(a), 0.30*math.sin(a), 0.21), 0.05, n=8), 'pglow')
    M.add(g, cyl((0, 0, 0.10), (0, 0, 0.22), 0.13, n=12), 'metal')
    M.add(g, cyl((0, 0, 0.22), (0, 0, 0.24), 0.08, n=12), 'pglow')
    g = 'main'
    frame(M, g, octo(1.02, ph=22.5), octo(0.52, ph=22.5), 0.08, 0.32, 'hull_mid')
    frame(M, g, octo(0.95, ph=22.5), octo(0.56, ph=22.5), 0.32, 0.34, 'magnet')
    for k in range(4):
        a = math.radians(45+90*k)
        x, y = 0.74*math.cos(a), 0.74*math.sin(a)
        M.add(g, cyl((x, y, 0.34), (x, y, 0.46), 0.11, n=12), 'coil')
        M.add(g, cyl((x, y, 0.46), (x, y, 0.48), 0.07, n=12), 'pglow')
    M.add(g, cbox(0, -0.80, 0.36, 0.40, 0.10, 0.06), 'glass')
    M.add(g, cbox(0, -0.80, 0.37, 0.30, 0.06, 0.06), 'gglow')
    chevrons(M, g, 0, 0.80, 0.34, 0.40, 0.10, n=3)
    return M

# ---------------------------------------------------------------- Heater (2x2, heat producer, rotates; output faces +X)
def heater():
    M = Model(); g = 'main'
    pad(M, g, 1.0, 0.10)
    M.add(g, prism(cham_rect(0.86, 0.86, 0.22), 0.10, 0.30, 0.94), 'hull_mid')
    M.add(g, cyl((-0.12, 0, 0.30), (-0.12, 0, 0.48), 0.42, n=18), 'tung')
    M.add(g, cyl((-0.12, 0, 0.48), (-0.12, 0, 0.50), 0.32, n=18), 'hull_dark')
    M.add(g, cyl((-0.12, 0, 0.46), (-0.12, 0, 0.505), 0.24, n=18), 'flame')
    for k in range(10):
        a = math.radians(36*k)
        M.add(g, tf(cbox(0.44, 0, 0.40, 0.10, 0.04, 0.12), rz(36*k), (-0.12, 0, 0)), 'metal')
    M.add(g, cbox(-0.70, 0.55, 0.40, 0.28, 0.30, 0.20), 'hull_dark')   # charge feeder
    M.add(g, cbox(-0.70, 0.55, 0.505, 0.22, 0.24, 0.01), 'charge')
    chevrons(M, g, -0.40, -0.74, 0.30, 0.70, 0.12, n=4)
    g = 'top'
    M.add(g, cbox(0.70, 0, 0.36, 0.56, 0.62, 0.28), 'hull_light')
    M.add(g, cbox(0.70, 0, 0.505, 0.44, 0.50, 0.01), 'hull_mid')
    M.add(g, cbox(0.93, 0, 0.42, 0.10, 0.46, 0.20), 'heat')
    for y in (-0.18, 0.0, 0.18): M.add(g, cbox(0.62, y, 0.52, 0.22, 0.05, 0.02), 'vent')
    bolts(M, g, [(0.50, 0.26), (0.50, -0.26)], 0.505, r=0.025)
    return M

def heat_mouth(mp, X, Y, g):
    return ((mp == MID['heat']) & (X > 0.8)).astype(float)

# ---------------------------------------------------------------- Heat conduit (1x1, conductor; output faces +X)
def heat_conduit():
    M = Model(); g = 'main'
    M.add(g, prism(cham_rect(0.49, 0.49, 0.10), 0, 0.10, 0.96), 'hull_dark')
    M.add(g, prism(cham_rect(0.42, 0.42, 0.08), 0.10, 0.16, 0.94), 'tung')
    g = 'top'
    M.add(g, cbox(0, 0, 0.24, 0.98, 0.34, 0.14), 'hull_mid')
    M.add(g, cbox(0, 0, 0.315, 0.90, 0.22, 0.01), 'heat')
    for x in (-0.30, 0.0, 0.30):
        M.add(g, cbox(x, 0, 0.27, 0.06, 0.40, 0.10), 'metal_light')
    M.add(g, prism(P([(0.16, -0.10), (0.30, 0.0), (0.16, 0.10)]), 0.32, 0.33), 'yellow')
    return M

def heat_strip(mp, X, Y, g):
    return (mp == MID['heat']).astype(float)

# ---------------------------------------------------------------- Mass separator II (3x3): slag -> 4 rare ores
def separator2():
    M = Model(); g = 'bottom'
    pad(M, g, 1.5, 0.08)
    M.add(g, cyl((0, 0, 0.08), (0, 0, 0.10), 0.72, n=24), 'vent')
    g = 'spinner'
    M.add(g, cyl((0, 0, 0.10), (0, 0, 0.24), 0.18, n=14), 'metal')
    for k in range(3):
        M.add(g, tf(prism(P([(0.10, -0.06), (0.62, -0.10), (0.66, 0.02), (0.10, 0.06)]), 0.16, 0.22), rz(120*k)), 'metal_light')
    M.add(g, cyl((0, 0, 0.24), (0, 0, 0.26), 0.10, n=14), 'glow')
    g = 'main'
    frame(M, g, cham_rect(1.45, 1.45, 0.40), cham_rect(0.80, 0.80, 0.33), 0.08, 0.34, 'hull_mid')
    frame(M, g, cham_rect(1.36, 1.36, 0.38), cham_rect(0.84, 0.84, 0.34), 0.34, 0.36, 'hull_light')
    for k, mat in enumerate(('ore_baux', 'ore_cob', 'ore_wolf', 'ore_neo')):
        R = rz(90*k + 45)
        M.add(g, tf(prism(cham_rect(0.20, 0.20, 0.05), 0.36, 0.52, 0.85), R, (0, 0, 0)) if False else tf(prism(cham_rect(0.20, 0.20, 0.05, cy=1.30), 0.36, 0.52, 0.85), R), 'hull_dark')
        M.add(g, tf(prism(cham_rect(0.15, 0.15, 0.04, cy=1.30), 0.52, 0.54), R), mat)
    for k in range(4):
        R = rz(90*k)
        M.add(g, tf(cbox(0, -1.12, 0.40, 0.70, 0.10, 0.06), R), 'glass')
        M.add(g, tf(cbox(0, -1.12, 0.42, 0.56, 0.05, 0.06), R), 'glow')
    return M

# ---------------------------------------------------------------- Impact drill (3x3)
def impact_drill():
    M = Model(); g = 'main'
    uef_base(M, g, 1.5, top=0.14, vents=True)
    frame(M, g, octo(1.20), octo(0.66), 0.14, 0.40, 'hull_mid')
    frame(M, g, octo(1.12), octo(0.70), 0.40, 0.42, 'yellow')
    for k in range(4):
        a = math.radians(45+90*k)
        M.add(g, cyl((1.0*math.cos(a), 1.0*math.sin(a), 0.14), (1.0*math.cos(a), 1.0*math.sin(a), 0.56), 0.11, n=10), 'hull_light')
        M.add(g, cyl((1.0*math.cos(a), 1.0*math.sin(a), 0.56), (1.0*math.cos(a), 1.0*math.sin(a), 0.58), 0.08, n=10), 'metal')
    g = 'rotator'
    M.add(g, cyl((0, 0, 0.14), (0, 0, 0.30), 0.64, n=24), 'metal')
    for k in range(3):
        M.add(g, tf(prism(P([(-0.12, 0.10), (0.12, 0.10), (0.16, 0.62), (-0.16, 0.62)]), 0.30, 0.42, 0.85), rz(120*k)), 'tung')
        M.add(g, tf(cyl((0, 0.50, 0.42), (0, 0.50, 0.48), 0.10, n=10), rz(120*k)), 'metal_light')
    g = 'top'
    M.add(g, cyl((0, 0, 0.42), (0, 0, 0.62), 0.28, n=16), 'hull_light')
    M.add(g, cyl((0, 0, 0.62), (0, 0, 0.66), 0.20, n=16), 'hull_dark')
    M.add(g, cyl((0, 0, 0.66), (0, 0, 0.68), 0.10, n=12), 'glow')
    bolts(M, g, [(0.20*math.cos(math.radians(60*k)), 0.20*math.sin(math.radians(60*k))) for k in range(6)], 0.62, r=0.022)
    return M

# ---------------------------------------------------------------- Decoy (2x2): fake heavy turret
def decoy():
    M = Model(); g = 'main'
    pad(M, g, 1.0, 0.12)
    M.add(g, prism(cham_rect(0.90, 0.90, 0.24), 0.12, 0.30, 0.92), 'hull_mid')
    for k in range(4):
        R = rz(90*k)
        st = P([(-0.90, 0.90), (-0.50, 0.90), (-0.90, 0.50)])
        M.add(g, tf(prism(st, 0.30, 0.31), R), 'yellow')
    M.add(g, prism(octo(0.60), 0.30, 0.52, 0.86), 'hull_light')
    M.add(g, prism(octo(0.48), 0.52, 0.56, 0.9), 'hull_dark')
    M.add(g, cyl((0, 0.10, 0.48), (0, 0.98, 0.48), 0.12, n=12), 'metal')
    M.add(g, cyl((0, 0.86, 0.48), (0, 1.0, 0.48), 0.15, n=12), 'hull_dark')
    for y in (-0.30, -0.05, 0.20): M.add(g, cbox(0, y, 0.57, 0.80, 0.07, 0.02), 'metal')
    M.add(g, cyl((0.30, -0.30, 0.56), (0.30, -0.30, 0.64), 0.07, n=10), 'rglow')
    bolts(M, g, [(sx*0.70, sy*0.70) for sx in (-1, 1) for sy in (-1, 1)], 0.30, r=0.035)
    return M

# ---------------------------------------------------------------- Radar T3 (3x3): base + rotating head
def radar():
    M = Model(); g = 'base'
    uef_base(M, g, 1.5, top=0.16)
    M.add(g, cyl((0, 0, 0.16), (0, 0, 0.24), 0.70, n=24), 'metal')
    g = 'head'
    M.add(g, cyl((0, 0, 0.24), (0, 0, 0.40), 0.30, n=16), 'hull_mid')
    dish = [(1.10*math.cos(a), 0.30+0.44*math.sin(a)) for a in np.linspace(0, 2*math.pi, 20, endpoint=False)]
    M.add(g, prism(P(dish), 0.52, 0.60, 0.80), 'metal_light')
    M.add(g, prism(scale_poly(P(dish), 0.82), 0.60, 0.61), 'metal')
    for x in np.linspace(-0.8, 0.8, 7): M.add(g, cbox(x, 0.30, 0.615, 0.04, 0.64, 0.01), 'hull_mid')
    M.add(g, cbox(0, 0.0, 0.52, 0.16, 0.70, 0.12), 'hull_dark')
    M.add(g, cyl((0, 0.30, 0.61), (0, 0.30, 0.90), 0.05, n=8), 'metal')
    M.add(g, sphereish((0, 0.30, 0.92), 0.08, n=10), 'glow')
    M.add(g, cbox(0, -0.40, 0.46, 0.44, 0.30, 0.16), 'hull_light')
    M.add(g, cbox(0, -0.40, 0.545, 0.30, 0.06, 0.01), 'glow')
    return M

# ---------------------------------------------------------------- Shield ED (Cybran, 2x2)
def ed_shield():
    M = Model(); g = 'main'
    cy_base(M, g, 1.0)
    M.add(g, prism(hexa(0.62), 0.16, 0.36, 0.86), 'cy_mid')
    M.add(g, prism(hexa(0.46), 0.36, 0.40, 0.9), 'cy_dark')
    for k in range(6):
        a = math.radians(30+60*k)
        M.add(g, tf(prism(P([(-0.05, 0.40), (0.05, 0.40), (0.0, 0.66)]), 0.30, 0.46, 0.6), rz(60*k-60)), 'red_armor')
    M.add(g, sphereish((0, 0, 0.44), 0.22, n=14), 'rglow')
    M.add(g, cyl((0, 0, 0.40), (0, 0, 0.44), 0.30, n=6), 'metal')
    return M

# ---------------------------------------------------------------- Pulse shield (UEF, 3x3)
def pulse_shield():
    M = Model(); g = 'main'
    uef_base(M, g, 1.5)
    M.add(g, prism(octo(1.04), 0.17, 0.40, 0.88), 'hull_mid')
    M.add(g, prism(octo(0.86), 0.40, 0.44, 0.94), 'hull_light')
    for k in range(4):
        a = math.radians(45+90*k); x, y = 0.66*math.cos(a), 0.66*math.sin(a)
        M.add(g, cyl((x, y, 0.44), (x, y, 0.66), 0.13, n=12), 'metal')
        M.add(g, cyl((x, y, 0.66), (x, y, 0.72), 0.10, n=12), 'glow')
        M.add(g, tube_path([(x, y, 0.60), (x*0.5, y*0.5, 0.64), (0, 0, 0.66)], 0.03, n=6), 'cable')
    M.add(g, cyl((0, 0, 0.44), (0, 0, 0.70), 0.30, n=18), 'hull_dark')
    M.add(g, sphereish((0, 0, 0.74), 0.24, n=16), 'glow')
    chevrons(M, g, 0, -0.92, 0.17, 0.80, 0.12, n=5)
    return M

# ---------------------------------------------------------------- Nanite repairer (Cybran, 2x2)
def nanite_repairer():
    M = Model(); g = 'main'
    cy_base(M, g, 1.0)
    M.add(g, prism(cham_rect(0.60, 0.60, 0.20), 0.16, 0.34, 0.88), 'cy_mid')
    M.add(g, cyl((0, 0, 0.34), (0, 0, 0.42), 0.36, n=16), 'glass')
    M.add(g, cyl((0, 0, 0.36), (0, 0, 0.425), 0.28, n=16), 'gglow')
    for k in range(4):
        M.add(g, tf(cbox(0, 0.48, 0.42, 0.10, 0.22, 0.10), rz(90*k)), 'red_armor')
        M.add(g, tf(cbox(0, 0.52, 0.475, 0.04, 0.10, 0.01), rz(90*k)), 'rglow')
    return M

# ---------------------------------------------------------------- Tungsten walls
def tung_wall(half):
    M = Model(); g = 'main'; h = half
    M.add(g, prism(cham_rect(h*0.99, h*0.99, h*0.08), 0, 0.12, 0.99), 'hull_dark')
    M.add(g, prism(cham_rect(h*0.93, h*0.93, h*0.12), 0.12, 0.28, 0.88), 'tung')
    M.add(g, prism(cham_rect(h*0.62, h*0.62, h*0.10), 0.28, 0.33, 0.9), 'hull_mid')
    n = 2 if h > 0.6 else 1
    for i in range(n):
        for j in range(n):
            cx = (-h/2 + h*i) if n == 2 else 0; cy = (-h/2 + h*j) if n == 2 else 0
            bolts(M, g, [(cx+sx*h*0.30/n*2, cy+sy*h*0.30/n*2) for sx in (-1, 1) for sy in (-1, 1)], 0.28, r=0.03)
    M.add(g, prism(P([(-h*0.93, -h*0.20), (-h*0.93, -h*0.05), (h*0.93, h*0.05), (h*0.93, -h*0.10)]), 0.28, 0.285) if False else cbox(0, 0, 0.33, h*1.1, 0.04, 0.01), 'cobalt')
    return M

# ---------------------------------------------------------------- Items
def item_alu():
    M = Model()
    for k, (x, y, z) in enumerate(((-0.08, -0.06, 0), (0.08, 0.06, 0), (0.0, 0.0, 0.12))):
        T = prism(rect(0, 0, 0.30, 0.13), z, z+0.11, top_poly=rect(0, 0, 0.25, 0.09))
        M.add('main', tf(T, rz(-30 if k < 2 else 60), (x, y, 0)), 'alu')
    return M

def item_cobalt_alloy():
    M = Model()
    for k in range(3):
        T = prism(cham_rect(0.30, 0.22, 0.08), 0.08*k, 0.08*k+0.07, 0.92)
        M.add('main', tf(T, rz(-20+12*k), (0.02*k, 0.03*k, 0)), 'cobalt')
    M.add('main', tf(prism(cham_rect(0.18, 0.04, 0.02), 0.23, 0.235), rz(4)), 'alu')
    return M

def item_tungsten_core():
    M = Model(); R = rz(-40)
    M.add('main', tf(cyl((0, -0.36, 0.12), (0, 0.22, 0.12), 0.11, n=12), R), 'tung')
    M.add('main', tf(cyl((0, 0.22, 0.12), (0, 0.40, 0.12), 0.11, 0.02, n=12), R), 'metal_light')
    M.add('main', tf(cyl((0, -0.10, 0.12), (0, -0.02, 0.12), 0.125, n=12), R), 'copper')
    M.add('main', tf(cyl((0, -0.36, 0.12), (0, -0.30, 0.12), 0.12, n=12), R), 'hull_dark')
    return M

def item_magnet():
    M = Model()
    pts = [(0.24*math.cos(a), 0.06+0.24*math.sin(a), 0.1) for a in np.linspace(math.radians(200), math.radians(-20), 9)]
    M.add('main', tube_path([(pts[0][0], pts[0][1]-0.22, 0.1)] + pts + [(pts[-1][0], pts[-1][1]-0.22, 0.1)], 0.085, n=10), 'magnet')
    for x in (pts[0][0], pts[-1][0]):
        M.add('main', cyl((x, -0.20, 0.1), (x, -0.32, 0.1), 0.09, n=10), 'red_armor' if x < 0 else 'metal_light')
    return M

def item_chlorine():
    M = Model()
    d = [(0.30*math.sin(a)*(1-0.15*math.cos(a)), -0.06+0.30*(-math.cos(a))) for a in np.linspace(0, 2*math.pi, 18, endpoint=False)]
    d = [(x*(1-max(0, y)/0.42), y*1.2) for x, y in d]
    M.add('main', prism(P(d), 0, 0.14, 0.7), 'chlor')
    M.add('main', cbox(-0.08, -0.12, 0.15, 0.06, 0.10, 0.01), 'gglow')
    return M
