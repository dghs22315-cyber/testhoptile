"""Defence workstream (hero rework): shields, walls, nanite repairer.

    .venv/bin/python tools/art/g_defense.py

Regenerates into mod/sprites:
  blocks/defense/shield-emitter{,-top,-full}   UEF T1 ForceProjector 2x2
  blocks/defense/ed-shield{,-top,-full}        Cybran T2 ForceProjector 2x2
  blocks/defense/pulse-shield{,-top,-full}     UEF T3 ForceProjector 3x3
  blocks/defense/nanite-repairer{,-top,-full}  Cybran T3 MendProjector 2x2
  blocks/walls/steel-wall, steel-wall-large, wolfram-wall{,-full}, wolfram-wall-large{,-full}
ForceProjector draws `-top` additively (alpha = shield buildup), MendProjector draws it tinted with
baseColor and a pulsing alpha, so both `-top` layers are white masks of the emitter core / coils.
1.0 = one tile, Z up, origin = block centre.
"""
import math
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from geom import *  # noqa: E402,F401
from mats import Model, MID  # noqa: E402
from hero import P, slope_plate, bolts_R, buttress, grille, cable, seam, antenna  # noqa: E402
from models import bolts, light, chevrons  # noqa: E402
import rend  # noqa: E402
from export import save, layer, FULL, qa_sheet  # noqa: E402

# nanite slurry glow, matched to the repairer's baseColor (84f491) at ramp step 3
rend.add_material('nanite', ['1c5a26', '2f9a3e', '52d064', '84f491', 'b4fac0', 'e0ffe6'], glow=True)

DEF = 'blocks/defense'
WAL = 'blocks/walls'


# ------------------------------------------------------------------ small geometry kit
def ngon(n, r, cx=0.0, cy=0.0, rot=0.0, sx=1.0, sy=1.0):
    return P([(cx+sx*r*math.cos(math.radians(rot+360.0*i/n)), cy+sy*r*math.sin(math.radians(rot+360.0*i/n))) for i in range(n)])


def circ(r, n, cx=0.0, cy=0.0, rot=0.0):
    a = np.radians(rot+np.arange(n)*360.0/n)
    return np.column_stack([cx+r*np.cos(a), cy+r*np.sin(a)])


def band(ri, ro, z, n=32, cx=0.0, cy=0.0, h=0.0, zi=None):
    """Flat (or conical when zi is given) annulus; h adds an outer skirt down to z-h."""
    zi = z if zi is None else zi
    T = [loft(ring(circ(ro, n, cx, cy), z), ring(circ(ri, n, cx, cy), zi), False, False)]
    if h > 0:
        T.append(loft(ring(circ(ro, n, cx, cy), z-h), ring(circ(ro, n, cx, cy), z), False, False))
    return np.concatenate(T)


def torus(M, g, R, r, z, m, n=28, k=8, a0=0.0, cx=0.0, cy=0.0):
    for i in range(n):
        a, b = math.radians(a0+360*i/n), math.radians(a0+360*(i+1)/n)
        M.add(g, cyl((cx+R*math.cos(a), cy+R*math.sin(a), z), (cx+R*math.cos(b), cy+R*math.sin(b), z), r, n=k), m)


def bipyr(n, r, zb, zm, zt, cx=0.0, cy=0.0, rot=0.0, sx=1.0, sy=1.0):
    mid = [np.array([x, y, zm]) for x, y in ngon(n, r, cx, cy, rot, sx, sy)]
    top = np.array([cx, cy, zt]); bot = np.array([cx, cy, zb])
    T = []
    for i in range(n):
        a, b = mid[i], mid[(i+1) % n]
        T.append([a, b, top]); T.append([b, a, bot])
    return clean(T)


def rod(p0, p1, r0, r1=None, n=8):
    return cyl(p0, p1, r0, r1, n=n)


def B(x0, x1, y0, y1, z0, z1):
    return box(min(x0, x1), max(x0, x1), min(y0, y1), max(y0, y1), z0, z1)


def rot_pts(pts, deg):
    c, s = math.cos(math.radians(deg)), math.sin(math.radians(deg))
    return [(x*c-y*s, x*s+y*c) for x, y in pts]


