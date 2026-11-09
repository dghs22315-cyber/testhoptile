"""2.5.0-alpha1 procedural sounds: T4 tier (original synthesis, SupCom-flavoured)."""
import numpy as np
src = open('/data/vg2/sfx.py').read().split('# Howl mortar shot')[0]
exec(src)
R = np.random.default_rng(55)

def saw(t, f, nh=12):
    s = np.zeros_like(t)
    for k in range(1, nh+1): s += np.sin(2*np.pi*f*k*t)/k
    return s
def boom(t, f0=110, f1=34, tau=0.35, nlp=900, g=1.0):
    n = noise(len(t))
    return (sweep(t, f0, f1, 0.06)*env(t, tau)*1.0 + lp(n, nlp)*env(t, tau*0.7)*0.9 + bp(n, 1200, 5000)*env(t, 0.03)*0.5)*g
def chirp(t, f0, f1, T):
    f = f0*(f1/f0)**np.clip(t/T, 0, 1)
    return np.sin(2*np.pi*np.cumsum(f)/SR)
def loopify(x, fade=0.5):
    n = int(fade*SR); w = np.linspace(0, 1, n)
    y = x[:-n].copy(); y[:n] = x[:n]*w + x[-n:]*(1-w)
    return y

# --- Monolith: UEF strategic artillery. Huge low blast, metallic ring, breech clank, hydraulic hiss
t = t_(3.0); x = boom(t, 95, 22, 0.8, 520, 1.3)
x += metal(t, [205, 390, 655, 1080], 0.5)*0.32
x += lp(crackle(t, 90, 0.9), 2200)*0.3
at(x, metal(t_(0.4), [1450, 2150, 3100], 0.05)*0.35, 0.70)                      # breech clank
h = t_(0.9); at(x, bp(noise(len(h)), 2500, 7000)*env(h, 0.35, 0.08)*0.18, 1.05)  # hydraulic hiss
save(reverb(x, 0.45, 0.97), 'monolith-shoot')

# --- Monolith impact: deep detonation + debris rain
t = t_(2.6); x = boom(t, 80, 18, 0.7, 450, 1.4)
x += lp(crackle(t, 260, 0.9), 3000)*0.4
x += bp(noise(len(t)), 150, 800)*env(t, 1.1, 0.05)*0.4
save(reverb(x, 0.5, 1.0), 'monolith-hit')

# --- Bastion: railgun. Rising capacitor charge, then supersonic crack
T = 0.55; t = t_(1.85); x = np.zeros_like(t)
c = t_(T); ch = (chirp(c, 300, 2600, T)*0.5 + chirp(c, 600, 5200, T)*0.25) * (c/T)**1.5
at(x, ch, 0.0, 0.45)
k = t_(1.3)
cr = hp(noise(len(k)), 1800)*env(k, 0.025, 0.0005)*1.1 + boom(k, 160, 40, 0.35, 900, 0.8) + metal(k, [1850, 2650, 3950, 5300], 0.25)*0.3
at(x, cr, T)
save(reverb(x, 0.35, 0.9), 'bastion-shoot')

# --- Suppressor: EMP discharge. Buzzing saw core, crackle, falling sweep, soft thump
t = t_(1.4)
x = saw(t, 70, 10)*env(t, 0.4, 0.01)*0.35
x += bp(crackle(t, 600, 0.35), 1500, 7000)*0.5
x += sweep(t, 1800, 120, 0.12)*env(t, 0.25)*0.45
x += boom(t, 140, 50, 0.25, 800, 0.6)
save(reverb(x, 0.3, 0.85), 'suppressor-shoot')

# --- Loops
t = t_(3.5)   # citadel: deep shield-generator hum, slow AM
am = 1 + 0.25*np.sin(2*np.pi*(2/3.5)*t)
x = (np.sin(2*np.pi*55*t) + 0.6*np.sin(2*np.pi*110*t) + 0.35*np.sin(2*np.pi*165.5*t))*am
x += bp(noise(len(t)), 300, 1200)*0.06
save(loopify(x, 0.5), 'citadel-hum', loop=True, peak=0.7)

t = t_(4.5)   # fusion reactor: plasma roar + transformer hum + fizz
x = np.sin(2*np.pi*50*t)*0.6 + np.sin(2*np.pi*100*t)*0.35 + saw(t, 150, 6)*0.08
x += lp(noise(len(t)), 400)*0.5*(1 + 0.3*np.sin(2*np.pi*(3/4.5)*t))
x += hp(crackle(t, 40, 9.0), 3000)*0.25
save(loopify(x, 0.5), 'fusion-loop', loop=True, peak=0.75)

t = t_(3.0)   # cryocondenser: compressor pump + hiss
pump = 0.5 + 0.5*np.sin(2*np.pi*(4/3.0)*t)
x = np.sin(2*np.pi*72*t)*0.4*pump + bp(noise(len(t)), 3000, 9000)*0.25 + lp(noise(len(t)), 250)*0.2
save(loopify(x, 0.5), 'cryo-loop', loop=True, peak=0.65)

t = t_(3.0)   # plasma heater: hot torch roar, shimmering
x = bp(noise(len(t)), 120, 900)*0.6*(1 + 0.2*np.sin(2*np.pi*(5/3.0)*t)) + np.sin(2*np.pi*88*t)*0.2
x += hp(crackle(t, 70, 9.0), 2500)*0.2
save(loopify(x, 0.5), 'plasma-loop', loop=True, peak=0.7)

t = t_(3.0)   # superconductor chamber: high cold whine + magnet buzz
x = np.sin(2*np.pi*880*t)*0.12*(1 + 0.4*np.sin(2*np.pi*(2/3.0)*t)) + saw(t, 120, 8)*0.12 + bp(noise(len(t)), 4000, 9000)*0.08
save(loopify(x, 0.5), 'chamber-loop', loop=True, peak=0.6)
print('sfx5 ok')
