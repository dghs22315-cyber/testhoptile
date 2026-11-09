"""Procedurally synthesized sounds for the Cybran LRA (original, not ripped from SC2).
Outputs 44.1 kHz mono WAV + OGG Vorbis (Mindustry mods load sounds/*.ogg)."""
import numpy as np, wave, os, subprocess

SR = 44100
OUT = '/data/cybran/out/sounds'
os.makedirs(OUT, exist_ok=True)
rng = np.random.default_rng(7)

def t_(dur): return np.arange(int(SR*dur))/SR

def lp(x, fc):
    """one-pole lowpass; fc may be scalar or per-sample array"""
    fc = np.broadcast_to(np.asarray(fc, float), x.shape)
    a = 1 - np.exp(-2*np.pi*fc/SR)
    y = np.empty_like(x); s = 0.0
    for i in range(len(x)):
        s += a[i]*(x[i]-s); y[i] = s
    return y

def lp2(x, fc): return lp(lp(x, fc), fc)
def hp(x, fc): return x - lp(x, fc)

def env_exp(t, tau, attack=0.002):
    return np.minimum(t/attack, 1.0)*np.exp(-t/tau)

def sweep(t, f0, f1, tau):
    f = f1 + (f0-f1)*np.exp(-t/tau)
    return np.sin(2*np.pi*np.cumsum(f)/SR)

def pad(x, dur):
    n = int(SR*dur)
    return np.pad(x, (0, max(0, n-len(x))))[:n]

def at(dst, src, sec, gain=1.0):
    i = int(sec*SR); n = min(len(src), len(dst)-i)
    if n > 0: dst[i:i+n] += src[:n]*gain

def echo(x, delays=((0.047, 0.32), (0.083, 0.22), (0.131, 0.14), (0.197, 0.08)), damp=2500):
    y = x.copy()
    for d, g in delays:
        i = int(d*SR); y[i:] += lp(x, damp)[:len(x)-i]*g
    return y

def metal(t, freqs=(412, 1131, 1873, 2690), tau=0.18, seed=0):
    r = np.random.default_rng(seed); s = np.zeros_like(t)
    for k, f in enumerate(freqs):
        s += np.sin(2*np.pi*f*t + r.uniform(0, 6.28))*np.exp(-t/(tau/(1+0.35*k)))/(1+k*0.6)
    return s

def crackle(t, rate, tau, seed=1, width=0.0015):
    r = np.random.default_rng(seed); s = np.zeros_like(t)
    n = int(rate*t[-1]); ts = np.sort(r.uniform(0, t[-1], n))
    for c in ts:
        i = int(c*SR); L = int(width*SR*r.uniform(0.5, 2))
        if i+L >= len(t): continue
        s[i:i+L] += r.normal(0, 1, L)*np.exp(-np.arange(L)/(L/3))*np.exp(-c/tau)*r.uniform(0.3, 1)
    return s

def finish(x, name, peak=0.89, drive=1.6):
    x = x - np.mean(x)
    x = np.tanh(drive*x/np.max(np.abs(x)))
    x *= peak/np.max(np.abs(x))
    fade = int(0.02*SR); x[-fade:] *= np.linspace(1, 0, fade)
    pcm = (x*32767).astype(np.int16)
    w = wave.open(f'{OUT}/{name}.wav', 'wb'); w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes(pcm.tobytes()); w.close()
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', f'{OUT}/{name}.wav', '-c:a', 'libvorbis',
                    '-q:a', '5', f'{OUT}/{name}.ogg'], check=True)
    return x

# ---------------------------------------------------------------- shoot
# magnetic accelerator zap -> heavy cannon thump -> recoil clank -> barrel return servo
D = 1.6; t = t_(D); s = np.zeros_like(t)
crack = hp(rng.normal(0, 1, len(t)), 1800)*env_exp(t, 0.012, 0.0005)
thump = sweep(t, 120, 36, 0.09)*env_exp(t, 0.28, 0.001)
body = lp2(rng.normal(0, 1, len(t)), 900*np.exp(-t/0.15)+120)*env_exp(t, 0.35, 0.002)*2.6
zap = sweep(t, 2600, 260, 0.035)
zap = np.sign(zap)*np.abs(zap)**0.5*env_exp(t, 0.06, 0.0005)*(0.6+0.4*np.sin(2*np.pi*93*t))
clank = metal(t, tau=0.22, seed=3)*0.0
k1 = metal(t_(0.6), (380, 1020, 1710, 2480), 0.16, seed=4)
servo_t = t_(0.9)
servo = (np.sin(2*np.pi*np.cumsum(180+160*np.sin(np.pi*servo_t/0.9))/SR) +
         0.4*np.sin(2*np.pi*np.cumsum(2*(180+160*np.sin(np.pi*servo_t/0.9)))/SR))*np.sin(np.pi*servo_t/0.9)**2
s += crack*0.55 + thump*1.0 + body*0.55 + zap*0.32
at(s, k1, 0.035, 0.30)
at(s, servo, 0.55, 0.05)
at(s, metal(t_(0.3), (520, 1350, 2210), 0.07, seed=9), 1.38, 0.10)
shoot = finish(echo(s), 'cybran-lra-shoot', drive=2.0)

