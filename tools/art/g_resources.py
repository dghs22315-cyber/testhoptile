"""Art workstream g_resources: T1-T3 item icons, chlorine gas icon and the six ore overlays (all 32 px).

    .venv/bin/python tools/art/g_resources.py [name ...]     (no args = everything)

Items/liquid: one low-poly model each, rendered with rend.render_layer and exported like the T4 items
(outline '25262b', r=1). Ores: three scattered clusters per ore, no outline (v146 OreBlock.createIcons adds
its own 30% black drop shadow 3 px below every opaque pixel at load time).
"""
import math
import os
import sys

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from geom import box, cbox, cyl, loft, ring, rx, ry, rz, tf, clean, cham_rect, rect, prism, scale_poly  # noqa: E402
from hero import P  # noqa: E402
from mats import Model  # noqa: E402
from rend import render_layer, outline, add_material  # noqa: E402
from export import save, FULL, SS, REPO  # noqa: E402

# ---------------------------------------------------------------- materials (append-only)
add_material('rock_m', ['141317', '1e1c22', '2a272e', '38343c', '49444d', '5e5862'])      # matrix stone
add_material('fer_vein', ['4a1a0c', '6e2812', '963918', 'bc4e20', 'dc672a', 'f48c44'])    # bright rust vein
add_material('salt_rock', ['2a2622', '3a3530', '4c4640', '5f5850', '736b62', '898076'])   # saltpeter host rock
add_material('baux_mx', ['2a1008', '3e180b', '55210f', '6e2c14', '88391a', 'a14822'])     # lateritic clay
add_material('baux_pale', ['6a5038', '86684a', 'a2835e', 'bc9d74', 'd4b78c', 'eccfa6'])   # gibbsite specks
add_material('cob_hi', ['16305e', '1f4382', '2c5aa8', '3b74cc', '5592e8', '86b8ff'])      # bright cobalt facets
add_material('wolf_hi', ['121216', '1d1e24', '2b2d35', '41444f', '646a7a', '9aa2b6'])     # submetallic blades
add_material('neo_hi', ['4a1a3c', '6e2658', '963676', 'bc4a96', 'e064b8', 'ff96dc'])      # neodymite crystal
add_material('brass', ['3a2808', '5a3e0e', '7e5816', 'a4741e', 'c8952c', 'ecbc4c'])       # cartridge brass
add_material('magnet_red', ['3a0c10', '5c1218', '861a22', 'ae242e', 'd0343c', 'ee5a5c'])  # magnet paint
add_material('chlor_gas', ['1c3e10', '285a16', '357a1e', '449a28', '5ab836', '86d85a'])    # gas body
rng0 = np.random.default_rng


# ---------------------------------------------------------------- geometry helpers
def subdiv_until(T, emax):
    """Split triangles 1->4 until every edge is shorter than emax (coplanar, so shading is unchanged)."""
    T = np.asarray(T, float)
    done = []
    for _ in range(8):
        e = np.max(np.stack([np.linalg.norm(T[:, i] - T[:, (i + 1) % 3], axis=1) for i in range(3)]), 0)
        big = e > emax
        done.append(T[~big])
        T = T[big]
        if not len(T):
            break
        a, b, c = T[:, 0], T[:, 1], T[:, 2]
        ab, bc, ca = (a + b) / 2, (b + c) / 2, (c + a) / 2
        T = np.concatenate([np.stack(q, 1) for q in ((a, ab, ca), (ab, b, bc), (ca, bc, c), (ab, bc, ca))])
    done.append(T)
    return np.concatenate(done)


def paint(M, g, T, base, rules, emax=0.02):
    """Add T with per-sub-triangle materials: rules = [(fn(centroids) -> bool mask, mat)], later rules win.
    Only upward faces are subdivided (the rest is never seen from the top-down camera)."""
    T = clean(T)
    n = np.cross(T[:, 1] - T[:, 0], T[:, 2] - T[:, 0])
    n /= np.linalg.norm(n, axis=1, keepdims=True) + 1e-12
    up = np.abs(n[:, 2]) > 0.08
    M.add(g, T[~up], base)
    S = subdiv_until(T[up], emax)
    cen = S.mean(1)
    lab = np.array([base] * len(S), dtype=object)
    for fn, m in rules:
        lab[fn(cen)] = m
    for m in dict.fromkeys(lab):
        M.add(g, S[lab == m], m)


