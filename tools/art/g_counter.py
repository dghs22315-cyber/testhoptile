"""Counter-measure hero models: Spotter Beacon (T1 UEF), Interceptor (T1 UEF point defence),
Decoy (T2 UEF dummy turret), Recon Radar (T3 Cybran array).

    .venv/bin/python tools/art/g_counter.py

Layer rules (Mindustry v146):
  Radar               -> @-base static, @ rotates about the centre (rotateSpeed * totalProgress), @-glow is drawn
                         additively with the same rotation and tinted with glowColor, so it is a white mask.
  PointDefenseTurret  -> @-base static, @ rotates with the aim (head faces +Y in the sprite).
  Wall                -> @ only.
Rotating layers carry a baked dark outline so they separate from the base like turret heads do."""
import math
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import numpy as np  # noqa: E402
import rend  # noqa: E402
from geom import *  # noqa: E402,F401
from mats import Model  # noqa: E402
from models import bolts, light, chevrons  # noqa: E402
from hero import *  # noqa: E402,F401
import export  # noqa: E402
from export import save, layer, glowfn, FULL  # noqa: E402
from rend import outline, heat_sprite, over  # noqa: E402

rend.add_material('sand', ['2e2619', '453a26', '5e5034', '786846', '93825a', 'ad9b70'])
rend.add_material('canvas', ['262a2e', '363c42', '4b535b', '646e78', '808b96', '9faab4'])


def B(x0, x1, y0, y1, z0, z1):
    return box(min(x0, x1), max(x0, x1), min(y0, y1), max(y0, y1), z0, z1)


def octp(r, cx=0.0, cy=0.0, rot=22.5):
    return P([(cx + r * math.cos(math.radians(rot + 45 * i)), cy + r * math.sin(math.radians(rot + 45 * i))) for i in range(8)])


def hexp(r, rot=30, sx=1.0, sy=1.0, cx=0.0, cy=0.0):
    return P([(cx + sx * r * math.cos(math.radians(rot + 60 * i)), cy + sy * r * math.sin(math.radians(rot + 60 * i))) for i in range(6)])


def ellipsoid(c, rx_, ry_, rz_, n=16, lat=6, z_min=-math.pi / 2):
    """Lat-long ellipsoid; z_min > -pi/2 drops the hidden underside."""
    c = np.asarray(c, float)
    T = []
    for i in range(lat):
        t0 = z_min + (math.pi / 2 - z_min) * i / lat
        t1 = z_min + (math.pi / 2 - z_min) * (i + 1) / lat
        for j in range(n):
            p0, p1 = 2 * math.pi * j / n, 2 * math.pi * (j + 1) / n

            def Q(t, p):
                return c + np.array([rx_ * math.cos(t) * math.cos(p), ry_ * math.cos(t) * math.sin(p), rz_ * math.sin(t)])
            T.append([Q(t0, p0), Q(t0, p1), Q(t1, p1)])
            T.append([Q(t0, p0), Q(t1, p1), Q(t1, p0)])
    return clean(T)


def hazard(M, g, cx, cy, z, w, d, n, ang=0.0, slant=0.35):
    """Black plate with slanted yellow stripes (reads as hazard tape at game scale)."""
    R = rz(ang)
    M.add(g, tf(cbox(0, 0, z + 0.006, w, d, 0.012), R, (cx, cy, 0)), 'cable')
    step = w / n
    for i in range(n):
        x = -w / 2 + (i + 0.5) * step
        k = slant * d
        p = ccw([(x - step * 0.26 - k / 2, -d / 2 * 0.92), (x + step * 0.26 - k / 2, -d / 2 * 0.92),
                 (x + step * 0.26 + k / 2, d / 2 * 0.92), (x - step * 0.26 + k / 2, d / 2 * 0.92)])
        p = np.clip(p, [-w / 2, -d / 2], [w / 2, d / 2])
        M.add(g, tf(prism(ccw(p), z + 0.012, z + 0.022), R, (cx, cy, 0)), 'yellow')


