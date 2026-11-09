"""Hero-level remakes of the direct-fire / anti-air line (art workstream g_turrets).

    .venv/bin/python tools/art/g_turrets.py

Rivet (T1 UEF twin MG, 2x2), Sparrow (T1 UEF twin flak, 2x2), Lash (T2 Cybran twin pulse laser, 2x2),
Hydra (T3 Cybran 8-cell missile battery, 3x3), Wasp (T3 Cybran quad-rail AA launcher, 3x3).
Groups: base (static), body (rotating head), barrel (recoiling RegionPart "-barrel").
SPEC[name] holds the numbers the block JSON depends on (muzzle y -> shootY, barrel x -> shoot.spread)."""
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from geom import *  # noqa: E402,F401
from mats import Model, MID  # noqa: E402
from models import bolts, light, chevrons  # noqa: E402
from hero import *  # noqa: E402,F401
import export  # noqa: E402
from rend import dilate  # noqa: E402

SPEC = {}


def B(x0, x1, y0, y1, z0, z1):
    return box(min(x0, x1), max(x0, x1), min(y0, y1), max(y0, y1), min(z0, z1), max(z0, z1))


def missile(M, g, x, y0, y1, z, r, body='metal_light', tip='red_armor', band='red_armor', fin='hull_mid', fins=True):
    """Missile lying along +Y: motor nozzle, body, warning band, nose cone, cruciform tail fins."""
    L = y1 - y0
    yn = y1 - L * 0.24
    M.add(g, cyl((x, y0, z), (x, y0 + 0.035, z), r * 0.70, r * 0.92, n=12), 'hull_dark')
    M.add(g, cyl((x, y0 + 0.035, z), (x, yn, z), r, n=12), body)
    M.add(g, cyl((x, yn - 0.06, z), (x, yn - 0.035, z), r * 1.04, n=12), band)
    M.add(g, cyl((x, yn, z), (x, y1, z), r, r * 0.18, n=12), tip)
    if fins:
        fw, fl = r * 1.25, L * 0.20
        for s in (-1, 1):
            p = ccw([(x + s * r * 0.8, y0 + 0.03), (x + s * (r + fw), y0 + 0.03), (x + s * (r + fw), y0 + fl * 0.45), (x + s * r * 0.8, y0 + fl)])
            M.add(g, prism(p, z - 0.008, z + 0.008), fin)
        M.add(g, B(x - 0.008, x + 0.008, y0 + 0.03, y0 + fl, z + r * 0.8, z + r + fw), fin)


