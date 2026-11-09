"""Procedural sounds for Vanguard Arsenal 2.0 stage 1 (original synthesis, no ripped assets)."""
import numpy as np, wave, os, subprocess
SR = 44100
OUT = '/data/vg2/out/sounds'; os.makedirs(OUT, exist_ok=True)
R = np.random.default_rng(11)

def t_(d): return np.arange(int(SR*d))/SR
def spec_filter(x, H):
    X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1/SR)
    return np.fft.irfft(X*H(f), len(x))
def lp(x, fc, o=2): return spec_filter(x, lambda f: 1/np.sqrt(1+(f/fc)**(2*o)))
def hp(x, fc, o=2): return spec_filter(x, lambda f: (f/fc)**o/np.sqrt(1+(f/fc)**(2*o)))
def bp(x, lo, hi): return hp(lp(x, hi), lo)
def env(t, tau, a=0.002): return np.minimum(t/a, 1.0)*np.exp(-t/tau)
def sweep(t, f0, f1, tau): return np.sin(2*np.pi*np.cumsum(f1+(f0-f1)*np.exp(-t/tau))/SR)
def noise(n): return R.normal(0, 1, n)
def at(dst, src, sec, g=1.0):
    i = int(sec*SR); n = min(len(src), len(dst)-i)
    if n > 0: dst[i:i+n] += src[:n]*g
def metal(t, fr, tau):
    s = np.zeros_like(t)
    for k, f in enumerate(fr): s += np.sin(2*np.pi*f*t+R.uniform(0, 6))*np.exp(-t/(tau/(1+0.4*k)))/(1+0.6*k)
    return s
def crackle(t, rate, tau):
    s = np.zeros_like(t); n = int(rate*t[-1])
    for c in np.sort(R.uniform(0, t[-1], n)):
        i = int(c*SR); L = int(SR*0.002*R.uniform(0.5, 2))
        if i+L < len(t): s[i:i+L] += noise(L)*np.exp(-np.arange(L)/(L/3))*np.exp(-c/tau)*R.uniform(0.3, 1)
    return s
def reverb(x, mix=0.25, size=0.9):
    y = x.copy()
    for d, g in ((0.031, .5), (0.057, .38), (0.089, .3), (0.13, .22), (0.19, .15), (0.27, .1)):
        i = int(d*size*SR); y[i:] += lp(x, 2500)[:len(x)-i]*g*mix*2
    return y
def save(x, name, loop=False, peak=0.9):
    x = x - x.mean()
    if loop:
        n = int(0.04*SR); fade = np.linspace(0, 1, n)
        x[:n] = x[:n]*fade + x[-n:]*(1-fade); x = x[:-n]
    else:
        n = int(0.01*SR); x[-n:] *= np.linspace(1, 0, n)
    x = np.tanh(1.4*x/np.max(np.abs(x)+1e-9))
    x = x/np.max(np.abs(x))*peak
    w = f'{OUT}/{name}.wav'
    with wave.open(w, 'wb') as f:
        f.setnchannels(1); f.setsampwidth(2); f.setframerate(SR); f.writeframes((x*32767).astype(np.int16).tobytes())
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', w, '-c:a', 'libvorbis', '-q:a', '5', f'{OUT}/{name}.ogg'], check=True)
    os.remove(w)