def loft3(rings):
    out = []
    for i in range(len(rings) - 1):
        out.append(loft(rings[i], rings[i + 1], cap_b=(i == 0), cap_t=(i == len(rings) - 2)))
    return np.concatenate(out)


def nugget(rng, r=0.16, h=0.14, n=7, ell=(1.0, 1.0), rot=0.0, mid=(0.5, 0.94), top=0.58, tilt=0.30, jit=0.22,
           at=(0.0, 0.0, 0.0), z0=0.0):
    """Faceted rock: base ring -> jittered shoulder ring -> flat (tilted) top facet. Returns triangles."""
    a0 = rng.uniform(0, 2 * math.pi)
    ang = a0 + (np.arange(n) + rng.uniform(-0.28, 0.28, n)) * 2 * math.pi / n
    rad = r * (1 + jit * rng.uniform(-1, 1, n))
    c, s = np.cos(ang), np.sin(ang)
    base = np.stack([rad * c * ell[0], rad * s * ell[1]], 1)
    R2 = np.array([[math.cos(rot), -math.sin(rot)], [math.sin(rot), math.cos(rot)]])
    base = base @ R2.T
    sh = base * (mid[1] * (1 + 0.06 * rng.uniform(-1, 1, n)))[:, None]
    zs = z0 + h * mid[0] * (1 + 0.25 * rng.uniform(-1, 1, n))
    off = rng.uniform(-0.12, 0.12, 2) * r
    tp = base * top + off
    gx, gy = rng.uniform(-1, 1, 2) * tilt * h / max(r, 1e-6)
    zt = z0 + h + gx * (tp[:, 0] - off[0]) + gy * (tp[:, 1] - off[1])
    rings = [np.column_stack([base, np.full(n, z0)]), np.column_stack([sh, zs]), np.column_stack([tp, zt])]
    return tf(loft3(rings), None, at)


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


def blade(L, w, t, cut=0.75):
    """Flat bladed crystal (wolframite habit): width along X, thickness along Y, grows along +Z, slanted tip."""
    poly = P([(-w, 0), (w, 0), (w, L * cut), (w * 0.15, L), (-w, L * (cut + 0.12))])
    return tf(prism(poly, -t / 2, t / 2, 0.80), rx(90))


def ellipsoid(c, rr, nlon=14, nlat=7, top_only=False):
    c = np.asarray(c, float)
    T = []
    l0 = 0 if not top_only else nlat // 2
    for i in range(l0, nlat):
        t0 = math.pi * i / nlat - math.pi / 2
        t1 = math.pi * (i + 1) / nlat - math.pi / 2
        for j in range(nlon):
            p0 = 2 * math.pi * j / nlon
            p1 = 2 * math.pi * (j + 1) / nlon

            def Q(t, p):
                return c + np.array([rr[0] * math.cos(t) * math.cos(p), rr[1] * math.cos(t) * math.sin(p), rr[2] * math.sin(t)])
            T.append([Q(t0, p0), Q(t0, p1), Q(t1, p1)])
            T.append([Q(t0, p0), Q(t1, p1), Q(t1, p0)])
    return clean(T)


def veins(rng, c, nv=2, w=0.014, wob=0.018, flat=0.5):
    """Bands where planes cut the rock (wobbled) -> thin mineral veins following the facets."""
    pl = []
    for _ in range(nv):
        n = rng.normal(size=3)
        n[2] *= flat
        n /= np.linalg.norm(n)
        pl.append((n, rng.uniform(-0.05, 0.05), rng.uniform(22, 40), rng.uniform(0, 6.3), rng.uniform(0.8, 1.3)))
    c = np.asarray(c, float)

    def f(Pc):
        q = Pc - c
        m = np.zeros(len(q), bool)
        for n, off, k, ph, ww in pl:
            d = q @ n - off + wob * np.sin(k * (q[:, 0] - 0.7 * q[:, 1]) + ph)
            m |= np.abs(d) < w * ww
        return m
    return f


def specks(rng, p):
    return lambda Pc: rng.random(len(Pc)) < p


