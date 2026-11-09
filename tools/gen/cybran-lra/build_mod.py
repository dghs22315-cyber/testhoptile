import os, shutil, glob
from PIL import Image

ROOT = '/data/mod/cybran-arsenal'
shutil.rmtree(ROOT, ignore_errors=True)
for d in ('content/blocks', 'sprites/blocks/turrets/cybran-lra', 'bundles', 'sounds', 'scripts'):
    os.makedirs(f'{ROOT}/{d}', exist_ok=True)

for f in glob.glob('/data/cybran/out/sprites/*.png'):
    if f.endswith('-full.png'): continue
    shutil.copy(f, f'{ROOT}/sprites/blocks/turrets/cybran-lra/')

# accelerator charge glow part: transparent base region + additive heat layer (dilated, softened barrel heat)
import numpy as np
from PIL import ImageFilter
SP = f'{ROOT}/sprites/blocks/turrets/cybran-lra'
C = Image.open('/data/cybran/out/sprites/cybran-lra-barrel.png').size[0]
Image.new('RGBA', (C, C)).save(f'{SP}/cybran-lra-coil.png')
bh = np.array(Image.open('/data/cybran/out/sprites/cybran-lra-barrel-heat.png').convert('RGBA')).astype(float)
m = Image.fromarray(bh[..., 3].astype(np.uint8)).filter(ImageFilter.MaxFilter(5)).filter(ImageFilter.GaussianBlur(1.6))
a = np.clip(np.array(m).astype(float)*1.9, 0, 255)
a[:int(C/2 - 1.9*32), :] = 0  # coils only, not the hot muzzle
coil = np.zeros((C, C, 4), np.uint8); coil[..., :3] = 255; coil[..., 3] = a.astype(np.uint8)
Image.fromarray(coil).save(f'{SP}/cybran-lra-coil-heat.png')

for f in glob.glob('/data/cybran/out/sounds/*.ogg'):
    shutil.copy(f, f'{ROOT}/sounds/')

# mod icon: crop of the hero render
h = Image.open('/data/cybran/out/hero.png').convert('RGB')
W, H = h.size
icon = h.crop((int(W*0.17), int(H*0.04), int(W*0.17)+int(H*0.92), int(H*0.96))).resize((256, 256), Image.LANCZOS)
icon.save(f'{ROOT}/icon.png')

open(f'{ROOT}/mod.hjson', 'w', encoding='utf-8').write('''name: "cybran-arsenal"
displayName: "Cybran Arsenal"
author: "fan-made"
description: "Cybran Nation long range artillery inspired by Supreme Commander 2. Adds one 3x3 artillery turret (Turret tab, research after Ripple). Sprites are rendered from a hand-built 3D model."
version: "1.2"
minGameVersion: "146"
''')

def boom(wave, spark, smoke, rad, sparks=8, smokes=7, life=26):
    rad = rad*1.5; sparks = sparks+4; smokes = smokes+3; life = life+8
    return f'''{{
        type: ExplosionEffect
        lifetime: {life}
        waveColor: "{wave}"
        sparkColor: "{spark}"
        smokeColor: "{smoke}"
        waveRad: {rad}
        waveStroke: 4
        waveLife: 9
        sparkRad: {int(rad*1.15)}
        sparkLen: 5
        sparkStroke: 1.6
        sparks: {sparks}
        smokeRad: {int(rad*0.9)}
        smokeSize: 5
        smokes: {smokes}
      }}'''