# ================================================================== Rivet - T1 UEF twin machine gun (2x2)
def rivet():
    M = Model(); g = 'base'
    z = uef_hero_base(M, g, 1.0, top=0.18)
    g = 'body'
    hull = mirror_half([(0, 0.42), (0.34, 0.40), (0.52, 0.22), (0.56, -0.26), (0.46, -0.54), (0.22, -0.66), (0, -0.68)])
    M.add(g, prism(hull, z, z + 0.17, 0.93), 'hull_mid')
    M.add(g, prism(scale_poly(hull, 0.86, (0, 0)), z + 0.17, z + 0.22, 0.95), 'hull_light')
    top = z + 0.22
    # front mantlet: sloped glacis with yellow hazard inlay, gun saddle on top
    zf = (lambda x, y: top + 0.10 - (y - 0.16) * 0.40)
    slope_plate(M, g, [(-0.36, 0.16), (0.36, 0.16), (0.30, 0.42), (-0.30, 0.42)], zf, 'hull_light', thick=0.12, inlay='yellow', isc=0.70, ih=0.016)
    bolts_on(M, g, [(-0.30, 0.20), (0.30, 0.20), (-0.26, 0.38), (0.26, 0.38)], zf, r=0.018)
    for s in (-1, 1):
        # ammunition can + belt feed into each receiver
        cx = s * 0.43
        M.add(g, B(cx - 0.11, cx + 0.11, -0.48, 0.04, top - 0.04, top + 0.12), 'steel')
        M.add(g, B(cx - 0.095, cx + 0.095, -0.46, 0.02, top + 0.12, top + 0.135), 'hull_mid')
        M.add(g, B(cx - 0.095, cx + 0.095, -0.46, -0.41, top + 0.135, top + 0.145), 'yellow')
        M.add(g, B(cx - 0.02, cx + 0.02, -0.34, -0.10, top + 0.135, top + 0.15), 'metal_light')
        bolts(M, g, [(cx - 0.07, -0.02), (cx + 0.07, -0.02), (cx - 0.07, -0.30), (cx + 0.07, -0.30)], top + 0.135, r=0.013)
        for i in range(5):
            t = i / 4.0
            bx = cx - s * (0.04 + t * 0.16); by = -0.02 + t * 0.06; bz = top + 0.15 + math.sin(t * math.pi) * 0.04
            M.add(g, cyl((bx, by - 0.055, bz), (bx, by + 0.035, bz), 0.024, n=8), 'copper')
            M.add(g, cyl((bx, by + 0.035, bz), (bx, by + 0.07, bz), 0.024, 0.008, n=8), 'metal')
            M.add(g, B(bx - 0.03, bx + 0.03, by - 0.03, by - 0.015, bz - 0.02, bz + 0.026), 'hull_dark')
        # side armour skirt with lamp
        light(M, g, s * 0.50, 0.14, top - 0.02, 0.04, 0.04)
        M.add(g, cyl((s * 0.28, -0.60, top - 0.04), (s * 0.28, -0.60, top + 0.06), 0.04, n=10), 'metal')
        M.add(g, cyl((s * 0.28, -0.60, top + 0.06), (s * 0.28, -0.60, top + 0.065), 0.028, n=8), 'heat')
    # rear: cooling grille, gunner sight, antenna, seams
    grille(M, g, 0, -0.46, top, 0.34, 0.12, n=6, glow='glow')
    M.add(g, B(-0.24, -0.06, -0.30, -0.14, top - 0.01, top + 0.10), 'hull_mid')
    M.add(g, B(-0.22, -0.08, -0.15, -0.13, top + 0.03, top + 0.08), 'glass')
    M.add(g, B(-0.20, -0.10, -0.28, -0.18, top + 0.10, top + 0.11), 'glow')
    antenna(M, g, (0.14, -0.60, top), (0.20, -0.84, top + 0.36))
    seam(M, g, (-0.30, 0.02), (0.30, 0.02), top, w=0.02, h=0.01)
    bolts(M, g, [(-0.34, -0.56), (0.34, -0.56), (0, -0.62)], top, r=0.016)
    # ---- twin gun cradle (recoiling part)
    g = 'barrel'; zg = top + 0.16; XS = (-0.19, 0.19)
    M.add(g, B(-0.11, 0.11, -0.24, 0.20, zg - 0.08, zg + 0.02), 'hull_dark')
    M.add(g, B(-0.06, 0.06, -0.18, 0.12, zg + 0.02, zg + 0.035), 'glow')
    for x in XS:
        s = 1 if x > 0 else -1
        M.add(g, B(x - 0.075, x + 0.075, -0.32, 0.22, zg - 0.07, zg + 0.06), 'hull_light')        # receiver
        M.add(g, B(x - 0.06, x + 0.06, -0.28, 0.18, zg + 0.06, zg + 0.085), 'hull_mid')           # top cover
        M.add(g, B(x - 0.045, x + 0.045, 0.06, 0.16, zg + 0.085, zg + 0.095), 'yellow')
        M.add(g, B(x + s * 0.075, x + s * 0.10, -0.10, 0.06, zg - 0.03, zg + 0.05), 'metal')         # feed tray
        M.add(g, B(x - s * 0.075, x - s * 0.105, -0.20, -0.16, zg - 0.01, zg + 0.03), 'metal_light')  # charging handle
        M.add(g, B(x - 0.05, x + 0.05, -0.40, -0.32, zg - 0.05, zg + 0.04), 'metal')              # buffer
        M.add(g, cyl((x, -0.40, zg), (x, -0.43, zg), 0.03, n=8), 'glow')
        bolts(M, g, [(x - 0.04, -0.24), (x + 0.04, -0.24)], zg + 0.085, r=0.012)
        # perforated cooling jacket
        for k in range(7):
            y = 0.22 + k * 0.08
            M.add(g, cyl((x, y, zg), (x, y + 0.055, zg), 0.064, n=14), 'metal')
            M.add(g, cyl((x, y + 0.055, zg), (x, y + 0.08, zg), 0.052, n=14), 'vent')
        M.add(g, cyl((x, 0.78, zg), (x, 0.80, zg), 0.07, n=14), 'hull_mid')
        M.add(g, cyl((x, 0.80, zg), (x, 1.06, zg), 0.033, n=12), 'metal_light')
        M.add(g, cyl((x, 1.06, zg), (x, 1.18, zg), 0.046, n=12), 'hull_dark')                    # flash hider
        for a in (0, 90, 180, 270):
            M.add(g, tf(B(-0.012, 0.012, 1.08, 1.17, 0.040, 0.05), ry(a), (x, 0, zg)), 'metal')
        M.add(g, cyl((x, 1.18, zg), (x, 1.19, zg), 0.028, n=10), 'bore')
    M.add(g, B(-0.19, 0.19, 0.60, 0.66, zg - 0.03, zg + 0.03), 'hull_mid')                       # barrel clamp
    M.add(g, B(-0.08, 0.08, 0.61, 0.65, zg + 0.03, zg + 0.045), 'yellow')
    M.add(g, B(-0.012, 0.012, 0.56, 0.66, zg + 0.045, zg + 0.10), 'metal')                         # front sight post
    SPEC['rivet'] = dict(shootY=1.19 * 8, spread=0.38 * 8, top=top)
    return M