def blobs(pts, rad):
    """Mask of centroids within any of the given discs (in XY)."""
    pts = np.asarray(pts, float)

    def f(Pc):
        d = np.min(np.linalg.norm(Pc[:, None, :2] - pts[None, :, :2], axis=2) - np.asarray(rad)[None], 1)
        return d < 0
    return f


def zabove(z):
    return lambda Pc: Pc[:, 2] > z


def chamfer_bar(hx, hy, h, ch=0.035, top_in=0.045):
    """Ingot-style bar: chamfered footprint, sloped sides, smaller top."""
    return prism(cham_rect(hx, hy, ch), 0, h, top_poly=cham_rect(hx - top_in, hy - top_in, ch * 0.8))


# ================================================================ raw ores (items)
def item_ferrolite():
    """Two angular haematite-rich boulders + a chip: rust-red body, bright rust veins, dark matrix pits, glints."""
    M = Model()
    rng = rng0(11)
    for (x, y, r, h, rot, n) in ((-0.07, -0.05, 0.25, 0.26, 0.3, 8), (0.16, 0.15, 0.15, 0.20, 1.4, 7), (-0.22, 0.22, 0.09, 0.12, 2.2, 6)):
        T = nugget(rng, r=r, h=h, n=n, rot=rot, ell=(1.0, 0.82), top=0.52, tilt=0.45, jit=0.18, at=(x, y, 0))
        paint(M, 'main', T, 'ore_fer', [(veins(rng, (x, y, h * 0.6), nv=2, w=0.013), 'fer_vein'),
                                       (specks(rng, 0.05), 'rock_m'), (specks(rng, 0.02), 'metal_light')], emax=0.022)
    return M


def item_saltpeter():
    """Druse of white prismatic nitre needles fanning out of a grey-brown host rock crusted with salt."""
    M = Model()
    rng = rng0(12)
    T = nugget(rng, r=0.27, h=0.12, n=8, ell=(1.0, 0.72), rot=-0.35, top=0.62, tilt=0.2, at=(0.0, -0.10, 0))
    paint(M, 'main', T, 'salt_rock', [(specks(rng, 0.10), 'ore_salt'), (veins(rng, (0, -0.1, 0.08), nv=1, w=0.012), 'ore_salt')])
    spec = ((-0.16, -0.08, 0.30, 0.050, -60, 40), (-0.06, -0.02, 0.42, 0.060, -25, 48), (0.06, -0.04, 0.40, 0.058, 15, 44),
            (0.17, -0.10, 0.30, 0.048, 55, 42), (0.0, -0.14, 0.26, 0.042, 180, 30), (-0.11, 0.02, 0.24, 0.038, -40, 62),
            (0.12, 0.02, 0.26, 0.040, 35, 60), (0.0, 0.04, 0.30, 0.045, 0, 64), (0.22, -0.20, 0.16, 0.034, 130, 50),
            (-0.22, -0.20, 0.17, 0.034, -130, 52))
    for (x, y, L, r, yaw, tilt) in spec:
        R = rz(yaw) @ rx(-tilt)
        M.add('main', tf(crystal(L, r, tip=0.26, taper=0.9, phase=0.3), R, (x, y, 0.06)), 'ore_salt')
    return M


def item_bauxite():
    """Lateritic clay lump studded with round pisoliths (orange-brown) and pale gibbsite specks."""
    M = Model()
    rng = rng0(13)
    T = nugget(rng, r=0.31, h=0.15, n=9, ell=(1.0, 0.86), rot=0.4, top=0.66, tilt=0.15, jit=0.12, at=(0, 0, 0))
    paint(M, 'main', T, 'baux_mx', [(specks(rng, 0.06), 'baux_pale')], emax=0.025)
    pis = ((-0.13, 0.06, 0.10), (0.05, 0.11, 0.085), (0.14, -0.03, 0.10), (-0.04, -0.12, 0.09), (0.17, 0.16, 0.06),
           (-0.21, -0.10, 0.06), (-0.01, 0.0, 0.075), (0.08, -0.17, 0.055), (-0.18, 0.18, 0.05), (0.23, -0.15, 0.045))
    for (x, y, r) in pis:
        z = 0.15 - 0.05 * (abs(x) + abs(y)) / 0.3
        M.add('main', ellipsoid((x, y, z - r * 0.35), (r, r * 0.95, r * 0.85), nlon=12, nlat=6), 'ore_baux')
    return M