def capacitor(M, g, x, y, z0, h, r, body='metal_light', band_m='yellow', cap='hull_mid', tip='glow', collar='hull_dark'):
    """Upright capacitor can: collar, ribbed body, coloured band, cap with two terminals + status light."""
    M.add(g, cyl((x, y, z0), (x, y, z0+0.05), r*1.18, n=16), collar)
    M.add(g, cyl((x, y, z0+0.05), (x, y, z0+h), r, n=16), body)
    M.add(g, cyl((x, y, z0+h*0.55), (x, y, z0+h*0.72), r*1.05, n=16), band_m)
    M.add(g, cyl((x, y, z0+h), (x, y, z0+h+0.035), r*0.98, r*0.80, n=16), cap)
    for s in (-1, 1):
        M.add(g, cyl((x+s*r*0.42, y, z0+h+0.03), (x+s*r*0.42, y, z0+h+0.075), r*0.20, n=8), 'metal')
    if tip:
        M.add(g, cyl((x, y+r*0.40, z0+h+0.03), (x, y+r*0.40, z0+h+0.05), r*0.17, n=8), tip)


def fin_bank(M, g, x0, x1, y0, y1, z0, z1, n, fin='metal', base='vent', frame='hull_light', glow=None, R=None):
    """Cooling fins: n thin plates across y, standing on a dark trough, framed at both ends."""
    def A(T, m): M.add(g, tf(T, R), m)
    A(B(x0, x1, y0, y1, z0-0.01, z0+0.01), base)
    if glow:
        A(B(x0+0.03, x1-0.03, y0+0.02, y1-0.02, z0-0.01, z0+0.016), glow)
    st = (y1-y0)/n
    for i in range(n):
        y = y0+st*(i+0.5)
        A(prism(rect((x0+x1)/2, y, (x1-x0)/2-0.01, st*0.24), z0, z1, top_poly=rect((x0+x1)/2, y, (x1-x0)/2-0.03, st*0.14)), fin)
    for yy in (y0-0.03, y1+0.03):
        A(B(x0-0.02, x1+0.02, yy-0.03, yy+0.03, z0-0.01, z1+0.02), frame)


def heatmask(weights):
    """heat fn from {material: weight}."""
    ids = {MID[k]: v for k, v in weights.items()}

    def f(mp, X, Y, g):
        out = np.zeros(mp.shape)
        for i, v in ids.items():
            out = np.where(mp == i, v, out)
        return out
    return f


