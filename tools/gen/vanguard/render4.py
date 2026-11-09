"""Stage 3 renders (T1-T3 arsenal): turrets, industry, heat, defence, items, ores, liquid + QA sheet."""
import numpy as np, os, time, math
from PIL import Image, ImageDraw, ImageFont
from geom import *
from mats import Model, MID
from models2 import chunks
from models4a import *
from models4b import *
from rend import render_layer, outline, heat_sprite, over, hexc

OUT = '/data/vg2/out/sprites'
for d in ('blocks/turrets', 'blocks/crafting', 'blocks/defense', 'blocks/walls', 'blocks/heat', 'blocks/drills', 'items', 'liquids', 'blocks/ores'):
    os.makedirs(f'{OUT}/{d}', exist_ok=True)
SS = 4
FULL = {}
GL = [MID[k] for k in ('glow', 'rglow', 'flame', 'pglow', 'gglow')]
def save(a, d, n): Image.fromarray(a).save(f'{OUT}/{d}/{n}.png')
def blank(n): return np.zeros((n, n, 4), np.uint8)
def glowfn(mp, X, Y, g): return np.isin(mp, GL).astype(float)
def flamefn(mp, X, Y, g): return np.isin(mp, [MID['flame'], MID['heat']]).astype(float)
def liquid_fill(bot, col, r, sq=True):
    f = bot.copy(); n = f.shape[0]; yy, xx = np.mgrid[0:n, 0:n]; c = (n-1)/2
    m = (np.maximum(abs(xx-c), abs(yy-c)) < r) if sq else ((xx-c)**2+(yy-c)**2 < r*r)
    f[m, :3] = (f[m, :3]*0.35 + hexc(col)*0.65).astype(np.uint8); f[m, 3] = 255
    return f

t0 = time.time()
# ================================================================ turrets
def turret(name, M, bc, tc, heat=None, parts=False):
    d = 'blocks/turrets'
    base, _ = render_layer(M, ['base'], ['base'], bc, SS)
    body, _ = render_layer(M, ['body'], ['body', 'barrel'] if parts else ['body'], tc, SS, heat if not parts else None)
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
    save(f, d, f'{name}-full'); FULL[name] = f

turret('redoubt', redoubt(), 96, 128, heat_redoubt, parts=True)
turret('mantis', mantis(), 128, 160, heat_mantis, parts=True)
turret('lash', lash(), 64, 96, heat_front(0.85, 1.2))
turret('hydra', hydra(), 96, 128, heat_front(0.6, 0.95))
turret('wasp', wasp(), 96, 128, heat_front(0.55, 0.9))
turret('rivet', rivet(), 64, 96, heat_front(0.75, 1.15))
turret('sparrow', sparrow(), 64, 96, heat_front(0.65, 0.97))
print('turrets', round(time.time()-t0, 1))

# ================================================================ crafting
d = 'blocks/crafting'
M = electrolyzer()
bot, _ = render_layer(M, ['bottom'], ['bottom', 'main'], 64, SS)
main, hg = render_layer(M, ['main'], ['main'], 64, SS, glowfn)
save(bot, d, 'electrolyzer-bottom'); save(main, d, 'electrolyzer'); save(heat_sprite(hg), d, 'electrolyzer-glow')
f = over(liquid_fill(bot, '74d45a', 14), main); save(f, d, 'electrolyzer-full'); FULL['electrolyzer'] = f

M = alloy_furnace()
main, hg = render_layer(M, ['main'], ['main'], 96, SS, flamefn)
save(main, d, 'alloy-furnace'); save(heat_sprite(hg), d, 'alloy-furnace-glow'); save(main, d, 'alloy-furnace-full'); FULL['alloy-furnace'] = main

M = tungsten_forge()
main, hg = render_layer(M, ['main'], ['main'], 96, SS, lambda mp, X, Y, g: (mp == MID['flame']).astype(float))
_, hh = render_layer(M, ['main'], ['main'], 96, SS, heat_right_port)
save(main, d, 'tungsten-forge'); save(heat_sprite(hg), d, 'tungsten-forge-glow'); save(heat_sprite(hh), d, 'tungsten-forge-heat')
save(main, d, 'tungsten-forge-full'); FULL['tungsten-forge'] = main