def item_cobaltite():
    """Interlocked cobaltite cubes (pyritohedral habit) on a dark matrix: three-face lit cubes in cobalt blue."""
    M = Model()
    rng = rng0(14)
    T = nugget(rng, r=0.25, h=0.08, n=8, ell=(1.0, 0.8), rot=0.2, top=0.7, tilt=0.15, at=(0.0, -0.04, 0))
    paint(M, 'main', T, 'rock_m', [(specks(rng, 0.08), 'ore_cob')])
    cubes = ((-0.08, 0.02, 0.24, 20, 0.08), (0.14, 0.10, 0.17, 50, 0.07), (0.10, -0.15, 0.15, -15, 0.06),
             (-0.20, -0.14, 0.12, 35, 0.06), (-0.17, 0.20, 0.10, 65, 0.06), (0.24, -0.02, 0.09, 10, 0.05))
    for (x, y, s, yaw, z) in cubes:
        R = rz(yaw) @ rx(32) @ ry(38)
        Cb = tf(cbox(0, 0, 0, s, s, s), R, (x, y, z + s * 0.45))
        M.add('main', Cb, 'cob_hi')
    return M


def item_wolframite():
    """Fan of black submetallic wolframite blades with bright cleavage edges, set in a grey matrix."""
    M = Model()
    rng = rng0(15)
    T = nugget(rng, r=0.24, h=0.10, n=8, ell=(1.0, 0.8), rot=0.6, top=0.62, tilt=0.2, at=(-0.03, -0.10, 0))
    paint(M, 'main', T, 'ore_wolf', [(specks(rng, 0.06), 'metal_light'), (veins(rng, (0, -0.1, 0.06), nv=1), 'rock_m')])
    bl = ((-0.14, -0.08, 0.40, 0.085, -38, 55), (0.02, -0.06, 0.46, 0.095, 2, 50), (0.15, -0.10, 0.38, 0.08, 40, 58),
          (-0.04, -0.16, 0.26, 0.07, 160, 50), (0.24, -0.20, 0.20, 0.06, 80, 60))
    for (x, y, L, w, yaw, tilt) in bl:
        R = rz(yaw) @ rx(-tilt)
        M.add('main', tf(blade(L, w, 0.035), R, (x, y, 0.06)), 'wolf_hi')
    return M


def item_neodymite():
    """Split geode: dark rind, pale chalcedony band, cavity lined with magenta neodymite crystals."""
    M = Model()
    rng = rng0(16)
    n = 12
    a = np.arange(n) * 2 * math.pi / n + 0.2
    rr = 0.33 * (1 + 0.07 * rng.uniform(-1, 1, n))
    outer = np.stack([rr * np.cos(a), rr * 0.86 * np.sin(a)], 1)
    rim = outer * 0.93
    band = outer * 0.80
    inner = outer * 0.68
    z = 0.16
    M.add('main', loft3([np.column_stack([outer, np.zeros(n)]), np.column_stack([outer * 1.02, np.full(n, z * 0.55)]),
                         np.column_stack([rim, np.full(n, z)])]), 'rock_m')
    M.add('main', loft(np.column_stack([rim, np.full(n, z)]), np.column_stack([band, np.full(n, z - 0.004)]), False, False), 'cy_mid')
    M.add('main', loft(np.column_stack([band, np.full(n, z - 0.004)]), np.column_stack([inner, np.full(n, z - 0.03)]), False, False), 'baux_pale')
    M.add('main', loft(np.column_stack([inner, np.full(n, z - 0.03)]), np.column_stack([inner * 0.9, np.full(n, 0.03)]), False, True), 'magnet')
    for i in range(16):
        ang = rng.uniform(0, 2 * math.pi)
        d = rng.uniform(0.0, 0.17)
        x, y = d * math.cos(ang), d * 0.86 * math.sin(ang)
        L = rng.uniform(0.06, 0.11) * (1.2 - d * 2)
        R = rz(math.degrees(ang) + 90) @ rx(-(15 + d * 220))
        M.add('main', tf(crystal(L + 0.03, rng.uniform(0.028, 0.04), tip=0.55, sides=6), R, (x, y, 0.04 + 0.4 * d)), 'neo_hi')
    return M