# ================================================================== Spotter Beacon - T1 UEF (1x1, Radar)
def spotter_beacon():
    M = Model()
    g = 'base'
    M.add(g, prism(cham_rect(0.485, 0.485, 0.12), 0.0, 0.06, 0.975), 'hull_dark')
    M.add(g, prism(cham_rect(0.43, 0.43, 0.12), 0.06, 0.12, 0.93), 'hull_mid')
    for k in range(4):
        S = rz(90 * k)
        # yellow corner caps with a dark hazard slash
        cp = P([(0.40, 0.22), (0.40, 0.33), (0.33, 0.40), (0.22, 0.40), (0.22, 0.22)])
        M.add(g, tf(prism(cp, 0.10, 0.135, 0.96), S), 'yellow')
        M.add(g, tf(tf(cbox(0, 0, 0.137, 0.15, 0.03, 0.006), rz(-45), (0.31, 0.31, 0)), S), 'cable')
        # quad-pod strut from the corner up to the mast collar
        M.add(g, tf(cbox(0.27, 0.27, 0.13, 0.08, 0.08, 0.02), S), 'metal')
        M.add(g, tf(tube_path([(0.27, 0.27, 0.14), (0.15, 0.15, 0.26), (0.075, 0.075, 0.36)], 0.022, n=8), S), 'metal_light')
        M.add(g, tf(cyl((0.27, 0.27, 0.13), (0.27, 0.27, 0.155), 0.022, n=8), S), 'metal_light')
    # side vents (two sides) and a power pack with status lamp on the back edge
    for s in (-1, 1):
        M.add(g, B(s * 0.40, s * 0.45, -0.16, 0.16, 0.06, 0.125), 'vent')
        for y in (-0.10, -0.03, 0.04, 0.11):
            M.add(g, B(s * 0.395, s * 0.455, y - 0.012, y + 0.012, 0.06, 0.13), 'metal')
    M.add(g, B(-0.17, 0.17, -0.44, -0.30, 0.12, 0.20), 'hull_light')
    M.add(g, B(-0.14, 0.14, -0.43, -0.32, 0.20, 0.21), 'hull_mid')
    M.add(g, B(-0.13, -0.05, -0.41, -0.34, 0.21, 0.217), 'glow')
    M.add(g, B(0.02, 0.13, -0.40, -0.35, 0.21, 0.216), 'yellow')
    cable(M, g, [(0.10, -0.30, 0.17), (0.10, -0.20, 0.20), (0.05, -0.10, 0.24)], 0.018, ends='yellow')
    bolts(M, g, [(0.25, -0.05), (-0.25, 0.05)], 0.12, r=0.018)
    # mast foot
    M.add(g, cyl((0, 0, 0.12), (0, 0, 0.18), 0.13, 0.12, n=20), 'hull_light')
    M.add(g, cyl((0, 0, 0.18), (0, 0, 0.22), 0.10, n=18), 'metal')
    M.add(g, cyl((0, 0, 0.22), (0, 0, 0.36), 0.065, n=14), 'metal_light')
    M.add(g, cyl((0, 0, 0.34), (0, 0, 0.38), 0.09, n=14), 'hull_dark')

    g = 'head'                                      # rotating sensor head (centred)
    z = 0.38
    M.add(g, cyl((0, 0, z), (0, 0, z + 0.05), 0.095, n=18), 'hull_mid')
    M.add(g, cyl((0, 0, z + 0.035), (0, 0, z + 0.045), 0.105, n=18), 'yellow')
    # electronics housing behind the array
    hs = mirror_half([(0, 0.06), (0.11, 0.06), (0.14, 0.0), (0.14, -0.17), (0.10, -0.23), (0, -0.24)])
    M.add(g, prism(hs, z + 0.04, z + 0.14, 0.90), 'hull_light')
    M.add(g, prism(scale_poly(hs, 0.75, (0, -0.08)), z + 0.14, z + 0.155, 0.95), 'hull_mid')
    for y in (-0.16, -0.11):
        M.add(g, B(-0.07, 0.07, y - 0.014, y + 0.014, z + 0.15, z + 0.17), 'metal')
    M.add(g, B(-0.10, 0.10, -0.235, -0.215, z + 0.06, z + 0.13), 'yellow')
    # phased-array paddle facing +Y, tilted back
    R = rx(-38)
    o = np.array([0, 0.17, z + 0.17])
    M.add(g, tf(B(-0.42, 0.42, -0.085, 0.085, -0.035, 0.0), R, o), 'hull_dark')
    M.add(g, tf(B(-0.40, 0.40, -0.068, 0.068, 0.0, 0.012), R, o), 'hull_mid')
    for i in range(8):
        x = -0.35 + i * 0.10
        M.add(g, tf(B(x - 0.035, x + 0.035, -0.05, 0.05, 0.012, 0.024), R, o), 'metal')
        M.add(g, tf(B(x - 0.02, x + 0.02, -0.018, 0.018, 0.024, 0.03), R, o), 'glow')
    for s in (-1, 1):
        M.add(g, tf(B(s * 0.40, s * 0.45, -0.09, 0.09, -0.04, 0.03), R, o), 'yellow')
        M.add(g, tube_path([(s * 0.10, -0.02, z + 0.10), (s * 0.20, 0.10, z + 0.14), (s * 0.24, 0.14, z + 0.15)], 0.016, n=6), 'metal_light')
    # beacon lamp on top of the hub + whip antenna
    M.add(g, cyl((0, -0.06, z + 0.155), (0, -0.06, z + 0.19), 0.055, n=12), 'hull_dark')
    M.add(g, sphereish((0, -0.06, z + 0.21), 0.042, n=10), 'glow')
    for a in (45, 135, 225, 315):
        ca, sa = math.cos(math.radians(a)), math.sin(math.radians(a))
        M.add(g, cyl((0.05 * ca, -0.06 + 0.05 * sa, z + 0.18), (0.045 * ca, -0.06 + 0.045 * sa, z + 0.25), 0.008, n=4), 'metal_light')
    antenna(M, g, (0.08, -0.18, z + 0.15), (0.13, -0.33, z + 0.42), r=0.014)
    return M