RED = dict(back='a82a38', front='ff8f9a', hit='ff4d5e')
block = f'''// Cybran Long Range Artillery - fan adaptation of the Supreme Commander 2 structure.
// Turret layers: -base, body, -outline, -heat, -preview + parts (wings slide out on warmup, barrel recoils).
type: ItemTurret
name: "Cybran Long Range Artillery"
description: "Stationary Cybran artillery. Fires heavy shells over walls at distant ground targets."
category: turret
research: ripple
size: 3
health: 2400
requirements: [
  copper/350
  graphite/220
  titanium/160
  silicon/140
  plastanium/80
]

targetAir: false
range: 1200
reload: 100
rotateSpeed: 1.6
shootCone: 10
inaccuracy: 1.2
velocityRnd: 0.04
recoil: 1
shake: 4
shootY: 26
shoot: {{ firstShotDelay: 40 }}
shootSound: cybran-lra-shoot
chargeSound: cybran-lra-charge
loopSound: cybran-lra-hum
loopSoundVolume: 0.3
ammoUseEffect: casing3Double
ammoEjectBack: 3
maxAmmo: 24
heatColor: "ff3a4f"
cooldownTime: 90
shootWarmupSpeed: 0.06
minWarmup: 0.9
coolantMultiplier: 3
consumes: {{
  coolant: {{ amount: 0.3 }}
}}

drawer: {{
  type: DrawTurret
  parts: [
    {{ type: RegionPart, suffix: "-wingl", progress: warmup, moveX: -1.2, moveY: -0.5, under: true, mirror: false }}
    {{ type: RegionPart, suffix: "-wingr", progress: warmup, moveX: 1.2, moveY: -0.5, under: true, mirror: false }}
    {{ type: RegionPart, suffix: "-barrel", progress: recoil, moveY: -3.5, heatColor: "ff3a4f", mirror: false }}
    {{ type: RegionPart, suffix: "-coil", progress: recoil, moveY: -3.5, heatProgress: charge, heatColor: "ff2a45", outline: false, mirror: false }}
  ]
}}

ammoTypes: {{
  graphite: {{
    type: ArtilleryBulletType
    speed: 5
    lifetime: 250
    width: 17
    height: 21
    shrinkX: 0.55
    shrinkY: 0.7
    knockback: 1.2
    splashDamage: 160
    splashDamageRadius: 60
    hitShake: 4
    status: blasted
    backColor: "{RED['back']}"
    frontColor: "{RED['front']}"
    hitColor: "{RED['hit']}"
    hitEffect: {boom('ff3355', 'ff8a96', '5a1a22', 38)}
  }}
  silicon: {{
    type: ArtilleryBulletType
    speed: 5
    lifetime: 250
    width: 16
    height: 20
    shrinkX: 0.55
    shrinkY: 0.7
    splashDamage: 125
    splashDamageRadius: 51
    reloadMultiplier: 1.2
    ammoMultiplier: 2
    homingPower: 0.08
    homingRange: 50
    backColor: "{RED['back']}"
    frontColor: "ffd0d5"
    hitColor: "{RED['hit']}"
    hitEffect: {boom('ff5566', 'ffd0d5', '4a1a20', 32, sparks=6, smokes=5)}
  }}
  pyratite: {{
    type: ArtilleryBulletType
    speed: 5
    lifetime: 250
    width: 17
    height: 21
    shrinkX: 0.55
    shrinkY: 0.7
    splashDamage: 110
    splashDamageRadius: 63
    status: burning
    statusDuration: 360
    makeFire: true
    incendAmount: 4
    incendSpread: 14
    incendChance: 0.8
    backColor: "d8432a"
    frontColor: "ffb38a"
    hitColor: "ff6a3d"
    hitEffect: {boom('ff6a3d', 'ffb38a', '5a2a1a', 40)}
  }}
  blast-compound: {{
    type: ArtilleryBulletType
    speed: 5
    lifetime: 250
    width: 18
    height: 22
    shrinkX: 0.55
    shrinkY: 0.7
    splashDamage: 120
    splashDamageRadius: 66
    reloadMultiplier: 0.85
    status: blasted
    fragBullets: 7
    fragBullet: {{
      type: BasicBulletType
      speed: 3
      damage: 10
      width: 7
      height: 9
      lifetime: 16
      splashDamage: 24
      splashDamageRadius: 16
      collidesAir: false
      backColor: "{RED['back']}"
      frontColor: "{RED['front']}"
      hitEffect: flakExplosion
    }}
    backColor: "{RED['back']}"
    frontColor: "{RED['front']}"
    hitColor: "{RED['hit']}"
    hitEffect: {boom('ff3355', 'ff8a96', '5a1a22', 46, sparks=10, smokes=8)}
  }}
  surge-alloy: {{
    type: ArtilleryBulletType
    speed: 5
    lifetime: 250
    width: 19
    height: 23
    shrinkX: 0.55
    shrinkY: 0.7
    splashDamage: 260
    splashDamageRadius: 84
    reloadMultiplier: 0.8
    hitShake: 4
    lightning: 5
    lightningLength: 9
    lightningDamage: 22
    lightningColor: "ff3355"
    status: electrified
    statusDuration: 240
    backColor: "c0203a"
    frontColor: "ffd6dc"
    hitColor: "ff3355"
    hitEffect: {boom('ff3355', 'ff8a96', '5a1a22', 52, sparks=12, smokes=9, life=30)}
  }}
}}
'''
FX = '''    hitSound: @SND@
    trailLength: 10
    trailWidth: 2.4
    trailColor: "@TRAIL@"
    chargeEffect: {
      type: MultiEffect
      effects: [
        { type: ParticleEffect, lifetime: 40, particles: 14, cone: 180, baseLength: 22, length: -22, sizeFrom: 0.6, sizeTo: 2.2, colorFrom: "ffd6dc", colorTo: "ff3355" }
        { type: WaveEffect, lifetime: 40, sizeFrom: 18, sizeTo: 2, strokeFrom: 0.4, strokeTo: 2.4, colorFrom: "ff335500", colorTo: "ff3355" }
      ]
    }
    shootEffect: {
      type: MultiEffect
      effects: [
        { type: ParticleEffect, lifetime: 18, particles: 9, cone: 22, length: 26, baseLength: 2, line: true, strokeFrom: 2, strokeTo: 0, lenFrom: 9, lenTo: 2, colorFrom: "ffd6dc", colorTo: "ff3355" }
        { type: WaveEffect, lifetime: 14, sizeFrom: 2, sizeTo: 16, strokeFrom: 3, strokeTo: 0, colorFrom: "ffd6dc", colorTo: "ff3355" }
      ]
    }
    smokeEffect: { type: ParticleEffect, lifetime: 60, particles: 8, cone: 28, length: 22, baseLength: 4, sizeFrom: 4.5, sizeTo: 0, colorFrom: "6a5a5f", colorTo: "3a3035" }'''
