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
    """Upright charge coil: collar, dark/glow windings with steel separators; the top winding stays visible
    from above as a glowing annulus around a small steel cap."""
    M.add(g, cyl((x, y, z0), (x, y, z0 + 0.06), r * 1.25, n=18), 'hull_mid')
    M.add(g, cyl((x, y, z0 + 0.06), (x, y, z0 + h), r * 0.82, n=18), body)
    st = (h - 0.12) / n
    for i in range(n):
        zz = z0 + 0.08 + i * st
        M.add(g, cyl((x, y, zz), (x, y, zz + st * 0.55), r, n=18), glow)
        M.add(g, cyl((x, y, zz + st * 0.55), (x, y, zz + st * 0.75), r * 1.05, n=18), 'metal')
    M.add(g, cyl((x, y, z0 + h - 0.06), (x, y, z0 + h + 0.02), r * 0.97, n=18), glow)
    for i in range(4):
        M.add(g, tf(cbox(r * 0.78, 0, z0 + h + 0.03, r * 0.42, 0.045, 0.03), rz(45 + 90 * i), (x, y, 0)), 'metal')
    M.add(g, cyl((x, y, z0 + h), (x, y, z0 + h + 0.07), r * 0.60, r * 0.52, n=16), cap)
    M.add(g, cyl((x, y, z0 + h + 0.07), (x, y, z0 + h + 0.08), r * 0.34, n=12), 'hull_dark')
    M.add(g, cyl((x, y, z0 + h + 0.08), (x, y, z0 + h + 0.095), r * 0.20, n=10), glow)


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
    # ---- star platform on an armoured pad
    M.add(g, prism(cham_rect(3.97, 3.97, 1.10), 0.0, 0.10, 0.99), 'hull_dark')
    star = []
    for k in range(8):
        a = 45 * k
        rt = 3.95 if k % 2 == 0 else 5.20
        star.append((rt * math.cos(math.radians(a)), rt * math.sin(math.radians(a))))
        star.append((3.30 * math.cos(math.radians(a + 22.5)), 3.30 * math.sin(math.radians(a + 22.5))))
    star = P(star)
    M.add(g, prism(star, 0.10, 0.24, top_poly=inset(star, 0.06)), 'hull_mid')
    M.add(g, prism(inset(star, 0.32), 0.24, 0.27, top_poly=inset(star, 0.36)), 'hull_dark')
    for k in range(4):
        S = rz(90 * k)
        # diagonal buttress arms with yellow inlays and green tip lights
        buttress(M, g, 45 + 90 * k, 2.80, 5.10, 0.66, 0.66, 0.26, z0=0.10, mat='hull_light', inlay='yellow', tip='gglow')
        # cardinal arm: charge-coil pylon on a plinth
        M.add(g, tf(prism(cham_rect(0.50, 0.46, 0.14, cx=0, cy=-3.38), 0.24, 0.40, 0.92), S), 'hull_light')
        M.add(g, tf(cbox(0, -3.38, 0.405, 0.72, 0.07, 0.012), S), 'yellow')
        p = S @ np.array([0, -3.38, 0])
        coil_stack(M, g, p[0], p[1], 0.40, 0.42, 0.25, n=3)
        for s in (-1, 1):
            cable(M, g, [(s * 0.30, -3.10, 0.48), (s * 0.42, -2.92, 0.42), (s * 0.55, -2.80, 0.32)], 0.04, ends='yellow', R=S)
            # radiator banks either side of each pylon (in the star valleys)
            radiator(M, g, -0.44, 0.44, -3.62, -3.12, 0.24, 0.40, 6, R=rz(90 * k + s * 24))
            # corner floodlight posts on the pad between star tips
            q = S @ np.array([s * 2.25, -3.74, 0])
            M.add(g, cyl((q[0], q[1], 0.10), (q[0], q[1], 0.22), 0.11, n=12), 'hull_light')
            M.add(g, cyl((q[0], q[1], 0.22), (q[0], q[1], 0.25), 0.07, n=10), 'gglow')
        # hazard strips + bolts along the pad edge
        chevrons(M, g, 0, -3.86, 0.10, 1.10, 0.14, n=6, ang=90 * k)
        bolts_R(M, g, [(-1.55, -3.80), (1.55, -3.80), (-2.85, -3.80), (2.85, -3.80)], 0.10, S, r=0.035)
        seam(M, g, *[tuple((S @ np.array([x, -2.98, 0]))[:2]) for x in (-0.85, 0.85)], 0.27, w=0.03, h=0.012)
        grille(M, g, 0, -2.98, 0.27, 0.90, 0.14, n=7, glow='gglow', R=rz(90 * k + 45))
    for k in range(8):
        a = math.radians(22.5 + 45 * k)
        bolts(M, g, [(3.05 * math.cos(a), 3.05 * math.sin(a))], 0.27, r=0.035)
    z = turntable(M, g, 2.72, 0.27, teeth=56, nb=16, trim='gglow')

    # ---- rotating tower: octagonal hull, raised gun-house, radiator wings, coil bank
    g = 'body'
    hull = mirror_half([(0, 1.95), (0.95, 1.90), (1.90, 1.20), (2.25, 0.25), (2.25, -1.30), (1.75, -2.30), (0.85, -2.72), (0, -2.78)])
    M.add(g, prism(hull, z, z + 0.42, 0.95), 'hull_dark')
    M.add(g, prism(inset(hull, 0.16), z + 0.42, z + 0.54, 0.98), 'hull_mid')
    top = z + 0.54
    for s in (-1, 1):
        # ribbed flank skirt
        for y in np.arange(-1.85, 0.55, 0.20):
            M.add(g, B(s * 2.12, s * 2.34, y - 0.045, y + 0.045, z + 0.04, z + 0.40), 'steel')
        # radiator wings bolted to the flanks
        M.add(g, B(s * 2.10, s * 2.95, -1.95, -0.05, z + 0.10, z + 0.30), 'hull_mid')
        radiator(M, g, s * 2.22, s * 2.88, -1.85, -0.15, z + 0.30, z + 0.52, 10, fin='metal')
        M.add(g, B(s * 2.90, s * 3.02, -2.00, 0.00, z + 0.10, z + 0.58), 'hull_light')
        M.add(g, B(s * 2.93, s * 2.99, -1.80, -0.20, z + 0.58, z + 0.60), 'yellow')
        bolts(M, g, [(s * 2.96, -1.90), (s * 2.96, -0.10)], z + 0.58, r=0.03)
        # shoulder armour with yellow inlay
        sp = [(s * 0.95, 0.30), (s * 1.95, 0.30), (s * 1.75, 1.15), (s * 0.95, 1.65)]
        zf = (lambda x, y: top + 0.14 - (abs(x) - 0.95) * 0.10)
        slope_plate(M, g, P(sp), zf, 'hull_light', thick=0.16, inlay='yellow', isc=0.58, ih=0.022)
        bolts_on(M, g, [(s * 1.06, 0.40), (s * 1.82, 0.40), (s * 1.68, 1.05), (s * 1.06, 1.52)], zf, r=0.028)
        # side slope plates over the radiator roots
        sp2 = [(s * 1.30, -1.95), (s * 2.02, -1.80), (s * 2.02, -0.05), (s * 1.30, 0.10)]
        zf2 = (lambda x, y: top + 0.10 - (abs(x) - 1.30) * 0.16)
        slope_plate(M, g, P(sp2), zf2, 'hull_light', thick=0.14, inlay='hull_mid', isc=0.62, ih=0.016)
        for y in (-1.55, -1.00, -0.45):
            M.add(g, cbox(s * 1.66, y, zf2(1.66, 0) + 0.02, 0.30, 0.06, 0.02), 'gglow')
        # exhaust stacks at the rear corners
        ex, ey = s * 1.62, -2.18
        M.add(g, cyl((ex, ey, z + 0.30), (ex, ey, top + 0.26), 0.14, n=16), 'metal')
        M.add(g, cyl((ex, ey, top + 0.26), (ex, ey, top + 0.31), 0.17, n=16), 'hull_dark')
        M.add(g, cyl((ex, ey, top + 0.31), (ex, ey, top + 0.315), 0.10, n=14), 'heat')
        antenna(M, g, (s * 0.78, -2.50, top), (s * 1.10, -3.25, top + 0.95), tip='gglow')
    # rear charge-coil bank feeding the barrels
    # armoured roof tier (light mass between coil bank and gun-house)
    roof = cham_rect(1.22, 0.62, 0.22, cy=-0.95)
    M.add(g, prism(roof, top - 0.02, top + 0.16, top_poly=inset(roof, 0.07)), 'hull_light')
    M.add(g, prism(inset(roof, 0.20), top + 0.16, top + 0.18, 0.98), 'hull_mid')
    for s in (-1, 1):
        M.add(g, B(s * 0.78, s * 1.08, -1.40, -0.50, top + 0.16, top + 0.185), 'yellow')
        bolts(M, g, [(s * 1.10, -1.48), (s * 1.10, -0.42)], top + 0.12, r=0.026)
    grille(M, g, 0, -0.62, top + 0.18, 1.10, 0.18, n=9, glow='gglow')
    # rear charge-coil bank: four horizontal coils, windings visible from above, cabled to the breeches
    M.add(g, B(-1.30, 1.30, -2.62, -1.62, top - 0.02, top + 0.04), 'hull_dark')
    for x in (-1.30, 1.30):
        M.add(g, B(x - 0.06, x + 0.06, -2.62, -1.62, top - 0.02, top + 0.30), 'hull_light')
    for i, x in enumerate((-0.96, -0.32, 0.32, 0.96)):
        M.add(g, cyl((x, -2.58, top + 0.20), (x, -1.66, top + 0.20), 0.20, n=18), 'hull_dark')
        for k in range(6):
            y = -2.50 + k * 0.135
            M.add(g, cyl((x, y, top + 0.20), (x, y + 0.085, top + 0.20), 0.25, n=18), 'gglow')
        for y in (-2.62, -1.70):
            M.add(g, cyl((x, y, top + 0.20), (x, y + 0.08, top + 0.20), 0.27, n=18), 'steel')
        cable(M, g, [(x, -1.62, top + 0.26), (x * 0.95, -1.45, top + 0.32), (BARREL_X[i] * 0.80, -1.42, top + 0.24)], 0.04, ends='yellow')
    chevrons(M, g, 0, -2.72, top - 0.02, 1.7, 0.12, n=8)
    # fire-control cupola on the roof
    M.add(g, prism(cham_rect(0.46, 0.24, 0.10, cy=-1.10), top + 0.18, top + 0.34, 0.92), 'hull_mid')
    M.add(g, prism(cham_rect(0.36, 0.15, 0.07, cy=-1.10), top + 0.34, top + 0.37, 0.96), 'hull_dark')
    M.add(g, B(-0.32, 0.32, -0.88, -0.85, top + 0.22, top + 0.30), 'glass')
    M.add(g, cbox(0, -1.10, top + 0.375, 0.50, 0.04, 0.008), 'gglow')
    seam(M, g, (-1.10, -1.62), (1.10, -1.62), top, w=0.03, h=0.012)
    # trunnion cheeks
    for s in (-1, 1):
        M.add(g, B(s * 1.92, s * 2.24, 0.25, 1.45, top - 0.02, top + 0.40), 'hull_light')
        M.add(g, B(s * 1.97, s * 2.19, 0.35, 1.35, top + 0.40, top + 0.43), 'yellow')
        M.add(g, cyl((s * 1.86, 0.85, top + 0.30), (s * 2.30, 0.85, top + 0.30), 0.25, n=22), 'metal')
        M.add(g, cyl((s * 2.30, 0.85, top + 0.30), (s * 2.38, 0.85, top + 0.30), 0.17, n=18), 'hull_dark')
        M.add(g, cyl((s * 2.38, 0.85, top + 0.30), (s * 2.40, 0.85, top + 0.30), 0.085, n=12), 'gglow')

    # ---- four-barrel cradle (recoiling part)
    g = 'barrel_local'
    M.add(g, box(-1.86, 1.86, -1.10, 0.30, -0.28, 0.10), 'hull_dark')            # lower frame
    M.add(g, box(-1.60, 1.60, -1.42, -1.10, -0.20, 0.10), 'metal')
    for i, x in enumerate(BARREL_X):
        # individual breech housing
        M.add(g, prism(cham_rect(0.38, 0.70, 0.10, cx=x, cy=-0.40), 0.05, 0.30, 0.92), 'hull_light')
        M.add(g, prism(cham_rect(0.26, 0.56, 0.07, cx=x, cy=-0.40), 0.30, 0.34, 0.95), 'hull_mid')
        M.add(g, box(x - 0.24, x + 0.24, -0.02, 0.06, 0.30, 0.345), 'yellow')
        M.add(g, box(x - 0.14, x + 0.14, -0.86, -0.36, 0.34, 0.352), 'vent')
        for yy in (-0.80, -0.68, -0.56, -0.44):
            M.add(g, box(x - 0.12, x + 0.12, yy, yy + 0.04, 0.34, 0.37), 'metal')
        bolts(M, g, [(x - 0.28, -1.00), (x + 0.28, -1.00), (x - 0.28, 0.20), (x + 0.28, 0.20)], 0.30, r=0.026)
        M.add(g, cyl((x, -1.42, 0), (x, -1.50, 0), 0.12, n=14), 'gglow')
        # barrel: jacket, quantum charge coils, tube, collars, brake
        M.add(g, cyl((x, 0.30, 0), (x, 1.30, 0), 0.36, n=22), 'hull_dark')
        for y in (0.36, 0.86):
            M.add(g, cyl((x, y, 0), (x, y + 0.08, 0), 0.38, n=22), 'metal_light')
        for k in range(5):
            y = 1.32 + k * 0.20
            M.add(g, cyl((x, y, 0), (x, y + 0.08, 0), 0.355, n=20), 'hull_mid')
            M.add(g, cyl((x, y + 0.08, 0), (x, y + 0.20, 0), 0.33, n=20), 'gglow')
        M.add(g, cyl((x, 2.32, 0), (x, 2.46, 0), 0.37, n=22), 'hull_dark')
        M.add(g, cyl((x, 2.46, 0), (x, 4.55, 0), 0.25, 0.22, n=20), 'steel')
        for y in (2.95, 3.70):
            M.add(g, cyl((x, y - 0.05, 0), (x, y + 0.05, 0), 0.29, n=20), 'hull_mid')
        M.add(g, box(x - 0.035, x + 0.035, 2.55, 4.45, 0.21, 0.245), 'yellow')
        muzzle_brake(M, g, 4.55, 0.52, 0.27, x=x, nb=3, trim='yellow', baffle='metal_light', bore_r=0.12, out=0.08)
    for y0, y1 in ((1.18, 1.30), (3.25, 3.36)):                      # barrel clamps
        M.add(g, box(-1.70, 1.70, y0, y1, -0.20, 0.33), 'hull_mid')
        M.add(g, box(-1.62, 1.62, y0 + 0.02, y1 - 0.02, 0.33, 0.35), 'yellow')
    for s in (-1, 1):
        hydraulic(M, g, s * 1.86, 0.05, -1.00, 0.70, 1.70, r=0.10)
        cable(M, g, [(s * 1.52, -0.95, 0.30), (s * 1.62, 0.20, 0.36), (s * 1.31, 1.18, 0.40)], 0.04, ends='yellow')
    pv = (0, 0.85, top + 0.30)
    elevate(M, 8, pv)
    SPEC['tempest'] = muzzle_world(8, pv, 5.07)
    return M