# ================================================================== Interceptor - T1 UEF twin-laser point defence (2x2)
def interceptor():
    M = Model()
    g = 'base'
    M.add(g, prism(cham_rect(0.985, 0.985, 0.24), 0.0, 0.09, 0.985), 'hull_dark')
    M.add(g, prism(cham_rect(0.90, 0.90, 0.28), 0.09, 0.18, 0.95), 'hull_mid')
    M.add(g, prism(cham_rect(0.74, 0.74, 0.24), 0.18, 0.192, 0.97), 'hull_dark')
    for k in range(4):
        S = rz(90 * k)
        R = rz(45 + 90 * k)
        # corner capacitor pods (charge rings glow)
        M.add(g, tf(prism(octp(0.155, cx=0.97), 0.09, 0.28, 0.93), R), 'hull_light')
        M.add(g, tf(cyl((0.97, 0, 0.17), (0.97, 0, 0.20), 0.15, n=16), R), 'yellow')
        M.add(g, tf(cyl((0.97, 0, 0.28), (0.97, 0, 0.30), 0.12, n=16), R), 'hull_dark')
        M.add(g, tf(cyl((0.97, 0, 0.30), (0.97, 0, 0.305), 0.085, n=16), R), 'glow')
        M.add(g, tf(cyl((0.97, 0, 0.30), (0.97, 0, 0.325), 0.05, n=12), R), 'metal_light')
        for a in range(0, 360, 90):
            ca, sa = math.cos(math.radians(a + 45)), math.sin(math.radians(a + 45))
            M.add(g, tf(cyl((0.97 + 0.10 * ca, 0.10 * sa, 0.28), (0.97 + 0.10 * ca, 0.10 * sa, 0.30), 0.016, n=6), R), 'metal_light')
        cable(M, g, [(0.84, 0, 0.24), (0.72, 0, 0.27), (0.62, 0, 0.24)], 0.026, ends='yellow', R=R)
        # radiator grille on every side + feet
        grille(M, g, 0, -0.79, 0.18, 0.56, 0.085, n=7, glow='glow', R=S)
        for x in (-0.42, 0.42):
            M.add(g, tf(cbox(x, -0.935, 0.10, 0.10, 0.06, 0.04), S), 'metal')
            M.add(g, tf(cyl((x, -0.935, 0.12), (x, -0.935, 0.145), 0.022, n=8), S), 'metal_light')
        bolts_R(M, g, [(-0.56, -0.62), (0.56, -0.62)], 0.192, S, r=0.02)
        seam(M, g, (-0.32, -0.66), (0.32, -0.66), 0.192, w=0.022, h=0.01)
    z = turntable(M, g, 0.60, 0.192, teeth=34, nb=12)

    g = 'head'
    z += 0.005
    M.add(g, cyl((0, 0, z - 0.01), (0, 0, z + 0.05), 0.50, n=36), 'metal')
    hull = mirror_half([(0, 0.34), (0.26, 0.32), (0.44, 0.16), (0.47, -0.20), (0.40, -0.50), (0.22, -0.62), (0, -0.64)])
    M.add(g, prism(hull, z + 0.04, z + 0.22, 0.92), 'hull_mid')
    M.add(g, prism(scale_poly(hull, 0.86, (0, -0.1)), z + 0.22, z + 0.26, 0.95), 'hull_light')
    top = z + 0.26
    for s in (-1, 1):
        pl = [(s * 0.27, 0.22), (s * 0.40, 0.12), (s * 0.43, -0.24), (s * 0.36, -0.44), (s * 0.27, -0.40)]
        zf = (lambda x, y: top + 0.07 - (abs(x) - 0.27) * 0.45)
        slope_plate(M, g, pl, zf, 'hull_light', thick=0.10, inlay='yellow', isc=0.58, ih=0.018)
        bolts_on(M, g, [(s * 0.30, 0.14), (s * 0.40, -0.10), (s * 0.33, -0.38)], zf, r=0.017)
        # side vents
        M.add(g, B(s * 0.44, s * 0.49, -0.40, 0.04, z + 0.06, z + 0.20), 'vent')
        for y in np.arange(-0.36, 0.02, 0.07):
            M.add(g, B(s * 0.43, s * 0.50, y - 0.015, y + 0.015, z + 0.05, z + 0.21), 'metal')
        # twin laser emitters: housing, finned cooling sleeve, focusing head, lens
        x = s * 0.155
        bz = top + 0.035
        M.add(g, B(s * 0.07, s * 0.25, 0.02, 0.40, top - 0.05, top + 0.09), 'hull_dark')
        M.add(g, B(s * 0.09, s * 0.23, 0.05, 0.36, top + 0.09, top + 0.10), 'hull_mid')
        M.add(g, B(s * 0.10, s * 0.22, 0.30, 0.34, top + 0.10, top + 0.105), 'yellow')
        M.add(g, cyl((x, 0.38, bz), (x, 0.84, bz), 0.048, n=14), 'metal')
        for y in np.arange(0.42, 0.66, 0.045):
            M.add(g, cyl((x, y, bz), (x, y + 0.022, bz), 0.072, n=14), 'hull_dark')
        M.add(g, cyl((x, 0.68, bz), (x, 0.72, bz), 0.066, n=14), 'yellow')
        M.add(g, cyl((x, 0.80, bz), (x, 0.88, bz), 0.062, 0.070, n=14), 'hull_mid')
        M.add(g, cyl((x, 0.88, bz), (x, 0.892, bz), 0.052, n=14), 'metal_light')
        M.add(g, cyl((x, 0.88, bz), (x, 0.90, bz), 0.036, n=12), 'glow')
        cable(M, g, [(s * 0.30, -0.10, top + 0.03), (s * 0.30, 0.10, top + 0.10), (s * 0.20, 0.30, top + 0.10)], 0.022)
        light(M, g, s * 0.36, 0.24, top - 0.02, 0.04, 0.035)
    # rangefinder between the emitters
    M.add(g, B(-0.055, 0.055, 0.12, 0.52, top, top + 0.075), 'hull_light')
    M.add(g, B(-0.04, 0.04, 0.16, 0.48, top + 0.075, top + 0.085), 'hull_mid')
    M.add(g, cyl((0, 0.52, top + 0.04), (0, 0.55, top + 0.04), 0.032, n=12), 'glass')
    M.add(g, B(-0.02, 0.02, 0.36, 0.44, top + 0.085, top + 0.09), 'glow')
    # sensor radome (CIWS-style)
    rc = (0, -0.20)
    M.add(g, cyl((rc[0], rc[1], top - 0.01), (rc[0], rc[1], top + 0.14), 0.235, 0.225, n=28), 'hull_light')
    M.add(g, cyl((rc[0], rc[1], top + 0.12), (rc[0], rc[1], top + 0.145), 0.232, n=28), 'hull_dark')
    M.add(g, ellipsoid((rc[0], rc[1], top + 0.14), 0.222, 0.222, 0.16, n=24, lat=6, z_min=0.0), 'metal_light')
    M.add(g, tf(B(-0.10, 0.10, 0.0, 0.02, -0.03, 0.03), rx(-25), (rc[0], rc[1] + 0.215, top + 0.17)), 'glass')
    M.add(g, tf(B(-0.06, 0.06, 0.02, 0.026, -0.012, 0.012), rx(-25), (rc[0], rc[1] + 0.215, top + 0.17)), 'glow')
    M.add(g, cyl((rc[0], rc[1], top + 0.29), (rc[0], rc[1], top + 0.31), 0.03, n=10), 'hull_dark')
    # rear power coupling + antennas + hazard plate
    grille(M, g, 0, -0.53, top - 0.02, 0.30, 0.07, n=5, glow='glow')
    for s in (-1, 1):
        antenna(M, g, (s * 0.30, -0.46, top), (s * 0.36, -0.66, top + 0.34), r=0.016)
    bolts(M, g, [(-0.14, 0.26), (0.14, 0.26), (-0.18, -0.48), (0.18, -0.48)], top, r=0.016)
    return M