# ================================================================ products
def item_steel():
    """Heavy rolled-steel billet: chamfered ingot, recessed stamping panel with raised bars, bright bevels."""
    M = Model()
    R = rz(28)
    hx, hy, h = 0.36, 0.20, 0.17
    M.add('main', tf(chamfer_bar(hx, hy, h - 0.03, ch=0.06, top_in=0.06), R), 'steel')
    th = h - 0.03
    ix, iy = hx - 0.06, hy - 0.06
    # raised frame around the recessed stamp panel
    fw = 0.045
    for (x0, x1, y0, y1) in ((-ix, ix, iy - fw, iy), (-ix, ix, -iy, -iy + fw), (-ix, -ix + fw, -iy, iy), (ix - fw, ix, -iy, iy)):
        M.add('main', tf(box(x0, x1, y0, y1, th, h), R), 'steel')
    M.add('main', tf(box(-0.17, 0.10, -0.03, 0.03, th, th + 0.025), R), 'metal_light')
    M.add('main', tf(box(0.15, 0.22, -0.08, 0.08, th, th + 0.025), R), 'metal_light')
    for (x, y) in ((-0.22, 0.07), (-0.22, -0.07)):
        M.add('main', tf(cyl((x, y, th), (x, y, th + 0.02), 0.022, n=8), R), 'hull_dark')
    return M


def item_charge():
    """Pair of modular propellant charges: combustible case, brass end rings, red igniter band, primer pad."""
    M = Model()
    for k, (dx, dy, L) in enumerate(((-0.13, -0.03, 0.66), (0.13, 0.05, 0.60))):
        R = rz(-22)
        r = 0.115
        y0, y1 = -L / 2, L / 2
        z = r + 0.01

        def C(a, b, rad, m, rad2=None, n=16):
            M.add('main', tf(cyl((dx, a, z), (dx, b, z), rad, rad2, n=n), R, (0, dy, 0)), m)
        C(y0 + 0.05, y1 - 0.07, r, 'charge')
        C(y0, y0 + 0.05, r * 1.06, 'brass')
        C(y1 - 0.07, y1 - 0.02, r * 1.06, 'brass')
        C(y1 - 0.02, y1 + 0.02, r * 0.9, r * 0.6, 'brass') if False else C(y1 - 0.02, y1 + 0.03, r * 0.86, 'brass', r * 0.55)
        C(-0.03, 0.03, r * 1.03, 'red_armor')
        C(y0 - 0.015, y0, r * 0.45, 'hull_dark')
        for yy in (y0 + 0.16, y1 - 0.18):
            C(yy, yy + 0.015, r * 1.01, 'yellow')
    return M


def item_aluminum():
    """Stack of rolled aluminium sheet: two flat sheets under a corrugated profile sheet, bright cut edges."""
    M = Model()
    for k, (rot, dx, dy) in enumerate(((-24, -0.03, -0.04), (-10, 0.02, 0.02))):
        z0 = 0.03 * k
        M.add('main', tf(prism(cham_rect(0.36, 0.25, 0.03), z0, z0 + 0.026), rz(rot), (dx, dy, 0)), 'alu')
    # corrugated top sheet: strips along x with sinusoidal height
    R = rz(-17)
    n = 9
    hy = 0.23
    xs = np.linspace(-0.34, 0.34, 2)
    z0 = 0.065
    prof = []
    for i in range(n * 4 + 1):
        y = -hy + 2 * hy * i / (n * 4)
        prof.append((y, z0 + 0.03 * (1 + math.sin(i / 4 * 2 * math.pi))))
    T = []
    for (y_a, z_a), (y_b, z_b) in zip(prof[:-1], prof[1:]):
        a0 = (xs[0], y_a, z_a); a1 = (xs[1], y_a, z_a); b0 = (xs[0], y_b, z_b); b1 = (xs[1], y_b, z_b)
        T += [[a0, a1, b1], [a0, b1, b0]]
        T += [[(xs[0], y_a, z0), (xs[0], y_a, z_a), (xs[0], y_b, z_b)], [(xs[0], y_a, z0), (xs[0], y_b, z_b), (xs[0], y_b, z0)]]
        T += [[(xs[1], y_a, z0), (xs[1], y_a, z_a), (xs[1], y_b, z_b)], [(xs[1], y_a, z0), (xs[1], y_b, z_b), (xs[1], y_b, z0)]]
    M.add('main', tf(np.array(T), R, (0.0, 0.03, 0)), 'alu')
    M.add('main', tf(box(0.20, 0.30, -0.25, -0.17, 0.09, 0.10), R, (0.0, 0.03, 0)), 'metal_light') if False else None
    return M