def heat_tempest(mp, X, Y, g):
    ids = [MID[m] for m in ('metal', 'hull_dark', 'hull_mid', 'metal_light', 'steel', 'bore')]
    grad = np.where(np.isin(mp, ids), np.clip((Y - 3.8) / (5.95 - 3.8), 0, 1) * 0.85, 0)
    return np.maximum(grad, np.isin(mp, [MID['gglow']]).astype(float) * 0.9)


def crescent_node(M, g, cx, cy, ang, z, r=0.42, crystal_m='aeon_crystal', core='lumen'):
    """Aeon corner ornament: gold crescent cupping a crystal node, opening toward `ang`."""
    arc(M, g, r * 0.95, r * 1.30, ang + 40, ang + 320, z, z + 0.07, 'aeon_gold', n=20, cx=cx, cy=cy)
    arc(M, g, r * 1.00, r * 1.12, ang + 60, ang + 300, z + 0.07, z + 0.085, 'aeon_cream', n=18, cx=cx, cy=cy)
    M.add(g, cyl((cx, cy, z - 0.02), (cx, cy, z + 0.06), r * 0.80, r * 0.72, n=18), 'aeon_cream')
    M.add(g, cyl((cx, cy, z + 0.06), (cx, cy, z + 0.075), r * 0.60, n=16), 'aeon_dark')
    M.add(g, bipyr(6, r * 0.42, z + 0.06, z + 0.16, z + 0.42, cx, cy, rot=15), crystal_m)
    M.add(g, bipyr(6, r * 0.20, z + 0.10, z + 0.20, z + 0.46, cx, cy, rot=45), core)


