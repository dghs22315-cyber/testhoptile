"""T5 art workstream (2.5.0-alpha2): Aeon tier + the UEF Tempest. Every sprite here is new.

    .venv/bin/python tools/art/g_t5.py [name ...]     (no args = everything)

Design language (docs/VANGUARD-TZ.md 2.2): Aeon = smooth streamlined forms, ivory hull, gold trim, green glow,
violet for quantum tech. Tempest is UEF (SC2 Disruptor Station): blue-grey steel, yellow hazard trim, four barrels,
radiators and charge coils with a green quantum glow. 1.0 = one tile, Z up, origin = block centre, heads face +Y
(BeamDrill heads face +X, its rotation 0).
"""
import math
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from geom import *  # noqa: E402,F401,F403
from mats import Model, MID  # noqa: E402
from hero import (P, slope_plate, bolts_on, bolts_R, buttress, turntable, grille, cable, seam, antenna,  # noqa: E402
                  hydraulic, muzzle_brake, elevate, muzzle_world)
from models import bolts, chevrons  # noqa: E402
import rend  # noqa: E402
from rend import outline, heat_sprite, over, hexc  # noqa: E402
from export import save, layer, turret, FULL, qa_sheet, blank, SS, REPO  # noqa: E402

# ------------------------------------------------------------------ materials (append-only)
rend.add_material('aeon_cream', ['37322a', '575142', '7c745f', 'a19982', 'c6bfa6', 'ebe5ce'])     # ivory hull
rend.add_material('aeon_gold', ['3a2908', '5f4410', '8a6619', 'b68b24', 'dbb03b', 'f7da70'])      # gold trim
rend.add_material('aeon_dark', ['0f110d', '181b15', '22261e', '2d3228', '3a4033', '4a5142'])      # olive recess
rend.add_material('aeon_crystal', ['163c2a', '215c3d', '2d8052', '44a46b', '6cc88d', 'a8ecbf'])   # pale green crystal
rend.add_material('nullq', ['3a3550', '55506f', '767195', '9893b9', 'bdb8da', 'e5e2f7'])          # null-quartz
rend.add_material('quantum', ['4a3290', '6a50c0', '9a7ef0', 'b8a0ff', 'd8caff', 'f2ecff'], glow=True)
rend.add_material('lumen', ['2a8a3a', '3cb050', '5cd870', '9df0a8', 'c8ffd0', 'f0fff4'], glow=True)  # mint core

TUR, DEF, WAL, CRA, PWR, DRL = 'blocks/turrets', 'blocks/defense', 'blocks/walls', 'blocks/crafting', 'blocks/power', 'blocks/drills'
SPEC = {}


# ------------------------------------------------------------------ geometry kit
def B(x0, x1, y0, y1, z0, z1):
    return box(min(x0, x1), max(x0, x1), min(y0, y1), max(y0, y1), z0, z1)


def circ(r, n, cx=0.0, cy=0.0, rot=0.0, sx=1.0, sy=1.0):
    a = np.radians(rot + np.arange(n) * 360.0 / n)
    return np.column_stack([cx + sx * r * np.cos(a), cy + sy * r * np.sin(a)])


def sqc(h, n=64, k=5.0, cx=0.0, cy=0.0, rot=0.0, hy=None):
    """Superellipse 'rounded square' sampled at n even angles (matches circ() vertex-for-vertex)."""
    hy = h if hy is None else hy
    a = np.radians(rot + np.arange(n) * 360.0 / n)
    c, s = np.cos(a), np.sin(a)
    r = 1.0 / (np.abs(c / h) ** k + np.abs(s / hy) ** k) ** (1.0 / k)
    return np.column_stack([cx + r * c, cy + r * s])


def inset(poly, d):
    """Miter offset of a ccw polygon (d > 0 shrinks)."""
    p = ccw(poly)
    n = len(p)
    out = []
    for i in range(n):
        a, b, c = p[i - 1], p[i], p[(i + 1) % n]
        e1, e2 = b - a, c - b
        n1 = np.array([-e1[1], e1[0]]) / (np.linalg.norm(e1) + 1e-12)
        n2 = np.array([-e2[1], e2[0]]) / (np.linalg.norm(e2) + 1e-12)
        m = n1 + n2
        m /= np.linalg.norm(m) + 1e-12
        out.append(b + m * d / max(float(np.dot(m, n1)), 0.35))
    return np.array(out)