# ================================================================== Decoy - T2 armoured dummy turret (2x2, Wall)
def decoy():
    M = Model()
    g = 'main'
    # armoured ballast sled (explains the 4000 hp / armour 8)
    M.add(g, prism(cham_rect(0.975, 0.975, 0.16), 0.0, 0.08, 0.985), 'hull_dark')
    M.add(g, prism(cham_rect(0.88, 0.88, 0.18), 0.08, 0.19, 0.95), 'steel')
    M.add(g, prism(cham_rect(0.70, 0.70, 0.16), 0.19, 0.20, 0.97), 'hull_mid')
    for s in (-1, 1):
        # skid runners with upturned ends and tow eyes
        M.add(g, B(s * 0.86, s * 0.97, -0.84, 0.84, 0.0, 0.13), 'metal')
        M.add(g, B(s * 0.875, s * 0.955, -0.82, 0.82, 0.13, 0.15), 'metal_light')
        for y in (-0.88, 0.88):
            M.add(g, cyl((s * 0.915, y, 0.08), (s * 0.915, y * 1.06, 0.10), 0.055, n=10), 'metal')
        # hazard tape on the front and back skirt
        hazard(M, g, 0, s * 0.80, 0.19, 1.30, 0.12, 11, slant=0.9)
        bolts(M, g, [(x, s * 0.70) for x in (-0.62, -0.31, 0.0, 0.31, 0.62)], 0.20, r=0.02)
    # heavy corner armour blocks
    for k in range(4):
        S = rz(90 * k)
        M.add(g, tf(prism(P([(0.62, 0.45), (0.74, 0.45), (0.74, 0.62), (0.62, 0.74), (0.45, 0.74), (0.45, 0.62)]), 0.19, 0.27, 0.90), S), 'hull_light')
        bolts_R(M, g, [(0.60, 0.60)], 0.27, S, r=0.024)
    # sandbags on two corners (field-made ballast)
    for (cx, cy, a) in ((-0.70, 0.62, 10), (0.66, -0.66, -20)):
        for (dx, dy, dz) in ((0.0, 0.0, 0.0), (0.13, -0.05, 0.0), (0.06, -0.02, 0.07)):
            M.add(g, tf(ellipsoid((0, 0, 0), 0.10, 0.065, 0.045, n=10, lat=4, z_min=-0.3), rz(a), (cx + dx, cy + dy, 0.24 + dz)), 'sand')
    # sheet-metal dummy turret, deliberately a bit crooked
    Rk = rz(4)
    body = octp(0.56)
    M.add(g, tf(prism(body, 0.20, 0.40, 0.84), Rk), 'hull_light')
    M.add(g, tf(prism(scale_poly(body, 0.80, (0, 0)), 0.40, 0.42, 0.96), Rk), 'hull_mid')
    for i in range(8):                         # panel seams (rivet lines) on the faceted skirt
        a = math.radians(22.5 + 45 * i)
        p0 = (0.56 * math.cos(a), 0.56 * math.sin(a), 0.20)
        p1 = (0.46 * math.cos(a), 0.46 * math.sin(a), 0.40)
        M.add(g, tf(cyl(p0, p1, 0.012, n=4), Rk), 'hull_dark')
        for t in (0.25, 0.6):
            q = [p0[j] + (p1[j] - p0[j]) * t for j in range(3)]
            M.add(g, tf(sphereish(q, 0.016, n=6), Rk), 'metal_light')
    # mismatched patches
    M.add(g, tf(tf(B(-0.10, 0.10, -0.06, 0.06, 0.0, 0.012), rx(-27) @ rz(8), (0.0, -0.50, 0.31)), Rk), 'steel')
    M.add(g, tf(tf(B(-0.07, 0.07, -0.05, 0.05, 0.0, 0.012), ry(27) @ rz(-12), (0.49, 0.10, 0.31)), Rk), 'hull_mid')
    # inflatable dome with gores and seams
    dc = np.array([0, -0.04, 0.41])
    M.add(g, tf(ellipsoid(dc, 0.40, 0.40, 0.24, n=24, lat=7, z_min=0.0), Rk), 'canvas')
    for i in range(8):
        a = math.radians(45 * i + 10)
        pts = [dc + np.array([0.405 * math.cos(t) * math.cos(a), 0.405 * math.cos(t) * math.sin(a), 0.245 * math.sin(t)]) for t in np.radians([2, 28, 52, 74])]
        M.add(g, tf(tube_path(pts, 0.012, n=5), Rk), 'cable')
    M.add(g, tf(cyl(dc + (0, 0, 0.23), dc + (0, 0, 0.26), 0.07, n=12), Rk), 'hull_mid')
    # fake "gun": a capped pipe on a sawhorse
    bz = 0.52
    M.add(g, tf(cyl((0, 0.18, bz - 0.02), (0, 0.84, bz), 0.062, n=14), Rk), 'metal')
    for y in (0.40, 0.62):
        M.add(g, tf(cyl((0, y, bz - 0.01), (0, y + 0.04, bz - 0.01), 0.068, n=14), Rk), 'cable')
    M.add(g, tf(cyl((0, 0.80, bz), (0, 0.95, bz), 0.095, n=14), Rk), 'hull_mid')
    M.add(g, tf(cyl((0, 0.95, bz), (0, 0.96, bz), 0.07, n=12), Rk), 'bore')
    M.add(g, tf(cyl((0, 0.86, bz), (0, 0.90, bz), 0.10, n=14), Rk), 'yellow')
    for s in (-1, 1):
        M.add(g, tf(tube_path([(s * 0.16, 0.70, 0.27), (s * 0.02, 0.70, bz - 0.05)], 0.018, n=6), Rk), 'metal_light')
        # ratchet straps from the dome to the corner blocks
        p_dome = dc + np.array([s * 0.30, -0.16, 0.12])
        M.add(g, tf(tube_path([p_dome, dc + np.array([s * 0.40, -0.40, 0.02]), (s * 0.58, -0.60, 0.28)], 0.018, n=6), Rk), 'cable')
        M.add(g, tf(cbox(s * 0.45, -0.46, 0.33, 0.06, 0.05, 0.03), Rk), 'yellow')
    # blower that keeps the dome up, with hose
    M.add(g, B(-0.82, -0.56, -0.20, 0.10, 0.19, 0.30), 'hull_light')
    M.add(g, cyl((-0.69, -0.05, 0.30), (-0.69, -0.05, 0.31), 0.11, n=16), 'vent')
    for i in range(5):
        M.add(g, tf(cbox(0.05, 0, 0.315, 0.10, 0.02, 0.01), rz(72 * i + 15), (-0.69, -0.05, 0)), 'metal')
    M.add(g, cyl((-0.69, -0.05, 0.31), (-0.69, -0.05, 0.325), 0.03, n=8), 'metal_light')
    cable(M, g, [(-0.60, 0.08, 0.28), (-0.48, 0.14, 0.38), (-0.36, 0.06, 0.48)], 0.028, m='canvas', ends='metal')
    # strobe beacon on a pole (rear left corner)
    sx, sy = -0.62, -0.62
    M.add(g, cyl((sx, sy, 0.27), (sx, sy, 0.50), 0.025, n=8), 'metal')
    M.add(g, cyl((sx, sy, 0.50), (sx, sy, 0.54), 0.075, n=14), 'hull_dark')
    M.add(g, cyl((sx, sy, 0.54), (sx, sy, 0.60), 0.058, n=14), 'rglow')
    M.add(g, sphereish((sx, sy, 0.60), 0.058, n=12), 'rglow')
    for a in (0, 90, 180, 270):
        ca, sa = math.cos(math.radians(a)), math.sin(math.radians(a))
        M.add(g, cyl((sx + 0.07 * ca, sy + 0.07 * sa, 0.53), (sx + 0.05 * ca, sy + 0.05 * sa, 0.67), 0.010, n=4), 'metal_light')
    # radar corner reflector (trihedral) on a stub (front right corner)
    cx, cy, cz = 0.60, 0.60, 0.40
    a = 0.20
    ax = np.array([1.0, 1.0, 1.0]) / math.sqrt(3)
    u, v, w = basis(ax)
    Rr = np.column_stack([u, v, w]).T                  # maps the (1,1,1) axis to +Z
    O = np.zeros(3)
    E = [Rr @ (a * np.eye(3)[i]) for i in range(3)]
    for i in range(3):
        j = (i + 1) % 3
        tri = np.array([[O, E[i], E[j]]]) + np.array([cx, cy, cz])
        M.add(g, tf(tri - (cx, cy, cz), rz(30), (cx, cy, cz)), 'metal_light')
        M.add(g, tf(cyl(O, E[i], 0.012, n=4), rz(30), (cx, cy, cz)), 'hull_dark')
    M.add(g, cyl((cx, cy, 0.27), (cx, cy, cz), 0.025, n=8), 'metal')
    return M