# ================================================================== SHIELD EMITTER - UEF T1 (2x2)
def shield_emitter():
    M = Model(); g = 'main'
    # stepped foundation
    M.add(g, prism(cham_rect(0.985, 0.985, 0.26), 0.0, 0.08, 0.985), 'hull_dark')
    M.add(g, prism(cham_rect(0.92, 0.92, 0.28), 0.08, 0.20, 0.95), 'hull_mid')
    M.add(g, prism(cham_rect(0.72, 0.72, 0.24), 0.20, 0.21, 0.98), 'hull_dark')
    for k in range(4):                                         # deck seams + bolts per quadrant
        S = rz(90*k)
        seam(M, g, *[tuple((S @ np.array([x, -0.62, 0]))[:2]) for x in (-0.34, 0.34)], 0.20, w=0.025, h=0.012)
        bolts_R(M, g, [(-0.42, -0.80), (0.42, -0.80)], 0.20, S, r=0.024)
    # corner capacitor cans (yellow-banded UEF stores)
    for sx in (-1, 1):
        for sy in (-1, 1):
            capacitor(M, g, sx*0.62, sy*0.62, 0.20, 0.24, 0.150)
            cable(M, g, [(sx*0.55, sy*0.50, 0.40), (sx*0.44, sy*0.38, 0.46), (sx*0.30, sy*0.26, 0.40)], 0.028, ends='yellow')
    # side cooling fin banks with blue glow in the trough
    for s in (-1, 1):
        fin_bank(M, g, 0.74, 0.92, -0.36, 0.36, 0.20, 0.34, 6, glow='glow', R=rz(0 if s > 0 else 180))
    # front: hazard strip + status lights; back: power intake box
    chevrons(M, g, 0, -0.86, 0.20, 0.52, 0.08, n=5)
    light(M, g, -0.38, -0.86, 0.20, 0.05, 0.04, 0.015)
    light(M, g, 0.38, -0.86, 0.20, 0.05, 0.04, 0.015)
    M.add(g, B(-0.30, 0.30, 0.74, 0.94, 0.20, 0.30), 'hull_light')
    M.add(g, B(-0.24, 0.24, 0.78, 0.90, 0.30, 0.315), 'vent')
    for x in (-0.16, 0.0, 0.16):
        M.add(g, B(x-0.035, x+0.035, 0.79, 0.89, 0.30, 0.33), 'yellow')
    # emitter pedestal: octagonal turret-like plinth
    M.add(g, prism(ngon(8, 0.50, rot=22.5), 0.20, 0.30, 0.94), 'hull_light')
    M.add(g, prism(ngon(8, 0.45, rot=22.5), 0.30, 0.34, 0.95), 'hull_mid')
    bolts(M, g, [(0.40*math.cos(math.radians(a)), 0.40*math.sin(math.radians(a))) for a in range(0, 360, 45)], 0.34, r=0.022)
    # copper field coil around the dish
    torus(M, g, 0.395, 0.04, 0.37, 'copper', n=28, k=8)
    for i in range(8):
        a = math.radians(22.5+45*i)
        M.add(g, tf(cbox(0.395, 0, 0.37, 0.07, 0.05, 0.10), rz(math.degrees(a))), 'hull_dark')
    # projector dish: rim + concave glass bowl + emitter mast and crystal on a tripod
    M.add(g, band(0.33, 0.37, 0.42, n=32, h=0.08), 'metal_light')
    M.add(g, band(0.12, 0.33, 0.42, n=32, zi=0.33), 'glass')
    M.add(g, band(0.0, 0.12, 0.33, n=20), 'hull_dark')
    for i in range(3):                                          # dish ribs
        a = math.radians(90+120*i+60)
        M.add(g, rod((0.14*math.cos(a), 0.14*math.sin(a), 0.345), (0.33*math.cos(a), 0.33*math.sin(a), 0.43), 0.016, n=6), 'metal')
    M.add(g, rod((0, 0, 0.33), (0, 0, 0.60), 0.045, n=10), 'metal')
    for i in range(3):
        a = math.radians(90+120*i)
        p0 = (0.35*math.cos(a), 0.35*math.sin(a), 0.43)
        M.add(g, rod(p0, (0.05*math.cos(a), 0.05*math.sin(a), 0.62), 0.022, 0.016, n=6), 'metal_light')
        M.add(g, cyl(p0, (p0[0], p0[1], p0[2]+0.03), 0.04, n=8), 'yellow')
    M.add(g, cyl((0, 0, 0.58), (0, 0, 0.62), 0.07, n=12), 'hull_mid')
    M.add(g, bipyr(6, 0.075, 0.60, 0.67, 0.76), 'glow')
    return M