def lofts(rings, cap_b=True, cap_t=True):
    out = []
    for i in range(len(rings) - 1):
        out.append(loft(rings[i], rings[i + 1], cap_b=cap_b and i == 0, cap_t=cap_t and i == len(rings) - 2))
    return np.concatenate(out)


def rslab(poly, z0, z1, r=0.06, steps=3):
    """Slab with a vertical side and a quarter-round top edge (the smooth Aeon bevel)."""
    rings = [ring(ccw(poly), z0)]
    for i in range(steps + 1):
        t = (i / steps) * math.pi / 2
        rings.append(ring(inset(poly, r * (1 - math.cos(t))), z1 - r + r * math.sin(t)))
    return lofts(rings)


def prof(poly, pr):
    """Loft through [(inset, z), ...] - arbitrary smooth hull profile."""
    return lofts([ring(inset(poly, d) if d else ccw(poly), z) for d, z in pr])


def dome(cx, cy, z0, r, h, n=32, lat=6, sx=1.0, sy=1.0, t0=0.0):
    rings = []
    for i in range(lat + 1):
        t = t0 + (i / lat) * (math.pi / 2 - t0)
        rr = max(r * math.cos(t), r * 0.03)
        rings.append(ring(circ(rr, n, cx, cy, sx=sx, sy=sy), z0 + h * (math.sin(t) - math.sin(t0)) / (1 - math.sin(t0))))
    return lofts(rings, cap_b=True, cap_t=True)


def annulus(r0, r1, z0, z1, n=48, cx=0.0, cy=0.0, zi=None):
    """Thick ring; zi (inner top height) makes a conical top."""
    zi = z1 if zi is None else zi
    o, i_ = circ(r1, n, cx, cy), circ(r0, n, cx, cy)
    return np.concatenate([loft(ring(o, z0), ring(o, z1), False, False), loft(ring(o, z1), ring(i_, zi), False, False),
                           loft(ring(i_, zi), ring(i_, z0), False, False), loft(ring(i_, z0), ring(o, z0), False, False)])


def arc_poly(r0, r1, a0, a1, n=16, cx=0.0, cy=0.0):
    A = np.radians(np.linspace(a0, a1, n))
    outer = [(cx + r1 * math.cos(a), cy + r1 * math.sin(a)) for a in A]
    inner = [(cx + r0 * math.cos(a), cy + r0 * math.sin(a)) for a in A[::-1]]
    return ccw(outer + inner)


def arc(M, g, r0, r1, a0, a1, z0, z1, m, n=16, cx=0.0, cy=0.0, R=None):
    M.add(g, tf(prism(arc_poly(r0, r1, a0, a1, n, cx, cy), z0, z1), R), m)


def torus(M, g, R_, r, z, m, n=32, k=10, cx=0.0, cy=0.0, tilt=0.0, a0=0.0, a1=360.0, Rm=None, t=(0, 0, 0)):
    """Torus segment; tilt rotates it about X (ring leans toward +Y)."""
    rot = rx(tilt) if Rm is None else Rm
    for i in range(n):
        a = math.radians(a0 + (a1 - a0) * i / n)
        b = math.radians(a0 + (a1 - a0) * (i + 1) / n)
        p0 = rot @ np.array([R_ * math.cos(a), R_ * math.sin(a), 0.0])
        p1 = rot @ np.array([R_ * math.cos(b), R_ * math.sin(b), 0.0])
        o = np.array([cx, cy, z]) + np.asarray(t, float)
        M.add(g, cyl(p0 + o, p1 + o, r, n=k), m)


def strip(pts, w, z0, z1):
    """Flat band along a 2D polyline (grooves, inlays, glow channels)."""
    out = []
    pts = [np.asarray(p, float) for p in pts]
    for a, b in zip(pts[:-1], pts[1:]):
        d = b - a
        L = float(np.linalg.norm(d))
        if L < 1e-6:
            continue
        ang = math.degrees(math.atan2(d[1], d[0]))
        c = (a + b) / 2
        out.append(tf(cbox(0, 0, (z0 + z1) / 2, L + w * 0.8, w, z1 - z0), rz(ang), (c[0], c[1], 0)))
    return np.concatenate(out)