heat_rivet = heat_grad(0.55, 1.19, mats=('metal', 'metal_light', 'hull_dark', 'bore', 'vent'), always=())


# ================================================================== Sparrow - T1 UEF twin flak (2x2)
def sparrow():
    M = Model(); g = 'base'
    z = uef_hero_base(M, g, 1.0, top=0.18)
    g = 'body'
    hull = P([(0.52 * math.cos(math.radians(22.5 + 45 * i)), 0.52 * math.sin(math.radians(22.5 + 45 * i)) - 0.06) for i in range(8)])
    M.add(g, prism(hull, z, z + 0.15, 0.93), 'hull_mid')
    M.add(g, prism(scale_poly(hull, 0.84), z + 0.15, z + 0.20, 0.95), 'hull_light')
    top = z + 0.20
    for s in (-1, 1):
        # trunnion cheeks carrying each gun
        M.add(g, B(s * 0.18, s * 0.46, -0.16, 0.30, top - 0.02, top + 0.10), 'hull_light')
        M.add(g, B(s * 0.20, s * 0.44, -0.14, 0.28, top + 0.10, top + 0.12), 'hull_mid')
        M.add(g, B(s * 0.42, s * 0.445, -0.10, 0.24, top + 0.12, top + 0.125), 'yellow')
        bolts(M, g, [(s * 0.22, -0.12), (s * 0.42, -0.12), (s * 0.22, 0.26), (s * 0.42, 0.26)], top + 0.12, r=0.014)
        light(M, g, s * 0.50, -0.30, top - 0.04, 0.035, 0.05)
        # ready-ammo racks on the rear flanks
        for i in range(3):
            shell(M, g, s * (0.30 + i * 0.07), -0.44, top + 0.03, L=0.22, r=0.03)
        M.add(g, B(s * 0.25, s * 0.48, -0.57, -0.53, top - 0.01, top + 0.06), 'hull_light')
    # rear radar mast + dish (fire-control) and optics box
    M.add(g, cyl((0, -0.40, top - 0.01), (0, -0.40, top + 0.16), 0.05, n=12), 'metal')
    dish_c = np.array([0.0, -0.40, top + 0.20])
    rings = []
    for k, (r, dz) in enumerate(((0.05, -0.04), (0.17, 0.0), (0.24, 0.05))):
        pts = [(dish_c[0] + r * math.cos(a), dish_c[1] + 0.62 * r * math.sin(a), dish_c[2] + dz) for a in np.linspace(0, 2 * math.pi, 20, endpoint=False)]
        rings.append(np.array(pts))
    M.add(g, tf(loft(rings[0], rings[1]), rx(-25), (0, 0, 0)) - tf(np.array([dish_c]), rx(-25))[0] + dish_c, 'metal_light')
    M.add(g, tf(loft(rings[1], rings[2]), rx(-25), (0, 0, 0)) - tf(np.array([dish_c]), rx(-25))[0] + dish_c, 'metal_light')
    M.add(g, cyl((0, -0.40, top + 0.16), (0, -0.33, top + 0.30), 0.012, n=6), 'metal')
    M.add(g, sphereish((0, -0.33, top + 0.30), 0.025, n=8), 'glow')
    M.add(g, B(-0.12, 0.12, -0.12, 0.08, top - 0.01, top + 0.07), 'hull_dark')
    M.add(g, B(-0.08, 0.08, 0.06, 0.09, top + 0.01, top + 0.06), 'glass')
    seam(M, g, (-0.14, -0.20), (0.14, -0.20), top, w=0.02, h=0.01)
    grille(M, g, 0, -0.58, top - 0.04, 0.22, 0.06, n=4)
    # ---- twin elevated flak guns (recoiling part)
    g = 'barrel_local'; XS = (-0.31, 0.31)
    for x in XS:
        s = 1 if x > 0 else -1
        M.add(g, B(x - 0.10, x + 0.10, -0.36, 0.14, -0.09, 0.08), 'hull_light')                    # breech block
        M.add(g, B(x - 0.085, x + 0.085, -0.32, 0.10, 0.08, 0.10), 'hull_mid')
        M.add(g, B(x - 0.07, x + 0.07, -0.30, -0.26, 0.10, 0.11), 'yellow')
        for i in range(4):                                                                         # 4-round clip
            yy = -0.18 + i * 0.075
            M.add(g, cyl((x, yy, 0.10), (x, yy, 0.18), 0.03, n=10), 'copper')
            M.add(g, cyl((x, yy, 0.18), (x, yy, 0.24), 0.03, 0.008, n=10), 'metal')
        M.add(g, B(x - 0.045, x + 0.045, -0.23, 0.07, 0.10, 0.13), 'metal')
        M.add(g, cyl((x, 0.14, 0), (x, 0.40, 0), 0.085, n=16), 'hull_dark')                         # recoil sleeve
        for y in (0.18, 0.32):
            M.add(g, cyl((x, y, 0), (x, y + 0.035, 0), 0.098, n=16), 'metal_light')
        M.add(g, cyl((x, 0.40, 0), (x, 0.92, 0), 0.05, 0.045, n=14), 'metal')
        M.add(g, cyl((x, 0.62, 0), (x, 0.66, 0), 0.062, n=14), 'hull_mid')
        muzzle_brake(M, g, 0.92, 0.20, 0.062, x=x, nb=2, trim='yellow', bore_r=0.03, out=0.03)
        hydraulic(M, g, x - s * 0.11, -0.03, -0.26, 0.20, 0.42, r=0.03)
    M.add(g, B(-0.21, 0.21, -0.06, 0.06, -0.05, 0.04), 'hull_mid')                                  # cross shaft
    M.add(g, cyl((-0.21, 0.0, 0), (0.21, 0.0, 0), 0.05, n=12), 'metal')
    pv = (0, 0.04, top + 0.13); elevate(M, 28, pv)
    my, mz = muzzle_world(28, pv, 1.12 + 0.022)
    SPEC['sparrow'] = dict(shootY=my * 8, spread=0.62 * 8, top=top)
    return M