import re
out, cur = [], None
for line in block.split('\n'):
    out.append(line)
    mm = re.match(r'^  ([a-z-]+): \{$', line)
    if mm: cur = mm.group(1)
    if line == '    type: ArtilleryBulletType':
        snd = {'surge-alloy': 'cybran-lra-emp', 'pyratite': 'cybran-lra-fire'}.get(cur, 'cybran-lra-hit')
        out.append(FX.replace('@SND@', snd).replace('@TRAIL@', 'ff6a3d' if cur == 'pyratite' else 'ff3355'))
block = '\n'.join(out)
open(f'{ROOT}/content/blocks/cybran-lra.hjson', 'w', encoding='utf-8').write(block)

K = 'block.cybran-arsenal-cybran-lra'
open(f'{ROOT}/bundles/bundle.properties', 'w', encoding='utf-8').write(f'''{K}.name = Cybran Long Range Artillery
{K}.description = Stationary Cybran Nation artillery. Lobs heavy shells over walls at ground targets up to 150 tiles away. Shows the shell shadow and an impact marker in flight. Side armor plates unfold while it is firing.
{K}.details = Fan adaptation of the Supreme Commander 2 structure. Graphite: HE shell. Silicon: guided shell. Pyratite: incendiary. Blast compound: cluster. Surge alloy: EMP shell with chain lightning.
''')
open(f'{ROOT}/bundles/bundle_ru.properties', 'w', encoding='utf-8').write(f'''{K}.name = Дальнобойная артиллерия Кибран
{K}.description = Стационарная артиллерия Кибранской нации. Бьёт тяжёлыми снарядами навесом через стены по наземным целям на расстоянии до 150 клеток. В полёте видна тень снаряда и метка точки падения. Боковые бронепластины раскрываются во время стрельбы.
{K}.details = Фан-адаптация постройки из Supreme Commander 2. Графит - фугасный снаряд. Кремний - наводящийся снаряд. Пиротит - зажигательный. Взрывчатка - кассетный. Кинетический сплав - ЭМИ-снаряд с цепной молнией.
''')
print(open(f'{ROOT}/content/blocks/cybran-lra.hjson').read()[:400])

shutil.copy('/data/cybran/main.js', f'{ROOT}/scripts/main.js')
print('script copied')
