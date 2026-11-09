"""Stage 2 procedural sounds (original synthesis)."""
import numpy as np
src = open('/data/vg2/sfx.py').read().split('# Howl mortar shot')[0]
exec(src)
R = np.random.default_rng(23)

def saw(t, f, nh=12):
    s = np.zeros_like(t)
    for k in range(1, nh+1): s += np.sin(2*np.pi*f*k*t)/k
    return s

# 1. UEF ACU plasma cannon: charged zap + body thump + ionised crackle
t = t_(0.75); x = np.zeros_like(t)
x += sweep(t, 2400, 260, 0.035)*env(t, 0.09)*0.7
x += sweep(t, 1200, 180, 0.05)*env(t, 0.14)*0.5
x += sweep(t, 140, 48, 0.05)*env(t, 0.18)*1.0
x += bp(noise(len(t)), 900, 6000)*env(t, 0.05)*0.6
x += hp(crackle(t, 260, 0.12), 1500)*0.5
save(reverb(x, 0.28), 'acu-uef-shot')

# 2. tactical missile launch: ignition pop + rising rocket roar + whoosh away
t = t_(1.3); x = np.zeros_like(t)
n = noise(len(t))
roar = lp(n, 1800)*np.minimum(t/0.05, 1)*np.exp(-t/0.5)
x += roar*0.8
wh = bp(n, 1500, 7000)*np.exp(-((t-0.35)/0.25)**2)*0.5
x += wh
x += sweep(t, 90, 40, 0.04)*env(t, 0.1)*0.9
x += metal(t, [820, 1310, 2140], 0.05)*0.25
save(reverb(x, 0.3), 'acu-missile')

# 3. Cybran microwave laser: buzzing saw beam + rising whine + sizzle
t = t_(1.0); x = np.zeros_like(t)
e = np.minimum(t/0.03, 1)*np.clip((1.0-t)/0.25, 0, 1)
x += lp(saw(t, 118+12*np.sin(2*np.pi*9*t), 16), 3500)*e*0.55
x += np.sin(2*np.pi*np.cumsum(900+900*t)/SR)*e*0.25
x += hp(noise(len(t)), 4000)*e*0.18
x += sweep(t, 600, 120, 0.03)*env(t, 0.06)*0.5
save(reverb(x, 0.22), 'acu-cybran-laser')

# 4. Cybran EMP: electric snap + falling tone + crackle tail
t = t_(1.0); x = np.zeros_like(t)
x += hp(crackle(t, 900, 0.18), 1200)*1.0
x += sweep(t, 3200, 90, 0.08)*env(t, 0.22)*0.45
x += bp(noise(len(t)), 200, 2500)*env(t, 0.03)*0.8
x += np.sin(2*np.pi*50*t)*np.sign(np.sin(2*np.pi*7*t))*env(t, 0.3)*0.15
save(reverb(x, 0.25), 'acu-cybran-emp')

# 5. ACU death: overload whine, then huge blast + sub boom + debris + long tail
t = t_(4.2); x = np.zeros_like(t)
pre = t < 0.55
x[pre] += np.sin(2*np.pi*np.cumsum(300+2600*(t[pre]/0.55)**2)/SR)*(t[pre]/0.55)*0.35
b = t_(3.65)
boom = sweep(b, 70, 22, 0.35)*env(b, 0.9, 0.004)*1.3 + lp(noise(len(b)), 900)*env(b, 0.6, 0.003)*1.0
boom += bp(noise(len(b)), 1200, 8000)*env(b, 0.12)*0.6 + crackle(b, 160, 1.2)*0.6
boom += metal(b, [310, 517, 742, 1113], 0.7)*0.18
at(x, boom, 0.55)
save(reverb(x, 0.45, 1.6), 'acu-death', peak=0.95)

# 6. heavy mech footstep: ground thud + hydraulic hiss + clank
t = t_(0.5); x = np.zeros_like(t)
x += sweep(t, 85, 38, 0.05)*env(t, 0.12, 0.003)*1.0
x += lp(noise(len(t)), 400)*env(t, 0.06)*0.6
x += metal(t, [640, 1020, 1580], 0.06)*0.3
hs = hp(noise(len(t)), 3000)*np.exp(-((t-0.16)/0.07)**2)*0.15
x += hs
save(x, 'acu-step', peak=0.8)

# 7. core hum loop: reactor drone with slow beating + faint data chatter
t = t_(4.04); x = np.zeros_like(t)
for f, a in ((55, 1.0), (110, 0.5), (165, 0.25), (220.5, 0.15), (330.25, 0.08)):
    x += np.sin(2*np.pi*f*t)*a
x *= 0.8 + 0.2*np.sin(2*np.pi*0.5*t)
x += lp(noise(len(t)), 300)*0.12
for k in range(10):
    s = t_(0.04); at(x, np.sin(2*np.pi*R.choice([1800, 2400, 3000])*s)*env(s, 0.012)*0.06, R.uniform(0, 3.9))
save(x, 'core-hum', loop=True, peak=0.5)

# 8. engineering bay loop: servo whir + weld sizzle bursts + periodic clank
t = t_(3.04); x = np.zeros_like(t)
x += np.sin(2*np.pi*np.cumsum(240+60*np.sin(2*np.pi*0.66*t))/SR)*0.18
weld = hp(crackle(t, 500, 99), 2000)*(0.5+0.5*np.sign(np.sin(2*np.pi*0.66*t+1)))
x += weld*0.5
for c in (0.4, 1.9):
    s = t_(0.4); at(x, (metal(s, [700, 1150, 1720], 0.08)*0.5 + sweep(s, 120, 50, 0.04)*env(s, 0.08)*0.6), c)
x += lp(noise(len(t)), 500)*0.08
save(x, 'bay-loop', loop=True, peak=0.55)

# 9. spotter ping: sonar chirp with echoes
t = t_(1.4); x = np.zeros_like(t)
p = t_(0.5); ping = (np.sin(2*np.pi*1450*p) + 0.3*np.sin(2*np.pi*2900*p))*env(p, 0.12, 0.004)
for i, (d, g) in enumerate(((0, 1.0), (0.28, 0.4), (0.56, 0.16), (0.84, 0.06))):
    at(x, ping, d, g)
save(reverb(x, 0.3, 1.3), 'spot-ping', peak=0.7)
print('stage2 sounds ok')