def item_cobalt_alloy():
    """Bullion stack of three cobalt-alloy bars (two below, one across), machined bright chamfers + stamp tag."""
    M = Model()
    R = rz(-30)
    for x in (-0.13, 0.13):
        M.add('main', tf(chamfer_bar(0.12, 0.34, 0.12, ch=0.03, top_in=0.03), R, (0, 0, 0)) + tf(np.zeros(3), R, (0, 0, 0)) * 0
              + np.array([0, 0, 0]), 'cobalt') if False else None
        M.add('main', tf(tf(chamfer_bar(0.12, 0.34, 0.12, ch=0.03, top_in=0.03), None, (x, 0, 0)), R), 'cobalt')
    top = tf(chamfer_bar(0.36, 0.12, 0.12, ch=0.03, top_in=0.03), None, (0, 0.02, 0.12))
    M.add('main', tf(top, R), 'cob_hi')
    M.add('main', tf(box(-0.16, 0.16, -0.035, 0.035, 0.24, 0.252), R, (0, 0, 0)), 'alu')
    for x in (-0.25, 0.25):
        M.add('main', tf(cyl((x, 0.02, 0.24), (x, 0.02, 0.255), 0.022, n=8), R), 'metal_light')
    return M


def item_tungsten_core():
    """APFSDS penetrator: long tungsten rod, ogive tip, segmented sabot collar, four tail fins."""
    M = Model()
    R = rz(-45)
    z = 0.10
    M.add('main', tf(cyl((0, -0.40, z), (0, 0.26, z), 0.055, n=12), R), 'tung')
    M.add('main', tf(cyl((0, 0.26, z), (0, 0.44, z), 0.055, 0.008, n=12), R), 'metal_light')
    M.add('main', tf(cyl((0, -0.06, z), (0, 0.14, z), 0.10, 0.10, n=14), R), 'brass')
    for y in (-0.06, 0.04, 0.12):
        M.add('main', tf(cyl((0, y, z), (0, y + 0.02, z), 0.106, n=14), R), 'hull_dark')
    for a in (0, 90, 180, 270):
        F = tf(prism(P([(0.04, -0.42), (0.16, -0.44), (0.16, -0.36), (0.04, -0.24)]), -0.012, 0.012), ry(a + 45))
        M.add('main', tf(F, R, (0, 0, z)), 'metal')
    M.add('main', tf(cyl((0, -0.44, z), (0, -0.40, z), 0.04, n=10), R), 'yellow')
    return M


def item_magnet():
    """Neodymium horseshoe: square-section red body, steel keeper poles with N/S marks, field sparks."""
    M = Model()
    R = rz(-30)
    Rr, w, hz = 0.20, 0.085, 0.11
    leg = 0.22
    cy0 = 0.04

    def sec(cx, cy, ang):
        # rectangular cross-section ring at a point of the centre line (ang = direction of travel)
        nx, ny = -math.sin(ang), math.cos(ang)  # unused; section in plane normal to travel
        return None
    pts = []
    for i in range(13):
        a = math.radians(180 - 180 * i / 12)
        pts.append((Rr * math.cos(a), cy0 + Rr * math.sin(a), a))
    path = [(-Rr, cy0 - leg, math.pi / 2)] + pts + [(Rr, cy0 - leg, -math.pi / 2)]
    rings = []
    for i, (x, y, a) in enumerate(path):
        if i == 0 or i == len(path) - 1:
            nx, ny = (1.0, 0.0)
        else:
            nx, ny = math.cos(a), math.sin(a)        # radial direction
        ro, ri = (x + nx * w, y + ny * w), (x - nx * w, y - ny * w)
        rings.append([(ro[0], ro[1], 0.0), (ro[0], ro[1], hz), (ri[0], ri[1], hz), (ri[0], ri[1], 0.0)])
    T = []
    for A, Bq in zip(rings[:-1], rings[1:]):
        for k in range(4):
            T += [[A[k], A[(k + 1) % 4], Bq[(k + 1) % 4]], [A[k], Bq[(k + 1) % 4], Bq[k]]]
    T = clean(T)
    M.add('main', tf(T, R), 'magnet_red')
    for s in (-1, 1):
        M.add('main', tf(box(s * Rr - w, s * Rr + w, cy0 - leg - 0.12, cy0 - leg, 0, hz + 0.005), R), 'metal_light')
        M.add('main', tf(box(s * Rr - w * 0.5, s * Rr + w * 0.5, cy0 - leg - 0.02, cy0 - leg + 0.005, hz, hz + 0.01), R), 'magnet' if s < 0 else 'hull_dark')
    for i, yy in enumerate((-0.18, -0.25, -0.32)):
        M.add('main', tf(box(-0.06, 0.06, cy0 + yy - 0.008, cy0 + yy + 0.008, 0.02, 0.03), R), 'pglow')
    return M