def arc_pts(r, a0, a1, n, cx=0.0, cy=0.0):
    return [(cx + r * math.cos(math.radians(a)), cy + r * math.sin(math.radians(a))) for a in np.linspace(a0, a1, n)]


def crystal(L, r, tip=0.30, sides=6, taper=0.92, phase=0.0):
    """Prismatic crystal along +Z with a pyramidal termination."""
    a = phase + np.arange(sides) * 2 * math.pi / sides
    r0 = np.column_stack([r * np.cos(a), r * np.sin(a), np.zeros(sides)])
    zt = L * (1 - tip)
    r1 = np.column_stack([r * taper * np.cos(a), r * taper * np.sin(a), np.full(sides, zt)])
    T = list(loft(r0, r1, cap_b=True, cap_t=False))
    apex = np.array([0, 0, L])
    for i in range(sides):
        T.append([r1[i], r1[(i + 1) % sides], apex])
    return clean(T)


def bipyr(n, r, zb, zm, zt, cx=0.0, cy=0.0, rot=0.0, sx=1.0, sy=1.0):
    a = np.radians(rot + np.arange(n) * 360.0 / n)
    mid = [np.array([cx + sx * r * math.cos(t), cy + sy * r * math.sin(t), zm]) for t in a]
    top, bot = np.array([cx, cy, zt]), np.array([cx, cy, zb])
    T = []
    for i in range(n):
        p, q = mid[i], mid[(i + 1) % n]
        T.append([p, q, top])
        T.append([q, p, bot])
    return clean(T)


def leaf(L, w, n=12, back=0.0):
    """Petal outline along +X from 0 to L (pointed tip, rounded shoulder)."""
    t = np.linspace(0, 1, n)
    up = [(back + L * tt, w * math.sin(math.pi * min(1.0, tt * 1.15)) ** 0.75 * (1 - 0.25 * tt)) for tt in t]
    up[-1] = (back + L, 0.0)
    lo = [(x, -y) for x, y in up[-2:0:-1]]
    return P(up + lo)


def node(M, g, x, y, z, r=0.07, glow='gglow', rim='aeon_gold', h=0.03):
    """Aeon light: gold bezel ring with a domed glow lens."""
    M.add(g, cyl((x, y, z - 0.01), (x, y, z + h), r * 1.5, r * 1.35, n=14), rim)
    M.add(g, dome(x, y, z + h, r, r * 0.55, n=12, lat=3), glow)


def channel(M, g, pts, z, w=0.07, glow='gglow', bed='aeon_dark'):
    """Engraved glow channel: dark bed with a narrower glowing core."""
    M.add(g, strip(pts, w, z - 0.004, z + 0.006), bed)
    M.add(g, strip(pts, w * 0.45, z - 0.004, z + 0.011), glow)


def groove(M, g, pts, z, w=0.03, m='aeon_dark'):
    M.add(g, strip(pts, w, z - 0.004, z + 0.005), m)


def inlay(M, g, pts, z, w=0.045, m='aeon_gold', h=0.018):
    M.add(g, strip(pts, w, z - 0.004, z + h), m)


def rot2(pts, deg, t=(0.0, 0.0)):
    c, s = math.cos(math.radians(deg)), math.sin(math.radians(deg))
    return [(x * c - y * s + t[0], x * s + y * c + t[1]) for x, y in pts]


def aeon_pad(M, g, h, z1=0.22, k=4.0, n=96):
    """Smooth Aeon foundation: dark skirt, ivory rounded-square slab, gold rim inlay, engraved inner border."""
    M.add(g, rslab(sqc(h * 0.99, n, k), 0.0, 0.10, r=0.04, steps=2), 'aeon_dark')
    M.add(g, rslab(sqc(h * 0.93, n, k), 0.08, z1, r=min(0.10, (z1 - 0.08) * 0.8), steps=3), 'aeon_cream')
    rim = sqc(h * 0.93 - 0.12, n, k)
    M.add(g, loft(ring(rim, z1 + 0.002), ring(inset(rim, 0.05), z1 + 0.002), False, False), 'aeon_gold')
    M.add(g, loft(ring(rim, z1 - 0.004), ring(rim, z1 + 0.002), False, False), 'aeon_gold')
    in2 = sqc(h * 0.93 - 0.26, n, k)
    M.add(g, loft(ring(in2, z1 + 0.003), ring(inset(in2, 0.025), z1 + 0.003), False, False), 'aeon_dark')
    return z1