# ================================================================== ED SHIELD - Cybran T2 (2x2)
def ed_shield():
    M = Model(); g = 'main'
    M.add(g, prism(cham_rect(0.97, 0.97, 0.40), 0.0, 0.09, 0.985), 'cy_dark')
    M.add(g, prism(cham_rect(0.84, 0.84, 0.40), 0.09, 0.21, 0.93), 'cy_mid')
    M.add(g, prism(cham_rect(0.66, 0.66, 0.30), 0.21, 0.22, 0.98), 'hull_dark')
    # diagonal Cybran legs with red inlays and glowing toes
    for k in range(4):
        buttress(M, g, 45+90*k, 0.60, 1.30, 0.15, 0.36, 0.12, z0=0.06, mat='cy_mid', inlay='red_armor', tip='rglow')
    # four sloped armour cheeks between the legs: two red-inlaid, two vented
    for k in range(4):
        S = rz(90*k)
        poly = [(-0.34, -0.50), (0.34, -0.50), (0.26, -0.88), (-0.26, -0.88)]
        zf = (lambda x, y: 0.34+(y+0.50)*0.32)
        if k % 2 == 0:
            slope_plate(M, g, poly, zf, 'cy_mid', thick=0.14, inlay='red_armor', isc=0.66, ih=0.03, R=S)
            bolts_R(M, g, [(-0.24, -0.56), (0.24, -0.56)], zf(0, -0.56)-0.005, S, r=0.022)
            M.add(g, tf(cbox(0, -0.80, zf(0, -0.80)+0.01, 0.20, 0.04, 0.04), S), 'rglow')
        else:
            M.add(g, tf(prism(P(poly), 0.20, 0.25, 0.95), S), 'cy_dark')
            grille(M, g, 0, -0.69, 0.25, 0.46, 0.22, n=6, glow='rglow', slat='cy_mid', frame='hull_dark', R=S)
    # hexagonal emitter housing
    M.add(g, prism(ngon(6, 0.46, rot=0), 0.21, 0.36, 0.90), 'cy_mid')
    M.add(g, prism(ngon(6, 0.40, rot=0), 0.36, 0.40, 0.95), 'hull_dark')
    for i in range(6):                                         # red armour facets on the housing
        a = 60*i+30
        pp = rot_pts([(0.27, -0.12), (0.36, -0.17), (0.36, 0.17), (0.27, 0.12)], a)
        M.add(g, prism(P(pp), 0.40, 0.43, 0.9), 'red_armor' if i % 2 == 0 else 'cy_mid')
    M.add(g, band(0.0, 0.25, 0.405, n=24), 'bore')
    M.add(g, band(0.18, 0.23, 0.42, n=24), 'rglow')
    # three claws hugging the crystal
    for i in range(3):
        a = math.radians(90+120*i)
        c, s = math.cos(a), math.sin(a)
        pts = [(0.36*c, 0.36*s, 0.42), (0.30*c, 0.30*s, 0.62), (0.16*c, 0.16*s, 0.76)]
        M.add(g, rod(pts[0], pts[1], 0.055, 0.045, n=6), 'cy_dark')
        M.add(g, rod(pts[1], pts[2], 0.045, 0.012, n=6), 'red_armor')
        M.add(g, sphereish(pts[1], 0.05, n=8), 'hull_dark')
    # the ED crystal: tall red bipyramid with a dark collar
    M.add(g, cyl((0, 0, 0.40), (0, 0, 0.48), 0.12, 0.09, n=12), 'hull_dark')
    M.add(g, bipyr(6, 0.115, 0.44, 0.58, 0.90, rot=30), 'rglow')
    # cables from the legs into the housing
    for k in range(4):
        R = rz(45+90*k)
        cable(M, g, [(0.80, 0, 0.30), (0.62, 0.0, 0.40), (0.44, 0, 0.36)], 0.03, ends='red_armor', R=R)
    antenna(M, g, (0.52, -0.30, 0.26), (0.76, -0.46, 0.70), tip='rglow', baseM='cy_mid')
    return M