# ================================================================== Recon Radar - T3 Cybran array (3x3, Radar)
def recon_radar():
    M = Model()
    g = 'base'
    M.add(g, prism(cham_rect(1.475, 1.475, 0.40), 0.0, 0.12, 0.985), 'cy_dark')
    M.add(g, prism(cham_rect(1.30, 1.30, 0.50), 0.12, 0.28, 0.93), 'cy_mid')
    M.add(g, prism(cham_rect(1.12, 1.12, 0.44), 0.28, 0.30, 0.97), 'cy_dark')
    for k in range(4):
        S = rz(90 * k)
        R = rz(45 + 90 * k)
        # sloped red glacis on every side with a lit slit
        pl = [(-0.66, -1.42), (0.66, -1.42), (0.48, -1.12), (-0.48, -1.12)]
        zf = (lambda x, y: 0.31 + (y + 1.12) * 0.42)
        slope_plate(M, g, pl, zf, 'red_armor', thick=0.10, inlay='cy_dark', isc=0.70, ih=0.012, R=S)
        M.add(g, tf(B(-0.36, 0.36, -1.30, -1.26, 0.0, 0.26), S), 'rglow')
        M.add(g, tf(B(-0.40, 0.40, -1.32, -1.31, 0.0, 0.27), S), 'cy_dark')
        # angular corner sensor pylons
        M.add(g, tf(prism(hexp(0.20, rot=0, cx=1.16), 0.12, 0.40, 0.80), R), 'cy_mid')
        M.add(g, tf(prism(hexp(0.15, rot=0, cx=1.16), 0.40, 0.46, 0.85), R), 'red_armor')
        M.add(g, tf(cyl((1.16, 0, 0.46), (1.16, 0, 0.50), 0.06, n=10), R), 'rglow')
        M.add(g, tf(prism(P([(0.86, -0.06), (1.00, -0.10), (1.00, 0.10), (0.86, 0.06)]), 0.28, 0.36, 0.9), R), 'cy_dark')
        bolts_R(M, g, [(1.30, -0.10), (1.30, 0.10)], 0.40, R, r=0.02)
        # cooling fins and conduits between glacis and pylons
        for sgn in (-1, 1):
            for i in range(4):
                x = sgn * (0.72 + i * 0.07)
                M.add(g, tf(B(x - 0.018, x + 0.018, -1.10, -0.96, 0.28, 0.38), S), 'metal')
            M.add(g, tf(B(sgn * 0.70, sgn * 0.96, -1.11, -0.95, 0.28, 0.30), S), 'vent')
        cable(M, g, [(0.98, 0, 0.36), (0.94, 0, 0.42), (0.86, 0, 0.40)], 0.03, R=R)
        seam(M, g, (-0.30, -0.98), (0.30, -0.98), 0.30, m='cy_dark', w=0.025, h=0.01)
        bolts_R(M, g, [(-0.58, -1.02), (0.58, -1.02)], 0.30, S, r=0.022)
    # bearing ring with teeth and a lit trim
    M.add(g, cyl((0, 0, 0.30), (0, 0, 0.40), 0.88, n=48), 'metal')
    M.add(g, cyl((0, 0, 0.36), (0, 0, 0.372), 0.895, n=48), 'rglow')
    M.add(g, cyl((0, 0, 0.40), (0, 0, 0.43), 0.86, 0.82, n=48), 'cy_mid')
    M.add(g, cyl((0, 0, 0.43), (0, 0, 0.435), 0.72, n=40), 'vent')
    for i in range(36):
        M.add(g, tf(cbox(0.91, 0, 0.35, 0.05, 0.06, 0.08), rz(10 * i)), 'metal')
    for i in range(12):
        a = math.radians(30 * i + 15)
        M.add(g, cyl((0.78 * math.cos(a), 0.78 * math.sin(a), 0.43), (0.78 * math.cos(a), 0.78 * math.sin(a), 0.45), 0.024, n=8), 'metal_light')

    g = 'head'                                       # rotating array, centred on the pivot
    z = 0.435
    M.add(g, prism(hexp(0.42, rot=0), z, z + 0.16, 0.92), 'cy_mid')
    M.add(g, prism(hexp(0.34, rot=0), z + 0.16, z + 0.20, 0.92), 'red_armor')
    M.add(g, cyl((0, 0, z + 0.20), (0, 0, z + 0.24), 0.14, 0.12, n=16), 'cy_dark')
    M.add(g, sphereish((0, 0, z + 0.25), 0.07, n=12), 'rglow')
    bolts(M, g, [(0.27 * math.cos(math.radians(a)), 0.27 * math.sin(math.radians(a))) for a in range(30, 360, 60)], z + 0.20, r=0.02)
    # main phased array: elongated hex panel, tilted back, facing +Y
    R = rx(-36)
    o = np.array([0, 0.40, z + 0.42])
    pan = P([(-1.30, 0.0), (-1.16, -0.22), (1.16, -0.22), (1.30, 0.0), (1.16, 0.22), (-1.16, 0.22)])
    M.add(g, tf(prism(pan, -0.07, 0.0, 0.98), R, o), 'cy_dark')
    M.add(g, tf(prism(scale_poly(pan, (0.97, 0.84), (0, 0)), 0.0, 0.02, 0.98), R, o), 'cy_mid')
    for i in range(14):
        x = -1.04 + i * 0.16
        for j, y in enumerate((-0.095, 0.095)):
            M.add(g, tf(B(x - 0.065, x + 0.065, y - 0.075, y + 0.075, 0.02, 0.036), R, o), 'hull_dark')
            M.add(g, tf(B(x - 0.022, x + 0.022, y - 0.05, y + 0.05, 0.036, 0.044), R, o), 'rglow' if (i + j) % 2 == 0 else 'metal')
    for s in (-1, 1):
        M.add(g, tf(prism(P([(s * 1.14, -0.23), (s * 1.32, 0.0), (s * 1.14, 0.23), (s * 1.08, 0.0)]), -0.08, 0.06, 0.9), R, o), 'red_armor')
        M.add(g, tf(cyl((s * 1.20, 0, 0.06), (s * 1.20, 0, 0.09), 0.035, n=8), R, o), 'rglow')
    M.add(g, tf(B(-0.12, 0.12, -0.23, 0.23, 0.02, 0.06), R, o), 'red_armor')
    # boom + truss behind the panel
    M.add(g, B(-1.05, 1.05, 0.10, 0.20, z + 0.30, z + 0.37), 'cy_dark')
    M.add(g, B(-1.00, 1.00, 0.12, 0.18, z + 0.37, z + 0.38), 'metal')
    for s in (-1, 1):
        for (x0, x1) in ((0.20, 0.55), (0.55, 0.92)):
            M.add(g, tube_path([(s * x0, 0.15, z + 0.16), (s * x1, 0.15, z + 0.33)], 0.02, n=6), 'metal_light')
        M.add(g, tube_path([(s * 0.30, 0.0, z + 0.16), (s * 0.40, 0.15, z + 0.33)], 0.03, n=8), 'metal')
        cable(M, g, [(s * 0.28, -0.12, z + 0.16), (s * 0.52, 0.02, z + 0.30), (s * 0.70, 0.18, z + 0.36)], 0.025)
    # rear electronics / counterweight module
    cw = P([(-0.40, -0.36), (0.40, -0.36), (0.52, -0.62), (0.30, -0.92), (-0.30, -0.92), (-0.52, -0.62)])
    M.add(g, prism(cw, z + 0.02, z + 0.20, 0.92), 'cy_dark')
    zf = (lambda x, y: z + 0.24 + (y + 0.36) * 0.12)
    slope_plate(M, g, [(-0.34, -0.40), (0.34, -0.40), (0.42, -0.62), (0.24, -0.84), (-0.24, -0.84), (-0.42, -0.62)], zf,
                'red_armor', thick=0.06, inlay='cy_dark', isc=0.62, ih=0.012)
    grille(M, g, 0, -0.62, zf(0, -0.62) + 0.01, 0.34, 0.12, n=6, glow='rglow', slat='metal', frame='cy_mid')
    # secondary IFF bar at the back
    M.add(g, B(-0.08, 0.08, -0.98, -0.88, z + 0.10, z + 0.26), 'metal')
    M.add(g, tf(B(-0.62, 0.62, -0.05, 0.05, -0.03, 0.03), rx(30), (0, -1.02, z + 0.28)), 'cy_dark')
    for i in range(7):
        x = -0.48 + i * 0.16
        M.add(g, tf(B(x - 0.04, x + 0.04, -0.03, 0.03, 0.03, 0.045), rx(30), (0, -1.02, z + 0.28)), 'rglow' if i % 2 == 0 else 'metal')
    for s in (-1, 1):
        M.add(g, tf(B(s * 0.62, s * 0.70, -0.06, 0.06, -0.04, 0.05), rx(30), (0, -1.02, z + 0.28)), 'red_armor')
        antenna(M, g, (s * 0.36, -0.44, z + 0.20), (s * 0.46, -0.70, z + 0.55), r=0.016, tip='rglow')
    return M


