"""2.5.0-alpha1 renders: T4 tier (Monolith, Bastion, Suppressor, Citadel, industry, items)."""
import numpy as np, os, time, math, json, sys
sys.path.insert(0, '/data/vg2')
from PIL import Image, ImageDraw, ImageFont
from rend import render_layer, outline, heat_sprite, over, hexc
from mats import MID
from hero import heat_grad
from models6 import *

OUT = '/data/vg2/out/sprites'
for d in ('blocks/turrets', 'blocks/crafting', 'blocks/defense', 'blocks/heat', 'blocks/power', 'items', 'liquids'):
    os.makedirs(f'{OUT}/{d}', exist_ok=True)
SS = 4; FULL = {}; t0 = time.time()
GL = [MID[k] for k in ('glow', 'rglow', 'flame', 'pglow', 'gglow')]
def save(a, d, n): Image.fromarray(np.asarray(a)).save(f'{OUT}/{d}/{n}.png')
def blank(n): return np.zeros((n, n, 4), np.uint8)
def glowfn(mp, X, Y, g): return np.isin(mp, GL).astype(float)
def liquid_fill(bot, col, r, sq=True):
    f = np.asarray(bot).copy(); n = f.shape[0]; yy, xx = np.mgrid[0:n, 0:n]; c = (n-1)/2
    m = (np.maximum(abs(xx-c), abs(yy-c)) < r) if sq else ((xx-c)**2+(yy-c)**2 < r*r)
    m = m & (f[..., 3] > 0)
    f[m, :3] = (f[m, :3]*0.35 + hexc(col)*0.65).astype(np.uint8); f[m, 3] = 255
    return f

def turret(name, M, bc, tc, heat=None, parts=False):
    d = 'blocks/turrets'
    base, _ = render_layer(M, ['base'], ['base'], bc, SS)
    body, _ = render_layer(M, ['body'], ['body', 'barrel'] if parts else ['body'], tc, SS)
    save(base, d, f'{name}-base'); save(body, d, name); save(outline(body), d, f'{name}-outline')
    off = (tc-bc)//2
    f = over(blank(tc), base, off, off); f = over(f, outline(body)); f = over(f, body)
    if parts:
        bar, hbar = render_layer(M, ['barrel'], ['barrel'], tc, SS, heat)
        save(bar, d, f'{name}-barrel'); save(outline(bar), d, f'{name}-barrel-outline'); save(heat_sprite(hbar), d, f'{name}-barrel-heat')
        f = over(f, outline(bar)); f = over(f, bar)
    elif heat is not None:
        _, hb = render_layer(M, ['body'], ['body'], tc, SS, heat)
        save(heat_sprite(hb), d, f'{name}-heat')
    save(f, d, f'{name}-full'); FULL[name] = np.asarray(f)
    print(name, 'tris', M.ntri(), round(time.time()-t0, 1), 's', flush=True)

turret('monolith', monolith6(), 160, 320, heat_grad(2.2, 4.6), parts=True)
turret('bastion', bastion6(), 128, 256, heat_grad(1.2, 3.8, mats=('metal', 'copper', 'hull_dark', 'metal_light'), always=('coil', 'glow')), parts=True)
turret('suppressor', suppressor6(), 96, 160, None, parts=False)
# suppressor heat: red coils + rglow light up after the EMP discharge
M = suppressor6()
_, hb = render_layer(M, ['body'], ['body'], 160, SS, lambda mp, X, Y, g: np.isin(mp, [MID['rglow'], MID['coil']]).astype(float)*0.9)
save(heat_sprite(hb), 'blocks/turrets', 'suppressor-heat')

# ---------------- defence
d = 'blocks/defense'
M = citadel6()
main, hg = render_layer(M, ['main'], ['main'], 128, SS, glowfn)
save(main, d, 'citadel'); save(heat_sprite(hg), d, 'citadel-top'); save(main, d, 'citadel-full'); FULL['citadel'] = np.asarray(main)
print('citadel', M.ntri(), round(time.time()-t0, 1), flush=True)

# ---------------- crafting
d = 'blocks/crafting'
M = cryocondenser()
bot, _ = render_layer(M, ['bottom'], ['bottom', 'main'], 64, SS)
main, hg = render_layer(M, ['main'], ['main'], 64, SS, glowfn)
save(bot, d, 'cryocondenser-bottom'); save(main, d, 'cryocondenser'); save(heat_sprite(hg), d, 'cryocondenser-glow')
f = over(liquid_fill(bot, 'bfe9ff', 13), main); save(f, d, 'cryocondenser-full'); FULL['cryocondenser'] = np.asarray(f)