def halo():
    M = Model()
    g = 'base'
    z1 = aeon_pad(M, g, 3.0, z1=0.22)
    # levitation well: dark bowl, glowing lift ring, gold lip
    M.add(g, annulus(1.95, 2.38, z1 - 0.02, z1 + 0.05, n=72, zi=z1 - 0.01), 'aeon_dark')
    M.add(g, annulus(2.38, 2.48, z1 - 0.02, z1 + 0.07, n=72), 'aeon_gold')
    torus(M, g, 2.17, 0.05, z1 + 0.02, 'gglow', n=48, k=8)
    for i in range(12):                                     # lift emitters around the well
        a = 15 + 30 * i
        x, y = 2.17 * math.cos(math.radians(a)), 2.17 * math.sin(math.radians(a))
        M.add(g, cyl((x, y, z1 - 0.01), (x, y, z1 + 0.09), 0.10, 0.08, n=10), 'aeon_cream')
        M.add(g, cyl((x, y, z1 + 0.09), (x, y, z1 + 0.10), 0.05, n=8), 'lumen')
    for k in range(4):
        S = rz(45 + 90 * k)
        d = S @ np.array([3.30, 0, 0])
        crescent_node(M, g, d[0], d[1], 45 + 90 * k + 180, z1, r=0.40)
        channel(M, g, rot2([(2.52, 0), (2.86, 0)], 45 + 90 * k), z1, w=0.08)
        # side intakes (lumen-ether feed) with gold filigree arcs
        T = rz(90 * k)
        M.add(g, tf(rslab(cham_rect(0.36, 0.10, 0.07, cx=0, cy=-2.62), z1 - 0.02, z1 + 0.10, r=0.04), T), 'aeon_cream')
        M.add(g, tf(cbox(0, -2.62, z1 + 0.105, 0.44, 0.05, 0.01), T), 'lumen')
        for s in (-1, 1):
            pts = arc_pts(2.60, 270 + s * 11, 270 + s * 36, 12)
            inlay(M, g, rot2(pts, 90 * k), z1, w=0.04)
            q = rot2([(s * 1.45, -2.56)], 90 * k)[0]
            node(M, g, q[0], q[1], z1, r=0.06)
        groove(M, g, rot2(arc_pts(2.70, 245, 295, 14), 90 * k), z1, w=0.025)

    # ---- hovering body: saucer + streamlined hull + forward ring emitter
    g = 'body'
    zb = 0.42
    sau = circ(2.05, 72)
    M.add(g, prof(sau, [(0.10, zb - 0.06), (0.0, zb + 0.04), (0.0, zb + 0.10), (0.05, zb + 0.16), (0.16, zb + 0.21), (0.34, zb + 0.24)]), 'aeon_cream')
    torus(M, g, 2.04, 0.04, zb + 0.07, 'aeon_gold', n=64, k=8)
    torus(M, g, 2.10, 0.022, zb + 0.02, 'gglow', n=64, k=6)
    zs = zb + 0.24
    M.add(g, loft(ring(circ(1.62, 72), zs + 0.004), ring(circ(1.56, 72), zs + 0.004), False, False), 'aeon_gold')
    for i in range(16):                                      # engraved saucer panelling
        a = math.radians(11.25 + 22.5 * i)
        groove(M, g, [(1.62 * math.cos(a), 1.62 * math.sin(a)), (1.95 * math.cos(a), 1.95 * math.sin(a))], zs - 0.03, w=0.025)
    for i in range(8):
        a = math.radians(22.5 + 45 * i)
        node(M, g, 1.80 * math.cos(a), 1.80 * math.sin(a), zs - 0.035, r=0.05)
    M.add(g, loft(ring(circ(1.30, 64), zs + 0.004), ring(circ(1.27, 64), zs + 0.004), False, False), 'aeon_dark')
    for a in (45, 135, 225, 315):                              # gold field-shaper arcs + lens pads on the saucer
        arc(M, g, 1.36, 1.50, a - 16, a + 16, zs - 0.01, zs + 0.03, 'aeon_gold', n=10)
        arc(M, g, 1.40, 1.46, a - 10, a + 10, zs + 0.03, zs + 0.036, 'lumen', n=8)
        q = rot2([(1.10, 0)], a)[0]
        M.add(g, dome(q[0], q[1], zs - 0.01, 0.13, 0.07, n=14, lat=3), 'aeon_cream')
        M.add(g, cyl((q[0], q[1], zs + 0.05), (q[0], q[1], zs + 0.065), 0.06, n=10), 'aeon_crystal')
    # streamlined spine hull
    hull = mirror_half([(0, 1.25), (0.42, 1.10), (0.78, 0.55), (0.92, -0.30), (0.80, -1.15), (0.42, -1.70), (0, -1.82)])
    M.add(g, prof(hull, [(0.0, zs - 0.02), (0.0, zs + 0.10), (0.06, zs + 0.20), (0.16, zs + 0.27), (0.30, zs + 0.31)]), 'aeon_cream')
    hz = zs + 0.31
    crest = mirror_half([(0, 0.95), (0.16, 0.85), (0.22, -0.20), (0.16, -1.30), (0, -1.45)])
    M.add(g, prism(crest, hz - 0.01, hz + 0.05, 0.85), 'aeon_gold')
    channel(M, g, [(0, -1.25), (0, 0.80)], hz + 0.05, w=0.07, glow='lumen')
    for s in (-1, 1):
        groove(M, g, [(s * 0.22, 0.80), (s * 0.40, 0.30), (s * 0.44, -0.60), (s * 0.28, -1.30)], hz, w=0.03)
        groove(M, g, [(s * 0.12, -0.30), (s * 0.44, -0.30)], hz, w=0.025)
        node(M, g, s * 0.30, 0.05, hz, r=0.04)
        # swept tail fins
        fin = P([(s * 0.70, -0.95), (s * 1.55, -1.55), (s * 1.70, -1.95), (s * 1.10, -1.72), (s * 0.55, -1.50)])
        M.add(g, prism(fin, zs - 0.02, zs + 0.16, 0.90), 'aeon_cream')
        M.add(g, prism(scale_poly(fin, 0.62), zs + 0.16, zs + 0.18), 'aeon_gold')
        node(M, g, s * 1.50, -1.80, zs + 0.10, r=0.045)
        # lumen-ether cells along the flanks
        for y in (0.15, -0.35):
            M.add(g, cyl((s * 1.08, y - 0.20, zs + 0.08), (s * 1.08, y + 0.20, zs + 0.08), 0.13, n=16), 'aeon_crystal')
            for yy in (y - 0.22, y + 0.18):
                M.add(g, cyl((s * 1.08, yy, zs + 0.08), (s * 1.08, yy + 0.04, zs + 0.08), 0.15, n=16), 'aeon_gold')
            M.add(g, cyl((s * 1.08, y - 0.10, zs + 0.08), (s * 1.08, y + 0.10, zs + 0.08), 0.135, n=16), 'lumen')
        # crescent arms sweeping forward to the ring
        arm = [(s * 0.55, 0.70), (s * 0.95, 1.05), (s * 1.20, 1.60), (s * 1.18, 2.20), (s * 1.02, 2.20), (s * 0.98, 1.65), (s * 0.70, 1.20), (s * 0.35, 1.05)]
        za = (lambda x, y: hz - 0.06 + max(0.0, y - 0.9) * 0.22)
        slope_plate(M, g, P(arm), za, 'aeon_gold', thick=0.12, inlay='aeon_cream', isc=0.55, ih=0.015)
    # forward ring emitter (faces +Y, leaning forward 32 deg)
    cy0, cz = 2.15, hz + 0.32
    torus(M, g, 0.98, 0.12, cz, 'aeon_gold', n=48, k=12, cy=cy0, tilt=-32)
    torus(M, g, 0.84, 0.06, cz, 'lumen', n=48, k=8, cy=cy0, tilt=-32)
    torus(M, g, 1.10, 0.035, cz, 'aeon_cream', n=48, k=6, cy=cy0, tilt=-32)
    o = np.array([0, cy0, cz])
    for i in range(6):                                         # emitter vanes holding the focus crystal
        a = math.radians(30 + 60 * i)
        p0 = rx(-32) @ np.array([0.80 * math.cos(a), 0.80 * math.sin(a), 0])
        p1 = rx(-32) @ np.array([0.22 * math.cos(a), 0.22 * math.sin(a), 0])
        M.add(g, cyl(p0 + o, p1 + o, 0.03, 0.02, n=6), 'aeon_gold')
    M.add(g, tf(bipyr(6, 0.22, -0.30, 0.0, 0.30), rx(-32 + 90), o), 'aeon_crystal')
    M.add(g, sphereish((0, cy0 + 0.05, cz + 0.05), 0.12, n=10), 'lumen')
    SPEC['halo'] = cy0
    return M