# ================================================================== PULSE SHIELD - UEF T3 (3x3)
def pulse_shield():
    M = Model(); g = 'main'
    M.add(g, prism(cham_rect(1.48, 1.48, 0.42), 0.0, 0.10, 0.985), 'hull_dark')
    M.add(g, prism(cham_rect(1.36, 1.36, 0.46), 0.10, 0.26, 0.95), 'hull_mid')
    M.add(g, prism(cham_rect(1.10, 1.10, 0.40), 0.26, 0.275, 0.98), 'hull_dark')
    for k in range(4):                                         # diagonal yellow-inlaid buttresses with beacons
        buttress(M, g, 45+90*k, 1.02, 1.80, 0.20, 0.44, 0.14, z0=0.08, mat='hull_light', inlay='yellow', tip='glow')
    for k in (0, 2):                                           # front/back: three-can capacitor banks
        S = rz(90*k)
        M.add(g, tf(B(-0.62, 0.62, -1.40, -1.04, 0.26, 0.30), S), 'hull_light')
        M.add(g, tf(B(-0.58, 0.58, -1.36, -1.08, 0.30, 0.31), S), 'hull_dark')
        for x in (-0.38, 0.0, 0.38):
            xx, yy, _ = S @ np.array([x, -1.22, 0])
            capacitor(M, g, xx, yy, 0.30, 0.26, 0.13)
        bolts_R(M, g, [(-0.58, -1.38), (0.58, -1.38), (-0.58, -1.06), (0.58, -1.06)], 0.30, S, r=0.024)
        for x in (-0.38, 0.38):
            cable(M, g, [(x, -1.10, 0.52), (x*0.8, -0.98, 0.62), (x*0.6, -0.86, 0.56)], 0.035, ends='yellow', R=S)
    for k in (1, 3):                                           # sides: heat-sink fin banks with lit trough
        S = rz(90*k)
        fin_bank(M, g, -0.58, 0.58, -1.42, -1.06, 0.26, 0.44, 1, R=S)    # frame only
        for i in range(9):
            x = -0.50+i*0.125
            M.add(g, tf(prism(rect(x, -1.24, 0.022, 0.17), 0.27, 0.46, top_poly=rect(x, -1.24, 0.012, 0.15)), S), 'metal')
        M.add(g, tf(B(-0.54, 0.54, -1.38, -1.10, 0.265, 0.285), S), 'glow')
        light(M, g, *tuple((S @ np.array([0, -0.96, 0]))[:2]), 0.275, 0.10, 0.03)
    # deck bolts and seams
    for k in range(4):
        S = rz(90*k)
        seam(M, g, *[tuple((S @ np.array([x, -0.98, 0]))[:2]) for x in (-0.50, 0.50)], 0.275, w=0.03, h=0.012)
    # pulse ring: big copper-wound torus on four clamps
    z = 0.58
    M.add(g, band(0.86, 1.00, 0.30, n=48, h=0.04), 'metal')
    torus(M, g, 0.86, 0.10, z, 'metal_light', n=40, k=10)
    for i in range(16):
        a = 360*i/16+11.25
        ca, sa = math.cos(math.radians(a)), math.sin(math.radians(a))
        c = np.array([0.86*ca, 0.86*sa, z]); t = np.array([-sa, ca, 0])
        M.add(g, cyl(c-t*0.06, c+t*0.06, 0.135, n=12), 'copper')
        M.add(g, cyl(c-t*0.075, c-t*0.06, 0.145, n=12), 'hull_dark')
    for i in range(4):
        R = rz(45+90*i)
        M.add(g, tf(B(0.72, 1.02, -0.09, 0.09, 0.30, z+0.16), R), 'hull_light')
        M.add(g, tf(B(0.76, 0.98, -0.06, 0.06, z+0.16, z+0.18), R), 'yellow')
        M.add(g, tf(cyl((0.87, 0, z+0.18), (0.87, 0, z+0.21), 0.035, n=8), R), 'glow')
    # central pulse tower: three stepped drums with glow seams
    M.add(g, cyl((0, 0, 0.27), (0, 0, 0.44), 0.62, 0.58, n=40), 'hull_light')
    M.add(g, band(0.50, 0.58, 0.44, n=40), 'hull_mid')
    M.add(g, cyl((0, 0, 0.44), (0, 0, 0.58), 0.50, 0.46, n=36), 'hull_mid')
    M.add(g, band(0.44, 0.50, 0.585, n=36), 'glow')
    M.add(g, cyl((0, 0, 0.58), (0, 0, 0.70), 0.42, 0.36, n=32), 'metal')
    for i in range(8):
        a = math.radians(22.5+45*i)
        M.add(g, tf(cbox(0.39, 0, 0.66, 0.08, 0.09, 0.10), rz(math.degrees(a))), 'hull_dark')
    M.add(g, band(0.0, 0.36, 0.70, n=32), 'hull_dark')
    bolts(M, g, [(0.53*math.cos(math.radians(a)), 0.53*math.sin(math.radians(a))) for a in range(0, 360, 30)], 0.44, r=0.022)
    # four converging emitter prongs and the pulse orb
    for i in range(4):
        a = math.radians(45+90*i); c, s = math.cos(a), math.sin(a)
        pts = [(0.30*c, 0.30*s, 0.70), (0.30*c, 0.30*s, 0.86), (0.20*c, 0.20*s, 0.98), (0.11*c, 0.11*s, 1.02)]
        M.add(g, tube_path(pts, 0.035, n=8), 'metal_light')
        M.add(g, cyl((0.30*c, 0.30*s, 0.70), (0.30*c, 0.30*s, 0.76), 0.06, n=10), 'yellow')
        M.add(g, cyl((0.30*c, 0.30*s, 0.82), (0.30*c, 0.30*s, 0.86), 0.05, n=10), 'copper')
    for i in range(4):
        a = math.radians(90*i); c, s = math.cos(a), math.sin(a)
        M.add(g, tf(B(0.10, 0.30, -0.035, 0.035, 0.70, 0.72), rz(90*i)), 'glow')
    M.add(g, sphereish((0, 0, 1.0), 0.15, n=14), 'glow')
    # power conduits from the capacitor banks to the tower
    for s in (-1, 1):
        cable(M, g, [(s*0.98, 0.10, 0.30), (s*0.80, 0.10, 0.36), (s*0.62, 0.10, 0.40)], 0.035, ends='yellow')
    return M