def liquid_chlorine():
    """Chlorine gas: cluster of greenish bubbles with glinting highlights (cf. liquid-nitrogen's drop)."""
    M = Model()
    for (x, y, r) in ((-0.05, -0.04, 0.24), (0.19, 0.17, 0.13), (-0.21, 0.22, 0.09), (0.22, -0.18, 0.07)):
        M.add('main', ellipsoid((x, y, 0.0), (r, r, r * 0.75), nlon=22, nlat=10, top_only=True), 'chlor_gas')
        M.add('main', ellipsoid((x - r * 0.38, y + r * 0.38, r * 0.62), (r * 0.18, r * 0.12, r * 0.06), nlon=10, nlat=4), 'gglow')
    return M


# ================================================================ ore overlays
def place(rng, n, rmin, rmax, lim=0.40, gap=0.035):
    out = []
    tries = 0
    while len(out) < n and tries < 4000:
        tries += 1
        r = rng.uniform(rmin, rmax)
        x, y = rng.uniform(-lim + r, lim - r, 2)
        if all(math.hypot(x - a, y - b) > r + c + gap for a, b, c in out):
            out.append((x, y, r))
    return out


def ore_chunks(kind, v):
    M = Model()
    rng = rng0(900 + 37 * v + 101 * ['ferrolite', 'saltpeter', 'bauxite', 'cobaltite', 'wolframite', 'neodymite'].index(kind))
    n = (5, 4, 6)[v]
    spots = place(rng, n, 0.07, 0.13)
    for k, (x, y, r) in enumerate(spots):
        if kind == 'ferrolite':
            T = nugget(rng, r=r, h=r * 0.9, n=7, rot=rng.uniform(0, 6), ell=(1, 0.85), top=0.5, tilt=0.4, at=(x, y, 0))
            paint(M, 'main', T, 'ore_fer', [(veins(rng, (x, y, r * 0.5), nv=1, w=0.012), 'fer_vein'), (specks(rng, 0.03), 'metal_light')])
        elif kind == 'saltpeter':
            M.add('main', nugget(rng, r=r * 0.8, h=r * 0.35, n=6, at=(x, y, 0)), 'salt_rock')
            for j in range(4):
                yaw = rng.uniform(0, 360)
                M.add('main', tf(crystal(r * rng.uniform(1.1, 1.6), r * 0.22, tip=0.3), rz(yaw) @ rx(-rng.uniform(30, 60)),
                                 (x + rng.uniform(-0.3, 0.3) * r, y + rng.uniform(-0.3, 0.3) * r, r * 0.2)), 'ore_salt')
        elif kind == 'bauxite':
            M.add('main', ellipsoid((x, y, 0), (r, r * 0.9, r * 0.6), nlon=12, nlat=6, top_only=True), 'ore_baux')
            M.add('main', ellipsoid((x - r * 0.2, y + r * 0.2, r * 0.45), (r * 0.35, r * 0.35, r * 0.25), nlon=10, nlat=5), 'baux_pale') if rng.random() < 0.3 else None
        elif kind == 'cobaltite':
            s = r * 1.15
            M.add('main', tf(cbox(0, 0, 0, s, s, s), rz(rng.uniform(0, 90)) @ rx(32) @ ry(38), (x, y, s * 0.4)), 'cob_hi')
        elif kind == 'wolframite':
            M.add('main', nugget(rng, r=r, h=r * 0.6, n=7, at=(x, y, 0)), 'ore_wolf')
            M.add('main', tf(blade(r * 1.4, r * 0.4, 0.02), rz(rng.uniform(0, 360)) @ rx(-55), (x, y, r * 0.3)), 'wolf_hi')
        elif kind == 'neodymite':
            for j in range(3):
                M.add('main', tf(crystal(r * rng.uniform(1.0, 1.7), r * 0.33, tip=0.45), rz(rng.uniform(0, 360)) @ rx(-rng.uniform(25, 60)),
                                 (x + rng.uniform(-0.3, 0.3) * r, y + rng.uniform(-0.3, 0.3) * r, 0.0)), 'neo_hi')
    return M