M = magnet_factory()
bot, _ = render_layer(M, ['bottom'], ['bottom', 'main'], 64, SS)
spin, _ = render_layer(M, ['spinner'], ['spinner', 'main'], 64, SS)
main, hg = render_layer(M, ['main'], ['main'], 64, SS, glowfn)
save(bot, d, 'magnet-factory-bottom'); save(spin, d, 'magnet-factory-spinner'); save(main, d, 'magnet-factory'); save(heat_sprite(hg), d, 'magnet-factory-glow')
f = over(over(bot, spin), main); save(f, d, 'magnet-factory-full'); FULL['magnet-factory'] = f

M = separator2()
bot, _ = render_layer(M, ['bottom'], ['bottom', 'main'], 96, SS)
spin, _ = render_layer(M, ['spinner'], ['spinner', 'main'], 96, SS)
main, hg = render_layer(M, ['main'], ['main'], 96, SS, glowfn)
save(bot, d, 'mass-separator-2-bottom'); save(spin, d, 'mass-separator-2-spinner'); save(main, d, 'mass-separator-2'); save(heat_sprite(hg), d, 'mass-separator-2-glow')
f = over(over(liquid_fill(bot, 'ff7828', 24, sq=False), spin), main); save(f, d, 'mass-separator-2-full'); FULL['mass-separator-2'] = f

# ================================================================ heat
d = 'blocks/heat'
M = heater()
main, hg = render_layer(M, ['main'], ['main', 'top'], 64, SS, lambda mp, X, Y, g: (mp == MID['flame']).astype(float))
top, ht = render_layer(M, ['top'], ['top'], 64, SS, heat_mouth)
save(main, d, 'heater'); save(heat_sprite(hg), d, 'heater-glow'); save(top, d, 'heater-top1'); save(np.ascontiguousarray(top[::-1]), d, 'heater-top2'); save(heat_sprite(ht), d, 'heater-heat')
f = over(main, top); save(f, d, 'heater-full'); FULL['heater'] = f

M = heat_conduit()
main, _ = render_layer(M, ['main'], ['main', 'top'], 32, SS)
top, ht = render_layer(M, ['top'], ['top'], 32, SS, heat_strip)
save(main, d, 'heat-conduit'); save(top, d, 'heat-conduit-top1'); save(np.ascontiguousarray(top[::-1]), d, 'heat-conduit-top2'); save(heat_sprite(ht), d, 'heat-conduit-heat')
f = over(main, top); save(f, d, 'heat-conduit-full'); FULL['heat-conduit'] = f

# ================================================================ drill
d = 'blocks/drills'
M = impact_drill()
main, _ = render_layer(M, ['main'], ['main', 'rotator', 'top'], 96, SS)
rot, _ = render_layer(M, ['rotator'], ['rotator', 'top'], 96, SS)
top, _ = render_layer(M, ['top'], ['top'], 96, SS)
save(main, d, 'impact-drill'); save(rot, d, 'impact-drill-rotator'); save(top, d, 'impact-drill-top')
f = over(over(main, rot), top); save(f, d, 'impact-drill-full'); FULL['impact-drill'] = f
print('industry', round(time.time()-t0, 1))

# ================================================================ defence
d = 'blocks/defense'
M = radar()
base, _ = render_layer(M, ['base'], ['base', 'head'], 96, SS)
head, hg = render_layer(M, ['head'], ['head'], 96, SS, glowfn)
save(base, d, 'radar-base'); save(head, d, 'radar'); save(heat_sprite(hg), d, 'radar-glow')
f = over(base, outline(head, r=2)); f = over(f, head); save(f, d, 'radar-full'); FULL['radar'] = f
for name, M, c in (('ed-shield', ed_shield(), 64), ('pulse-shield', pulse_shield(), 96), ('nanite-repairer', nanite_repairer(), 64)):
    main, hg = render_layer(M, ['main'], ['main'], c, SS, glowfn)
    save(main, d, name); save(heat_sprite(hg), d, f'{name}-top'); save(main, d, f'{name}-full'); FULL[name] = main