# ================================================================== NANITE REPAIRER - Cybran T3 MendProjector (2x2)
def nanite_repairer():
    M = Model(); g = 'main'
    M.add(g, prism(cham_rect(0.97, 0.97, 0.34), 0.0, 0.09, 0.985), 'cy_dark')
    M.add(g, prism(cham_rect(0.86, 0.86, 0.34), 0.09, 0.20, 0.94), 'cy_mid')
    M.add(g, prism(cham_rect(0.70, 0.70, 0.26), 0.20, 0.21, 0.98), 'hull_dark')
    # left/right: feed pipes into the vat; front/back: red-inlaid sloped armour
    for s in (-1, 1):
        x0 = s*0.92
        for y in (-0.16, 0.16):
            M.add(g, cyl((x0, y, 0.30), (s*0.44, y, 0.30), 0.055, n=12), 'metal')
            for xc in (s*0.82, s*0.60):
                M.add(g, cyl((xc-0.025, y, 0.30), (xc+0.025, y, 0.30), 0.075, n=12), 'red_armor')
        M.add(g, B(s*0.70, s*0.94, -0.30, 0.30, 0.20, 0.26), 'cy_dark')
        M.add(g, cyl((s*0.86, -0.36, 0.20), (s*0.86, -0.36, 0.36), 0.07, n=12), 'cy_mid')
        M.add(g, cyl((s*0.86, -0.36, 0.36), (s*0.86, -0.36, 0.38), 0.045, n=10), 'rglow')
    for k in (0, 2):
        S = rz(90*k)
        poly = [(-0.34, -0.56), (0.34, -0.56), (0.26, -0.90), (-0.26, -0.90)]
        zf = (lambda x, y: 0.32+(y+0.56)*0.30)
        slope_plate(M, g, poly, zf, 'cy_mid', thick=0.13, inlay='red_armor', isc=0.62, ih=0.03, R=S)
        M.add(g, tf(cbox(0, -0.83, zf(0, -0.83)+0.01, 0.16, 0.035, 0.04), S), 'rglow')
    # four corner nanite emitter needles
    for sx in (-1, 1):
        for sy in (-1, 1):
            cx, cy = sx*0.66, sy*0.66
            M.add(g, prism(ngon(6, 0.15, cx, cy, 30), 0.20, 0.36, 0.82), 'cy_mid')
            M.add(g, prism(ngon(6, 0.10, cx, cy, 30), 0.36, 0.40, 0.9), 'red_armor')
            tip = (cx*1.10, cy*1.10, 0.66)
            M.add(g, rod((cx, cy, 0.40), tip, 0.045, 0.018, n=6), 'metal_light')
            M.add(g, sphereish(tip, 0.045, n=8), 'nanite')
            cable(M, g, [(cx*0.86, cy*0.86, 0.32), (cx*0.74, cy*0.74, 0.42), (cx*0.62, cy*0.62, 0.40)], 0.026, ends='red_armor')
    # the vat: armoured drum, red bands, dark well with a three-arm nanite swirl and rotor hub
    M.add(g, cyl((0, 0, 0.20), (0, 0, 0.44), 0.50, 0.47, n=36), 'cy_mid')
    for zb in (0.25, 0.36):
        M.add(g, cyl((0, 0, zb), (0, 0, zb+0.04), 0.505, n=36), 'red_armor')
    M.add(g, band(0.38, 0.47, 0.46, n=36, h=0.02), 'metal')
    for i in range(6):
        a = math.radians(30+60*i)
        M.add(g, tf(cbox(0.425, 0, 0.465, 0.08, 0.06, 0.03), rz(math.degrees(a))), 'hull_dark')
    M.add(g, band(0.0, 0.38, 0.40, n=36), 'bore')
    for j in range(3):
        prev = None
        for t in np.linspace(0, 1, 9):
            r = 0.09+0.27*t; a = math.radians(120*j+20+t*170)
            p = np.array([r*math.cos(a), r*math.sin(a), 0.41])
            if prev is not None:
                w = 0.040-0.016*t
                M.add(g, rod(prev, p, w, w, n=6), 'nanite')
            prev = p
    M.add(g, cyl((0, 0, 0.40), (0, 0, 0.47), 0.085, n=14), 'cy_mid')
    M.add(g, cyl((0, 0, 0.47), (0, 0, 0.49), 0.05, n=10), 'rglow')
    for i in range(3):
        a = math.radians(90+120*i)
        M.add(g, rod((0.06*math.cos(a), 0.06*math.sin(a), 0.47), (0.40*math.cos(a), 0.40*math.sin(a), 0.47), 0.018, n=6), 'metal_light')
    return M