# ================================================================ driver
ITEMS = {'ferrolite': item_ferrolite, 'saltpeter': item_saltpeter, 'bauxite': item_bauxite, 'cobaltite': item_cobaltite,
         'wolframite': item_wolframite, 'neodymite': item_neodymite, 'steel': item_steel, 'charge': item_charge,
         'aluminum': item_aluminum, 'cobalt-alloy': item_cobalt_alloy, 'tungsten-core': item_tungsten_core, 'magnet': item_magnet}
ORES = ['ferrolite', 'saltpeter', 'bauxite', 'cobaltite', 'wolframite', 'neodymite']
BUILD = os.path.join(REPO, 'build', 'g_resources')


def render_icon(M):
    a, _ = render_layer(M, ['main'], ['main'], 32, SS)
    return outline(a, '25262b', r=1)


def preview(keys, fn, k=4):
    """x4 sheet; ore overlays are shown on a dark and a light floor."""
    ims = [(n, FULL[n]) for n in keys if n in FULL]
    c = 32 * k + 20
    cols = 9
    rows = (len(ims) + cols - 1) // cols
    bg = Image.new('RGB', (cols * c + 20, rows * (c + 14) + 20), (54, 57, 64))
    d = ImageDraw.Draw(bg)
    for i, (n, a) in enumerate(ims):
        r, cc = divmod(i, cols)
        x, y = 20 + cc * c, 20 + r * (c + 14)
        im = Image.fromarray(a).resize((32 * k, 32 * k), Image.NEAREST)
        if n.startswith('ore-'):
            d.rectangle([x, y, x + 32 * k - 1, y + 32 * k - 1], fill=(46, 44, 50) if i % 2 == 0 else (156, 146, 128))
        bg.paste(im, (x, y), im)
        d.text((x, y + 32 * k + 1), n, fill=(220, 220, 225))
    os.makedirs(BUILD, exist_ok=True)
    out = os.path.join(BUILD, fn)
    bg.save(out)
    return out


def main(only=()):
    def want(n):
        return not only or n in only
    for name, fn in ITEMS.items():
        if not want(name):
            continue
        M = fn()
        a = render_icon(M)
        save(a, 'items', name)
        FULL[name] = np.asarray(a)
        print(f'items/{name:16s} {M.ntri():6d} tris')
    if want('chlorine'):
        M = liquid_chlorine()
        a = render_icon(M)
        save(a, 'liquids', 'chlorine')
        FULL['chlorine'] = np.asarray(a)
        print(f'liquids/chlorine        {M.ntri():6d} tris')
    for ore in ORES:
        if not want(ore) and not want('ore-' + ore):
            continue
        for v in range(3):
            M = ore_chunks(ore, v)
            a, _ = render_layer(M, ['main'], ['main'], 32, SS)
            save(a, 'blocks/ores', f'ore-{ore}{v + 1}')
            FULL[f'ore-{ore}{v + 1}'] = np.asarray(a)
            print(f'blocks/ores/ore-{ore}{v + 1:<4d} {M.ntri():6d} tris')
    keys = list(ITEMS) + ['chlorine'] + [f'ore-{o}{v}' for o in ORES for v in (1, 2, 3)]
    print(preview(keys, 'preview-x4.png'))


if __name__ == '__main__':
    main(tuple(sys.argv[1:]))
