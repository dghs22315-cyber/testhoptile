"""Walk/fire preview GIF for stage 2: UEF ACU, Cybran ACU, engineer (uses the real mod sprites, Mindustry drawMech-style legs)."""
import numpy as np, math
from PIL import Image, ImageDraw, ImageFont
SP = '/data/vg2/out/sprites/units'
def L(n, d=SP): return Image.open(f'{d}/{n}.png').convert('RGBA')
def tint(im, col):
    a = np.array(im).astype(float); a[..., :3] *= np.array(col)/255.0; return Image.fromarray(a.astype(np.uint8))
TEAM = (255, 211, 127)
P = 112; N = 24; SC = 2
FONT = ImageFont.truetype('/usr/share/fonts/liberation-sans/LiberationSans-Bold.ttf', 12)

def ground(seed):
    r = np.random.default_rng(seed)
    g = np.zeros((P, P, 3), np.uint8) + np.array([46, 44, 42], np.uint8)
    g = (g.astype(int) + r.integers(-5, 6, (P, P, 1))).clip(0, 255).astype(np.uint8)
    im = Image.fromarray(g).convert('RGBA'); d = ImageDraw.Draw(im)
    for x in range(0, P, 32): d.line([(x, 0), (x, P)], fill=(56, 54, 52)); d.line([(0, x), (P, x)], fill=(56, 54, 52))
    return im

def put(dst, im, cx, cy, rot=0):
    if rot: im = im.rotate(rot, resample=Image.NEAREST, expand=True)
    dst.alpha_composite(im, (int(round(cx-im.width/2)), int(round(cy-im.height/2))))

def mech_frame(name, guns, f, scroll, fire):
    bg = ground(3); 
    off = int(scroll) % 32
    bg = bg.transform(bg.size, Image.AFFINE, (1, 0, 0, 0, 1, -off), resample=Image.NEAREST)
    can = bg.copy()
    leg = L(f'{name}-leg'); base = L(f'{name}-base'); body = L(name); outl = L(f'{name}-outline'); cell = tint(L(f'{name}-cell'), TEAM)
    stride = 6.5*4
    wt = f/N*4  # walkExtend(true) in [0,4)
    raw = wt*stride
    ext = raw if raw <= stride else (2*stride-raw if raw <= 3*stride else raw-4*stride)
    s = math.sin(wt*math.pi/2)
    cx, cy = P/2, P/2+4
    sway = math.sin(wt*math.pi/2)*1.2
    sh = Image.new('RGBA', (P, P)); ImageDraw.Draw(sh).ellipse([cx-24, cy-12, cx+24, cy+18], fill=(0, 0, 0, 70)); can.alpha_composite(sh)
    for i in (1, -1):
        lg = leg if i == 1 else leg.transpose(Image.FLIP_LEFT_RIGHT)
        hs = 1 - max(-s*i, 0)*0.35
        lg = lg.resize((lg.width, max(1, int(lg.height*hs))), Image.NEAREST)
        put(can, lg, cx, cy - ext*i*0.5)
    put(can, base, cx, cy)
    for gname, gx, gy, kind in guns:
        g = L(gname, SP+'/weapons'); go = L(gname+'-outline', SP+'/weapons')
        rc = 2 if fire and kind in ('bolt', 'laser') else 0
        put(can, go, cx+gx*4+sway, cy-gy*4+rc); put(can, g, cx+gx*4+sway, cy-gy*4+rc)
    put(can, outl, cx+sway, cy); put(can, body, cx+sway, cy); put(can, cell, cx+sway, cy)
    d = ImageDraw.Draw(can)
    for gname, gx, gy, kind in guns:
        mx = cx+gx*4+sway; my = cy-gy*4-22
        if kind == 'bolt':
            t = (f % 8)/8
            y = my - t*60
            d.line([(mx, y), (mx, y+9)], fill=(106, 184, 255), width=3); d.line([(mx, y+1), (mx, y+6)], fill=(230, 246, 255), width=1)
            if f % 8 == 0: d.ellipse([mx-4, my-4, mx+4, my+4], fill=(230, 246, 255, 220))
        if kind == 'laser' and f % 12 < 4:
            d.line([(mx, my), (mx, 0)], fill=(255, 51, 85), width=4); d.line([(mx, my), (mx, 0)], fill=(255, 214, 221), width=1)
            d.ellipse([mx-3, my-3, mx+3, my+3], fill=(255, 214, 221))
        if kind == 'missile' and 10 <= f < 22:
            t = (f-10)/12
            for k in (0, 1):
                y = my - t*70 + k*10; x = mx + (k-0.5)*4 + math.sin(t*6+k)*2
                d.line([(x, y), (x, y+7)], fill=(255, 179, 71), width=2)
                for q in range(4): d.point((x+math.sin(q+f)*1.5, y+9+q*3), fill=(184, 184, 184))
        if kind == 'emp' and 6 <= f < 9:
            pts = [(mx, my)]
            for q in range(6): pts.append((mx + np.random.default_rng(f*7+q).integers(-6, 7), my - (q+1)*7))
            d.line(pts, fill=(255, 85, 119), width=2); d.line(pts, fill=(255, 220, 230), width=1)
    return can