heat_sparrow = heat_grad(0.45, 1.05, mats=('metal', 'metal_light', 'hull_dark', 'bore'), always=())


# ================================================================== Lash - T2 Cybran twin pulse laser (2x2)
def lash():
    M = Model(); g = 'base'
    z = cy_hero_base(M, g, 2 / 3)
    g = 'body'
    hull = mirror_half([(0, 0.34), (0.22, 0.34), (0.38, 0.10), (0.40, -0.30), (0.26, -0.54), (0, -0.60)])
    M.add(g, prism(hull, z, z + 0.16, 0.90), 'hull_dark')
    M.add(g, prism(scale_poly(hull, 0.80, (0, 0)), z + 0.16, z + 0.22, 0.92), 'cy_mid')
    top = z + 0.22
    for s in (1, -1):
        # swept red armour wings (Scorpion family)
        W = [(0.30, 0.22), (0.52, 0.02), (0.62, -0.46), (0.54, -0.62), (0.40, -0.40), (0.30, -0.10)]
        zw = (lambda x, y: top - 0.02 - (abs(x) - 0.30) * 0.40)
        slope_plate(M, g, [(s * x, y) for x, y in W], zw, 'hull_light', thick=0.10, inlay='red_armor', isc=0.66, ih=0.02)
        M.add(g, cbox(s * 0.58, -0.50, zw(0.58, 0) + 0.01, 0.04, 0.08, 0.03), 'rglow')
        bolts_on(M, g, [(s * 0.34, 0.08), (s * 0.36, -0.30)], zw, r=0.016)
        cable(M, g, [(s * 0.22, -0.40, top + 0.07), (s * 0.24, -0.10, top + 0.10), (s * 0.20, 0.06, top + 0.12)], 0.022)
    # capacitor bank (glows with charge = heat layer)
    for i, y in enumerate((-0.18, -0.34)):
        M.add(g, cyl((-0.20, y, top + 0.06), (0.20, y, top + 0.06), 0.065, n=14), 'hull_dark')
        for x in np.arange(-0.16, 0.17, 0.064):
            M.add(g, cyl((x - 0.018, y, top + 0.06), (x + 0.018, y, top + 0.06), 0.072, n=14), 'coil')
        for sx in (-0.21, 0.21):
            M.add(g, cyl((sx - 0.015, y, top + 0.06), (sx + 0.015, y, top + 0.06), 0.08, n=14), 'red_armor')
    # heat sink fins + rear vent
    for i in range(6):
        x = -0.15 + i * 0.06
        M.add(g, B(x - 0.012, x + 0.012, -0.56, -0.44, top - 0.02, top + 0.07), 'metal')
    M.add(g, B(-0.19, 0.19, -0.57, -0.43, top - 0.03, top - 0.01), 'rglow')
    antenna(M, g, (-0.24, -0.50, top), (-0.30, -0.74, top + 0.30), tip='rglow')
    # ---- twin emitter prongs (recoiling part)
    g = 'barrel'; ze = top + 0.15; XS = (-0.17, 0.17)
    M.add(g, B(-0.13, 0.13, -0.06, 0.20, ze - 0.08, ze + 0.02), 'hull_dark')
    M.add(g, cbox(0, 0.10, ze + 0.03, 0.08, 0.08, 0.02), 'rglow')
    for x in XS:
        s = 1 if x > 0 else -1
        hx = [(x - 0.075, -0.10), (x + 0.075, -0.10), (x + 0.085, 0.10), (x + 0.06, 0.40), (x - 0.06, 0.40), (x - 0.085, 0.10)]
        M.add(g, prism(P(hx), ze - 0.07, ze + 0.06, 0.88), 'hull_dark')
        M.add(g, prism(P([(x - 0.05, -0.06), (x + 0.05, -0.06), (x + 0.04, 0.34), (x - 0.04, 0.34)]), ze + 0.06, ze + 0.085, 0.9), 'red_armor')
        coil_jacket(M, g, 0.40, 4, 0.07, 0.058, band='red_armor', coil='coil', x=x, z=ze)
        M.add(g, cyl((x, 0.68, ze), (x, 0.72, ze), 0.07, n=14), 'hull_mid')
        for k, (y, r) in enumerate(((0.72, 0.052), (0.82, 0.046), (0.90, 0.040))):
            M.add(g, cyl((x, y, ze), (x, y + 0.05, ze), r, n=14), 'metal')
            M.add(g, cyl((x, y + 0.05, ze), (x, y + 0.075, ze), r * 1.18, n=14), 'glass')
        M.add(g, cyl((x, 0.975, ze), (x, 1.03, ze), 0.034, 0.02, n=12), 'rglow')
        # outer cheek plate
        M.add(g, prism(P([(x + s * 0.085, 0.02), (x + s * 0.11, 0.06), (x + s * 0.10, 0.50), (x + s * 0.075, 0.56)]), ze - 0.05, ze + 0.04), 'red_armor')
    SPEC['lash'] = dict(shootY=1.03 * 8, spread=0.34 * 8, top=top)
    return M