def quantum_interceptor():
    M = Model()
    g = 'base'
    z1 = aeon_pad(M, g, 2.0, z1=0.20)
    M.add(g, annulus(1.12, 1.42, z1 - 0.02, z1 + 0.05, n=64, zi=z1 - 0.01), 'aeon_dark')
    M.add(g, annulus(1.42, 1.52, z1 - 0.02, z1 + 0.07, n=64), 'aeon_gold')
    torus(M, g, 1.27, 0.035, z1 + 0.02, 'gglow', n=40, k=6)
    for k in range(4):
        a = 45 + 90 * k
        d = rz(a) @ np.array([2.05, 0, 0])
        crescent_node(M, g, d[0], d[1], a + 180, z1, r=0.30)
        channel(M, g, rot2([(-0.55, -1.62), (0.55, -1.62)], 90 * k), z1, w=0.07)
        for s in (-1, 1):
            q = rot2([(s * 0.80, -1.62)], 90 * k)[0]
            node(M, g, q[0], q[1], z1, r=0.05)
        M.add(g, tf(cbox(0, -1.86, z1 + 0.005, 0.70, 0.04, 0.01), rz(90 * k)), 'aeon_dark')
    # ---- rotating head: sphere emitter with three antennas (front one = shootLength 1.5 tiles)
    g = 'head'
    M.add(g, prof(circ(0.92, 56), [(0.0, z1), (0.0, z1 + 0.08), (0.06, z1 + 0.14), (0.16, z1 + 0.17)]), 'aeon_cream')
    torus(M, g, 0.90, 0.03, z1 + 0.06, 'aeon_gold', n=48, k=6)
    zc = z1 + 0.50
    M.add(g, sphereish((0, 0, zc), 0.52, n=28), 'aeon_cream')
    torus(M, g, 0.52, 0.045, zc, 'aeon_gold', n=40, k=8)
    torus(M, g, 0.40, 0.03, zc + 0.33, 'aeon_gold', n=32, k=6)
    M.add(g, dome(0, 0, zc + 0.33, 0.30, 0.20, n=24, lat=4), 'aeon_crystal')
    M.add(g, sphereish((0, 0, zc + 0.47), 0.09, n=10), 'lumen')
    for a, L in ((90, 1.50), (210, 1.36), (330, 1.36)):
        R = rz(a - 90)
        # antenna root housing on the sphere flank
        M.add(g, tf(rslab(cham_rect(0.15, 0.20, 0.06, cy=0.55), z1 + 0.10, z1 + 0.40, r=0.05), R), 'aeon_cream')
        M.add(g, tf(cbox(0, 0.55, z1 + 0.405, 0.12, 0.30, 0.012), R), 'aeon_gold')
        # tapered gold spar, crystal beads, glowing tip with prongs
        p0 = np.array([0, 0.60, z1 + 0.34])
        p1 = np.array([0, L - 0.08, z1 + 0.44])
        M.add(g, tf(cyl(p0, p1, 0.065, 0.035, n=10), R), 'aeon_gold')
        for t_ in (0.35, 0.65):
            q = p0 + (p1 - p0) * t_
            M.add(g, tf(bipyr(6, 0.075, -0.10, 0.0, 0.10), R @ rx(-90), R @ q), 'aeon_crystal')
        for s in (-1, 1):
            M.add(g, tf(cyl(p1 - np.array([0, 0.18, 0]), p1 + np.array([s * 0.09, 0.06, 0.02]), 0.02, n=6), R), 'aeon_gold')
        M.add(g, tf(sphereish(p1 + np.array([0, 0.02, 0.0]), 0.07, n=10), R), 'lumen')
    # front emitter eye
    M.add(g, cyl((0, 0.40, zc + 0.02), (0, 0.54, zc + 0.02), 0.20, n=20), 'aeon_gold')
    M.add(g, cyl((0, 0.54, zc + 0.02), (0, 0.58, zc + 0.02), 0.14, n=16), 'lumen')
    return M