# ================================================================== WALLS
def _wall_base(M, g, h, mat_frame, mat_plate, step=0.10, z1=0.24, ch=0.08):
    M.add(g, prism(cham_rect(h-0.005, h-0.005, ch), 0.0, 0.09, 0.975), mat_frame)
    M.add(g, prism(cham_rect(h-0.05, h-0.05, ch+0.01), 0.09, z1, top_poly=cham_rect(h-0.05-step*0.6, h-0.05-step*0.6, ch*0.9)), mat_plate)


def steel_wall():
    M = Model(); g = 'main'; h = 0.5
    _wall_base(M, g, h, 'hull_dark', 'steel', z1=0.22)
    M.add(g, prism(cham_rect(0.30, 0.30, 0.07), 0.22, 0.27, top_poly=cham_rect(0.26, 0.26, 0.06)), 'steel')
    M.add(g, B(-0.32, 0.32, -0.035, 0.035, 0.22, 0.30), 'hull_light')        # horizontal reinforcing rib
    for x in (-0.24, 0.24):
        M.add(g, cyl((x, 0, 0.30), (x, 0, 0.315), 0.03, n=8), 'metal_light')
    bolts(M, g, [(-0.36, -0.36), (0.36, -0.36), (-0.36, 0.36), (0.36, 0.36)], 0.22, r=0.035)
    M.add(g, prism(P([(0.14, -0.40), (0.24, -0.40), (0.30, -0.34), (0.20, -0.34)]), 0.22, 0.235), 'yellow')
    return M


def steel_wall_large():
    M = Model(); g = 'main'; h = 1.0
    _wall_base(M, g, h, 'hull_dark', 'steel', step=0.12, z1=0.24, ch=0.14)
    for sx in (-1, 1):                                          # two raised armour slabs split by a seam
        M.add(g, prism(cham_rect(0.36, 0.72, 0.10, cx=sx*0.42), 0.24, 0.31, top_poly=cham_rect(0.32, 0.68, 0.09, cx=sx*0.42)), 'steel')
        bolts(M, g, [(sx*0.42, y) for y in (-0.62, -0.30, 0.30, 0.62)], 0.31, r=0.032)
    M.add(g, B(-0.06, 0.06, -0.86, 0.86, 0.24, 0.27), 'hull_dark')          # central seam channel
    for y in (-0.46, 0.0, 0.46):                                   # three horizontal ribs across both slabs
        M.add(g, B(-0.80, 0.80, y-0.045, y+0.045, 0.24, 0.35), 'hull_light')
        for x in (-0.70, 0.70):
            M.add(g, cyl((x, y, 0.35), (x, y, 0.365), 0.032, n=8), 'metal_light')
    M.add(g, cyl((0, 0, 0.27), (0, 0, 0.40), 0.16, 0.13, n=8, phase=math.pi/8), 'steel')
    M.add(g, cyl((0, 0, 0.40), (0, 0, 0.415), 0.07, n=8, phase=math.pi/8), 'hull_dark')
    for sx, sy in ((-1, 1), (1, -1)):                              # yellow hazard corners
        c = np.array([sx*0.80, sy*0.80])
        for i in range(2):
            o = (i-0.5)*0.11
            pp = rot_pts([(-0.10, -0.022), (0.10, -0.022), (0.10, 0.022), (-0.10, 0.022)], -45*sx*sy)
            M.add(g, prism(P([(x+c[0]+o*sx, y+c[1]-o*sy*-1) for x, y in pp]), 0.24, 0.255), 'yellow')
    bolts(M, g, [(sx*0.88, sy*0.88) for sx in (-1, 1) for sy in (-1, 1)], 0.24, r=0.03)
    return M


