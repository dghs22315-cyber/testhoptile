import numpy as np, os, time, shutil, sys
sys.path.insert(0, '/data/vg2')
from PIL import Image, ImageDraw, ImageFont
from rend import render_layer, outline, heat_sprite, over
from models5 import *

OUT = '/data/vg2/out/sprites/blocks/turrets'; OLD = '/data/vg2/out/old'
os.makedirs(OLD, exist_ok=True)
for n in ('howl', 'redoubt', 'mantis'):
    if not os.path.exists(f'{OLD}/{n}-full.png') and os.path.exists(f'{OUT}/{n}-full.png'):
        shutil.copy(f'{OUT}/{n}-full.png', f'{OLD}/{n}-full.png')
SS = 4; t0 = time.time(); FULL = {}
def save(a, n): Image.fromarray(a).save(f'{OUT}/{n}.png')
def blank(n): return np.zeros((n, n, 4), np.uint8)

def turret(name, M, bc, tc, heat):
    base, _ = render_layer(M, ['base'], ['base'], bc, SS)
    body, _ = render_layer(M, ['body'], ['body', 'barrel'], tc, SS)
    bar, hb = render_layer(M, ['barrel'], ['barrel'], tc, SS, heat)
    bo, ro = outline(body), outline(bar)
    save(base, f'{name}-base'); save(body, name); save(bo, f'{name}-outline')
    save(bar, f'{name}-barrel'); save(ro, f'{name}-barrel-outline'); save(heat_sprite(hb), f'{name}-barrel-heat')
    off = (tc-bc)//2
    f = np.asarray(over(blank(tc), base, off, off))
    for L in (bo, body, ro, bar): f = np.asarray(over(f, L))
    save(f, f'{name}-full'); FULL[name] = f
    print(name, 'tris', M.ntri(), 'canvas', tc, 'muzzle(y,z)', [round(v, 3) for v in SPEC[name]], round(time.time()-t0, 1), 's', flush=True)

turret('howl', howl5(), 64, 128, heat_howl5)
turret('redoubt', redoubt5(), 96, 192, heat_redoubt5)
turret('mantis', mantis5(), 128, 256, heat_mantis5)

# ---------- comparison sheet: reference / before / after
F = '/usr/share/fonts/liberation-sans/LiberationSans-Bold.ttf'
font = ImageFont.truetype(F, 22); small = ImageFont.truetype(F, 16)
ref = Image.open('/data/cybran/out/sprites/cybran-lra-full.png').convert('RGBA')
cols = [('Эталон: Скорпион', ref, None)]
for n, ru in (('howl', 'Вой'), ('redoubt', 'Редут'), ('mantis', 'Богомол')):
    old = Image.open(f'{OLD}/{n}-full.png').convert('RGBA') if os.path.exists(f'{OLD}/{n}-full.png') else None
    cols.append((ru, Image.fromarray(FULL[n]), old))
K = 2; pad = 30
W = sum(max(c[1].width, c[2].width if c[2] else 0)*K + pad for c in cols) + pad
H = 60 + 2*(256*K + 40)
img = Image.new('RGBA', (W, H), (40, 41, 48, 255)); d = ImageDraw.Draw(img)
for x in range(0, W, 32*K): d.line([(x, 0), (x, H)], fill=(47, 48, 56, 255))
for y in range(0, H, 32*K): d.line([(0, y), (W, y)], fill=(47, 48, 56, 255))
d.text((pad, 14), 'Было (этап 3)', font=font, fill=(150, 150, 160, 255))
d.text((pad, 60+256*K+48), 'Стало (герой-уровень)', font=font, fill=(255, 210, 120, 255))
x = pad
for ru, new, old in cols:
    cw = max(new.width, old.width if old else 0)*K
    if old is not None:
        o = old.resize((old.width*K, old.height*K), Image.NEAREST)
        img.alpha_composite(o, (x+(cw-o.width)//2, 50+(256*K-o.height)//2))
    nn = new.resize((new.width*K, new.height*K), Image.NEAREST)
    yy = 60+256*K+80
    img.alpha_composite(nn, (x+(cw-nn.width)//2, yy+(256*K-nn.height)//2 - 30))
    d.text((x, H-34), ru, font=small, fill=(230, 230, 235, 255))
    x += cw+pad
img.convert('RGB').save('/data/vg2/out/hero-compare.png')
# small QA crops of the new heads only
for n in ('howl', 'redoubt', 'mantis'):
    a = Image.fromarray(FULL[n]); bg = Image.new('RGBA', a.size, (40, 41, 48, 255)); bg.alpha_composite(a)
    bg.convert('RGB').save(f'/data/vg2/out/qa5-{n}.jpg', quality=85)
print('sheet', img.size, round(time.time()-t0, 1))