heat_lash = heat_grad(0.60, 1.03, mats=('metal', 'hull_mid', 'glass'), always=('coil', 'rglow'))
heat_lash_body = matfn = (lambda mp, X, Y, g: np.isin(mp, [MID['coil']]).astype(float) * 0.9)


# ================================================================== Hydra - T3 Cybran 8-cell missile battery (3x3)
def hydra():
    M = Model(); g = 'base'
    z = cy_hero_base(M, g, 1.0)
    g = 'body'
    hull = mirror_half([(0, 0.62), (0.20, 0.60), (0.34, 0.30), (0.38, -0.40), (0.28, -0.82), (0, -0.90)])
    M.add(g, prism(hull, z, z + 0.24, 0.90), 'hull_dark')
    M.add(g, prism(scale_poly(hull, 0.80, (0, 0)), z + 0.24, z + 0.32, 0.92), 'hull_mid')
    top = z + 0.32
    # spine: stepped red plates with lights
    for i, y in enumerate((0.20, -0.04, -0.28)):
        M.add(g, prism(P([(-0.10, y - 0.10), (0.10, y - 0.10), (0.07, y + 0.10), (-0.07, y + 0.10)]), top, top + 0.06 - i * 0.01, 0.9), 'red_armor')
        M.add(g, B(-0.025, 0.025, y - 0.16, y - 0.12, top, top + 0.02), 'rglow')
    # targeting head
    M.add(g, prism(P([(-0.16, 0.36), (0.16, 0.36), (0.12, 0.62), (-0.12, 0.62)]), top - 0.04, top + 0.10, 0.85), 'hull_light')
    M.add(g, cyl((0, 0.52, top + 0.10), (0, 0.52, top + 0.14), 0.07, 0.05, n=14), 'glass')
    M.add(g, cyl((0, 0.52, top + 0.14), (0, 0.52, top + 0.15), 0.03, n=10), 'rglow')
    # rear magazine drum + exhaust
    M.add(g, cyl((-0.30, -0.66, top - 0.06), (0.30, -0.66, top - 0.06), 0.16, n=20), 'metal')
    for x in (-0.20, 0.0, 0.20):
        M.add(g, cyl((x - 0.02, -0.66, top - 0.06), (x + 0.02, -0.66, top - 0.06), 0.175, n=20), 'red_armor')
    for s in (-1, 1):
        M.add(g, cyl((s * 0.30, -0.66, top - 0.06), (s * 0.34, -0.66, top - 0.06), 0.11, n=14), 'hull_dark')
        # pod pylons
        M.add(g, B(s * 0.30, s * 0.46, -0.30, 0.20, z + 0.04, top + 0.02), 'hull_light')
        M.add(g, B(s * 0.32, s * 0.44, -0.26, 0.16, top + 0.02, top + 0.04), 'cy_mid')
        cable(M, g, [(s * 0.12, -0.50, top + 0.05), (s * 0.24, -0.40, top + 0.12), (s * 0.40, -0.30, top + 0.12)], 0.028)
        bolts(M, g, [(s * 0.34, -0.22), (s * 0.42, 0.12)], top + 0.04, r=0.018)
    antenna(M, g, (0.18, -0.80, top), (0.26, -1.10, top + 0.40), tip='rglow')
    # ---- two 4-cell pods, sliding hatch covers drawn back, missile noses in the open cells (recoiling part)
    g = 'barrel_local'; XS = (-0.68, 0.68)
    for x in XS:
        s = 1 if x > 0 else -1
        M.add(g, B(x - 0.25, x + 0.25, -0.62, 0.56, -0.18, 0.02), 'hull_dark')                       # pod hull
        for xw in (x - 0.25, x + 0.25):
            M.add(g, B(xw - 0.03, xw + 0.03, -0.62, 0.56, 0.02, 0.10), 'hull_mid')                  # side walls
        M.add(g, B(x - 0.25, x + 0.25, 0.52, 0.58, -0.18, 0.10), 'hull_mid')                          # front frame
        M.add(g, B(x - 0.012, x + 0.012, -0.10, 0.56, 0.0, 0.08), 'hull_mid')                         # cell divider
        for mx in (x - 0.11, x + 0.11):
            M.add(g, B(mx - 0.09, mx + 0.09, -0.10, 0.52, -0.01, 0.0), 'vent')
            missile(M, g, mx, -0.10, 0.64, 0.05, 0.065, fins=False)
            M.add(g, cyl((mx, 0.52, 0.05), (mx, 0.58, 0.05), 0.09, n=14), 'hull_dark')             # tube collar
        # hatch cover slid back over the rear cells, red inlay + ready lights
        M.add(g, prism(cham_rect(0.26, 0.28, 0.06, cx=x, cy=-0.36), 0.10, 0.16, 0.94), 'hull_light')
        M.add(g, prism(cham_rect(0.16, 0.20, 0.04, cx=x + s * 0.02, cy=-0.38), 0.16, 0.18, 0.90), 'red_armor')
        for k in range(4):
            M.add(g, B(x - 0.16 + k * 0.105, x - 0.12 + k * 0.105, -0.06, -0.04, 0.10, 0.12), 'rglow')
        bolts(M, g, [(x - 0.21, -0.60), (x + 0.21, -0.60), (x - 0.21, -0.12), (x + 0.21, -0.12)], 0.16, r=0.018)
        M.add(g, B(x - 0.20, x + 0.20, -0.66, -0.62, -0.14, 0.06), 'vent')                             # back-blast vents
        for k in range(5):
            M.add(g, B(x - 0.18 + k * 0.09, x - 0.16 + k * 0.09, -0.68, -0.62, -0.12, 0.05), 'metal')
        # trunnion
        M.add(g, cyl((x - s * 0.25, -0.10, -0.06), (x - s * 0.34, -0.10, -0.06), 0.09, n=14), 'metal')
        # outer armour slope with red inlay
        so = [(x + s * 0.25, -0.50), (x + s * 0.33, -0.40), (x + s * 0.33, 0.36), (x + s * 0.25, 0.50)]
        M.add(g, prism(P(so), -0.16, 0.06, 0.85), 'hull_light')
        M.add(g, prism(P([(x + s * 0.27, -0.32), (x + s * 0.31, -0.26), (x + s * 0.31, 0.24), (x + s * 0.27, 0.32)]), 0.06, 0.075), 'red_armor')
    pv = (0, 0.10, top + 0.12); elevate(M, 10, pv)
    my, _ = muzzle_world(10, pv, 0.64)
    SPEC['hydra'] = dict(shootY=my * 8, spread=1.36 * 8, top=top)
    return M