def heatmask(weights, ymin=None, ymax=None, rmax=None):
    """heat fn from {material: weight}, optionally clipped to a Y band / radius (sprite coordinates, tiles)."""
    ids = {MID[k]: v for k, v in weights.items()}

    def f(mp, X, Y, g):
        out = np.zeros(mp.shape)
        for i, v in ids.items():
            out = np.where(mp == i, v, out)
        if ymin is not None:
            out = np.where(Y >= ymin, out, 0)
        if ymax is not None:
            out = np.where(Y <= ymax, out, 0)
        if rmax is not None:
            out = np.where(X * X + Y * Y <= rmax * rmax, out, 0)
        return out
    return f


def tint(hm_sprite, col):
    """Colour a white heat_sprite mask (for layers Mindustry draws untinted)."""
    a = np.asarray(hm_sprite).copy()
    a[..., :3] = hexc(col).astype(np.uint8)
    return a


# ================================================================== TEMPEST - T5 UEF Disruptor (8x8)
SPREAD = 7 / 8.0           # ShootAlternate spread 7 world units -> barrel pitch in tiles
BARREL_X = [(i - 1.5) * SPREAD for i in range(4)]


def coil_stack(M, g, x, y, z0, h, r, n=4, glow='gglow', body='hull_dark', cap='steel'):
    """Upright charge coil: collar, alternating dark/glow windings, steel cap with emitter tip."""
    M.add(g, cyl((x, y, z0), (x, y, z0 + 0.06), r * 1.25, n=18), 'hull_mid')
    M.add(g, cyl((x, y, z0 + 0.06), (x, y, z0 + h), r * 0.82, n=18), body)
    st = (h - 0.12) / n
    for i in range(n):
        zz = z0 + 0.10 + i * st
        M.add(g, cyl((x, y, zz), (x, y, zz + st * 0.42), r, n=18), glow)
        M.add(g, cyl((x, y, zz + st * 0.42), (x, y, zz + st * 0.62), r * 1.04, n=18), 'metal')
    M.add(g, cyl((x, y, z0 + h), (x, y, z0 + h + 0.05), r * 1.06, r * 0.86, n=18), cap)
    M.add(g, cyl((x, y, z0 + h + 0.05), (x, y, z0 + h + 0.07), r * 0.40, n=12), 'hull_dark')
    M.add(g, cyl((x, y, z0 + h + 0.07), (x, y, z0 + h + 0.085), r * 0.24, n=10), glow)


def radiator(M, g, x0, x1, y0, y1, z0, z1, n, R=None, fin='metal', gap='heat', frame='hull_light'):
    """Radiator block: hot core between thin fins, framed; fins run along X."""
    def A(T, m): M.add(g, tf(T, R), m)
    A(B(x0, x1, y0, y1, z0, z0 + (z1 - z0) * 0.55), 'vent')
    A(B(x0 + 0.03, x1 - 0.03, y0 + 0.03, y1 - 0.03, z0, z0 + (z1 - z0) * 0.62), gap)
    st = (y1 - y0) / n
    for i in range(n):
        y = y0 + st * (i + 0.5)
        A(prism(rect((x0 + x1) / 2, y, (x1 - x0) / 2 - 0.02, st * 0.22), z0, z1,
                top_poly=rect((x0 + x1) / 2, y, (x1 - x0) / 2 - 0.04, st * 0.13)), fin)
    for yy in (y0 - 0.035, y1 + 0.035):
        A(B(x0 - 0.03, x1 + 0.03, yy - 0.04, yy + 0.04, z0, z1 + 0.03), frame)
    for xx in (x0 - 0.03, x1 + 0.03):
        A(B(xx - 0.03, xx + 0.03, y0 - 0.07, y1 + 0.07, z0, z1 + 0.015), 'hull_mid')


