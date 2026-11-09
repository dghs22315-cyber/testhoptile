"""v1.2 in-game style clip: long-range artillery shot across a 160x90 tile map.
Simulates mod logic: rotateSpeed 1.6, warmup 0.06, charge 40 ticks, reload 100, shell 5 wu/tick,
shrinkX 0.55 / shrinkY 0.7 (shell grows at the top of the arc), script shadow + impact marker + whistle."""
import numpy as np, math, random, os, subprocess, wave, shutil
from PIL import Image, ImageDraw, ImageFont, ImageFilter

S = '/data/cybran/out/sprites/cybran-lra'
OUT = '/data/cybran/out'; FR = f'{OUT}/vid'
shutil.rmtree(FR, ignore_errors=True); os.makedirs(FR)
def L(n): return Image.open(f'{S}{n}.png').convert('RGBA')
base, body, bo = L('-base'), L(''), L('-outline')
bar, baro = L('-barrel'), L('-barrel-outline')
wl, wlo, wr, wro = L('-wingl'), L('-wingl-outline'), L('-wingr'), L('-wingr-outline')
heat, bheat, prev = L('-heat'), L('-barrel-heat'), L('-preview')
coil = Image.open('/data/mod/cybran-arsenal/sprites/blocks/turrets/cybran-lra/cybran-lra-coil-heat.png').convert('RGBA')
C = body.size[0]

OW, OH = 1024, 576
WT, HT = 160, 90; WW, WH = WT*32, HT*32
rng = np.random.default_rng(3); random.seed(5)

