"""In-game style firing clip (top-down, Mindustry look) with synthesized soundtrack.
Simulates the turret logic from the mod: rotateSpeed 1.6, warmup 0.06, charge 40 ticks, reload 100,
recoil/heat decay, shell flight at 3.4 wu/tick, effects as configured in cybran-lra.hjson."""
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

TW, TH = 16, 9; W1, H1 = TW*32, TH*32; K = 2           # sprite px canvas, output scale
PX = 4*K                                                # output px per world unit
random.seed(5)

# ---------------------------------------------------------------- floor
floor = Image.new('RGBA', (W1, H1)); fd = ImageDraw.Draw(floor)
for ty in range(TH):
    for tx in range(TW):
        x, y = tx*32, ty*32
        dark = (tx >= 10)
        pal = [(82, 85, 94), (77, 80, 89), (88, 91, 100)] if not dark else [(70, 66, 64), (64, 61, 59), (76, 72, 69)]
        fill = random.choice([pal[0], pal[0], pal[0], pal[1], pal[2]])
        fd.rectangle([x, y, x+31, y+31], fill=fill+(255,))
        hi = tuple(min(255, c+14) for c in fill); lo = tuple(max(0, c-20) for c in fill)
        fd.line([x, y, x+31, y], fill=hi+(255,)); fd.line([x, y, x, y+31], fill=hi+(255,))
        fd.line([x, y+31, x+31, y+31], fill=lo+(255,)); fd.line([x+31, y, x+31, y+31], fill=lo+(255,))
        for (bx, by) in ((3, 3), (28, 3), (3, 28), (28, 28)):
            fd.point((x+bx, y+by), fill=lo+(255,))
        if dark and random.random() < 0.25:
            for _ in range(3):
                px, py = x+random.randint(4, 27), y+random.randint(4, 27)
                fd.point((px, py), fill=(56, 53, 51, 255))

# ---------------------------------------------------------------- enemy blocks (purple team)
TEAM = (162, 124, 229)
def wall(d, tx, ty):
    x, y = tx*32, ty*32
    d.rectangle([x+1, y+1, x+30, y+30], fill=(146, 98, 72, 255))
    d.rectangle([x+3, y+3, x+28, y+28], fill=(176, 120, 88, 255))
    d.line([x+3, y+3, x+28, y+3], fill=(205, 150, 112, 255)); d.line([x+3, y+3, x+3, y+28], fill=(205, 150, 112, 255))
    d.line([x+3, y+28, x+28, y+28], fill=(118, 78, 58, 255)); d.line([x+28, y+3, x+28, y+28], fill=(118, 78, 58, 255))
    d.rectangle([x+12, y+12, x+19, y+19], fill=(132, 88, 64, 255))
def eturret(d, tx, ty):
    x, y = tx*32, ty*32
    d.rectangle([x+2, y+2, x+61, y+61], fill=(70, 72, 82, 255))
    d.rectangle([x+6, y+6, x+57, y+57], fill=(96, 98, 110, 255))
    d.rectangle([x+6, y+6, x+57, y+9], fill=TEAM+(255,)); d.rectangle([x+6, y+54, x+57, y+57], fill=TEAM+(255,))
    d.ellipse([x+16, y+16, x+47, y+47], fill=(120, 122, 136, 255), outline=(60, 62, 70, 255), width=2)
    d.rectangle([x+27, y+0, x+36, y+30], fill=(140, 142, 156, 255), outline=(60, 62, 70, 255))
    d.ellipse([x+26, y+26, x+37, y+37], fill=TEAM+(255,))
enemy_tiles = [('t', 12, 2), ('w', 11, 1), ('w', 11, 2), ('w', 11, 3), ('w', 11, 4), ('w', 12, 4), ('w', 13, 4), ('w', 14, 2), ('w', 14, 3)]
TARGET = (12*32+32, 2*32+32)   # enemy turret centre (sprite px)

def draw_enemies(img, alive, flash):
    d = ImageDraw.Draw(img)
    for k, tx, ty in enemy_tiles:
        if alive: (eturret if k == 't' else wall)(d, tx, ty)
    if alive and flash > 0:
        a = np.array(img).astype(float)
        for k, tx, ty in enemy_tiles:
            s = 64 if k == 't' else 32
            sl = a[ty*32:ty*32+s, tx*32:tx*32+s, :3]; sl += (255-sl)*flash*0.8
        img = Image.fromarray(a.astype(np.uint8))
    return img

