import glob, os, math
import numpy as np
from PIL import Image, ImageDraw, ImageFont
P = {os.path.basename(p)[:-4]: p for p in glob.glob('/data/vg2/out/sprites/**/*.png', recursive=True)}
def L(n): return Image.open(P[n]).convert('RGBA')
W_, H_ = 760, 430
rng = np.random.default_rng(5)
bg = Image.new('RGBA', (W_, H_), (38, 41, 46, 255)); d = ImageDraw.Draw(bg)
for i in range(900):
    x, y = rng.integers(0, W_), rng.integers(0, H_); c = int(rng.integers(40, 56)); d.rectangle([x, y, x+2, y+2], fill=(c, c+2, c+5, 255))
for x in range(0, W_, 32): d.line([(x, 0), (x, H_)], fill=(46, 49, 55, 255))
for y in range(0, H_, 32): d.line([(0, y), (W_, y)], fill=(46, 49, 55, 255))
# enemy blocks at the top (targets)
for tx, ty in ((180, 60), (240, 70), (520, 52), (590, 66), (650, 48)):
    d.rectangle([tx-14, ty-14, tx+14, ty+14], fill=(92, 60, 60, 255), outline=(150, 80, 80, 255), width=2)
F = ImageFont.truetype('/usr/share/fonts/liberation-sans/LiberationSans-Bold.ttf', 16)
d.text((14, H_-26), 'Редут T2 — залп 3 × кассетный', font=F, fill=(255, 201, 74, 255))
d.text((420, H_-26), 'Богомол T3 — веер 6 × ЭМИ', font=F, fill=(255, 85, 119, 255))

def tint(im, col, a):
    arr = np.array(im).astype(np.float32); m = arr[..., 3:4]/255*a
    out = np.zeros_like(arr); out[..., :3] = col; out[..., 3:4] = m*255
    return Image.fromarray(out.clip(0, 255).astype(np.uint8))