heat_hydra = (lambda mp, X, Y, g: np.where(np.isin(mp, [MID['vent'], MID['metal']]) & (Y < -0.45), 0.85, 0.0)
              + np.where(np.isin(mp, [MID['hull_dark'], MID['vent']]) & (Y > 0.50), 0.7, 0.0))


# ================================================================== Wasp - T3 Cybran quad-rail AA launcher (3x3)
def wasp():
    M = Model(); g = 'base'
    z = cy_hero_base(M, g, 1.0)
    g = 'body'
    hull = mirror_half([(0, 0.40), (0.26, 0.38), (0.42, 0.10), (0.44, -0.40), (0.30, -0.72), (0, -0.78)])
    M.add(g, prism(hull, z, z + 0.22, 0.90), 'hull_dark')
    M.add(g, prism(scale_poly(hull, 0.80, (0, 0)), z + 0.22, z + 0.30, 0.92), 'cy_mid')
    top = z + 0.30
    for s in (1, -1):
        W = [(0.38, 0.20), (0.62, -0.06), (0.74, -0.62), (0.62, -0.84), (0.44, -0.58), (0.40, -0.20)]
        zw = (lambda x, y: top - 0.04 - (abs(x) - 0.38) * 0.40)
        slope_plate(M, g, [(s * x, y) for x, y in W], zw, 'hull_light', thick=0.12, inlay='red_armor', isc=0.62, ih=0.02)
        M.add(g, cbox(s * 0.66, -0.70, zw(0.66, 0) + 0.01, 0.05, 0.10, 0.03), 'rglow')
        bolts_on(M, g, [(s * 0.42, 0.06), (s * 0.48, -0.40)], zw, r=0.018)
    # phased-array sensor panel on a mast (tilted back), with emitter grid
    pc = (0, -0.46, top + 0.22)
    R = rx(-35)
    def SA(T, m): M.add(g, tf(T, R, pc), m)
    SA(B(-0.36, 0.36, -0.20, 0.20, -0.04, 0.0), 'hull_dark')
    SA(B(-0.33, 0.33, -0.17, 0.17, 0.0, 0.015), 'cy_dark')
    for i in range(6):
        for j in range(3):
            SA(B(-0.30 + i * 0.12, -0.24 + i * 0.12, -0.14 + j * 0.10, -0.08 + j * 0.10, 0.015, 0.028), 'rglow' if (i + j) % 2 == 0 else 'red_armor')
    SA(B(-0.38, 0.38, 0.18, 0.22, -0.05, 0.03), 'red_armor')
    for sx in (-0.38, 0.38):
        SA(B(sx - 0.03, sx + 0.03, -0.22, 0.22, -0.05, 0.03), 'hull_mid')
    M.add(g, cyl((0, -0.46, top - 0.01), (0, -0.46, top + 0.20), 0.06, n=12), 'metal')
    M.add(g, B(-0.08, 0.08, -0.40, -0.30, top - 0.01, top + 0.16), 'hull_mid')
    # secondary sensor dome + cables
    M.add(g, cyl((0.20, 0.14, top - 0.01), (0.20, 0.14, top + 0.08), 0.09, 0.08, n=16), 'hull_light')
    M.add(g, sphereish((0.20, 0.14, top + 0.08), 0.065, n=12), 'glass')
    M.add(g, cbox(0.20, 0.20, top + 0.13, 0.04, 0.02, 0.02), 'rglow')
    cable(M, g, [(-0.10, -0.30, top + 0.05), (-0.20, -0.05, top + 0.10), (-0.30, 0.10, top + 0.10)], 0.024)
    cable(M, g, [(0.10, -0.30, top + 0.05), (0.20, -0.05, top + 0.06)], 0.024)
    # ---- quad launch rails (two twin-rail beams) with exposed missiles (recoiling part)
    g = 'barrel_local'; XS = (-0.52, 0.52)
    M.add(g, cyl((-0.66, 0.0, -0.02), (0.66, 0.0, -0.02), 0.07, n=14), 'metal')                         # cross shaft
    M.add(g, B(-0.30, 0.30, -0.12, 0.12, -0.10, 0.06), 'hull_mid')
    M.add(g, B(-0.20, 0.20, -0.08, 0.08, 0.06, 0.08), 'red_armor')
    for x in XS:
        s = 1 if x > 0 else -1
        M.add(g, B(x - 0.18, x + 0.18, -0.40, 0.30, -0.08, 0.0), 'hull_dark')                          # launcher spine
        M.add(g, prism(P([(x - 0.16, 0.30), (x + 0.16, 0.30), (x + 0.10, 1.02), (x - 0.10, 1.02)]), -0.07, -0.01), 'hull_mid')
        M.add(g, B(x - 0.18, x + 0.18, -0.48, -0.40, -0.08, 0.04), 'metal')
        M.add(g, cyl((x, -0.48, -0.02), (x, -0.52, -0.02), 0.06, n=10), 'rglow')
        for rx_ in (x - 0.085, x + 0.085):
            M.add(g, B(rx_ - 0.018, rx_ + 0.018, -0.38, 1.04, 0.0, 0.03), 'metal_light')               # rail
            missile(M, g, rx_, -0.30, 1.06, 0.085, 0.052, body='metal_light', tip='red_armor')
            M.add(g, B(rx_ - 0.03, rx_ + 0.03, 0.10, 0.16, 0.0, 0.05), 'hull_dark')                    # shoe
            M.add(g, B(rx_ - 0.03, rx_ + 0.03, 0.62, 0.68, 0.0, 0.05), 'hull_dark')
        # outer armour cheek with red inlay and light
        so = [(x + s * 0.18, -0.44), (x + s * 0.24, -0.36), (x + s * 0.24, 0.24), (x + s * 0.18, 0.36)]
        M.add(g, prism(P(so), -0.10, 0.08, 0.85), 'hull_light')
        M.add(g, prism(P([(x + s * 0.195, -0.30), (x + s * 0.225, -0.24), (x + s * 0.225, 0.16), (x + s * 0.195, 0.22)]), 0.08, 0.095), 'red_armor')
        hydraulic(M, g, x - s * 0.24, -0.06, -0.36, 0.0, 0.18, r=0.04)
    pv = (0, 0.06, top + 0.16); elevate(M, 26, pv)
    my, _ = muzzle_world(26, pv, 1.06)
    SPEC['wasp'] = dict(shootY=my * 8, spread=1.04 * 8, top=top)
    return M


