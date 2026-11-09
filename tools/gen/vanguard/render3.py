"""Stage 2 renders: units (mech layers + cells + outlines + weapon heat), cores (+team), engineering bay."""
import numpy as np, os, time
from PIL import Image, ImageDraw, ImageFont
from models3 import *
from rend import render_layer, outline, heat_sprite, over, hexc
from mats import MID

OUT = '/data/vg2/out/sprites'
for d in ('units', 'units/weapons', 'blocks/cores', 'blocks/units'):
    os.makedirs(f'{OUT}/{d}', exist_ok=True)
SS = 4
FULL = {}
LAYERS = {}
TEAM = 'ffd37f'

def save(a, d, n): Image.fromarray(a).save(f'{OUT}/{d}/{n}.png')
def blank(n): return np.zeros((n, n, 4), np.uint8)
def teamfn(mp, X, Y, g): return (mp == MID['team']).astype(float)
def glowfn(mp, X, Y, g): return np.isin(mp, [MID['glow'], MID['rglow'], MID['flame']]).astype(float)

def cell_of(spr, hm):
    out = np.zeros_like(spr)
    m = (hm > 0.45) & (spr[..., 3] > 0)
    out[m] = spr[m]; out[m, 3] = 255
    return out

def tint(spr, col):
    o = spr.copy().astype(float)
    o[..., :3] = o[..., :3]*hexc(col)/255.0
    return o.astype(np.uint8)

def paste_c(dst, src, cx, cy):
    """composite src centred at pixel (cx, cy) of dst (clips safely)"""
    D = Image.fromarray(dst); S = Image.fromarray(src)
    x0 = int(round(cx - S.width/2)); y0 = int(round(cy - S.height/2))
    L = Image.new('RGBA', D.size, (0, 0, 0, 0)); L.paste(S, (x0, y0), S)
    return np.array(Image.alpha_composite(D, L))

def unit(name, M, canvas, guns=(), wcanvas=48, mech=True):
    d = 'units'
    body, hm = render_layer(M, ['body'], ['body'], canvas, SS, teamfn)
    r = 3 if canvas >= 64 else 2
    cell = cell_of(body, hm)
    save(body, d, name); save(outline(body, r=r), d, f'{name}-outline'); save(cell, d, f'{name}-cell')
    LAYERS[name] = {'body': body, 'cell': cell}
    f = blank(canvas)
    if mech:
        leg, _ = render_layer(M, ['leg'], ['leg'], canvas, SS)
        base, _ = render_layer(M, ['base'], ['base'], canvas, SS)
        leg = outline(leg, r=2); base = outline(base, r=2)
        save(leg, d, f'{name}-leg'); save(base, d, f'{name}-base')
        LAYERS[name].update(leg=leg, base=base)
        # full icon: legs at rest, base, guns (under body), body, team cell
        f = over(f, leg); f = over(f, np.ascontiguousarray(leg[:, ::-1])); f = over(f, base)
    for grp, wname, wx, wy in guns:
        g_, ghm = render_layer(M, [grp], [grp], wcanvas, SS, teamfn)
        _, hh = render_layer(M, [grp], [grp], wcanvas, SS, glowfn)
        save(g_, 'units/weapons', wname); save(outline(g_, r=2), 'units/weapons', f'{wname}-outline')
        wc = cell_of(g_, ghm)
        if wc[..., 3].any(): save(wc, 'units/weapons', f'{wname}-cell')
        if hh.max() > 0.05: save(heat_sprite(hh), 'units/weapons', f'{wname}-heat')
        LAYERS[name][wname] = g_
        cx = canvas/2 + wx*4; cy = canvas/2 - wy*4
        f = paste_c(f, outline(g_, r=2), cx, cy); f = paste_c(f, over(g_, tint(wc, TEAM)) if wc[..., 3].any() else g_, cx, cy)
    f = over(f, outline(body, r=r)); f = over(f, body); f = over(f, tint(cell, TEAM))
    save(f, d, f'{name}-full'); FULL[name] = f

def core(name, M):
    d = 'blocks/cores'
    main, hm = render_layer(M, ['main'], ['main'], 128, SS, teamfn)
    team = cell_of(main, hm)
    save(main, d, name); save(team, d, f'{name}-team')
    f = over(main.copy(), tint(team, TEAM)); save(f, d, f'{name}-full'); FULL[name] = f