def wolfram_wall():
    M = Model(); g = 'main'; h = 0.5
    _wall_base(M, g, h, 'tung', 'tung', step=0.10, z1=0.22)
    M.add(g, prism(cham_rect(0.36, 0.36, 0.10), 0.22, 0.30, top_poly=cham_rect(0.30, 0.30, 0.08)), 'tung')
    M.add(g, prism(cham_rect(0.20, 0.20, 0.06), 0.30, 0.36, top_poly=cham_rect(0.16, 0.16, 0.05)), 'ore_wolf')
    M.add(g, B(-0.14, 0.14, -0.02, 0.02, 0.36, 0.368), 'cobalt')
    for sx in (-1, 1):
        for sy in (-1, 1):
            M.add(g, cyl((sx*0.33, sy*0.33, 0.30), (sx*0.33, sy*0.33, 0.33), 0.045, 0.035, n=8), 'steel')
    return M


def wolfram_wall_large():
    M = Model(); g = 'main'; h = 1.0
    _wall_base(M, g, h, 'tung', 'tung', step=0.14, z1=0.24, ch=0.16)
    M.add(g, prism(cham_rect(0.80, 0.80, 0.18), 0.24, 0.34, top_poly=cham_rect(0.72, 0.72, 0.16)), 'tung')
    M.add(g, prism(cham_rect(0.56, 0.56, 0.12), 0.34, 0.42, top_poly=cham_rect(0.50, 0.50, 0.10)), 'ore_wolf')
    for y in (-0.22, 0.22):
        M.add(g, B(-0.60, 0.60, y-0.05, y+0.05, 0.34, 0.46), 'tung')
        for x in (-0.40, 0.0, 0.40):
            M.add(g, cyl((x, y, 0.46), (x, y, 0.48), 0.04, n=8), 'steel')
    M.add(g, B(-0.40, 0.40, -0.025, 0.025, 0.42, 0.43), 'cobalt')
    for sx in (-1, 1):
        for sy in (-1, 1):
            M.add(g, cyl((sx*0.70, sy*0.70, 0.34), (sx*0.70, sy*0.70, 0.38), 0.06, 0.05, n=8), 'steel')
    return M


# ================================================================== driver
UEF_TOP = heatmask({'glow': 1.0, 'copper': 0.75, 'yellow': 0.25})
CY_TOP = heatmask({'rglow': 1.0, 'red_armor': 0.35})
NANITE_TOP = heatmask({'nanite': 1.0, 'bore': 0.45, 'rglow': 0.5})


def block(name, M, canvas, topfn, d=DEF):
    from rend import heat_sprite
    main, hm = layer(M, ['main'], canvas, heat=topfn)
    save(main, d, name)
    save(heat_sprite(hm), d, f'{name}-top')
    save(main, d, f'{name}-full')
    FULL[name] = np.asarray(main)
    print(f'{name:18s} {M.ntri():6d} tris  {canvas}px', flush=True)


def wall(name, M, canvas, full=False):
    main, _ = layer(M, ['main'], canvas)
    save(main, WAL, name)
    if full:
        save(main, WAL, f'{name}-full')
    FULL[name] = np.asarray(main)
    print(f'{name:18s} {M.ntri():6d} tris  {canvas}px', flush=True)


def main():
    block('shield-emitter', shield_emitter(), 64, UEF_TOP)
    block('ed-shield', ed_shield(), 64, CY_TOP)
    block('pulse-shield', pulse_shield(), 96, UEF_TOP)
    block('nanite-repairer', nanite_repairer(), 64, NANITE_TOP)
    wall('steel-wall', steel_wall(), 32)
    wall('steel-wall-large', steel_wall_large(), 64)
    wall('wolfram-wall', wolfram_wall(), 32, full=True)
    wall('wolfram-wall-large', wolfram_wall_large(), 64, full=True)
    print(qa_sheet(['shield-emitter', 'ed-shield', 'pulse-shield', 'nanite-repairer'], 'g_defense-blocks.png', sc=3))
    print(qa_sheet(['steel-wall', 'steel-wall-large', 'wolfram-wall', 'wolfram-wall-large'], 'g_defense-walls.png', sc=4))


if __name__ == '__main__':
    main()