d = 'blocks/walls'
M = decoy(); a, _ = render_layer(M, ['main'], ['main'], 64, SS); save(a, d, 'decoy'); FULL['decoy'] = a
w1, _ = render_layer(tung_wall(0.5), ['main'], ['main'], 32, SS); save(w1, d, 'tungsten-wall'); FULL['tungsten-wall'] = w1
w2, _ = render_layer(tung_wall(1.0), ['main'], ['main'], 64, SS); save(w2, d, 'tungsten-wall-large'); FULL['tungsten-wall-large'] = w2

# ================================================================ items / liquid / ores
d = 'items'
for name, M in (('bauxite', chunks('ore_baux', 11, n=6, s=0.23)), ('cobaltite', chunks('ore_cob', 12, crystal=True)), ('wolframite', chunks('ore_wolf', 13, n=6, s=0.23)),
                ('neodymite', chunks('ore_neo', 14, crystal=True)), ('aluminum', item_alu()), ('cobalt-alloy', item_cobalt_alloy()),
                ('tungsten-core', item_tungsten_core()), ('magnet', item_magnet())):
    a, _ = render_layer(M, ['main'], ['main'], 32, SS)
    a = outline(a, '25262b', r=1); save(a, d, name); FULL['item-'+name] = a
a, _ = render_layer(item_chlorine(), ['main'], ['main'], 32, SS)
a = outline(a, '25262b', r=1); save(a, 'liquids', 'chlorine'); FULL['liquid-chlorine'] = a
d = 'blocks/ores'
for i, (name, mat, cr) in enumerate((('ore-bauxite', 'ore_baux', False), ('ore-cobaltite', 'ore_cob', True), ('ore-wolframite', 'ore_wolf', False), ('ore-neodymite', 'ore_neo', True))):
    for v in range(3):
        M = Model(); r = np.random.default_rng(300+10*i+v)
        for j in range(5 if cr else 6):
            x, y = r.uniform(-0.28, 0.28, 2); s = 0.09+0.07*r.random()
            if cr:
                p = [(s*0.5*math.cos(a), s*0.5*math.sin(a)) for a in np.linspace(0, 2*math.pi, 6, endpoint=False)]
                M.add('main', tf(prism(ccw(p), 0, s*1.6, 0.3), rx(r.uniform(30, 60))@rz(r.uniform(0, 360)), (x, y, 0.02)), mat)
            else:
                p = [(s*(0.7+0.5*r.random())*math.cos(a), s*(0.7+0.5*r.random())*math.sin(a)) for a in np.linspace(0, 2*math.pi, 7, endpoint=False)]
                M.add('main', prism(ccw(p), 0, s*0.8, 0.55), mat)
        a, _ = render_layer(M, ['main'], ['main'], 32, SS)
        save(a, d, f'{name}{v+1}')
        if v == 0: FULL[name] = a
print('rendered in', round(time.time()-t0, 1), 's')

# ================================================================ QA sheet
B = '/usr/share/fonts/liberation-sans/LiberationSans-Bold.ttf'; R = '/usr/share/fonts/liberation-sans/LiberationSans-Regular.ttf'
keys = list(FULL.keys()); C = 180; cols = 6; rows = math.ceil(len(keys)/cols)
S = Image.new('RGB', (cols*C, rows*C + 70), (24, 26, 31)); D = ImageDraw.Draw(S)
D.text((16, 18), 'Vanguard Arsenal 2.0.0-alpha3  ·  Этап 3: T1–T3', fill=(255, 211, 127), font=ImageFont.truetype(B, 28))
for i, k in enumerate(keys):
    a = FULL[k]; n = a.shape[0]; sc = max(1, min(4, 140//n))
    im = Image.fromarray(a).resize((n*sc, n*sc), Image.NEAREST)
    x = (i % cols)*C; y = 70 + (i//cols)*C
    D.rectangle([x+6, y+6, x+C-6, y+C-6], fill=(34, 37, 44))
    S.paste(im, (x + (C-im.width)//2, y + 8 + (150-im.height)//2), im)
    D.text((x+12, y+C-26), k, fill=(220, 224, 230), font=ImageFont.truetype(R, 15))
S.save('/data/vg2/out/stage3-sheet.png')
S.convert('RGB').resize((S.width//2, S.height//2), Image.LANCZOS).save('/data/vg2/out/sheet3_qa.jpg', quality=82)
np.save('/data/vg2/out/full4_keys.npy', np.array(keys))
print('sheet', S.size, len(keys))