# ---------------------------------------------------------------- charge (0.68 s = 40 ticks)
D = 0.72; t = t_(D); u = t/D
f = 140 + 1700*u**1.6
whine = np.sin(2*np.pi*np.cumsum(f)/SR) + 0.5*np.sin(2*np.pi*np.cumsum(f*2.01)/SR) + 0.25*np.sin(2*np.pi*np.cumsum(f*3.02)/SR)
hum = np.sin(2*np.pi*np.cumsum(55+90*u)/SR)*(0.5+0.5*np.sin(2*np.pi*np.cumsum(8+40*u)/SR))
fizz = hp(rng.normal(0, 1, len(t)), 3000)*u**2
cr = crackle(t, 90, 10, seed=5)*u**1.5
s = (whine*0.45*u**1.2 + hum*0.5*(0.4+0.6*u) + fizz*0.12 + cr*0.5)*np.minimum(t/0.03, 1)
s *= np.where(t > D-0.03, (D-t)/0.03, 1)
charge = finish(s, 'cybran-lra-charge', drive=1.3)

# ---------------------------------------------------------------- hit (heavy HE explosion)
D = 2.2; t = t_(D); s = np.zeros_like(t)
sub = sweep(t, 75, 28, 0.25)*env_exp(t, 0.45, 0.003)
blast = lp2(rng.normal(0, 1, len(t)), 3500*np.exp(-t/0.06)+180)*env_exp(t, 0.55, 0.002)*3.0
snap = hp(rng.normal(0, 1, len(t)), 2500)*env_exp(t, 0.02, 0.0005)
debris = lp(crackle(t, 120, 0.5, seed=11, width=0.003), 4000)
rumble = lp2(rng.normal(0, 1, len(t)), 90)*np.exp(-t/0.9)*np.minimum(t/0.15, 1)*14
s += sub*0.9 + blast*0.75 + snap*0.4 + debris*0.35 + rumble*0.5
hit = finish(echo(s, damp=1600), 'cybran-lra-hit', drive=2.2)

# ---------------------------------------------------------------- emp hit (surge shell)
D = 1.9; t = t_(D); s = np.zeros_like(t)
dis = sweep(t, 3200, 90, 0.12); dis = np.sign(dis)*env_exp(t, 0.4, 0.001)
buzz = np.sign(np.sin(2*np.pi*118*t))*np.exp(-t/0.5)*(0.5+0.5*np.sign(np.sin(2*np.pi*13*t)))
zaps = crackle(t, 260, 0.45, seed=13, width=0.004)
boom = lp2(rng.normal(0, 1, len(t)), 2200*np.exp(-t/0.05)+150)*env_exp(t, 0.35, 0.002)*2.6
s += lp(dis, 5000)*0.25 + lp(buzz, 2500)*0.22 + zaps*0.5 + boom*0.55 + sweep(t, 70, 30, 0.2)*env_exp(t, 0.35)*0.6
emp = finish(echo(s), 'cybran-lra-emp', drive=2.0)

# ---------------------------------------------------------------- incendiary hit
D = 2.0; t = t_(D); s = hit[:len(t)]*0.75
whoosh = lp(hp(rng.normal(0, 1, len(t)), 300), 2200)*np.sin(np.pi*np.minimum(t/1.6, 1))**1.5
fire_cr = crackle(t, 150, 3, seed=17, width=0.002)*np.minimum(t/0.2, 1)
s += whoosh*0.5 + fire_cr*0.35
fire = finish(s, 'cybran-lra-fire', drive=1.6)

# ---------------------------------------------------------------- hum loop (seamless 2 s, plays while engaged)
D = 2.0; t = t_(D)
h = sum(np.sin(2*np.pi*f*t + p)/(k+1) for k, (f, p) in enumerate([(50, 0), (100, 1), (150, 2), (250, 0.5), (350, 1.7)]))
h *= 0.75 + 0.25*np.sin(2*np.pi*1.5*t)
spec = np.fft.rfft(rng.normal(0, 1, len(t))); fr = np.fft.rfftfreq(len(t), 1/SR)
spec *= np.exp(-((fr-700)/300)**2); air = np.fft.irfft(spec, len(t)); air /= np.max(np.abs(air))
servo = np.sin(2*np.pi*330*t)*0.12*(0.5+0.5*np.sin(2*np.pi*0.5*t))
s = h*0.5 + air*0.18 + servo
s = s - s.mean(); s = np.tanh(1.2*s/np.max(np.abs(s))); s *= 0.6/np.max(np.abs(s))
pcm = (s*32767).astype(np.int16)
w = wave.open(f'{OUT}/cybran-lra-hum.wav', 'wb'); w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
w.writeframes(pcm.tobytes()); w.close()
subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', f'{OUT}/cybran-lra-hum.wav', '-c:a', 'libvorbis', '-q:a', '5',
                f'{OUT}/cybran-lra-hum.ogg'], check=True)

for f in sorted(os.listdir(OUT)):
    print(f, os.path.getsize(f'{OUT}/{f}'))