rubble = Image.new('RGBA', (W1, H1)); rd = ImageDraw.Draw(rubble)
random.seed(9)
for k, tx, ty in enemy_tiles:
    s = 64 if k == 't' else 32
    x, y = tx*32, ty*32
    for _ in range(14 if s == 64 else 6):
        cx, cy = x+random.randint(2, s-3), y+random.randint(2, s-3); r = random.randint(2, 6 if s == 64 else 4)
        rd.ellipse([cx-r, cy-r, cx+r, cy+r], fill=(38, 34, 34, 200))
    for _ in range(10 if s == 64 else 4):
        cx, cy = x+random.randint(2, s-3), y+random.randint(2, s-3)
        rd.rectangle([cx, cy, cx+random.randint(1, 3), cy+random.randint(1, 2)], fill=(110, 84, 70, 255))
rubble = rubble.filter(ImageFilter.GaussianBlur(0.6))
scorch = Image.new('RGBA', (W1, H1))

# ---------------------------------------------------------------- turret head
def shift(im, dx, dy):
    out = Image.new('RGBA', im.size); out.alpha_composite(im, (dx, dy)); return out
def additive(dst, h_im, color, k):
    if k <= 0.003: return dst
    d = np.array(dst).astype(float); h = np.array(h_im).astype(float)
    a = h[..., 3:4]/255.0*k
    d[..., :3] = np.clip(d[..., :3] + a*np.array(color), 0, 255)
    return Image.fromarray(d.astype(np.uint8))
def head(warm, recoil, heat_k, charge):
    wx = round(1.2*4*warm); wy = round(0.5*4*warm); ry = round(3.5*4*recoil)
    c = Image.new('RGBA', (160, 160))
    c.alpha_composite(shift(wlo, -wx, wy)); c.alpha_composite(shift(wro, wx, wy))
    c.alpha_composite(shift(wl, -wx, wy)); c.alpha_composite(shift(wr, wx, wy))
    c.alpha_composite(bo); c.alpha_composite(body)
    c = additive(c, heat, (255, 58, 79), heat_k)
    c.alpha_composite(shift(baro, 0, ry)); c.alpha_composite(shift(bar, 0, ry))
    c = additive(c, shift(bheat, 0, ry), (255, 58, 79), heat_k)
    c = additive(c, shift(coil, 0, ry), (255, 42, 69), charge)
    return c

TUR = (96, 160)   # turret centre (sprite px) - tiles 1.5..4.5 x 3.5..6.5
shadow = np.array(prev); shadow[..., :3] = 0; shadow[..., 3] = (shadow[..., 3] > 0)*56; shadow = Image.fromarray(shadow)

# ---------------------------------------------------------------- simulation (60 ticks/s)
dx, dy = TARGET[0]-TUR[0], TARGET[1]-TUR[1]
AIM = -math.degrees(math.atan2(dx, -dy))       # PIL rotation (ccw +); 0 = facing up
DIST = math.hypot(dx, dy)/4                       # world units
FLIGHT = int(round(DIST/3.4))
TICKS = 372
CHARGES = [52, 152]; SHOTS = [c+40 for c in CHARGES]; HITS = [s+FLIGHT for s in SHOTS]
DESTROY = HITS[1]
print('aim', AIM, 'dist wu', DIST, 'flight ticks', FLIGHT, 'shots', SHOTS, 'hits', HITS)

state = []
rot, warm, rec, ht = 0.0, 0.0, 0.0, 0.0
for t in range(TICKS+1):
    has_target = t < DESTROY + 8
    if has_target:
        diff = AIM-rot; rot += max(-1.6, min(1.6, diff))
        warm += (1-warm)*0.06
    else:
        warm += (0-warm)*0.06
    if t in SHOTS: rec, ht = 1.0, 1.0
    else:
        rec = max(0.0, rec-1/100); ht = max(0.0, ht-1/90)
    ch = 0.0
    for c in CHARGES:
        if c <= t < c+40: ch = (t-c)/40
    state.append(dict(rot=rot, warm=warm, rec=rec, heat=ht, charge=ch))

def muzzle(t, extra=0.0):
    s = state[t]; a = math.radians(-s['rot'])  # clockwise from up
    r = (16 - 1.0*s['rec']**1.8 - 3.5*s['rec'] + extra)*4
    return TUR[0] + math.sin(a)*r, TUR[1] - math.cos(a)*r, a

# shake: (start, intensity wu, duration ticks)
SHAKES = [(s, 2.5, 18) for s in SHOTS] + [(h, 2.0, 16) for h in HITS[:1]] + [(HITS[1], 4.0, 26)]
def shake_at(t):
    amp = 0.0
    for s0, i, dur in SHAKES:
        if s0 <= t < s0+dur: amp = max(amp, i*(1-(t-s0)/dur))
    r = random.Random(t*7919)
    return r.uniform(-amp, amp)*PX*0.5, r.uniform(-amp, amp)*PX*0.5