# Howl mortar shot: tube thump + breech clank + muzzle blast + tail
t = t_(1.5); x = np.zeros_like(t)
x += sweep(t, 110, 36, 0.06)*env(t, 0.28)*1.2
x += lp(noise(len(t)), 1100)*env(t, 0.07)*0.9
x += lp(noise(len(t)), 300)*env(t, 0.45, 0.01)*0.5
x += metal(t, (540, 1320, 2230, 3140), 0.14)*0.25
x += np.sin(2*np.pi*186*t)*env(t, 0.22)*0.3
at(x, metal(t_(0.3), (880, 1710, 2650), 0.05)*0.2, 0.28)
save(reverb(x, 0.3), 'howl-shoot')
# HE impact
t = t_(2.0); x = np.zeros_like(t)
n = noise(len(t)); fc = 200 + 3800*np.exp(-t/0.08)
x += (lp(n, 3500)*np.exp(-t/0.05) + lp(n, 600)*env(t, 0.35, 0.004))*1.0
x += sweep(t, 80, 28, 0.15)*env(t, 0.55, 0.003)*1.3
x += crackle(t, 140, 0.4)*0.35
save(reverb(x, 0.35, 1.2), 'howl-hit')
# incendiary impact: whoosh + fire crackle
t = t_(1.8); x = np.zeros_like(t)
x += bp(noise(len(t)), 250, 2200)*np.minimum(t/0.06, 1)*np.exp(-t/0.5)*0.9
x += sweep(t, 70, 35, 0.12)*env(t, 0.3)*0.7
x += crackle(t, 260, 0.9)*0.6
save(reverb(x, 0.25), 'howl-fire')
# incoming shell whistle (descending, crescendo)
t = t_(1.6)
f = 1900 - 1150*(t/t[-1])**1.3 + 9*np.sin(2*np.pi*6*t)
x = np.sin(2*np.pi*np.cumsum(f)/SR)*0.7 + bp(noise(len(t)), 900, 3000)*0.18
x *= np.minimum(t/0.9, 1)**2*(1 - np.clip((t-1.5)/0.1, 0, 1))
save(x, 'vg-shell-whistle')
# separator loop (2 s, integer cycles)
t = t_(2.04); x = np.zeros_like(t)
for h, g in ((60, .5), (120, .3), (180, .15)): x += np.sin(2*np.pi*h*t)*g
x += np.sin(2*np.pi*420*t)*(0.5+0.5*np.sin(2*np.pi*3*t))*0.22
x += lp(noise(len(t)), 220)*0.6
x += crackle(t, 30, 99)*0.15
save(x, 'separator-loop', loop=True, peak=0.6)
# smelter roar loop
t = t_(2.04); x = lp(noise(len(t)), 480)*(0.7+0.3*np.sin(2*np.pi*1*t))
x += np.sin(2*np.pi*50*t)*0.25 + crackle(t, 90, 99)*0.25
save(x, 'smelter-loop', loop=True, peak=0.6)
# press loop: two hydraulic strokes
t = t_(2.04); x = np.zeros_like(t)
for s in (0.05, 1.07):
    tt = t_(0.9)
    stroke = sweep(tt, 120, 55, 0.05)*env(tt, 0.12)*1.0 + metal(tt, (690, 1460, 2380), 0.06)*0.3
    hiss = hp(noise(len(tt)), 2500)*np.clip((tt-0.12)/0.03, 0, 1)*np.exp(-np.clip(tt-0.12, 0, None)/0.18)*0.3
    at(x, stroke+hiss, s)
save(x, 'press-loop', loop=True, peak=0.65)
# point-defence zap
t = t_(0.35)
x = sweep(t, 3400, 900, 0.05)*env(t, 0.07)*0.8 + np.sin(2*np.pi*(220*t+30*np.sin(2*np.pi*55*t)))*env(t, 0.12)*0.4 + hp(noise(len(t)), 3000)*env(t, 0.01)*0.4
save(x, 'pd-zap')
# beacon sonar ping loop (3 s)
t = t_(3.04); x = np.sin(2*np.pi*110*t)*0.05
for d, g in ((0, 1), (0.26, .4), (0.52, .16)):
    tt = t_(1.2); at(x, (np.sin(2*np.pi*1320*tt)+0.3*np.sin(2*np.pi*2640*tt))*env(tt, 0.35, 0.004)*g, 0.02+d)
save(x, 'beacon-loop', loop=True, peak=0.55)
# shield hum loop
t = t_(2.04); x = np.zeros_like(t)
for h, g in ((120, .5), (120.5, .4), (240, .25), (360.5, .12)): x += np.sin(2*np.pi*h*t)*g
x += crackle(t, 12, 99)*0.1
save(x, 'shield-hum', loop=True, peak=0.5)
# shield hit
t = t_(0.55)
x = sweep(t, 220, 90, 0.08)*env(t, 0.16)*0.9 + hp(noise(len(t)), 1500)*env(t, 0.04)*0.4 + metal(t, (1250, 2900), 0.08)*0.25
save(reverb(x, 0.2), 'shield-hit')
# shield break: glass shatter + collapse
t = t_(1.6); x = np.zeros_like(t)
for k in range(40):
    tt = t_(0.4); fr = R.uniform(2000, 6500)
    at(x, np.sin(2*np.pi*fr*tt)*np.exp(-tt/R.uniform(0.03, 0.12))*R.uniform(0.2, 0.6), R.uniform(0, 0.35))
x += sweep(t, 900, 80, 0.25)*env(t, 0.5)*0.6 + lp(noise(len(t)), 2000)*env(t, 0.12)*0.6
save(reverb(x, 0.3), 'shield-break')
print(sorted(os.listdir(OUT)))