M = iridium_smelter()
main, hg = render_layer(M, ['main'], ['main'], 96, SS, lambda mp, X, Y, g: (mp == MID['flame']).astype(float))
_, hh = render_layer(M, ['main'], ['main'], 96, SS, lambda mp, X, Y, g: ((X > 1.30) & (np.abs(Y) < 0.45) & (mp == MID['heat'])).astype(float))
save(main, d, 'iridium-smelter'); save(heat_sprite(hg), d, 'iridium-smelter-glow'); save(heat_sprite(hh), d, 'iridium-smelter-heat')
save(main, d, 'iridium-smelter-full'); FULL['iridium-smelter'] = np.asarray(main)

M = sc_chamber()
main, hg = render_layer(M, ['main'], ['main'], 96, SS, glowfn)
save(main, d, 'superconductor-chamber'); save(heat_sprite(hg), d, 'superconductor-chamber-glow'); save(main, d, 'superconductor-chamber-full')
FULL['superconductor-chamber'] = np.asarray(main)

# ---------------- heat
d = 'blocks/heat'
M = plasma_heater()
main, hg = render_layer(M, ['main'], ['main', 'top'], 96, SS, glowfn)
top, ht = render_layer(M, ['top'], ['top'], 96, SS, lambda mp, X, Y, g: ((X > 1.30) & (mp == MID['heat'])).astype(float))
save(main, d, 'plasma-heater'); save(heat_sprite(hg), d, 'plasma-heater-glow')
save(top, d, 'plasma-heater-top1'); save(np.ascontiguousarray(np.asarray(top)[::-1]), d, 'plasma-heater-top2'); save(heat_sprite(ht), d, 'plasma-heater-heat')
f = over(main, top); save(f, d, 'plasma-heater-full'); FULL['plasma-heater'] = np.asarray(f)

# ---------------- power
d = 'blocks/power'
M = fusion_reactor()
main, hg = render_layer(M, ['main'], ['main'], 128, SS, glowfn)
save(main, d, 'fusion-reactor'); save(heat_sprite(hg), d, 'fusion-reactor-glow'); save(main, d, 'fusion-reactor-full'); FULL['fusion-reactor'] = np.asarray(main)
print('industry', round(time.time()-t0, 1), flush=True)

# ---------------- items / liquid
for name, fn in (('iridite', item_iridite), ('tritium-ice', item_tritium), ('iridium', item_iridium), ('superconductor', item_superconductor)):
    a, _ = render_layer(fn(), ['main'], ['main'], 32, SS)
    a = outline(a, '25262b', r=1); save(a, 'items', name); FULL['item-'+name] = np.asarray(a)
a, _ = render_layer(liquid_nitrogen(), ['main'], ['main'], 32, SS)
a = outline(a, '25262b', r=1); save(a, 'liquids', 'liquid-nitrogen'); FULL['liquid-nitrogen'] = np.asarray(a)
json.dump({k: [float(v[0]), float(v[1])] for k, v in SPEC.items()}, open('/data/vg2/out/spec6.json', 'w'))

# ---------------- QA crops
def qa(keys, fn, sc):
    ims = [Image.fromarray(FULL[k]) for k in keys]
    W = sum(int(i.width*sc)+24 for i in ims)+24; H = max(int(i.height*sc) for i in ims)+48
    bg = Image.new('RGBA', (W, H), (34, 37, 44, 255)); x = 24
    for i in ims:
        j = i.resize((int(i.width*sc), int(i.height*sc)), Image.NEAREST)
        bg.alpha_composite(j, (x, 24+(H-48-j.height)//2)); x += j.width+24
    bg.convert('RGB').save(f'/data/vg2/out/{fn}', quality=88)
qa(['monolith'], 'qa6-monolith.jpg', 1.5)
qa(['bastion', 'suppressor'], 'qa6-bastion.jpg', 1.75)
qa(['citadel', 'fusion-reactor', 'iridium-smelter', 'superconductor-chamber', 'plasma-heater', 'cryocondenser'], 'qa6-misc.jpg', 2)
qa(['item-iridite', 'item-tritium-ice', 'item-iridium', 'item-superconductor', 'liquid-nitrogen'], 'qa6-items.jpg', 4)
print('done', round(time.time()-t0, 1), SPEC)
