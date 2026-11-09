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
    M.add(g, cyl((0, 0, z), (0, 0, z + 0.05), 0.11, n=18), 'hull_mid')
    M.add(g, cyl((0, 0, z + 0.035), (0, 0, z + 0.047), 0.12, n=18), 'yellow')
    # electronics housing behind the array, with side vents and a hazard stripe
    hs = mirror_half([(0, 0.02), (0.13, 0.02), (0.17, -0.04), (0.17, -0.17), (0.12, -0.24), (0, -0.25)])
    M.add(g, prism(hs, z + 0.04, z + 0.15, 0.90), 'hull_light')
    M.add(g, prism(scale_poly(hs, 0.72, (0, -0.10)), z + 0.15, z + 0.165, 0.95), 'hull_dark')
    for s in (-1, 1):
        M.add(g, B(s * 0.15, s * 0.185, -0.17, -0.04, z + 0.05, z + 0.13), 'vent')
        for y in (-0.15, -0.10, -0.06):
            M.add(g, B(s * 0.145, s * 0.19, y - 0.01, y + 0.01, z + 0.05, z + 0.135), 'metal')
    M.add(g, B(-0.11, 0.11, -0.25, -0.225, z + 0.06, z + 0.14), 'yellow')
    for x in (-0.06, 0.0, 0.06):
        M.add(g, B(x - 0.012, x + 0.012, -0.255, -0.24, z + 0.06, z + 0.142), 'cable')
    # phased-array paddle facing +Y, tilted back; framed cells with glowing emitters
    R = rx(-42)
    o = np.array([0, 0.14, z + 0.19])
    M.add(g, tf(B(-0.35, 0.35, -0.095, 0.095, -0.045, 0.0), R, o), 'hull_dark')
    M.add(g, tf(B(-0.33, 0.33, -0.078, 0.078, 0.0, 0.010), R, o), 'hull_mid')
    for i in range(6):
        x = -0.25 + i * 0.10
        M.add(g, tf(B(x - 0.038, x + 0.038, -0.062, 0.062, 0.010, 0.024), R, o), 'metal_light')
        M.add(g, tf(B(x - 0.020, x + 0.020, -0.030, 0.030, 0.024, 0.032), R, o), 'glow')
    for s in (-1, 1):
        M.add(g, tf(B(s * 0.33, s * 0.39, -0.10, 0.10, -0.05, 0.035), R, o), 'yellow')
        M.add(g, tf(B(s * 0.345, s * 0.375, -0.10, 0.10, 0.035, 0.04), R, o), 'cable')
        # yoke arms from the hub to the paddle back
        M.add(g, tube_path([(s * 0.10, -0.02, z + 0.08), (s * 0.20, 0.06, z + 0.14), (s * 0.24, 0.10, z + 0.17)], 0.018, n=6), 'metal_light')
    M.add(g, tf(B(-0.06, 0.06, -0.10, 0.10, -0.06, 0.02), R, o), 'hull_light')
    # beacon lamp (the blinking light) in a cage on top of the housing, plus whip antenna
    lc = (0, -0.09)
    M.add(g, cyl((lc[0], lc[1], z + 0.16), (lc[0], lc[1], z + 0.20), 0.07, 0.065, n=14), 'hull_dark')
    M.add(g, cyl((lc[0], lc[1], z + 0.20), (lc[0], lc[1], z + 0.24), 0.052, n=14), 'glow')
    M.add(g, sphereish((lc[0], lc[1], z + 0.24), 0.052, n=12), 'glow')
    for a in (45, 135, 225, 315):
        ca, sa = math.cos(math.radians(a)), math.sin(math.radians(a))
        M.add(g, cyl((lc[0] + 0.066 * ca, lc[1] + 0.066 * sa, z + 0.19), (lc[0] + 0.05 * ca, lc[1] + 0.05 * sa, z + 0.31), 0.009, n=4), 'metal_light')
    antenna(M, g, (0.11, -0.20, z + 0.15), (0.15, -0.36, z + 0.44), r=0.014)
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
        # side radiator boxes, part of the hull sides
        M.add(g, B(s * 0.36, s * 0.475, -0.42, 0.06, z + 0.04, z + 0.19), 'hull_dark')
        M.add(g, B(s * 0.38, s * 0.46, -0.40, 0.04, z + 0.19, z + 0.195), 'vent')
        for y in np.arange(-0.37, 0.03, 0.065):
            M.add(g, B(s * 0.375, s * 0.465, y - 0.016, y + 0.016, z + 0.19, z + 0.21), 'metal')
        # twin laser emitters: housing, finned cooling sleeve, glowing focus coil, focusing head, lens
        x = s * 0.155
        bz = top + 0.035
        M.add(g, B(s * 0.06, s * 0.26, 0.00, 0.40, top - 0.05, top + 0.09), 'hull_dark')
        M.add(g, B(s * 0.08, s * 0.24, 0.03, 0.37, top + 0.09, top + 0.10), 'hull_mid')
        M.add(g, B(s * 0.09, s * 0.23, 0.29, 0.34, top + 0.10, top + 0.106), 'yellow')
        bolts(M, g, [(s * 0.10, 0.06), (s * 0.22, 0.06)], top + 0.10, r=0.015)
        M.add(g, cyl((x, 0.38, bz), (x, 0.84, bz), 0.046, n=14), 'metal')
        for y in np.arange(0.42, 0.62, 0.042):
            M.add(g, cyl((x, y, bz), (x, y + 0.021, bz), 0.072, n=14), 'hull_dark')
        M.add(g, cyl((x, 0.64, bz), (x, 0.67, bz), 0.066, n=14), 'yellow')
        M.add(g, cyl((x, 0.69, bz), (x, 0.77, bz), 0.058, n=14), 'coil')
        for y in (0.70, 0.735):
            M.add(g, cyl((x, y, bz), (x, y + 0.016, bz), 0.062, n=14), 'glow')
        M.add(g, cyl((x, 0.78, bz), (x, 0.87, bz), 0.060, 0.070, n=14), 'hull_mid')
        M.add(g, cyl((x, 0.87, bz), (x, 0.882, bz), 0.054, n=14), 'metal_light')
        M.add(g, cyl((x, 0.87, bz), (x, 0.89, bz), 0.036, n=12), 'glow')
        cable(M, g, [(s * 0.30, -0.10, top + 0.03), (s * 0.30, 0.08, top + 0.10), (s * 0.24, 0.24, top + 0.10)], 0.022, ends='yellow')
        light(M, g, s * 0.37, 0.20, top - 0.02, 0.04, 0.035)
    # rangefinder between the emitters + access hatch behind it
    M.add(g, B(-0.05, 0.05, 0.22, 0.52, top, top + 0.075), 'hull_light')
    M.add(g, B(-0.036, 0.036, 0.25, 0.48, top + 0.075, top + 0.085), 'hull_mid')
    M.add(g, cyl((0, 0.52, top + 0.04), (0, 0.55, top + 0.04), 0.03, n=12), 'glass')
    M.add(g, B(-0.018, 0.018, 0.38, 0.45, top + 0.085, top + 0.09), 'glow')
    M.add(g, B(-0.09, 0.09, 0.03, 0.17, top, top + 0.02), 'hull_dark')
    M.add(g, B(-0.075, 0.075, 0.045, 0.155, top + 0.02, top + 0.03), 'hull_light')
    M.add(g, tube_path([(-0.04, 0.08, top + 0.03), (-0.04, 0.08, top + 0.05), (0.04, 0.08, top + 0.05), (0.04, 0.08, top + 0.03)], 0.01, n=5), 'metal_light')
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