# ---------------------------------------------------------------- effect drawing (output px space)
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

def wrand(seed):
    return random.Random(seed)

def fx_layer(t, ox, oy):
    lay = Image.new('RGBA', (W1*K, H1*K)); d = ImageDraw.Draw(lay, 'RGBA')
    def P(x, y): return x*K+ox, y*K+oy
    # --- charge (ParticleEffect converging + WaveEffect shrinking)
    for c in CHARGES:
        if c <= t < c+40:
            fin = (t-c)/40; mx, my, a = muzzle(t); X, Y = P(mx, my)
            r = wrand(c)
            for i in range(14):
                ang = r.uniform(0, 2*math.pi); fr = r.random()
                l = (22 - 22*fin)*fr
                col = lerpc('ffd6dc', 'ff3355', fin) + (230,)
                circ(d, X+math.cos(ang)*l*PX, Y+math.sin(ang)*l*PX, (0.6+1.6*fin)*PX, col)
            ring(d, X, Y, (18-16*fin)*PX, (0.4+2.0*fin)*PX, lerpc('ff3355', 'ff3355', fin)+(int(255*fin),))
    # --- muzzle flash + smoke
    for s in SHOTS:
        e = t-s
        if 0 <= e < 60:
            mx, my, a = muzzle(s); X, Y = P(mx, my)
            r = wrand(s*3)
            fin = e/60
            for i in range(8):
                ang = a + math.radians(r.uniform(-28, 28)); l = (4 + 22*fin)*r.random()
                sz = 4.5*(1-fin)
                circ(d, X+math.sin(ang)*l*PX, Y-math.cos(ang)*l*PX, sz*PX, lerpc('6a5a5f', '3a3035', fin)+(int(200*(1-fin*0.6)),))
        if 0 <= e < 18:
            mx, my, a = muzzle(s); X, Y = P(mx, my)
            fin = e/18; r = wrand(s*5)
            for i in range(9):
                ang = a + math.radians(r.uniform(-22, 22)); l = (2 + 26*fin)*r.random()
                ln = 9 - 7*fin; x0, y0 = X+math.sin(ang)*l*PX, Y-math.cos(ang)*l*PX
                seg(d, x0, y0, x0+math.sin(ang)*ln*PX, y0-math.cos(ang)*ln*PX, (2-2*fin)*PX, lerpc('ffd6dc', 'ff3355', fin)+(255,))
            if e < 14:
                f2 = e/14
                ring(d, X, Y, (2+14*f2)*PX, (3-3*f2)*PX, lerpc('ffd6dc', 'ff3355', f2)+(255,))
            if e < 4:
                circ(d, X, Y, (5-e)*PX*0.9, (255, 235, 238, 230))
        # casings (casing3Double)
        if 0 <= e < 40:
            fin = e/40; sr = state[s]['rot']; a = math.radians(-sr)
            cx, cy = TUR[0]-math.sin(a)*3*4, TUR[1]+math.cos(a)*3*4
            for sgn in (-1, 1):
                ln = (2 + (1-(1-fin)**2)*10)*sgn*4
                lr = a + math.pi/2 + math.radians(fin*20*sgn)
                px_, py_ = cx + math.sin(lr)*ln, cy - math.cos(lr)*ln
                X, Y = P(px_, py_)
                col = lerpc('ffd37f', 'a0a0a8', fin) + (int(255*min(1, (1-fin)*2)),)
                ang = lr + math.radians(fin*50*sgn)
                hw, hh = 1.25*PX, 2*PX
                pts = [(-hw, -hh), (hw, -hh), (hw, hh), (-hw, hh)]
                pts = [(X + px*math.cos(ang) - py*math.sin(ang), Y + px*math.sin(ang) + py*math.cos(ang)) for px, py in pts]
                d.polygon(pts, fill=col)
    # --- shells + trails
    for s, h in zip(SHOTS, HITS):
        if s <= t < h:
            mx, my, a = muzzle(s)
            def pos(tt):
                f = (tt-s)/FLIGHT
                return mx + (TARGET[0]-mx)*f, my + (TARGET[1]-my)*f, f
            # artilleryTrail puffs
            for tt in range(s, t, 3):
                x, y, f = pos(tt); age = (t-tt)/50
                if age < 1:
                    sl = (0.5-abs(f-0.5))*2
                    X, Y = P(x, y); circ(d, X, Y, (1.2+3*sl)*(1-age)*PX, hexa('a82a38', 0.75))
            # ribbon trail (10 points)
            pts = [pos(max(s, t-i)) for i in range(10)]
            for i in range(9):
                x0, y0, _ = pts[i]; x1, y1, _ = pts[i+1]
                w = 2.4*(1-i/9)*PX
                X0, Y0 = P(x0, y0); X1, Y1 = P(x1, y1)
                seg(d, X0, Y0, X1, Y1, w, hexa('ff3355', 0.9))
            x, y, f = pos(t); sl = (0.5-abs(f-0.5))*2; sc = 1 + 0.8*sl
            X, Y = P(x, y); ang = math.atan2(TARGET[1]-my, TARGET[0]-mx)
            for (hw, hh, col) in ((2.7, 4.3, 'a82a38'), (1.7, 2.9, 'ff8f9a')):
                pts2 = []
                for k in range(16):
                    th = 2*math.pi*k/16; ex, ey = hh*math.cos(th)*sc*PX, hw*math.sin(th)*sc*PX
                    pts2.append((X + ex*math.cos(ang) - ey*math.sin(ang), Y + ex*math.sin(ang) + ey*math.cos(ang)))
                d.polygon(pts2, fill=hexa(col))
    # --- explosions (ExplosionEffect as configured)
    for i, h in enumerate(HITS):
        big = (i == 1)
        e = t-h; life = 30 if big else 26
        if 0 <= e < life + (40 if big else 0):
            X, Y = P(*TARGET); fin = min(1, e/life); fout = 1-fin; finpow = 1-(1-fin)**3
            r = wrand(h)
            if e < life:
                if e < 9:
                    f9 = e/9; ring(d, X, Y, (38+8*big)*f9*PX, 4*(1-f9)*PX, hexa('ff3355'))
                for k in range(9 if big else 7):
                    ang = r.uniform(0, 2*math.pi); l = (2 + (34+6*big)*finpow)*r.random()
                    circ(d, X+math.cos(ang)*l*PX, Y+math.sin(ang)*l*PX, (fout*5+0.5)*PX, hexa('5a1a22', 0.85))
                for k in range(12 if big else 8):
                    ang = r.uniform(0, 2*math.pi); l = (1 + (43+6*big)*finpow)*r.random()
                    x0, y0 = X+math.cos(ang)*l*PX, Y+math.sin(ang)*l*PX; ln = (1+fout*5)*PX
                    seg(d, x0, y0, x0+math.cos(ang)*ln, y0+math.sin(ang)*ln, 1.6*fout*PX, hexa('ff8a96'))
                if e < 6:
                    circ(d, X, Y, (14-2*e)*PX*(1.3 if big else 1), (255, 200, 205, int(220*(1-e/6))))
            if big:  # block destruction: debris + lingering smoke
                f2 = e/(life+40)
                for k in range(16):
                    ang = r.uniform(0, 2*math.pi); l = (4 + 30*(1-(1-f2)**2))*r.uniform(0.3, 1)
                    circ(d, X+math.cos(ang)*l*PX, Y+math.sin(ang)*l*PX - f2*6*PX, (3.5*(1-f2)+0.5)*PX, (70, 64, 66, int(170*(1-f2))))
    # --- lingering fires on rubble
    if t > DESTROY:
        r = wrand(77)
        for k in range(5):
            fx_, fy_ = TARGET[0]+r.uniform(-40, 40), TARGET[1]+r.uniform(-34, 34)
            ph = (t*0.35 + k*1.7)
            X, Y = P(fx_, fy_); fl = 0.6+0.4*math.sin(ph*3.1)
            circ(d, X, Y, 2.2*fl*PX, (255, 120, 60, 150)); circ(d, X, Y, 1.1*fl*PX, (255, 210, 120, 200))
            sm = ((t + k*13) % 40)/40
            circ(d, X+sm*3*PX, Y-sm*12*PX, (1.5+2.5*sm)*PX, (60, 56, 58, int(120*(1-sm))))
    return lay