t0 = time.time()
unit('acu-uef', acu_uef(), 80, [('gunR', 'acu-uef-cannon', 6.0, 0.5), ('gunL', 'acu-uef-launcher', -6.0, 0.5)])
unit('acu-cybran', acu_cybran(), 80, [('gunR', 'acu-cybran-laser', 5.75, 0.75), ('gunL', 'acu-cybran-emp', -5.75, 0.75)])
import glob as _g
for _p in _g.glob(f'{OUT}/units/engineer-leg.png') + _g.glob(f'{OUT}/units/engineer-base.png'): os.remove(_p)
unit('engineer', engineer(), 40, mech=False)
core('core-uef', core_uef())
core('core-cybran', core_cybran())
M = bay(); d = 'blocks/units'
main, _ = render_layer(M, ['main'], ['main', 'top'], 96, SS)
top, _ = render_layer(M, ['top'], ['top'], 96, SS)
out, _ = render_layer(M, ['out'], ['out'], 96, SS)
save(main, d, 'engineering-bay'); save(top, d, 'engineering-bay-top'); save(out, d, 'engineering-bay-out')
f = over(over(main.copy(), out), top); save(f, d, 'engineering-bay-full'); FULL['engineering-bay'] = f
np.save('/data/vg2/out/full3.npy', {k: v for k, v in FULL.items()}, allow_pickle=True)
print('rendered stage2 in %.1fs' % (time.time()-t0))

# ---------------- QA sheet
font = ImageFont.truetype('/usr/share/fonts/liberation-sans/LiberationSans-Regular.ttf', 13)
items = [('acu-uef', 'БКМ «Страж» (UEF)'), ('acu-cybran', 'БКМ «Призрак» (Кибран)'), ('engineer', 'Инженер T1'),
         ('core-uef', 'Командный комплекс UEF'), ('core-cybran', 'Узел Кибран'), ('engineering-bay', 'Инженерный цех')]
lay = [('acu-uef', 'leg'), ('acu-uef', 'base'), ('acu-uef', 'body'), ('acu-uef', 'cell'), ('acu-uef', 'acu-uef-cannon'), ('acu-uef', 'acu-uef-launcher'),
       ('acu-cybran', 'leg'), ('acu-cybran', 'body'), ('acu-cybran', 'acu-cybran-laser'), ('acu-cybran', 'acu-cybran-emp')]
CW = 250; cols = 3; rows = 2
W = CW*cols; H = 46 + CW*rows + 40 + 130
S = Image.new('RGB', (W, H), (24, 26, 32)); D = ImageDraw.Draw(S)
D.text((12, 12), 'Vanguard Arsenal 2.0.0-alpha2 — этап 2: БКМ, инженеры, ядра', fill=(245, 200, 74), font=ImageFont.truetype('/usr/share/fonts/liberation-sans/LiberationSans-Bold.ttf', 16))
for i, (k, lab) in enumerate(items):
    x = (i % cols)*CW; y = 46 + (i//cols)*CW
    D.rectangle([x+6, y+6, x+CW-6, y+CW-6], fill=(34, 37, 45), outline=(52, 56, 66))
    im = Image.fromarray(FULL[k]); s = 196/max(im.width, im.height)
    im = im.resize((int(im.width*s), int(im.height*s)), Image.NEAREST)
    S.paste(im, (x+(CW-im.width)//2, y+12+(196-im.height)//2), im)
    D.text((x+CW//2, y+CW-22), lab, fill=(220, 224, 232), font=font, anchor='mm')
y = 46 + CW*rows + 8
D.text((12, y), 'Слои БКМ: нога / таз / корпус / маска команды / оружие', fill=(180, 186, 198), font=font)
for j, (u, l) in enumerate(lay):
    im = Image.fromarray(LAYERS[u][l]); s = 64/max(im.width, im.height)
    im = im.resize((max(1, int(im.width*s*1.0)), max(1, int(im.height*s))), Image.NEAREST)
    x = 10 + j*74; S.paste(im, (x+(64-im.width)//2, y+30+(64-im.height)//2), im)
    D.rectangle([x-2, y+28, x+66, y+96], outline=(52, 56, 66))
S.save('/data/vg2/stage2-sheet.png')
S.resize((W//1, H//1)).convert('RGB').save('/data/vg2/sheet2_qa.jpg', quality=88)
print('sheet', S.size)