def tempest():
    M = Model()
    g = 'base'
    h = 4.0
    # ---- star platform on an armoured pad
    M.add(g, prism(cham_rect(3.97, 3.97, 1.05), 0.0, 0.10, 0.99), 'hull_dark')
    star = []
    for k in range(8):
        a = 45 * k
        rt = 3.92 if k % 2 == 0 else 5.05
        star.append((rt * math.cos(math.radians(a)), rt * math.sin(math.radians(a))))
        star.append((3.05 * math.cos(math.radians(a + 22.5)), 3.05 * math.sin(math.radians(a + 22.5))))
    star = P(star)
    M.add(g, prism(star, 0.10, 0.24, top_poly=inset(star, 0.06)), 'hull_mid')
    M.add(g, prism(inset(star, 0.30), 0.24, 0.27, top_poly=inset(star, 0.34)), 'hull_dark')
    for k in range(4):
        S = rz(90 * k)
        # diagonal buttress arms with yellow inlays and green tip lights
        buttress(M, g, 45 + 90 * k, 2.85, 5.05, 0.62, 0.62, 0.26, z0=0.10, mat='hull_light', inlay='yellow', tip='gglow')
        # cardinal arm: charge-coil pylon on a plinth
        M.add(g, tf(prism(cham_rect(0.48, 0.50, 0.14, cx=0, cy=-3.32), 0.24, 0.40, 0.92), S), 'hull_light')
        M.add(g, tf(cbox(0, -3.32, 0.405, 0.70, 0.07, 0.012), S), 'yellow')
        p = S @ np.array([0, -3.32, 0])
        coil_stack(M, g, p[0], p[1], 0.40, 0.42, 0.24, n=3)
        cable(M, g, [(0.30, -3.05, 0.48), (0.42, -2.82, 0.42), (0.52, -2.66, 0.32)], 0.04, ends='yellow', R=S)
        cable(M, g, [(-0.30, -3.05, 0.48), (-0.42, -2.82, 0.42), (-0.52, -2.66, 0.32)], 0.04, ends='yellow', R=S)
        # radiator banks either side of each pylon (in the star valleys)
        for s in (-1, 1):
            R = rz(90 * k + s * 24)
            radiator(M, g, -0.42, 0.42, -3.40, -2.95, 0.24, 0.40, 6, R=R)
        # hazard strips + bolts along the pad edge
        chevrons(M, g, 0, -3.82, 0.10, 1.6, 0.16, n=8, ang=90 * k)
        bolts_R(M, g, [(-2.2, -3.72), (2.2, -3.72), (-1.2, -3.72), (1.2, -3.72)], 0.10, S, r=0.035)
        seam(M, g, *[tuple((S @ np.array([x, -2.88, 0]))[:2]) for x in (-0.95, 0.95)], 0.27, w=0.03, h=0.012)
    for k in range(8):
        a = math.radians(22.5 + 45 * k)
        bolts(M, g, [(2.98 * math.cos(a), 2.98 * math.sin(a))], 0.27, r=0.035)
    z = turntable(M, g, 2.80, 0.27, teeth=56, nb=16, trim='gglow')

    # ---- rotating tower
    g = 'body'
    hull = mirror_half([(0, 2.25), (1.25, 2.15), (2.30, 1.45), (2.62, 0.45), (2.62, -1.45), (2.20, -2.62), (1.15, -3.22), (0, -3.30)])
    M.add(g, prism(hull, z, z + 0.46, 0.95), 'hull_dark')
    deck = scale_poly(hull, 0.90, (0, -0.4))
    M.add(g, prism(deck, z + 0.46, z + 0.58, 0.97), 'hull_mid')
    top = z + 0.58
    # ribbed flanks
    for s in (-1, 1):
        for y in np.arange(-2.30, 0.95, 0.20):
            M.add(g, B(s * 2.50, s * 2.74, y - 0.045, y + 0.045, z + 0.04, z + 0.44), 'steel')
        M.add(g, B(s * 2.48, s * 2.76, -2.42, 1.06, z + 0.44, z + 0.48), 'hull_light')
        # big flank radiators
        radiator(M, g, s * 1.50, s * 2.30, -2.05, 0.30, top - 0.02, top + 0.20, 11, fin='metal')
        # shoulder armour with yellow inlay
        sp = [(s * 1.05, 0.55), (s * 2.25, 0.55), (s * 2.05, 1.40), (s * 1.10, 1.95)]
        zf = (lambda x, y: top + 0.14 - (abs(x) - 1.05) * 0.10)
        slope_plate(M, g, P(sp), zf, 'hull_light', thick=0.16, inlay='yellow', isc=0.60, ih=0.022)
        bolts_on(M, g, [(s * 1.18, 0.65), (s * 2.10, 0.65), (s * 1.95, 1.30), (s * 1.18, 1.80)], zf, r=0.03)
        # exhaust stacks at the rear corners
        ex, ey = s * 1.95, -2.55
        M.add(g, cyl((ex, ey, z + 0.30), (ex, ey, top + 0.24), 0.15, n=16), 'metal')
        M.add(g, cyl((ex, ey, top + 0.24), (ex, ey, top + 0.29), 0.18, n=16), 'hull_dark')
        M.add(g, cyl((ex, ey, top + 0.29), (ex, ey, top + 0.295), 0.11, n=14), 'heat')
        antenna(M, g, (s * 0.95, -2.85, top), (s * 1.25, -3.55, top + 0.95), tip='gglow')
    # rear charge-coil bank feeding the barrels
    M.add(g, B(-1.55, 1.55, -2.95, -2.05, top - 0.02, top + 0.06), 'hull_dark')
    for i, x in enumerate((-1.10, -0.37, 0.37, 1.10)):
        coil_stack(M, g, x, -2.50, top + 0.06, 0.48, 0.27, n=4)
        cable(M, g, [(x, -2.20, top + 0.36), (x * 0.9, -1.55, top + 0.44), (BARREL_X[i] * 0.85, -0.95, top + 0.34)], 0.045, ends='yellow')
    chevrons(M, g, 0, -3.12, top - 0.02, 2.2, 0.16, n=10)
    # fire-control cupola + capacitor deck in the middle
    M.add(g, prism(cham_rect(0.95, 0.45, 0.16, cy=-1.45), top - 0.01, top + 0.16, 0.94), 'hull_light')
    M.add(g, prism(cham_rect(0.80, 0.32, 0.12, cy=-1.45), top + 0.16, top + 0.20, 0.96), 'hull_mid')
    M.add(g, B(-0.62, 0.62, -1.20, -1.14, top + 0.08, top + 0.15), 'glass')
    M.add(g, cbox(0, -1.45, top + 0.205, 1.10, 0.05, 0.01), 'gglow')
    bolts(M, g, [(-0.85, -1.80), (0.85, -1.80), (-0.85, -1.10), (0.85, -1.10)], top + 0.16, r=0.026)
    grille(M, g, 0, -0.55, top, 1.70, 0.30, n=12, glow='gglow')
    seam(M, g, (-1.30, -0.20), (1.30, -0.20), top, w=0.03, h=0.012)
    seam(M, g, (-1.30, -2.00), (1.30, -2.00), top, w=0.03, h=0.012)
    # front mantlet cheeks holding the trunnion
    for s in (-1, 1):
        M.add(g, B(s * 1.95, s * 2.30, 0.20, 1.60, top - 0.02, top + 0.40), 'hull_light')
        M.add(g, B(s * 2.00, s * 2.25, 0.30, 1.50, top + 0.40, top + 0.43), 'yellow')
        M.add(g, cyl((s * 1.90, 0.90, top + 0.30), (s * 2.36, 0.90, top + 0.30), 0.26, n=22), 'metal')
        M.add(g, cyl((s * 2.36, 0.90, top + 0.30), (s * 2.44, 0.90, top + 0.30), 0.18, n=18), 'hull_dark')
        M.add(g, cyl((s * 2.44, 0.90, top + 0.30), (s * 2.46, 0.90, top + 0.30), 0.09, n=12), 'gglow')

    # ---- four-barrel cradle (recoiling part)
    g = 'barrel_local'
    M.add(g, box(-1.92, 1.92, -1.05, 0.35, -0.26, 0.20), 'hull_mid')
    M.add(g, box(-1.84, 1.84, -0.98, 0.28, 0.20, 0.25), 'hull_light')
    for y0 in (-0.80, -0.30):
        M.add(g, box(-1.70, 1.70, y0, y0 + 0.08, 0.25, 0.262), 'yellow')
    bolts(M, g, [(x, y) for x in (-1.72, -0.86, 0, 0.86, 1.72) for y in (-0.92, 0.20)], 0.25, r=0.028)
    M.add(g, box(-1.60, 1.60, -1.40, -1.05, -0.20, 0.14), 'metal')
    for x in BARREL_X:
        M.add(g, cyl((x, -1.40, 0), (x, -1.48, 0), 0.13, n=14), 'gglow')
    for i, x in enumerate(BARREL_X):
        M.add(g, cyl((x, 0.35, 0), (x, 1.45, 0), 0.36, n=22), 'hull_dark')
        for y in (0.42, 0.95):
            M.add(g, cyl((x, y, 0), (x, y + 0.08, 0), 0.38, n=22), 'metal_light')
        # quantum charge coils
        for k in range(5):
            y = 1.48 + k * 0.20
            M.add(g, cyl((x, y, 0), (x, y + 0.08, 0), 0.355, n=20), 'hull_mid')
            M.add(g, cyl((x, y + 0.08, 0), (x, y + 0.20, 0), 0.33, n=20), 'gglow')
        M.add(g, cyl((x, 2.48, 0), (x, 2.60, 0), 0.37, n=22), 'hull_dark')
        M.add(g, cyl((x, 2.60, 0), (x, 4.10, 0), 0.25, 0.23, n=20), 'steel')
        for y in (2.95, 3.55):
            M.add(g, cyl((x, y - 0.05, 0), (x, y + 0.05, 0), 0.29, n=20), 'hull_mid')
        M.add(g, box(x - 0.035, x + 0.035, 2.70, 4.00, 0.22, 0.255), 'yellow')
        muzzle_brake(M, g, 4.10, 0.50, 0.27, x=x, nb=3, trim='yellow', baffle='metal_light', bore_r=0.12, out=0.08)
    for y0, y1 in ((1.30, 1.42), (3.20, 3.30)):                      # barrel clamps
        M.add(g, box(-1.70, 1.70, y0, y1, -0.20, 0.33), 'hull_mid')
        M.add(g, box(-1.62, 1.62, y0 + 0.02, y1 - 0.02, 0.33, 0.35), 'yellow')
    for s in (-1, 1):
        hydraulic(M, g, s * 1.86, 0.05, -0.95, 0.70, 1.75, r=0.10)
        cable(M, g, [(s * 1.45, -0.80, 0.26), (s * 1.50, 0.35, 0.34), (s * 1.31, 1.30, 0.40)], 0.04, ends='yellow')
    pv = (0, 0.90, top + 0.30)
    elevate(M, 8, pv)
    SPEC['tempest'] = muzzle_world(8, pv, 4.60)
    return M


def heat_tempest(mp, X, Y, g):
    ids = [MID[m] for m in ('metal', 'hull_dark', 'hull_mid', 'metal_light', 'steel', 'bore')]
    grad = np.where(np.isin(mp, ids), np.clip((Y - 3.4) / (5.6 - 3.4), 0, 1) * 0.85, 0)
    return np.maximum(grad, np.isin(mp, [MID['gglow']]).astype(float) * 0.9)


# ================================================================== driver
def tris(M):
    return f'{M.ntri():6d} tris'


def do_tempest():
    M = tempest()
    turret('tempest', M, 256, 448, heat=heat_tempest, parts=True)
    my = SPEC['tempest'][0]
    print(f'tempest            {tris(M)}  base 256 / body 448 px  muzzle y={my:.3f} tiles -> shootY {my * 8:.1f}', flush=True)


JOBS = {'tempest': do_tempest}


def main(only=()):
    for name, fn in JOBS.items():
        if not only or name in only:
            fn()


if __name__ == '__main__':
    main(sys.argv[1:])
