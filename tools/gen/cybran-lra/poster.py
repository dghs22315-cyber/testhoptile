import numpy as np, random
from PIL import Image, ImageDraw, ImageFont

S = '/data/cybran/out/sprites/cybran-lra'
OUT = '/data/cybran/out'
def L(n): return Image.open(f'{S}{n}.png').convert('RGBA')
base, body, bo = L('-base'), L(''), L('-outline')
bar, baro = L('-barrel'), L('-barrel-outline')
wl, wlo, wr, wro = L('-wingl'), L('-wingl-outline'), L('-wingr'), L('-wingr-outline')
heat, bheat, prev = L('-heat'), L('-barrel-heat'), L('-preview')

# ---------------- in-game mock-up (Mindustry floor, 32 px per tile)
TW, TH = 10, 6
random.seed(3)
floor = Image.new('RGBA', (TW*32, TH*32))
fd = ImageDraw.Draw(floor)
for ty in range(TH):
    for tx in range(TW):
        x, y = tx*32, ty*32
        v = random.choice([0, 0, 0, 1, 2])
        fill = [(82, 85, 94), (77, 80, 89), (88, 91, 100)][v]
        fd.rectangle([x, y, x+31, y+31], fill=fill+(255,))
        fd.line([x, y, x+31, y], fill=(99, 102, 112, 255)); fd.line([x, y, x, y+31], fill=(99, 102, 112, 255))
        fd.line([x, y+31, x+31, y+31], fill=(60, 62, 70, 255)); fd.line([x+31, y, x+31, y+31], fill=(60, 62, 70, 255))
        for (bx, by) in ((3, 3), (28, 3), (3, 28), (28, 28)):
            fd.point((x+bx, y+by), fill=(66, 68, 76, 255))

def shift(im, dx, dy):
    out = Image.new('RGBA', im.size); out.alpha_composite(im, (dx, dy)); return out

def additive(dst, heat_im, color=(255, 58, 79), k=1.0):
    d = np.array(dst).astype(float); h = np.array(heat_im).astype(float)
    a = h[..., 3:4]/255.0*k
    d[..., :3] = np.clip(d[..., :3] + a*np.array(color), 0, 255)
    return Image.fromarray(d.astype(np.uint8))

CS = 224
def head(warm=0.0, recoil=0.0, heat_k=0.0):
    wx = round(1.2*4*warm); wy = round(0.5*4*warm); ry = round(3.5*4*recoil)
    c = Image.new('RGBA', (CS, CS))
    c.alpha_composite(shift(wlo, -wx, wy)); c.alpha_composite(shift(wro, wx, wy))
    c.alpha_composite(shift(wl, -wx, wy)); c.alpha_composite(shift(wr, wx, wy))
    c.alpha_composite(bo); c.alpha_composite(body)
    if heat_k: c = additive(c, heat, k=heat_k)
    c.alpha_composite(shift(baro, 0, ry)); c.alpha_composite(shift(bar, 0, ry))
    if heat_k: c = additive(c, shift(bheat, 0, ry), k=heat_k)
    return c

def place(scene, cx, cy, rot_deg, warm=0, recoil=0, heat_k=0):
    scene.paste(base, (cx-48, cy-48), base)
    sh = np.array(prev); sh[..., :3] = 0; sh[..., 3] = (sh[..., 3] > 0)*56
    shi = Image.fromarray(sh).rotate(rot_deg, resample=Image.NEAREST)
    scene.paste(shi, (cx-CS//2-6, cy-CS//2+6), shi)
    h = head(warm, recoil, heat_k)
    off = round(1*4*recoil)
    h = shift(h, 0, off).rotate(rot_deg, resample=Image.NEAREST)
    scene.paste(h, (cx-CS//2, cy-CS//2), h)

scene = floor.copy()
place(scene, 80, 112, 0)
place(scene, 224, 112, -38, warm=1.0, recoil=0.45, heat_k=0.85)
d = ImageDraw.Draw(scene)
import math
ang = math.radians(90-38)  # direction of turret B
for i in range(7):
    t = 104 + i*7
    x = 224 + math.cos(ang)*t; y = 112 - math.sin(ang)*t
    r = 1 if i < 6 else 3
    col = (255, 77, 94, 90+i*20) if i < 6 else (255, 143, 154, 255)
    d.ellipse([x-r, y-r, x+r, y+r], fill=col)
scene.save(f'{OUT}/ingame_1x.png')
scene.resize((TW*32*3, TH*32*3), Image.NEAREST).save(f'{OUT}/ingame.png')

# ---------------- poster
F = '/usr/share/fonts/liberation-sans/LiberationSans-'
fB = lambda s: ImageFont.truetype(F+'Bold.ttf', s)
fR = lambda s: ImageFont.truetype(F+'Regular.ttf', s)
W, H = 1920, 1080
g = np.linspace(0, 1, H)[:, None, None]
bg = (np.array([20, 20, 25])*(1-g) + np.array([12, 12, 15])*g)*np.ones((1, W, 1))
P = Image.fromarray(bg.astype(np.uint8)).convert('RGBA')
d = ImageDraw.Draw(P)
d.rectangle([40, 34, 48, 96], fill=(255, 43, 69))
d.text((64, 28), 'ДАЛЬНОБОЙНАЯ АРТИЛЛЕРИЯ КИБРАН', font=fB(46), fill=(236, 238, 244))
d.text((66, 84), 'Supreme Commander 2  •  фан-модель  →  Mindustry (мод, v7 / build 146+)', font=fR(22), fill=(150, 153, 165))
hero = Image.open(f'{OUT}/hero.png').convert('RGBA').resize((1120, 800), Image.LANCZOS)
P.alpha_composite(hero, (40, 126))
d.rectangle([40, 126, 1159, 925], outline=(52, 53, 62), width=2)
X = 1210
d.text((X, 122), 'В игре (макет, ×2): слева покой, справа залп', font=fB(22), fill=(220, 222, 230))
P.alpha_composite(scene.resize((640, 384), Image.NEAREST), (X, 158))
d.text((X, 566), 'Спрайты, отрендеренные из 3D-модели', font=fB(22), fill=(220, 222, 230))
P.alpha_composite(base.resize((192, 192), Image.NEAREST), (X, 640))
P.alpha_composite(head().resize((320, 320), Image.NEAREST), (X+230, 600))
d.text((X, 842), 'основание 3×3', font=fR(18), fill=(150, 153, 165))
d.text((X+300, 912), 'башня: корпус + крылья + ствол', font=fR(18), fill=(150, 153, 165))
hs = Image.new('RGBA', (CS, CS), (40, 12, 16, 255)); hs = additive(hs, heat); hs = additive(hs, bheat)
P.alpha_composite(hs.resize((96, 96), Image.NEAREST), (X+560, 640))
d.text((X+560, 744), 'heat', font=fR(18), fill=(150, 153, 165))
y = 960
d.line([40, 945, 1880, 945], fill=(52, 53, 62), width=2)
d.text((40, y), 'Размер 3×3  •  Прочность 2400  •  Дальность 150 клеток  •  Перезарядка 1,7 с  •  Только наземные цели  •  Охлаждение ×3',
       font=fR(24), fill=(210, 212, 220))
d.text((40, y+44), 'Снаряды: графит — фугас  •  кремний — самонаведение  •  пиротит — поджог  •  взрывчатая смесь — кассета  •  кинетический сплав — ЭМИ + молнии',
       font=fR(24), fill=(255, 120, 135))
P.convert('RGB').save(f'{OUT}/poster.png')
print('ok')