def eng_frame(f):
    can = ground(5)
    body = L('engineer'); outl = L('engineer-outline'); cell = tint(L('engineer-cell'), TEAM)
    bob = math.sin(f/N*2*math.pi)*1.5
    cx, cy = P/2-14, P/2+18+bob
    d = ImageDraw.Draw(can)
    bx, by = P/2+18, P/2-22
    prog = (f+1)/N
    d.rectangle([bx-16, by-16, bx+16, by+16], outline=(255, 211, 127), width=1)
    d.rectangle([bx-16, by+16-int(32*prog), bx+16, by+16], fill=(255, 211, 127, 60))
    for k in range(4): d.line([(bx-16+k*11, by-16), (bx-16+k*11, by+16)], fill=(255, 211, 127, 40))
    sh = Image.new('RGBA', (P, P)); ImageDraw.Draw(sh).ellipse([cx-9+6, cy-7+8, cx+9+6, cy+9+8], fill=(0, 0, 0, 80)); can.alpha_composite(sh)
    rot = -math.degrees(math.atan2(bx-cx, -(by-cy)))
    put(can, outl, cx, cy, rot); put(can, body, cx, cy, rot); put(can, cell, cx, cy, rot)
    d = ImageDraw.Draw(can)
    a = math.radians(-rot); nx, ny = cx + math.sin(-a)*0 + 0, cy
    tx = cx + (bx-cx)*0.30; ty = cy + (by-cy)*0.30
    ex = bx + math.sin(f*0.9)*12; ey = by + math.cos(f*0.7)*12
    d.polygon([(tx, ty), (ex-3, ey-3), (ex+3, ey+3)], fill=(255, 211, 127, 110))
    d.line([(tx, ty), (ex, ey)], fill=(255, 236, 190), width=1)
    for k in range(2):
        fx = cx + (-6 if k == 0 else 6); d.ellipse([fx-2, cy+6-2, fx+2, cy+6+2], fill=(140, 200, 255, 120))
    return can

frames = []
for f in range(N):
    a = mech_frame('acu-uef', [('acu-uef-cannon', 6, 0.5, 'bolt'), ('acu-uef-launcher', -6, 0.5, 'missile')], f, f*2.2, f % 8 < 2)
    b = mech_frame('acu-cybran', [('acu-cybran-laser', 5.75, 0.75, 'laser'), ('acu-cybran-emp', -5.75, 0.75, 'emp')], f, f*2.6, f % 12 < 2)
    c = eng_frame(f)
    row = Image.new('RGBA', (P*3+8, P), (20, 22, 27, 255))
    row.alpha_composite(a, (0, 0)); row.alpha_composite(b, (P+4, 0)); row.alpha_composite(c, (2*P+8, 0))
    big = row.resize((row.width*SC, row.height*SC), Image.NEAREST)
    out = Image.new('RGBA', (big.width, big.height+26), (20, 22, 27, 255)); out.alpha_composite(big, (0, 26))
    d = ImageDraw.Draw(out)
    for i, t in enumerate(('БКМ «Страж» · UEF', 'БКМ «Призрак» · Кибран', 'Инженер · помощь стройке')):
        d.text((i*(P+4)*SC + P*SC//2, 13), t, font=FONT, fill=(232, 184, 46), anchor='mm')
    frames.append(out.convert('P', palette=Image.ADAPTIVE, colors=128))
frames[0].save('/data/vg2/stage2-walk.gif', save_all=True, append_images=frames[1:], duration=70, loop=0, optimize=True)
frames[5].convert('RGB').resize((frames[5].width//2*2//2, frames[5].height//2*2//2)).save('/data/vg2/walk_qa.jpg', quality=85)
print('gif ok', frames[0].size)
