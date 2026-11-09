import numpy as np, os, time, math
from PIL import Image
from models import howl, heat_howl_barrel
from models2 import *
from rend import render_layer, outline, heat_sprite, over
from mats import MID

OUT = '/data/vg2/out/sprites'
for d in ('blocks/turrets', 'blocks/crafting', 'blocks/defense', 'blocks/walls', 'items', 'blocks/ores'):
    os.makedirs(f'{OUT}/{d}', exist_ok=True)
SS = 4
FULL = {}

def save(a, d, n):
    Image.fromarray(a).save(f'{OUT}/{d}/{n}.png')

def glowfn(mp, X, Y, g):
    return np.isin(mp, [MID['glow'], MID['flame'], MID['heat']]).astype(float)

def blank(n): return np.zeros((n, n, 4), np.uint8)

t0 = time.time()
# ---- Howl
M = howl(); d = 'blocks/turrets'
base, _ = render_layer(M, ['base'], ['base'], 64, SS)
body, hb = render_layer(M, ['body'], ['body', 'barrel'], 96, SS)
bar, hbar = render_layer(M, ['barrel'], ['barrel'], 96, SS, heat_howl_barrel)
save(base, d, 'howl-base'); save(body, d, 'howl'); save(outline(body), d, 'howl-outline')
save(bar, d, 'howl-barrel'); save(outline(bar), d, 'howl-barrel-outline'); save(heat_sprite(hbar), d, 'howl-barrel-heat')
f = over(blank(96), base, 16, 16); f = over(f, outline(body)); f = over(f, body); f = over(f, outline(bar)); f = over(f, bar)
save(f, d, 'howl-full'); FULL['howl'] = f

# ---- Interceptor
M = interceptor()
base, _ = render_layer(M, ['base'], ['base'], 64, SS)
head, _ = render_layer(M, ['head'], ['head'], 64, SS)
save(base, d, 'interceptor-base'); save(head, d, 'interceptor')
f = over(base.copy(), outline(head, r=2)); f = over(f, head)
save(f, d, 'interceptor-full'); FULL['interceptor'] = f

# ---- Beacon (radar)
M = beacon(); d = 'blocks/defense'
base, _ = render_layer(M, ['base'], ['base'], 32, SS)
head, hg = render_layer(M, ['head'], ['head'], 32, SS, glowfn)
save(base, d, 'spotter-beacon-base'); save(head, d, 'spotter-beacon'); save(heat_sprite(hg), d, 'spotter-beacon-glow')
f = over(base.copy(), head); save(f, d, 'spotter-beacon-full'); FULL['spotter-beacon'] = f

# ---- Emitter (force projector)
M = emitter()
main, hg = render_layer(M, ['main'], ['main'], 64, SS, glowfn)
save(main, d, 'shield-emitter'); save(heat_sprite(hg), d, 'shield-emitter-top')
save(main, d, 'shield-emitter-full'); FULL['shield-emitter'] = main

# ---- Separator
M = separator(); d = 'blocks/crafting'
bot, _ = render_layer(M, ['bottom'], ['bottom', 'main'], 64, SS)
spin, _ = render_layer(M, ['spinner'], ['spinner', 'main'], 64, SS)
main, hg = render_layer(M, ['main'], ['main'], 64, SS, glowfn)
save(bot, d, 'mass-separator-bottom'); save(spin, d, 'mass-separator-spinner'); save(main, d, 'mass-separator')
save(heat_sprite(hg), d, 'mass-separator-glow')
slag = bot.copy(); m = np.zeros((64, 64), bool); yy, xx = np.mgrid[0:64, 0:64]; m = (xx-31.5)**2+(yy-31.5)**2 < 17**2
slag[m, :3] = (slag[m, :3]*0.4 + np.array([255, 120, 40])*0.6).astype(np.uint8)
f = over(slag, spin); f = over(f, main); save(f, d, 'mass-separator-full'); FULL['mass-separator'] = f

# ---- Smelter
M = smelter()
main, hg = render_layer(M, ['main'], ['main'], 64, SS, glowfn)
save(main, d, 'steel-smelter'); save(heat_sprite(hg), d, 'steel-smelter-glow'); save(main, d, 'steel-smelter-full'); FULL['steel-smelter'] = main

# ---- Press
M = press()
bot, _ = render_layer(M, ['bottom'], ['bottom', 'main'], 64, SS)
pis, _ = render_layer(M, ['piston'], ['piston'], 32, SS)
main, _ = render_layer(M, ['main'], ['main'], 64, SS)
top, hg = render_layer(M, ['top'], ['top'], 64, SS, glowfn)
for a, n in ((bot, '-bottom'), (pis, '-piston'), (main, ''), (top, '-top')): save(a, d, 'propellant-press'+n)
save(heat_sprite(hg), d, 'propellant-press-glow')
f = bot.copy()
P = Image.fromarray(pis)
for k in range(4):
    ang = 90*k
    img = Image.new('RGBA', (64, 64)); img.paste(P, (32+6, 16), P)
    img = img.rotate(ang, resample=Image.NEAREST)
    f = over(f, np.array(img))
f = over(f, main); f = over(f, top); save(f, d, 'propellant-press-full'); FULL['propellant-press'] = f

# ---- Walls
d = 'blocks/walls'
w1, _ = render_layer(wall(0.5), ['main'], ['main'], 32, SS); save(w1, d, 'steel-wall'); FULL['steel-wall'] = w1
w2, _ = render_layer(wall(1.0), ['main'], ['main'], 64, SS); save(w2, d, 'steel-wall-large'); FULL['steel-wall-large'] = w2

# ---- Items
d = 'items'
for name, M in (('ferrolite', chunks('ore_fer', 3)), ('saltpeter', chunks('ore_salt', 4, crystal=True)), ('steel', ingot()), ('charge', cartridge())):
    a, _ = render_layer(M, ['main'], ['main'], 32, SS)
    a = outline(a, '25262b', r=1)
    save(a, d, name); FULL['item-'+name] = a

# ---- Ore overlays (3 variants each)
d = 'blocks/ores'
for name, mat, cr in (('ore-ferrolite', 'ore_fer', False), ('ore-saltpeter', 'ore_salt', True)):
    for v in range(3):
        M = Model(); r = np.random.default_rng(100+v+(7 if cr else 0))
        for j in range(5):
            x, y = r.uniform(-0.28, 0.28, 2); s = 0.10+0.07*r.random()
            if cr:
                p = [(s*0.5*math.cos(a), s*0.5*math.sin(a)) for a in np.linspace(0, 2*math.pi, 6, endpoint=False)]
                M.add('main', tf(prism(ccw(p), 0, s*1.5, 0.3), rx(r.uniform(30, 60))@rz(r.uniform(0, 360)), (x, y, 0.02)), mat)
            else:
                p = [(s*(0.7+0.5*r.random())*math.cos(a), s*(0.7+0.5*r.random())*math.sin(a)) for a in np.linspace(0, 2*math.pi, 6, endpoint=False)]
                M.add('main', prism(ccw(p), 0, s*0.8, 0.6), mat)
        a, _ = render_layer(M, ['main'], ['main'], 32, SS)
        save(a, d, f'{name}{v+1}')
        if v == 0: FULL[name] = a
print('rendered in', round(time.time()-t0, 1), 's')
np.save('/data/vg2/out/full_index.npy', np.array(list(FULL.keys())))
for k, a in FULL.items(): Image.fromarray(a).save(f'/data/vg2/out/full_{k}.png')