def aegis():
    M = Model()
    g = 'main'
    z1 = aeon_pad(M, g, 3.5, z1=0.24)
    # outer emitter ring with glowing segments
    M.add(g, annulus(2.62, 2.92, z1 - 0.02, z1 + 0.04, n=96, zi=z1 + 0.01), 'aeon_dark')
    for i in range(24):
        a0 = 15 * i + 2
        arc(M, g, 2.72, 2.82, a0, a0 + 10, z1 + 0.01, z1 + 0.05, 'gglow', n=4)
    M.add(g, annulus(2.92, 3.00, z1 - 0.02, z1 + 0.07, n=96), 'aeon_gold')
    # pedestal
    M.add(g, rslab(circ(2.55, 96), z1 - 0.02, z1 + 0.20, r=0.08), 'aeon_cream')
    zp = z1 + 0.20
    M.add(g, loft(ring(circ(2.40, 96), zp + 0.003), ring(circ(2.33, 96), zp + 0.003), False, False), 'aeon_gold')
    M.add(g, rslab(circ(1.45, 72), zp - 0.02, zp + 0.14, r=0.06), 'aeon_cream')
    zd = zp + 0.14
    # eight gold petals cupping the dome
    for i in range(8):
        a = 22.5 + 45 * i
        R = rz(a)
        pet = leaf(1.45, 0.42, n=12, back=1.05)
        zf = (lambda x, y: zd + 0.30 - (x - 1.05) * 0.24)
        slope_plate(M, g, pet, zf, 'aeon_gold', thick=0.10, inlay='aeon_cream', isc=0.55, ih=0.02, R=R)
        p = R @ np.array([2.18, 0, 0])
        node(M, g, p[0], p[1], zf(2.18, 0) - 0.03, r=0.05)
        # crystal spike between petals
        b = R @ rz(22.5) @ np.array([2.05, 0, 0])
        M.add(g, tf(crystal(0.36, 0.08, tip=0.4), rz(a + 22.5) @ ry(38), (b[0], b[1], zp - 0.02)), 'aeon_crystal')
        M.add(g, cyl((b[0], b[1], zp - 0.02), (b[0], b[1], zp + 0.03), 0.12, n=10), 'aeon_gold')
    # crystal dome with gold ribs and lumen apex
    M.add(g, dome(0, 0, zd, 1.08, 0.78, n=48, lat=8), 'aeon_crystal')
    for i in range(8):
        a = math.radians(45 * i)
        pts = [(1.09 * math.cos(t) * math.cos(a), 1.09 * math.cos(t) * math.sin(a), zd + 0.78 * math.sin(t) + 0.005)
               for t in np.radians([2, 20, 38, 56, 72])]
        M.add(g, tube_path(pts, 0.035, n=6), 'aeon_gold')
    torus(M, g, 1.08, 0.05, zd + 0.02, 'aeon_gold', n=64, k=8)
    M.add(g, cyl((0, 0, zd + 0.74), (0, 0, zd + 0.82), 0.26, 0.20, n=20), 'aeon_gold')
    M.add(g, dome(0, 0, zd + 0.82, 0.16, 0.10, n=16, lat=3), 'lumen')
    torus(M, g, 0.62, 0.03, zd + 0.62, 'lumen', n=40, k=6)
    # corner pylons: crystal spires on gold-rimmed plinths, channels to the ring
    for k in range(4):
        a = 45 + 90 * k
        p = rz(a) @ np.array([4.05, 0, 0])
        M.add(g, rslab(circ(0.42, 32, p[0], p[1]), z1 - 0.02, z1 + 0.12, r=0.04), 'aeon_cream')
        M.add(g, annulus(0.42, 0.50, z1 - 0.02, z1 + 0.10, n=32, cx=p[0], cy=p[1]), 'aeon_gold')
        M.add(g, tf(crystal(0.95, 0.20, tip=0.35), None, (p[0], p[1], z1 + 0.10)), 'aeon_crystal')
        M.add(g, tf(crystal(0.62, 0.11, tip=0.35, phase=0.5), None, (p[0], p[1], z1 + 0.30)), 'lumen')
        for j in range(3):
            b = rz(a + 120 * j + 30) @ np.array([0.30, 0, 0])
            M.add(g, tf(crystal(0.45, 0.08, tip=0.4), rz(a + 120 * j + 30) @ ry(30), (p[0] + b[0], p[1] + b[1], z1 + 0.10)), 'aeon_crystal')
        channel(M, g, rot2([(3.55, 0), (3.02, 0)], a), z1, w=0.09)
        # side panels: filigree + nodes
        T = 90 * k
        for s in (-1, 1):
            inlay(M, g, rot2(arc_pts(3.10, 270 + s * 12, 270 + s * 33, 10), T), z1, w=0.045)
            q = rot2([(s * 1.20, -3.18)], T)[0]
            node(M, g, q[0], q[1], z1, r=0.055)
        M.add(g, tf(rslab(cham_rect(0.50, 0.14, 0.10, cy=-3.22), z1 - 0.02, z1 + 0.10, r=0.04), rz(T)), 'aeon_cream')
        M.add(g, tf(cbox(0, -3.22, z1 + 0.105, 0.70, 0.06, 0.01), rz(T)), 'lumen')
    return M