# ---------------------------------------------------------------- render frames (30 fps -> every 2 ticks)
font = ImageFont.truetype('/usr/share/fonts/liberation-sans/LiberationSans-Bold.ttf', 22)
font2 = ImageFont.truetype('/usr/share/fonts/liberation-sans/LiberationSans-Regular.ttf', 16)
fi = 0
for t in range(0, TICKS, 2):
    s = state[t]
    sc = floor.copy()
    if t >= DESTROY: sc.alpha_composite(rubble)
    flash = 0.0
    for h in HITS[:1]:
        if 0 <= t-h < 8: flash = 1-(t-h)/8
    sc = draw_enemies(sc, t < DESTROY, flash)
    # turret
    sc.alpha_composite(base, (TUR[0]-48, TUR[1]-48))
    sc.alpha_composite(shadow.rotate(s['rot'], resample=Image.NEAREST), (TUR[0]-80-6, TUR[1]-80+6))
    hd = head(s['warm'], s['rec'], s['heat'], s['charge'])
    off = round(4*s['rec']**1.8)
    sc.alpha_composite(shift(hd, 0, off).rotate(s['rot'], resample=Image.NEAREST), (TUR[0]-80, TUR[1]-80))
    big = sc.resize((W1*K, H1*K), Image.NEAREST)
    ox, oy = shake_at(t)
    big.alpha_composite(fx_layer(t, 0, 0))
    if abs(ox) + abs(oy) > 0.5:
        frame = Image.new('RGBA', big.size, (30, 30, 34, 255)); frame.alpha_composite(big, (int(ox), int(oy))); big = frame
    dd = ImageDraw.Draw(big)
    dd.rectangle([0, H1*K-40, W1*K, H1*K], fill=(14, 12, 16, 170))
    dd.text((16, H1*K-32), 'CYBRAN ARSENAL', font=font, fill=(255, 64, 86))
    dd.text((236, H1*K-29), 'Дальнобойная артиллерия Кибран  ·  мод для Mindustry  ·  зарядка → выстрел → ЭМИ/фугас', font=font2, fill=(225, 220, 228))
    big.convert('RGB').save(f'{FR}/f{fi:04d}.png'); fi += 1