heat_wasp = (lambda mp, X, Y, g: np.where(np.isin(mp, [MID['hull_dark'], MID['metal'], MID['rglow']]) & (Y < -0.30), 0.8, 0.0))


# ================================================================== driver
D = 'blocks/turrets'
ASSETS = [
    # name, model, base px, body px, barrel heat, body heat (None -> no body -heat sprite)
    ('rivet', rivet, 64, 96, heat_rivet, None),
    ('sparrow', sparrow, 64, 96, heat_sparrow, None),
    ('lash', lash, 64, 96, heat_lash, heat_lash_body),
    ('hydra', hydra, 96, 128, heat_hydra, None),
    ('wasp', wasp, 96, 128, heat_wasp, None),
]


def body_heat(name, M, tc, fn):
    """Body -heat sprite (drawn by DrawTurret above everything), masked where the barrel part covers it."""
    _, hb = export.layer(M, ['body'], tc, fn, casters=['body', 'barrel'])
    bar, _ = export.layer(M, ['barrel'], tc)
    hb[dilate(bar[..., 3] > 0, 2)] = 0
    export.save(export.heat_sprite(hb), D, f'{name}-heat')


def main(names=None):
    for name, fn, bc, tc, heat, bheat in ASSETS:
        if names and name not in names:
            continue
        M = fn()
        export.turret(name, M, bc, tc, heat, parts=True)
        stale = os.path.join(export.SPR, D, f'{name}-heat.png')
        if bheat is not None:
            body_heat(name, M, tc, bheat)
        elif os.path.exists(stale):
            os.remove(stale)
        sp = SPEC[name]
        print(f'{name:8s} tris {M.ntri():6d} ' + ' '.join(f'{k}={len(sum((T for T, _ in M.parts.get(k, [])), []) if False else sum(len(T) for T, _ in M.parts.get(k, [])))}' for k in ('base', 'body', 'barrel'))
              + f'  shootY={sp["shootY"]:.2f} spread={sp["spread"]:.2f}')
    print('sheet:', export.qa_sheet([a[0] for a in ASSETS], 'g_turrets.png', sc=3))


if __name__ == '__main__':
    main(sys.argv[1:])