class Tur:
    def __init__(s, n, cx, cy, tgt, shootY, hc, shells, spread, delay, start):
        s.n, s.cx, s.cy, s.hc = n, cx, cy, hc
        s.base, s.out, s.main = L(n+'-base'), L(n+'-outline'), L(n)
        s.bar, s.baro, s.barh = L(n+'-barrel'), L(n+'-barrel-outline'), L(n+'-barrel-heat')
        s.tgt = tgt; dx, dy = tgt[0]-cx, tgt[1]-cy; s.ang = math.degrees(math.atan2(dx, -dy))
        s.sy = shootY; s.shots = [(start + k*delay, spread*(k-(shells-1)/2)) for k in range(shells)]
    def recoil(s, f):
        r = 0
        for t0, _ in s.shots:
            if f >= t0: r = max(r, math.exp(-(f-t0)/5))
        return r
    def heat(s, f):
        h = 0
        for t0, _ in s.shots:
            if f >= t0: h = max(h, math.exp(-(f-t0)/14))
        return h
    def draw(s, fr, f):
        b = s.base; fr.alpha_composite(b, (s.cx-b.width//2, s.cy-b.height//2))
        S = s.main.width; loc = Image.new('RGBA', (S, S), (0, 0, 0, 0))
        rc = int(round(s.recoil(f)*7))
        loc.alpha_composite(s.out); loc.alpha_composite(s.main)
        for im in (s.baro, s.bar): loc.alpha_composite(im, (0, rc))
        loc.alpha_composite(tint(s.barh, s.hc, s.heat(f)), (0, rc))
        rot = loc.rotate(-s.ang, resample=Image.BICUBIC, expand=True)
        fr.alpha_composite(rot, (s.cx-rot.width//2, s.cy-rot.height//2))
    def muzzle(s, da):
        a = math.radians(s.ang + da); return s.cx + math.sin(a)*s.sy, s.cy - math.cos(a)*s.sy

red = Tur('redoubt', 210, 330, (215, 64), 59, (255, 154, 58), 3, 2.0, 3, 2)
man = Tur('mantis', 560, 318, (590, 58), 68, (255, 51, 85), 6, 5.5, 3, 16)
NF, FL = 64, 26
shells = []
for T, col, kind, h in ((red, (255, 225, 150), 'cluster', 70), (man, (110, 190, 255), 'emp', 95)):
    for t0, da in T.shots:
        sx, sy = T.muzzle(da); a = math.radians(T.ang + da); dist = math.hypot(T.tgt[0]-T.cx, T.tgt[1]-T.cy) - T.sy
        dist *= 1 + rng.uniform(-0.06, 0.06)
        ex, ey = sx + math.sin(a)*dist, sy - math.cos(a)*dist
        shells.append(dict(t0=t0, sx=sx, sy=sy, ex=ex, ey=ey, col=col, kind=kind, h=h, seed=int(rng.integers(1e6))))
frames = []
for f in range(NF):
    fr = bg.copy(); top = Image.new('RGBA', (W_, H_), (0, 0, 0, 0)); dd = ImageDraw.Draw(top)
    for sh in shells:
        u = (f - sh['t0'])/FL
        if 0 <= u <= 1:
            x = sh['sx'] + (sh['ex']-sh['sx'])*u; y = sh['sy'] + (sh['ey']-sh['sy'])*u; z = math.sin(math.pi*u)*sh['h']*0.35
            dd.ellipse([x-4-z*0.12, y-3, x+4+z*0.12, y+3], fill=(0, 0, 0, 90))                       # ground shadow
            px, py = x - z*0.6, y - z
            for k in range(5):                                                                          # trail
                uu = max(0, u - 0.025*(k+1)); tx = sh['sx'] + (sh['ex']-sh['sx'])*uu; ty = sh['sy'] + (sh['ey']-sh['sy'])*uu
                tz = math.sin(math.pi*uu)*sh['h']*0.35; r = 3.2 - k*0.5
                dd.ellipse([tx-tz*0.6-r, ty-tz-r, tx-tz*0.6+r, ty-tz+r], fill=sh['col'] + (150 - 28*k,))
            dd.ellipse([px-4, py-4, px+4, py+4], fill=(255, 255, 255, 255), outline=sh['col'] + (255,), width=2)
            # impact marker on the ground
            m = 6 + 3*math.sin(f*0.8); dd.ellipse([sh['ex']-m, sh['ey']-m*0.6, sh['ex']+m, sh['ey']+m*0.6], outline=sh['col'] + (160,), width=1)
        v = f - sh['t0'] - FL
        if 0 <= v < 16:
            q = v/16; R = 6 + 34*q**0.6; a = int(255*(1-q))
            dd.ellipse([sh['ex']-R, sh['ey']-R, sh['ex']+R, sh['ey']+R], outline=sh['col'] + (a,), width=max(1, int(4*(1-q))))
            if v < 5: dd.ellipse([sh['ex']-10+v, sh['ey']-10+v, sh['ex']+10-v, sh['ey']+10-v], fill=(255, 250, 230, 230))
            r2 = np.random.default_rng(sh['seed'])
            if sh['kind'] == 'cluster':
                for k in range(7):
                    an = r2.uniform(0, 2*math.pi); dist = r2.uniform(14, 30); bx, by = sh['ex'] + math.cos(an)*dist, sh['ey'] + math.sin(an)*dist
                    w = v - 6 - k*0.6
                    if 0 <= w < 7: rr = 3 + w*1.6; dd.ellipse([bx-rr, by-rr, bx+rr, by+rr], fill=(255, 220, 150, int(220*(1-w/7))))
            else:
                for k in range(6):
                    an = r2.uniform(0, 2*math.pi); pts = [(sh['ex'], sh['ey'])]
                    for j in range(4): pts.append((pts[-1][0] + math.cos(an + r2.uniform(-0.7, 0.7))*8, pts[-1][1] + math.sin(an + r2.uniform(-0.7, 0.7))*8))
                    dd.line(pts, fill=(200, 235, 255, int(255*(1-q))), width=2)
            for k in range(6):
                an = r2.uniform(0, 2*math.pi); rr = 4 + 8*q; ox, oy = math.cos(an)*R*0.5, math.sin(an)*R*0.5 - v*0.8
                g = int(90 - 30*q); dd.ellipse([sh['ex']+ox-rr, sh['ey']+oy-rr, sh['ex']+ox+rr, sh['ey']+oy+rr], fill=(g, g, g+4, int(140*(1-q))))
    for T in (red, man):
        T.draw(fr, f)
        for t0, da in T.shots:
            w = f - t0
            if 0 <= w < 4:
                mx, my = T.muzzle(da); r = 12 - 2*w
                dd.ellipse([mx-r, my-r, mx+r, my+r], fill=(255, 240, 200, 220 - 50*w))
                a = math.radians(T.ang + da)
                for k in range(3):
                    sx, sy = mx + math.sin(a)*(6+k*6), my - math.cos(a)*(6+k*6); rr = 6 + w*3
                    dd.ellipse([sx-rr, sy-rr, sx+rr, sy+rr], fill=(170, 170, 175, 90 - 20*w))
    fr.alpha_composite(top)
    frames.append(fr.convert('RGB'))
frames[0].save('/data/vg2/out/stage3-fire.gif', save_all=True, append_images=frames[1:], duration=45, loop=0, optimize=True)
qa = Image.new('RGB', (W_, H_*2)); qa.paste(frames[4], (0, 0)); qa.paste(frames[46], (0, H_))
qa.resize((W_//2, H_)).save('/data/vg2/out/fire3_qa.jpg', quality=80)
print('gif', round(os.path.getsize('/data/vg2/out/stage3-fire.gif')/1e6, 2), 'MB', len(frames))