print('frames', fi)

# ---------------------------------------------------------------- soundtrack (stereo, panned)
SR = 44100; dur = TICKS/60
mix = np.zeros((int(SR*dur)+SR, 2))
def load(n):
    w = wave.open(f'{OUT}/sounds/{n}.wav'); x = np.frombuffer(w.readframes(w.getnframes()), np.int16)/32767; return x
def put(n, tick, gain, pan):
    x = load(n); i = int(tick/60*SR); m = min(len(x), len(mix)-i)
    l, r = math.cos((pan+1)*math.pi/4), math.sin((pan+1)*math.pi/4)
    mix[i:i+m, 0] += x[:m]*gain*l*1.41; mix[i:i+m, 1] += x[:m]*gain*r*1.41
hum = load('cybran-lra-hum'); n_h = int((DESTROY+40)/60*SR)
hl = np.tile(hum, n_h//len(hum)+1)[:n_h]*0.22
hl *= np.minimum(1, np.arange(n_h)/(0.3*SR)); hl[-int(0.6*SR):] *= np.linspace(1, 0, int(0.6*SR))
mix[:n_h, 0] += hl*0.9; mix[:n_h, 1] += hl*0.6
for c in CHARGES: put('cybran-lra-charge', c, 0.55, -0.45)
for s in SHOTS: put('cybran-lra-shoot', s, 0.95, -0.4)
put('cybran-lra-hit', HITS[0], 0.7, 0.55)
put('cybran-lra-hit', HITS[1], 0.85, 0.55); put('cybran-lra-fire', HITS[1]+10, 0.45, 0.6)
mix = mix[:int(SR*dur)]
mix = np.tanh(mix*1.1); mix *= 0.92/np.max(np.abs(mix))
mix[-int(0.25*SR):] *= np.linspace(1, 0, int(0.25*SR))[:, None]
w = wave.open(f'{OUT}/video_audio.wav', 'wb'); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
w.writeframes((mix*32767).astype(np.int16).tobytes()); w.close()

subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-framerate', '30', '-i', f'{FR}/f%04d.png', '-i', f'{OUT}/video_audio.wav',
                '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '18', '-preset', 'slow', '-c:a', 'aac', '-b:a', '160k',
                '-shortest', '-movflags', '+faststart', f'{OUT}/cybran-lra-ingame.mp4'], check=True)
subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-framerate', '30', '-i', f'{FR}/f%04d.png', '-vf',
                'fps=20,scale=640:-1:flags=lanczos,split[a][b];[a]palettegen=max_colors=128[p];[b][p]paletteuse=dither=bayer:bayer_scale=4',
                f'{OUT}/cybran-lra-ingame.gif'], check=True)
print('done', os.path.getsize(f'{OUT}/cybran-lra-ingame.mp4'), os.path.getsize(f'{OUT}/cybran-lra-ingame.gif'))