# ================================================================ floor (numpy)
yy, xx = np.mgrid[0:HT, 0:WT]
nz = np.array(Image.fromarray((np.random.default_rng(4).random((HT//6+2, WT//6+2))*255).astype(np.uint8)).resize((WT, HT), Image.BICUBIC)).astype(float)/255
kind = np.zeros((HT, WT), np.int8)
kind[nz > 0.58] = 1
kind[(xx > 85) & (nz > 0.42)] = 1
rc = 62 + 7*np.sin(yy/11.0) + 3*np.sin(yy/4.3 + 1.0)
dr = np.abs(xx - rc)
kind[(dr >= 6.5) & (dr < 8.0)] = 6
kind[dr < 6.5] = 4
kind[dr < 4.0] = 5
kind[(xx < 24) & (yy >= 46) & (yy < 72)] = 2
kind[(xx >= 106) & (xx < 140) & (yy >= 3) & (yy < 34)] = 3
PAL = {0: [(98, 94, 90), (92, 88, 84), (104, 100, 95)],
       1: [(74, 66, 62), (69, 61, 57), (79, 71, 66)],
       2: [(82, 85, 94), (77, 80, 89), (88, 91, 100)],
       3: [(62, 60, 70), (58, 56, 66), (67, 65, 75)],
       4: [(70, 104, 150), (66, 100, 146), (74, 108, 154)],
       5: [(44, 66, 122), (42, 63, 118), (46, 69, 126)],
       6: [(150, 134, 110), (144, 128, 104), (156, 140, 116)]}
col = np.zeros((HT, WT, 3), np.int16)
pick = rng.choice([0, 0, 0, 1, 2], size=(HT, WT))
for k, p in PAL.items():
    p = np.array(p, np.int16); m = kind == k
    col[m] = p[pick[m]]
img = np.repeat(np.repeat(col, 32, 0), 32, 1)
Kd = np.repeat(np.repeat(kind, 32, 0), 32, 1)
natural = (Kd == 0) | (Kd == 1) | (Kd == 6)
img += rng.integers(-4, 5, size=(WH, WW, 1), dtype=np.int16) * natural[..., None]
img[(Kd == 1) & (rng.random((WH, WW), dtype=np.float32) < 0.02)] -= 12
ly = (np.arange(WH) % 32)[:, None]; lx = (np.arange(WW) % 32)[None, :]
metal = (Kd == 2) | (Kd == 3)
img[metal & ((lx == 0) | (ly == 0))] += 14
img[metal & ((lx == 31) | (ly == 31))] -= 20
img[metal & ((lx == 3) | (lx == 28)) & ((ly == 3) | (ly == 28))] -= 20
Xg = np.arange(WW, dtype=np.float32)[None, :]; Yg = np.arange(WH, dtype=np.float32)[:, None]
wv = (np.sin(Xg*0.045 + Yg*0.09) * np.sin(Yg*0.031 - Xg*0.012)) > 0.8
img[((Kd == 4) | (Kd == 5)) & wv] += 16
floor = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8)).convert('RGBA')
del img, Kd, natural, metal, wv
fd = ImageDraw.Draw(floor)
r = random.Random(11)
for _ in range(28):   # copper / lead ore
    cx, cy = r.randint(26, 104), r.randint(3, 86); ore = r.choice([((196, 122, 84), (232, 160, 112), (140, 84, 60)), ((140, 120, 160), (176, 156, 196), (100, 84, 120))])
    for _ in range(r.randint(5, 12)):
        tx, ty = cx + r.randint(-2, 2), cy + r.randint(-2, 2)
        if not (0 <= tx < WT and 0 <= ty < HT) or kind[ty, tx] not in (0, 1): continue
        x, y = tx*32, ty*32
        for _ in range(3):
            bx, by = x + r.randint(3, 22), y + r.randint(3, 22); s = r.randint(4, 7)
            fd.rectangle([bx, by, bx+s, by+s], fill=ore[0]+(255,))
            fd.rectangle([bx, by, bx+s-2, by+1], fill=ore[1]+(255,))
            fd.rectangle([bx+s-1, by+1, bx+s, by+s], fill=ore[2]+(255,))
for _ in range(170):  # boulders
    tx, ty = r.randint(0, WT-1), r.randint(0, HT-1)
    if kind[ty, tx] not in (0, 1, 6): continue
    x, y = tx*32 + r.randint(4, 20), ty*32 + r.randint(4, 20); s = r.randint(8, 14)
    fd.ellipse([x, y+2, x+s, y+s+2], fill=(40, 38, 38, 140))
    fd.ellipse([x, y, x+s, y+s], fill=(118, 112, 106, 255))
    fd.ellipse([x+2, y+1, x+s-4, y+s-5], fill=(140, 134, 127, 255))

# ================================================================ blocks
TEAM = (162, 124, 229); OURS = (255, 211, 127)
def wall(d, tx, ty, kind_):
    x, y = tx*32, ty*32
    if kind_ == 'cw':
        c0, c1, hi, lo, mid = (146, 98, 72), (176, 120, 88), (205, 150, 112), (118, 78, 58), (132, 88, 64)
    else:
        c0, c1, hi, lo, mid = (98, 106, 124), (138, 148, 168), (176, 186, 204), (84, 90, 106), (112, 120, 138)
    d.rectangle([x+1, y+1, x+30, y+30], fill=c0+(255,))
    d.rectangle([x+3, y+3, x+28, y+28], fill=c1+(255,))
    d.line([x+3, y+3, x+28, y+3], fill=hi+(255,)); d.line([x+3, y+3, x+3, y+28], fill=hi+(255,))
    d.line([x+3, y+28, x+28, y+28], fill=lo+(255,)); d.line([x+28, y+3, x+28, y+28], fill=lo+(255,))
    d.rectangle([x+12, y+12, x+19, y+19], fill=mid+(255,))
def eturret(d, tx, ty):
    x, y = tx*32, ty*32
    d.rectangle([x+2, y+2, x+61, y+61], fill=(70, 72, 82, 255))
    d.rectangle([x+6, y+6, x+57, y+57], fill=(96, 98, 110, 255))
    d.rectangle([x+6, y+6, x+57, y+9], fill=TEAM+(255,)); d.rectangle([x+6, y+54, x+57, y+57], fill=TEAM+(255,))
    d.ellipse([x+16, y+16, x+47, y+47], fill=(120, 122, 136, 255), outline=(60, 62, 70, 255), width=2)
    d.rectangle([x+27, y+0, x+36, y+30], fill=(140, 142, 156, 255), outline=(60, 62, 70, 255))
    d.ellipse([x+26, y+26, x+37, y+37], fill=TEAM+(255,))
def ecore(d, tx, ty):
    x, y = tx*32, ty*32
    d.rectangle([x+1, y+1, x+94, y+94], fill=(64, 62, 74, 255))
    d.rectangle([x+6, y+6, x+89, y+89], fill=(92, 90, 104, 255))
    for k in range(4):
        d.rectangle([x+6+k*0, y+6, x+89, y+11], fill=TEAM+(255,))
    d.rectangle([x+6, y+84, x+89, y+89], fill=TEAM+(255,))
    d.rectangle([x+30, y+30, x+65, y+65], fill=(120, 116, 136, 255), outline=(50, 48, 58, 255), width=2)
    d.rectangle([x+40, y+40, x+55, y+55], fill=TEAM+(255,))

TT = (122, 18)                       # target enemy turret (2x2)
TARGET = (TT[0]*32+32, TT[1]*32+32)
blocks = [('cw', 15, y) for y in range(53, 64)] + [('cw', 16, y) for y in (55, 56, 60, 61)]
blocks += [('tw', 108, y) for y in range(4, 34) if y not in (19, 20)]
blocks += [('tw', 109, y) for y in range(8, 30, 3)]
for x in range(120, 126):
    for y in range(16, 22):
        if x in (120, 125) or y in (16, 21): blocks.append(('tw', x, y))
blocks += [('t', TT[0], TT[1]), ('t', 129, 25), ('t', 116, 9), ('t', 115, 26), ('core', 130, 8)]
blocks += [('tw', x, 24) for x in range(127, 133)] + [('tw', 114, y) for y in range(7, 13)] + [('tw', 113, y) for y in range(24, 30)]
def destroyed(k, tx, ty):
    if k == 't': return (tx, ty) == TT
    if k in ('cw', 'tw'): return math.hypot(tx+0.5 - (TT[0]+1), ty+0.5 - (TT[1]+1)) <= 3.2
    return False

def make_world(dead):
    im = floor.copy()
    if dead:   # scorch mark
        R = 150; yy2, xx2 = np.mgrid[-R:R, -R:R]
        rr = np.hypot(xx2, yy2)/R
        nz2 = np.random.default_rng(8).random((2*R, 2*R))
        a = np.clip(1 - rr, 0, 1)**0.7 * (0.75 + 0.25*nz2) * 0.8
        sc = np.zeros((2*R, 2*R, 4), np.uint8); sc[..., :3] = (30, 24, 24); sc[..., 3] = (a*255).astype(np.uint8)
        sc = Image.fromarray(sc).filter(ImageFilter.GaussianBlur(2))
        im.alpha_composite(sc, (TARGET[0]-R, TARGET[1]-R))
    d = ImageDraw.Draw(im)
    rr_ = random.Random(9)
    for k, tx, ty in blocks:
        if dead and destroyed(k, tx, ty):
            s = 64 if k == 't' else 32; x, y = tx*32, ty*32
            for _ in range(14 if s == 64 else 6):
                cx, cy = x+rr_.randint(2, s-3), y+rr_.randint(2, s-3); q = rr_.randint(2, 6 if s == 64 else 4)
                d.ellipse([cx-q, cy-q, cx+q, cy+q], fill=(38, 34, 34, 220))
            for _ in range(10 if s == 64 else 4):
                cx, cy = x+rr_.randint(2, s-3), y+rr_.randint(2, s-3)
                d.rectangle([cx, cy, cx+rr_.randint(1, 3), cy+rr_.randint(1, 2)], fill=(110, 104, 112, 255))
            continue
        if k == 't': eturret(d, tx, ty)
        elif k == 'core': ecore(d, tx, ty)
        else: wall(d, tx, ty, k)
    return im
world_alive = make_world(False); world_dead = make_world(True)
print('world ok')

# ================================================================ turret head
def shift(im, dx, dy):
    out = Image.new('RGBA', im.size); out.alpha_composite(im, (dx, dy)) if dx >= 0 and dy >= 0 else out.paste(im, (dx, dy), im); return out
def additive(dst, h_im, color, k):
    if k <= 0.003: return dst
    d = np.array(dst).astype(float); h = np.array(h_im).astype(float)
    a = h[..., 3:4]/255.0*k
    d[..., :3] = np.clip(d[..., :3] + a*np.array(color), 0, 255)
    return Image.fromarray(d.astype(np.uint8))
def head(warm, recoil, heat_k, charge):
    wx = round(1.2*4*warm); wy = round(0.5*4*warm); ry = round(3.5*4*recoil)
    c = Image.new('RGBA', (C, C))
    for im, sx in ((wlo, -wx), (wro, wx), (wl, -wx), (wr, wx)):
        c.alpha_composite(shift(im, sx, wy))
    c.alpha_composite(bo); c.alpha_composite(body)
    c = additive(c, heat, (255, 58, 79), heat_k)
    c.alpha_composite(shift(baro, 0, ry)); c.alpha_composite(shift(bar, 0, ry))
    c = additive(c, shift(bheat, 0, ry), (255, 58, 79), heat_k)
    c = additive(c, shift(coil, 0, ry), (255, 42, 69), charge)
    return c

TUR = (10*32+16, 58*32+16)
shadow = np.array(prev); shadow[..., :3] = 0; shadow[..., 3] = (shadow[..., 3] > 0)*56; shadow = Image.fromarray(shadow)
PS = prev.size[0]

# ================================================================ simulation (60 ticks/s)
dx, dy = TARGET[0]-TUR[0], TARGET[1]-TUR[1]
AIM = -math.degrees(math.atan2(dx, -dy))
TICKS = 560
CHARGES = [56, 156]; SHOTS = [c+40 for c in CHARGES]
state = []
rot, warm, rec, ht = 0.0, 0.0, 0.0, 0.0
for t in range(TICKS+1):
    diff = AIM-rot; rot += max(-1.6, min(1.6, diff))
    warm += ((1 if t < 420 else 0)-warm)*0.06
    if t in SHOTS: rec, ht = 1.0, 1.0
    else: rec = max(0.0, rec-1/100); ht = max(0.0, ht-1/90)
    ch = 0.0
    for c in CHARGES:
        if c <= t < c+40: ch = (t-c)/40
    state.append(dict(rot=rot, warm=warm, rec=rec, heat=ht, charge=ch))
def muzzle(t, extra=0.0):
    s = state[t]; a = math.radians(-s['rot'])
    rr = (26 - 1.0*s['rec']**1.8 - 3.5*s['rec'] + extra)*4
    return TUR[0] + math.sin(a)*rr, TUR[1] - math.cos(a)*rr, a
MZ = [muzzle(s) for s in SHOTS]
FLIGHT = int(round(math.hypot(TARGET[0]-MZ[0][0], TARGET[1]-MZ[0][1])/4/5))
HITS = [s+FLIGHT for s in SHOTS]; DESTROY = HITS[1]
DIST_TILES = math.hypot(dx, dy)/32
print('aim', AIM, 'dist tiles', DIST_TILES, 'flight', FLIGHT, 'shots', SHOTS, 'hits', HITS)
def shell(i, tt):
    s = SHOTS[i]; mx, my, _ = MZ[i]; f = (tt-s)/FLIGHT
    return mx + (TARGET[0]-mx)*f, my + (TARGET[1]-my)*f, f

# ================================================================ camera
def sm(x): x = max(0.0, min(1.0, x)); return x*x*(3-2*x)
def lerp(a, b, f): return a + (b-a)*f
def zl(z0, z1, f): return math.exp(lerp(math.log(z0), math.log(z1), f))
HOLD = (TARGET[0]-70, TARGET[1]+16); WC = (WW/2, WH/2)
START = (TUR[0]+70, TUR[1]-28)
def cam(t):
    T0, H0 = SHOTS[0], HITS[0]
    if t < T0:
        cx, cy = START; z = zl(2.3, 2.0, sm(t/T0))
    elif t < H0:
        u = (t-T0)/FLIGHT; sx, sy, _ = shell(0, t)
        a = sm(u/0.1); b = sm((u-0.55)/0.4)
        cx = lerp(lerp(START[0], sx, a), HOLD[0], b); cy = lerp(lerp(START[1], sy, a), HOLD[1], b)
        z = zl(2.0, 0.42, sm(u/0.4)) if u < 0.6 else zl(0.42, 1.3, sm((u-0.6)/0.4))
    elif t < 420:
        cx, cy = HOLD; z = zl(1.3, 1.12, (t-H0)/(420-H0))
    else:
        f = sm((t-420)/90); cx, cy = lerp(HOLD[0], WC[0], f), lerp(HOLD[1], WC[1], f); z = zl(1.12, 0.2, f)
    hw, hh = OW/2/z, OH/2/z
    cx = min(max(cx, hw), WW-hw); cy = min(max(cy, hh), WH-hh)
    return cx, cy, z
SHAKES = [(SHOTS[0], 4.0, 20), (SHOTS[1], 1.0, 14), (HITS[0], 3.0, 18), (HITS[1], 5.0, 28)]
def shake_at(t):
    amp = 0.0
    for s0, i, dur in SHAKES:
        if s0 <= t < s0+dur: amp = max(amp, i*(1-(t-s0)/dur))
    q = random.Random(t*7919)
    return q.uniform(-amp, amp)*2, q.uniform(-amp, amp)*2   # sprite px

# ================================================================ effects (screen space)
def hexa(h, a=1.0):
    h = h.lstrip('#'); c = tuple(int(h[i:i+2], 16) for i in (0, 2, 4))
    return c + (int(255*max(0, min(1, a))),)
def lerpc(c0, c1, f):
    a, b = hexa(c0), hexa(c1)
    return tuple(int(a[i]+(b[i]-a[i])*f) for i in range(3))
def circ(d, x, y, r, col):
    if r <= 0.3: return
    d.ellipse([x-r, y-r, x+r, y+r], fill=col)
def ring(d, x, y, r, w, col):
    if r <= 0.5 or w <= 0.3: return
    d.ellipse([x-r, y-r, x+r, y+r], outline=col, width=max(1, int(round(w))))
def seg(d, x0, y0, x1, y1, w, col):
    if w <= 0.3: return
    d.line([x0, y0, x1, y1], fill=col, width=max(1, int(round(w))))
def wrand(seed): return random.Random(seed)
RB = 1.5   # explosion scale (splash x1.5)
SPLASH = 60

def fx_layer(t, cx, cy, z):
    lay = Image.new('RGBA', (OW, OH)); d = ImageDraw.Draw(lay, 'RGBA')
    PX = 4*z
    def P(x, y): return (x-cx)*z + OW/2, (y-cy)*z + OH/2
    # charge
    for c in CHARGES:
        if c <= t < c+40:
            fin = (t-c)/40; mx, my, a = muzzle(t); X, Y = P(mx, my); q = wrand(c)
            for i in range(14):
                ang = q.uniform(0, 2*math.pi); l = (22 - 22*fin)*q.random()
                circ(d, X+math.cos(ang)*l*PX, Y+math.sin(ang)*l*PX, (0.6+1.6*fin)*PX, lerpc('ffd6dc', 'ff3355', fin)+(230,))
            ring(d, X, Y, (18-16*fin)*PX, (0.4+2.0*fin)*PX, hexa('ff3355', fin))
    # muzzle flash, smoke, casings
    for i, s in enumerate(SHOTS):
        e = t-s; mx, my, a = MZ[i]; X, Y = P(mx, my)
        if 0 <= e < 70:
            q = wrand(s*3); fin = e/70
            for k in range(12):
                ang = a + math.radians(q.uniform(-30, 30)); l = (4 + 30*fin)*q.random()
                circ(d, X+math.sin(ang)*l*PX, Y-math.cos(ang)*l*PX, 5.5*(1-fin)*PX, lerpc('6a5a5f', '3a3035', fin)+(int(200*(1-fin*0.6)),))
        if 0 <= e < 18:
            fin = e/18; q = wrand(s*5)
            for k in range(11):
                ang = a + math.radians(q.uniform(-22, 22)); l = (2 + 30*fin)*q.random()
                ln = 11 - 8*fin; x0, y0 = X+math.sin(ang)*l*PX, Y-math.cos(ang)*l*PX
                seg(d, x0, y0, x0+math.sin(ang)*ln*PX, y0-math.cos(ang)*ln*PX, (2.2-2*fin)*PX, lerpc('ffd6dc', 'ff3355', fin)+(255,))
            if e < 14:
                f2 = e/14; ring(d, X, Y, (2+18*f2)*PX, (3-3*f2)*PX, lerpc('ffd6dc', 'ff3355', f2)+(255,))
            if e < 5: circ(d, X, Y, (7-e)*PX*0.9, (255, 235, 238, 230))
        if 0 <= e < 40:
            fin = e/40; sr = state[s]['rot']; aa = math.radians(-sr)
            ccx, ccy = TUR[0]-math.sin(aa)*3*4, TUR[1]+math.cos(aa)*3*4
            for sgn in (-1, 1):
                ln = (2 + (1-(1-fin)**2)*10)*sgn*4; lr = aa + math.pi/2 + math.radians(fin*20*sgn)
                Xc, Yc = P(ccx + math.sin(lr)*ln, ccy - math.cos(lr)*ln)
                colc = lerpc('ffd37f', 'a0a0a8', fin) + (int(255*min(1, (1-fin)*2)),)
                ang = lr + math.radians(fin*50*sgn); hw, hh = 1.25*PX, 2*PX
                pts = [(Xc + px*math.cos(ang) - py*math.sin(ang), Yc + px*math.sin(ang) + py*math.cos(ang)) for px, py in ((-hw, -hh), (hw, -hh), (hw, hh), (-hw, hh))]
                d.polygon(pts, fill=colc)
    # shells
    for i, (s, h) in enumerate(zip(SHOTS, HITS)):
        if not (s <= t < h): continue
        x, y, f = shell(i, t); sl = 1 - abs(2*f - 1); fout = 1 - f
        mx, my, _ = MZ[i]; ang = math.atan2(TARGET[1]-my, TARGET[0]-mx)
        # ground shadow (script)
        hgt = sl*16*4
        X, Y = P(x - hgt*0.9, y + hgt); circ(d, X, Y, (2.2 + 2.8*sl)*PX, (0, 0, 0, int(255*(0.28+0.3*sl))))
        # artilleryTrail puffs
        for tt in range(s, t, 3):
            px_, py_, ff = shell(i, tt); age = (t-tt)/50
            if age < 1:
                s2 = 1 - abs(2*ff - 1); X, Y = P(px_, py_); circ(d, X, Y, 4*s2*(1-age)*PX + 0.6, hexa('a82a38', 0.7))
        pts = [shell(i, max(s, t-k)) for k in range(10)]
        for k in range(9):
            X0, Y0 = P(pts[k][0], pts[k][1]); X1, Y1 = P(pts[k+1][0], pts[k+1][1])
            seg(d, X0, Y0, X1, Y1, 2.4*(1-k/9)*PX*(0.6+0.8*sl), hexa('ff3355', 0.9))
        Wd = 17*(0.45 + 0.55*sl); Hd = 21*(0.3 + 0.7*sl)
        X, Y = P(x, y)
        circ(d, X, Y, Hd*0.75*PX, (255, 51, 85, 40))
        for (kw, kh, colr) in ((0.42, 0.48, 'a82a38'), (0.27, 0.33, 'ff8f9a')):
            hw, hh = Wd*kw*PX, Hd*kh*PX; poly = []
            for k in range(18):
                th = 2*math.pi*k/18; ex, ey = hh*math.cos(th), hw*math.sin(th)
                poly.append((X + ex*math.cos(ang) - ey*math.sin(ang), Y + ex*math.sin(ang) + ey*math.cos(ang)))
            d.polygon(poly, fill=hexa(colr))
        # impact marker (script)
        Xt, Yt = P(*TARGET); rr = max(8, SPLASH)*(0.4 + 0.6*fout)*PX
        al = 0.35 + 0.45*abs(math.sin(t/3))
        ring(d, Xt, Yt, rr, max(1.3*PX, 1.5), hexa('ff3355', al))
        for k in range(4):
            a2 = math.radians(k*90 + 45); r0 = rr*0.55
            seg(d, Xt + math.cos(a2)*r0, Yt + math.sin(a2)*r0, Xt + math.cos(a2)*(r0+rr*0.3), Yt + math.sin(a2)*(r0+rr*0.3), max(1.3*PX, 1.5), hexa('ff3355', al))
        circ(d, Xt, Yt, max(1.3*PX, 1.5), hexa('ff3355', 0.7))
    # explosions
    for i, h in enumerate(HITS):
        big = (i == 1); e = t-h; life = 34 if big else 30
        if 0 <= e < life + (40 if big else 0):
            X, Y = P(*TARGET); fin = min(1, e/life); fout = 1-fin; finpow = 1-(1-fin)**3; q = wrand(h)
            if e < life:
                if e < 10:
                    f9 = e/10; ring(d, X, Y, (38+8*big)*RB*f9*PX, 5*(1-f9)*PX, hexa('ff3355'))
                for k in range(14 if big else 11):
                    ang = q.uniform(0, 2*math.pi); l = (2 + (34+6*big)*RB*finpow)*q.random()
                    circ(d, X+math.cos(ang)*l*PX, Y+math.sin(ang)*l*PX, (fout*6+0.5)*PX, hexa('5a1a22', 0.85))
                for k in range(16 if big else 12):
                    ang = q.uniform(0, 2*math.pi); l = (1 + (43+6*big)*RB*finpow)*q.random()
                    x0, y0 = X+math.cos(ang)*l*PX, Y+math.sin(ang)*l*PX; ln = (1+fout*6)*PX
                    seg(d, x0, y0, x0+math.cos(ang)*ln, y0+math.sin(ang)*ln, 1.8*fout*PX, hexa('ff8a96'))
                if e < 6: circ(d, X, Y, (9-1.4*e)*PX*(1.25 if big else 1), (255, 214, 220, int(170*(1-e/6))))
            if big:
                f2 = e/(life+40)
                for k in range(18):
                    ang = q.uniform(0, 2*math.pi); l = (4 + 40*(1-(1-f2)**2))*q.uniform(0.3, 1)
                    circ(d, X+math.cos(ang)*l*PX, Y+math.sin(ang)*l*PX - f2*6*PX, (4*(1-f2)+0.5)*PX, (70, 64, 66, int(170*(1-f2))))
    if t > DESTROY:
        q = wrand(77)
        for k in range(6):
            fx_, fy_ = TARGET[0]+q.uniform(-48, 48), TARGET[1]+q.uniform(-40, 40)
            ph = t*0.35 + k*1.7; X, Y = P(fx_, fy_); fl = 0.6+0.4*math.sin(ph*3.1)
            circ(d, X, Y, 2.2*fl*PX, (255, 120, 60, 150)); circ(d, X, Y, 1.1*fl*PX, (255, 210, 120, 200))
            smk = ((t + k*13) % 40)/40
            circ(d, X+smk*3*PX, Y-smk*12*PX, (1.5+2.5*smk)*PX, (60, 56, 58, int(120*(1-smk))))
    return lay, P

# ================================================================ frames
font = ImageFont.truetype('/usr/share/fonts/liberation-sans/LiberationSans-Bold.ttf', 22)
font2 = ImageFont.truetype('/usr/share/fonts/liberation-sans/LiberationSans-Regular.ttf', 16)
font3 = ImageFont.truetype('/usr/share/fonts/liberation-sans/LiberationSans-Bold.ttf', 20)
def dashed(d, X, Y, R, col, w, step=3.0, on=1.8):
    a = 0.0
    while a < 360:
        d.arc([X-R, Y-R, X+R, Y+R], a, a+on, fill=col, width=w); a += step
def label(d, x, y, text, fnt, fg, anchor='la'):
    bb = d.textbbox((x, y), text, font=fnt, anchor=anchor)
    d.rectangle([bb[0]-6, bb[1]-4, bb[2]+6, bb[3]+4], fill=(14, 12, 16, 175))
    d.text((x, y), text, font=fnt, fill=fg, anchor=anchor)

fi = 0
for t in range(0, TICKS, 2):
    s = state[t]
    cx, cy, z = cam(t)
    sx, sy = shake_at(t); cx += sx; cy += sy
    vw, vh = OW/z, OH/z; x0, y0 = cx - vw/2, cy - vh/2
    ix0, iy0 = int(math.floor(x0)) - 2, int(math.floor(y0)) - 2
    ix1, iy1 = int(math.ceil(x0 + vw)) + 2, int(math.ceil(y0 + vh)) + 2
    crop = (world_dead if t >= DESTROY else world_alive).crop((ix0, iy0, ix1, iy1))
    if ix0 - C < TUR[0] < ix1 + C and iy0 - C < TUR[1] < iy1 + C:
        ox, oy = TUR[0] - ix0, TUR[1] - iy0
        crop.paste(base, (ox-48, oy-48), base)
        shr = shadow.rotate(s['rot'], resample=Image.NEAREST); crop.paste(shr, (ox-PS//2-6, oy-PS//2+6), shr)
        hd = head(s['warm'], s['rec'], s['heat'], s['charge'])
        hd = shift(hd, 0, round(4*s['rec']**1.8)).rotate(s['rot'], resample=Image.NEAREST)
        crop.paste(hd, (ox-C//2, oy-C//2), hd)
    frame = crop.resize((OW, OH), Image.NEAREST if z >= 1 else Image.BOX, box=(x0-ix0, y0-iy0, x0-ix0+vw, y0-iy0+vh))
    lay, P = fx_layer(t, cx, cy, z)
    frame.alpha_composite(lay)
    d = ImageDraw.Draw(frame, 'RGBA')
    # overview: range circles
    if t >= 440:
        al = sm((t-440)/40)
        TX, TY = P(*TUR)
        dashed(d, TX, TY, 360*4*z, (200, 200, 210, int(200*al)), 2)
        dashed(d, TX, TY, 1200*4*z, (255, 51, 85, int(255*al)), 3)
        ring(d, TX, TY, 14, 3, (255, 51, 85, int(255*al)))
        GX, GY = P(*TARGET); ring(d, GX, GY, 10, 2, (255, 210, 120, int(255*al)))
        if t >= 496:
            Rn = 1200*4*z; yy_ = OH - 78; xx_ = TX + math.sqrt(max(0, Rn*Rn - (yy_-TY)**2))
            label(d, min(xx_ - 12, OW - 12), yy_, 'дальность 150 клеток', font3, (255, 90, 110), 'ra')
            Ro = 360*4*z; a30 = math.radians(32)
            label(d, TX + Ro*math.cos(a30) + 10, TY - Ro*math.sin(a30) - 12, 'было 45', font2, (220, 220, 228), 'la')
            label(d, GX - 16, GY + 8, f'цель: {DIST_TILES:.0f} клеток', font2, (255, 220, 150), 'ra')
    # phase captions
    if t < SHOTS[0]:
        cap = 'ЗАРЯДКА УСКОРИТЕЛЯ' if t >= CHARGES[0] else 'ЦЕЛЬ ЗАХВАЧЕНА · наведение'
    elif t < HITS[0]:
        _, _, f = shell(0, t); cap = f'СНАРЯД В ПОЛЁТЕ · до цели {DIST_TILES*(1-f):.0f} клеток'
    elif t < DESTROY:
        cap = 'ПОПАДАНИЕ · второй снаряд на подлёте'
    elif t < 440:
        cap = 'ЦЕЛЬ УНИЧТОЖЕНА'
    else:
        cap = 'ДАЛЬНОСТЬ 150 КЛЕТОК (было 45)'
    label(d, 18, 18, cap, font3, (255, 230, 234))
    d.rectangle([0, OH-40, OW, OH], fill=(14, 12, 16, 170))
    d.text((16, OH-32), 'CYBRAN ARSENAL', font=font, fill=(255, 64, 86))
    d.text((236, OH-29), 'Дальнобойная артиллерия Кибран  ·  мод для Mindustry  ·  v1.2  ·  навесной огонь через стены', font=font2, fill=(225, 220, 228))
    frame.convert('RGB').save(f'{FR}/f{fi:04d}.png'); fi += 1
    if fi % 40 == 0: print('frame', fi, flush=True)
print('frames', fi)

# ================================================================ soundtrack
SR = 44100; dur = TICKS/60
mix = np.zeros((int(SR*dur)+3*SR, 2))
def load(n):
    w = wave.open(f'{OUT}/sounds/{n}.wav'); x = np.frombuffer(w.readframes(w.getnframes()), np.int16)/32767; return x
def put(n, tick, gain, pan=0.0):
    x = load(n); i = int(tick/60*SR); m = min(len(x), len(mix)-i)
    l, r_ = math.cos((pan+1)*math.pi/4), math.sin((pan+1)*math.pi/4)
    mix[i:i+m, 0] += x[:m]*gain*l*1.41; mix[i:i+m, 1] += x[:m]*gain*r_*1.41
hum = load('cybran-lra-hum'); n_h = int(170/60*SR)
hl = np.tile(hum, n_h//len(hum)+1)[:n_h]*0.22
hl *= np.minimum(1, np.arange(n_h)/(0.3*SR)); fo = int(1.2*SR); hl[-fo:] *= np.linspace(1, 0, fo)
mix[:n_h, 0] += hl*0.8; mix[:n_h, 1] += hl*0.7
put('cybran-lra-charge', CHARGES[0], 0.6, -0.2)
put('cybran-lra-shoot', SHOTS[0], 1.0, -0.2)
put('cybran-lra-charge', CHARGES[1], 0.07, -0.6)
put('cybran-lra-shoot', SHOTS[1], 0.28, -0.7)
put('cybran-lra-whistle', HITS[0]-75, 0.55, 0.1)
put('cybran-lra-hit', HITS[0], 0.85, 0.15)
put('cybran-lra-whistle', HITS[1]-75, 0.65, -0.1)
put('cybran-lra-hit', HITS[1], 1.0, 0.0); put('cybran-lra-fire', HITS[1]+10, 0.45, 0.2)
mix = mix[:int(SR*dur)]
mix = np.tanh(mix*1.1); mix *= 0.92/np.max(np.abs(mix))
mix[-int(0.3*SR):] *= np.linspace(1, 0, int(0.3*SR))[:, None]
w = wave.open(f'{OUT}/video_audio.wav', 'wb'); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
w.writeframes((mix*32767).astype(np.int16).tobytes()); w.close()

subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-framerate', '30', '-i', f'{FR}/f%04d.png', '-i', f'{OUT}/video_audio.wav',
                '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '20', '-preset', 'medium', '-c:a', 'aac', '-b:a', '160k',
                '-shortest', '-movflags', '+faststart', f'{OUT}/cybran-lra-ingame.mp4'], check=True)
subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-framerate', '30', '-i', f'{FR}/f%04d.png', '-vf',
                'fps=12,scale=480:-1:flags=lanczos,split[a][b];[a]palettegen=max_colors=128[p];[b][p]paletteuse=dither=bayer:bayer_scale=4',
                f'{OUT}/cybran-lra-ingame.gif'], check=True)
print('done', os.path.getsize(f'{OUT}/cybran-lra-ingame.mp4'), os.path.getsize(f'{OUT}/cybran-lra-ingame.gif'))