# ================================================================== render driver
def export_radar(name, M, canvas, d='blocks/defense', ol=2):
    base, _ = layer(M, ['base'], canvas)
    head, hg = layer(M, ['head'], canvas, heat=glowfn)
    head = outline(head, r=ol)
    save(base, d, f'{name}-base')
    save(head, d, name)
    save(heat_sprite(hg), d, f'{name}-glow')
    f = over(base, head)
    save(f, d, f'{name}-full')
    FULL[name] = np.asarray(f)


def export_pd(name, M, canvas, d='blocks/turrets'):
    base, _ = layer(M, ['base'], canvas)
    head, _ = layer(M, ['head'], canvas)
    head = outline(head, r=2)
    save(base, d, f'{name}-base')
    save(head, d, name)
    f = over(base, head)
    save(f, d, f'{name}-full')
    FULL[name] = np.asarray(f)


def export_wall(name, M, canvas, d='blocks/walls'):
    a, _ = layer(M, ['main'], canvas)
    save(a, d, name)
    save(a, d, f'{name}-full')
    FULL[name] = np.asarray(a)


def main():
    t0 = time.time()
    jobs = (('spotter-beacon', spotter_beacon, lambda n, M: export_radar(n, M, 32, ol=1)),
            ('interceptor', interceptor, lambda n, M: export_pd(n, M, 64)),
            ('decoy', decoy, lambda n, M: export_wall(n, M, 64)),
            ('recon-radar', recon_radar, lambda n, M: export_radar(n, M, 96)))
    for name, fn, ex in jobs:
        M = fn()
        ex(name, M)
        print(f'{name:16s} tris {M.ntri():6d}  {time.time() - t0:5.1f}s', flush=True)
    out = export.qa_sheet([j[0] for j in jobs], 'g_counter-sheet.png', sc=3)
    print('sheet', out)


if __name__ == '__main__':
    main()
