"""Stage 3 procedural sounds (original synthesis, SupCom-flavoured)."""
import numpy as np
src = open('/data/vg2/sfx.py').read().split('# Howl mortar shot')[0]
exec(src)
R = np.random.default_rng(31)

def saw(t, f, nh=12):
    s = np.zeros_like(t)
    for k in range(1, nh+1): s += np.sin(2*np.pi*f*k*t)/k
    return s

def boom(t, f0=110, f1=34, tau=0.35, nlp=900, g=1.0):
    n = noise(len(t))
    return (sweep(t, f0, f1, 0.06)*env(t, tau)*1.0 + lp(n, nlp)*env(t, tau*0.7)*0.9 + bp(n, 1200, 5000)*env(t, 0.03)*0.5)*g

# --- Redoubt: heavy fortified howitzer, three-round salvo (each sample = one round, deep + metallic breech)
t = t_(1.6); x = boom(t, 120, 30, 0.45, 700)
x += metal(t, [310, 545, 880, 1430], 0.18)*0.35
x += lp(crackle(t, 120, 0.4), 2500)*0.25
at(x, metal(t_(0.3), [1650, 2400], 0.04)*0.3, 0.42)            # breech clank
save(reverb(x, 0.35, 0.95), 'redoubt-shoot')

# --- Mantis: Cybran heavy artillery, sharp rippling launcher with electric tail
t = t_(1.4); x = boom(t, 150, 40, 0.3, 1100, 0.9)
x += sweep(t, 3200, 400, 0.05)*env(t, 0.07)*0.35
x += hp(crackle(t, 380, 0.25), 2000)*0.35
x += saw(t, 55, 8)*env(t, 0.35)*0.25
save(reverb(x, 0.33, 0.9), 'mantis-shoot')

# --- Lash: Cybran pulse laser (short bright zap + capacitor whine)
t = t_(0.42); x = np.zeros_like(t)
x += sweep(t, 4200, 700, 0.025)*env(t, 0.06)*0.7
x += saw(t, 880, 10)*env(t, 0.03)*0.25
x += bp(noise(len(t)), 2500, 9000)*env(t, 0.02)*0.5
x += np.sin(2*np.pi*(2600+800*t)*t)*env(t, 0.12)*0.08
save(reverb(x, 0.2, 0.6), 'lash-shoot')

# --- Hydra: tube missile launch (pop + hiss)
t = t_(0.9); n = noise(len(t)); x = np.zeros_like(t)
x += sweep(t, 180, 60, 0.03)*env(t, 0.07)*0.8
x += bp(n, 900, 6000)*np.minimum(t/0.02, 1)*np.exp(-t/0.28)*0.7
x += bp(n, 3000, 9000)*np.exp(-((t-0.18)/0.12)**2)*0.35
save(reverb(x, 0.25), 'hydra-launch')

# --- Wasp: AA rocket ripple (lighter, higher, quick double pop)
t = t_(0.8); n = noise(len(t)); x = np.zeros_like(t)
for d in (0.0, 0.07):
    s = t_(0.6); y = sweep(s, 260, 90, 0.02)*env(s, 0.05)*0.6 + bp(noise(len(s)), 1800, 9000)*env(s, 0.18)*0.5
    at(x, y, d)
save(reverb(x, 0.22), 'wasp-launch')

# --- Rivet: twin machine gun (single crack, short)
t = t_(0.18); x = bp(noise(len(t)), 600, 7000)*env(t, 0.018)*0.9 + sweep(t, 300, 90, 0.01)*env(t, 0.03)*0.6
x += metal(t, [2300, 3400], 0.02)*0.15
save(reverb(x, 0.12, 0.5), 'rivet-shoot')

# --- Sparrow: flak (dull thump)
t = t_(0.5); x = boom(t, 160, 60, 0.12, 1500, 0.8) + metal(t, [900, 1500], 0.05)*0.2
save(reverb(x, 0.22, 0.7), 'sparrow-shoot')

# --- impacts
t = t_(1.4); x = np.zeros_like(t)                              # cluster: many small pops
for k in range(9):
    s = t_(0.5); at(x, boom(s, 200, 70, 0.08, 2200, 0.5), 0.05 + 0.09*k + 0.03*R.random())
save(reverb(x, 0.3), 'cluster-hit')
t = t_(1.2); x = boom(t, 90, 28, 0.4, 600, 1.0) + metal(t, [420, 760, 1290, 2050], 0.22)*0.45   # armour-piercing
save(reverb(x, 0.3, 0.95), 'ap-hit')
t = t_(1.3); x = boom(t, 130, 40, 0.18, 900, 0.6)                # EMP: zap + electric crackle
x += hp(crackle(t, 520, 0.5), 2500)*0.6 + sweep(t, 6000, 300, 0.12)*env(t, 0.3)*0.25
save(reverb(x, 0.3), 'emp-hit')

# --- loops (2 s, seamless: integer-period tones, periodic noise modulation)
L = 2.0; t = t_(L); n = noise(len(t))
def tone(f, a=1.0): return np.sin(2*np.pi*round(f*L)/L*t)*a
x = tone(100, 0.4) + tone(200, 0.2) + bp(n, 2000, 7000)*(0.25+0.15*np.sin(2*np.pi*6*t/L))*0.4        # electrolyzer: hum + bubbling
for k in range(18): at(x, np.sin(2*np.pi*(900+600*R.random())*t_(0.04))*env(t_(0.04), 0.01)*0.15, R.uniform(0, L-0.05))
save(x, 'electrolyzer-loop', loop=True, peak=0.5)
x = lp(n, 400)*0.8 + tone(45, 0.4) + lp(crackle(t, 30, 0.6), 2000)*0.2                                  # alloy furnace roar
save(x, 'furnace-loop', loop=True, peak=0.5)
x = lp(n, 500)*0.5 + tone(38, 0.5)                                                                          # tungsten forge: roar + hammer
for d in (0.0, 1.0): at(x, boom(t_(0.6), 120, 50, 0.1, 1500, 0.7) + metal(t_(0.6), [700, 1180, 1900], 0.12)*0.4, d)
save(x, 'forge-loop', loop=True, peak=0.55)
x = lp(n, 900)*0.5*(1+0.2*np.sin(2*np.pi*4*t/L)) + tone(60, 0.25)                                         # heater burner
save(x, 'heater-loop', loop=True, peak=0.45)
x = tone(50, 0.4) + lp(n, 700)*0.3                                                                          # impact drill: hammering
for k in range(8): at(x, boom(t_(0.2), 160, 70, 0.04, 2000, 0.45), k*L/8)
save(x, 'drill-loop', loop=True, peak=0.5)
x = tone(220, 0.15) + tone(330, 0.08)                                                                        # radar sweep ping
at(x, np.sin(2*np.pi*1760*t_(0.5))*env(t_(0.5), 0.12)*0.35, 0.1)
x += bp(n, 3000, 8000)*0.03
save(x, 'radar-loop', loop=True, peak=0.4)
x = tone(150, 0.25) + tone(450, 0.1)*(0.5+0.5*np.sin(2*np.pi*2*t/L)) + bp(n, 4000, 9000)*0.05             # nanite repair hiss
save(x, 'nanite-loop', loop=True, peak=0.4)
print('ok')