def export_pd(name, M, canvas, d=TUR):
    base, _ = layer(M, ['base'], canvas)
    head, _ = layer(M, ['head'], canvas)
    head = outline(head, r=2)
    save(base, d, f'{name}-base')
    save(head, d, name)
    f = over(base, head)
    save(f, d, f'{name}-full')
    FULL[name] = np.asarray(f)


def export_block(name, M, canvas, d, glow=None, glow_suffix='-glow', glow_tint=None, groups=('main',)):
    """main (+ white or tinted glow mask) + -full."""
    main, hm = layer(M, list(groups), canvas, heat=glow)
    save(main, d, name)
    if glow is not None:
        gs = heat_sprite(hm)
        save(tint(gs, glow_tint) if glow_tint else gs, d, f'{name}{glow_suffix}')
    save(main, d, f'{name}-full')
    FULL[name] = np.asarray(main)
    return main


def do_halo():
    M = halo()
    turret('halo', M, 192, 224, heat=heatmask({'lumen': 1.0, 'gglow': 0.8, 'aeon_crystal': 0.45}, ymin=1.05))
    print(f'halo               {tris(M)}  base 192 / body 224 px  emitter y={SPEC["halo"]:.2f} -> shootY {SPEC["halo"] * 8:.1f}', flush=True)


def do_qi():
    M = quantum_interceptor()
    export_pd('quantum-interceptor', M, 128)
    print(f'quantum-interceptor {tris(M)}  128 px', flush=True)


def do_aegis():
    M = aegis()
    export_block('aegis', M, 224, DEF, glow=heatmask({'lumen': 1.0, 'gglow': 0.9, 'aeon_crystal': 0.5}),
                 glow_suffix='-top', glow_tint='b8f5c4')
    print(f'aegis              {tris(M)}  224 px', flush=True)


# ================================================================== driver
def tris(M):
    return f'{M.ntri():6d} tris'


def do_tempest():
    M = tempest()
    turret('tempest', M, 256, 448, heat=heat_tempest, parts=True)
    my = SPEC['tempest'][0]
    print(f'tempest            {tris(M)}  base 256 / body 448 px  muzzle y={my:.3f} tiles -> shootY {my * 8:.1f}', flush=True)


JOBS = {'tempest': do_tempest, 'halo': do_halo, 'quantum-interceptor': do_qi, 'aegis': do_aegis}


def main(only=()):
    for name, fn in JOBS.items():
        if not only or name in only:
            fn()


if __name__ == '__main__':
    main(sys.argv[1:])
