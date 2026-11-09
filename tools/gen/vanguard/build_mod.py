import json, os, re, shutil, glob, subprocess
from PIL import Image, ImageDraw, ImageFont
V = '2.0.0-alpha1'
ROOT = '/data/vg2/mod/vg'
shutil.rmtree(ROOT, ignore_errors=True)
for d in ('content/items', 'content/blocks', 'bundles', 'scripts', 'sounds'): os.makedirs(f'{ROOT}/{d}', exist_ok=True)
shutil.copytree('/data/vg2/out/sprites', f'{ROOT}/sprites')
for f in glob.glob('/data/vg2/out/sounds/*.ogg'): shutil.copy(f, f'{ROOT}/sounds/')

def W(path, obj): open(f'{ROOT}/content/{path}.json', 'w').write(json.dumps(obj, indent=1, ensure_ascii=False))

# ---------- effects
def flash(c1, c2, s=1.0): return {'type': 'MultiEffect', 'effects': [
    {'type': 'ParticleEffect', 'lifetime': 16, 'particles': 8, 'cone': 24, 'length': 20*s, 'baseLength': 2, 'line': True, 'strokeFrom': 1.8, 'strokeTo': 0, 'lenFrom': 7*s, 'lenTo': 1, 'colorFrom': c1, 'colorTo': c2},
    {'type': 'WaveEffect', 'lifetime': 12, 'sizeFrom': 1, 'sizeTo': 11*s, 'strokeFrom': 2.5, 'strokeTo': 0, 'colorFrom': c1, 'colorTo': c2}]}
SMOKE = {'type': 'ParticleEffect', 'lifetime': 55, 'particles': 7, 'cone': 30, 'length': 18, 'baseLength': 3, 'sizeFrom': 3.8, 'sizeTo': 0, 'colorFrom': '6b6b70', 'colorTo': '3c3c42'}
def boom(c, r, extra=None):
    e = [{'type': 'ExplosionEffect', 'lifetime': 40, 'waveColor': c, 'sparkColor': c, 'smokeColor': '55555a', 'waveStroke': 3, 'waveRad': r, 'waveLife': 12,
          'smokes': 7, 'smokeSize': 4.2, 'smokeSizeBase': 0.6, 'smokeRad': r*0.8, 'sparks': 9, 'sparkRad': r*1.2, 'sparkLen': 5, 'sparkStroke': 1.6},
         {'type': 'WaveEffect', 'lifetime': 30, 'sizeFrom': 2, 'sizeTo': r, 'strokeFrom': 2, 'strokeTo': 0, 'colorFrom': 'ffffffaa', 'colorTo': c+'00'}]
    if extra: e.append(extra)
    return {'type': 'MultiEffect', 'effects': e}
FIRE = {'type': 'ParticleEffect', 'lifetime': 70, 'particles': 12, 'cone': 180, 'length': 20, 'sizeFrom': 3, 'sizeTo': 0, 'colorFrom': 'ffd27a', 'colorTo': 'ff5a1e'}

# ---------- items & ores
ITEMS = {'ferrolite': {'color': 'a6553c', 'hardness': 2, 'cost': 0.8, 'research': 'scrap'},
         'saltpeter': {'color': 'd9dad2', 'hardness': 1, 'cost': 0.6, 'flammability': 0.3, 'explosiveness': 0.4, 'research': 'scrap'},
         'steel': {'color': '98a3b0', 'cost': 1.2, 'research': 'ferrolite'},
         'charge': {'color': 'a19946', 'cost': 0.9, 'flammability': 0.6, 'explosiveness': 0.9, 'research': 'saltpeter'}}
for k, v in ITEMS.items(): W(f'items/{k}', v)
for k in ('ferrolite', 'saltpeter'): W(f'blocks/ore-{k}', {'type': 'OreBlock', 'itemDrop': k, 'variants': 3})

# ---------- Howl (T1 mortar)
def shell(**kw):
    b = {'type': 'ArtilleryBulletType', 'speed': 3.2, 'lifetime': 100, 'width': 11, 'height': 13, 'knockback': 0.8, 'hitShake': 2.5,
         'hitSound': 'howl-hit', 'hitSoundVolume': 0.9, 'trailLength': 7, 'trailWidth': 1.8, 'shootEffect': flash('ffe8a0', 'ff9a3a'), 'smokeEffect': SMOKE}
    b.update(kw); return b
W('blocks/howl', {
    'type': 'ItemTurret', 'category': 'turret', 'size': 2, 'health': 900, 'research': 'hail',
    'requirements': ['copper/90', 'graphite/45', 'steel/30'],
    'targetAir': False, 'range': 320, 'minRange': 48, 'reload': 90, 'rotateSpeed': 3.5, 'inaccuracy': 2.5, 'velocityRnd': 0.08,
    'recoil': 0.6, 'shake': 1.5, 'shootY': 8.7, 'shootSound': 'howl-shoot', 'ammoUseEffect': 'casing2', 'heatColor': 'ffb050', 'cooldownTime': 60, 'maxAmmo': 20,
    'consumes': {'coolant': {'amount': 0.15}},
    'drawer': {'type': 'DrawTurret', 'parts': [{'type': 'RegionPart', 'suffix': '-barrel', 'progress': 'recoil', 'moveY': -2.4, 'heatColor': 'ff9a3a'}]},
    'ammoTypes': {
        'graphite': shell(splashDamage=80, splashDamageRadius=22, backColor='d9a441', frontColor='ffe8a0', trailColor='d9a44199', status='blasted', hitEffect=boom('ffd27a', 22)),
        'charge': shell(splashDamage=115, splashDamageRadius=26, ammoMultiplier=2, backColor='c7b35a', frontColor='fff1b0', trailColor='c7b35a99', status='blasted',
                        fragBullets=5, fragVelocityMin=0.6, fragBullet={'type': 'BasicBulletType', 'speed': 2.6, 'damage': 10, 'lifetime': 10, 'width': 4, 'height': 7,
                        'backColor': 'c7b35a', 'frontColor': 'fff1b0', 'collidesAir': False, 'hitEffect': 'hitBulletSmall', 'despawnEffect': 'hitBulletSmall'},
                        hitEffect=boom('fff1b0', 26)),
        'pyratite': shell(splashDamage=45, splashDamageRadius=26, backColor='ff7a1e', frontColor='ffcf8a', trailColor='ff7a1e99', status='burning', statusDuration=360,
                          makeFire=True, incendAmount=5, incendSpread=16, incendChance=0.8, hitSound='howl-fire', hitEffect=boom('ff9a3a', 26, FIRE)),
    }})

# ---------- crafters
W('blocks/mass-separator', {'type': 'Separator', 'category': 'crafting', 'size': 2, 'health': 320, 'research': 'melter',
   'requirements': ['copper/70', 'lead/50', 'graphite/30'], 'results': ['ferrolite/5', 'saltpeter/4'], 'craftTime': 40,
   'consumes': {'power': 1.1, 'liquid': {'liquid': 'slag', 'amount': 0.07}}, 'ambientSound': 'separator-loop', 'ambientSoundVolume': 0.1,
   'drawer': {'type': 'DrawMulti', 'drawers': [{'type': 'DrawRegion', 'suffix': '-bottom'}, {'type': 'DrawLiquidTile', 'drawLiquid': 'slag'},
              {'type': 'DrawRegion', 'suffix': '-spinner', 'spinSprite': True, 'rotateSpeed': 2.5}, {'type': 'DrawDefault'},
              {'type': 'DrawGlowRegion', 'color': '6ab8ff', 'alpha': 0.75}]}})
W('blocks/steel-smelter', {'type': 'GenericCrafter', 'category': 'crafting', 'size': 2, 'health': 360, 'research': 'mass-separator',
   'requirements': ['copper/80', 'lead/40', 'graphite/40'], 'outputItem': 'steel/1', 'craftTime': 60, 'craftEffect': 'smeltsmoke',
   'consumes': {'items': {'items': ['ferrolite/2', 'coal/1']}, 'power': 0.6}, 'ambientSound': 'smelter-loop', 'ambientSoundVolume': 0.12,
   'drawer': {'type': 'DrawMulti', 'drawers': [{'type': 'DrawDefault'}, {'type': 'DrawGlowRegion', 'color': 'ff7a1e', 'alpha': 0.9, 'glowScale': 6, 'glowIntensity': 0.35}]}})
W('blocks/propellant-press', {'type': 'GenericCrafter', 'category': 'crafting', 'size': 2, 'health': 300, 'research': 'mass-separator',
   'requirements': ['copper/60', 'lead/45', 'graphite/25'], 'outputItem': 'charge/2', 'craftTime': 50, 'craftEffect': 'pulverizeMedium',
   'consumes': {'items': {'items': ['saltpeter/1', 'coal/1']}, 'power': 0.5}, 'ambientSound': 'press-loop', 'ambientSoundVolume': 0.1,
   'drawer': {'type': 'DrawMulti', 'drawers': [{'type': 'DrawRegion', 'suffix': '-bottom'}, {'type': 'DrawPistons', 'sinMag': 2.2, 'sinScl': 5, 'lenOffset': 2.5, 'sides': 4},
              {'type': 'DrawDefault'}, {'type': 'DrawRegion', 'suffix': '-top'}, {'type': 'DrawGlowRegion', 'color': 'ffd060', 'alpha': 0.7}]}})

# ---------- defence
W('blocks/interceptor', {'type': 'PointDefenseTurret', 'category': 'turret', 'size': 2, 'health': 700, 'research': 'howl',
   'requirements': ['copper/60', 'lead/50', 'silicon/40', 'steel/20'], 'range': 176, 'reload': 8, 'bulletDamage': 28, 'shootLength': 6,
   'rotateSpeed': 18, 'color': '8fd0fa', 'shootSound': 'pd-zap', 'consumes': {'power': 1.5}})
W('blocks/spotter-beacon', {'type': 'Radar', 'category': 'effect', 'size': 1, 'health': 220, 'research': 'howl', 'buildVisibility': 'shown',
   'requirements': ['copper/30', 'lead/25', 'silicon/15'], 'fogRadius': 25, 'discoveryTime': 300, 'rotateSpeed': 2, 'glowColor': '6ab8ff',
   'consumes': {'power': 0.3}, 'ambientSound': 'beacon-loop', 'ambientSoundVolume': 0.05})
W('blocks/shield-emitter', {'type': 'ForceProjector', 'category': 'effect', 'size': 2, 'health': 600, 'research': 'interceptor',
   'requirements': ['lead/90', 'silicon/60', 'steel/40'], 'radius': 56, 'shieldHealth': 600, 'cooldownNormal': 1.6, 'cooldownLiquid': 1.3,
   'cooldownBrokenBase': 0.4, 'consumes': {'power': 1.4}, 'ambientSound': 'shield-hum', 'ambientSoundVolume': 0.08})
W('blocks/steel-wall', {'type': 'Wall', 'category': 'defense', 'size': 1, 'health': 500, 'research': 'titanium-wall', 'requirements': ['steel/6']})
W('blocks/steel-wall-large', {'type': 'Wall', 'category': 'defense', 'size': 2, 'health': 2000, 'research': 'steel-wall', 'requirements': ['steel/24']})

# ---------- Scorpion = Cybran LRA port (T2 heavy artillery)
src = open('/data/mod/cybran-arsenal/content/blocks/cybran-lra.hjson').read()
s = src.replace('cybran-lra-', 'scorpion-').replace('research: ripple', 'research: howl')
s = re.sub(r'requirements: \[[^\]]*\]', 'requirements: [ copper/250, graphite/180, steel/150, silicon/120, titanium/100 ]', s, count=1)
s = re.sub(r'^range: 1200', 'range: 640', s, flags=re.M); s = re.sub(r'^reload: 100', 'reload: 240', s, flags=re.M)
s = re.sub(r'^  silicon: \{', '  charge: {', s, flags=re.M)
dm = iter([300, 360, 200, 420, 420, 420]); rm = iter([32, 36, 36, 40, 40, 40])
s = re.sub(r'^    splashDamage: \d+', lambda m: f'    splashDamage: {next(dm)}', s, flags=re.M)
s = re.sub(r'^    splashDamageRadius: \d+', lambda m: f'    splashDamageRadius: {next(rm)}', s, flags=re.M)
s = re.sub(r'^    speed: 5\b', '    speed: 4\n    hittable: false\n    reflectable: false\n    absorbable: true', s, flags=re.M)
s = re.sub(r'^    lifetime: 250\b', '    lifetime: 165', s, flags=re.M)
open(f'{ROOT}/content/blocks/scorpion.hjson', 'w').write(s)
os.makedirs(f'{ROOT}/sprites/blocks/turrets/scorpion', exist_ok=True)
for f in glob.glob('/data/mod/cybran-arsenal/sprites/blocks/turrets/cybran-lra/*.png'):
    shutil.copy(f, f'{ROOT}/sprites/blocks/turrets/scorpion/' + os.path.basename(f).replace('cybran-lra', 'scorpion'))
shutil.copy(f'{ROOT}/sprites/blocks/turrets/scorpion/scorpion-preview.png', f'{ROOT}/sprites/blocks/turrets/scorpion/scorpion-full.png')
for n in ('shoot', 'charge', 'hit', 'hum', 'whistle', 'fire', 'emp'):
    p = f'/data/mod/cybran-arsenal/sounds/cybran-lra-{n}.ogg'
    if os.path.exists(p): shutil.copy(p, f'{ROOT}/sounds/scorpion-{n}.ogg')

# ---------- mod.hjson, bundles, script
open(f'{ROOT}/mod.hjson', 'w').write(f'''name: vg
displayName: Vanguard Arsenal
author: Muse
version: "{V}"
minGameVersion: 146
java: false
description: "UEF-style artillery, defence and industry. 2.0 stage 1: Howl, Scorpion, interceptor, shield emitter, spotter beacon, steel chain. Ultra: БКМ cores, Serafis campaign — next stages."
''')
NAMES = {
 'item.vg-ferrolite': ('Ferrolite', 'Феролит', 'Rust-red iron ore. Extracted from slag by the mass separator.', 'Ржаво-красная железная руда. Добывается из шлака масс-сепаратором.'),
 'item.vg-saltpeter': ('Saltpeter', 'Селитра', 'Oxidiser crystals for propellant.', 'Кристаллы окислителя для порохового заряда.'),
 'item.vg-steel': ('Steel', 'Сталь', 'Structural alloy for artillery and armour.', 'Конструкционный сплав для артиллерии и брони.'),
 'item.vg-charge': ('Propellant Charge', 'Пороховой заряд', 'Volatile shell charge. Doubles Howl ammo and adds shrapnel.', 'Взрывоопасный заряд. Удваивает боезапас Howl и добавляет шрапнель.'),
 'block.vg-ore-ferrolite': ('Ferrolite Ore', 'Феролитовая руда', '', ''),
 'block.vg-ore-saltpeter': ('Saltpeter Ore', 'Селитряная руда', '', ''),
 'block.vg-howl': ('Howl', 'Вой', 'T1 field mortar. Ground only, dead zone 6 tiles. Shells can be shot down by point defence.', 'Т1 полевая мортира. Только наземные цели, мёртвая зона 6 клеток. Снаряды сбиваются точечной ПРО.'),
 'block.vg-scorpion': ('Scorpion', 'Скорпион', 'T2 heavy artillery (ex Cybran LRA). Shells ignore point defence and are stopped only by shields.', 'Т2 тяжёлая артиллерия (бывшая Cybran LRA). Снаряды не сбиваются ПРО — их держат только щиты.'),
 'block.vg-mass-separator': ('Mass Separator I', 'Масс-сепаратор I', 'Separates slag into ferrolite and saltpeter.', 'Разделяет шлак на феролит и селитру.'),
 'block.vg-steel-smelter': ('Steel Smelter', 'Сталеплавильня', 'Ferrolite + coal → steel.', 'Феролит + уголь → сталь.'),
 'block.vg-propellant-press': ('Propellant Press', 'Пороховой пресс', 'Saltpeter + coal → 2 propellant charges.', 'Селитра + уголь → 2 пороховых заряда.'),
 'block.vg-interceptor': ('Interceptor', 'Перехватчик', 'Twin-laser point defence. Shoots down T1 shells and bullets.', 'Двухлазерная точечная ПРО. Сбивает снаряды Т1 и пули.'),
 'block.vg-spotter-beacon': ('Spotter Beacon', 'Маяк корректировщика', 'Reveals fog in a 25-tile radius for your artillery.', 'Открывает туман в радиусе 25 клеток для вашей артиллерии.'),
 'block.vg-shield-emitter': ('Shield Emitter', 'Эмиттер щита', 'T1 shield dome. Absorbs any shell, including Scorpion.', 'Т1 купол-щит. Поглощает любые снаряды, включая Скорпион.'),
 'block.vg-steel-wall': ('Steel Wall', 'Стальная стена', '', ''),
 'block.vg-steel-wall-large': ('Large Steel Wall', 'Большая стальная стена', '', ''),
}
for lang, i in (('bundle', 0), ('bundle_ru', 1)):
    L = []
    for k, v in NAMES.items():
        L.append(f'{k}.name = {v[i]}')
        if v[2+i]: L.append(f'{k}.description = {v[2+i]}')
    open(f'{ROOT}/bundles/{lang}.properties', 'w', encoding='utf-8').write('\n'.join(L)+'\n')
shutil.copy('/data/vg2/main.js', f'{ROOT}/scripts/main.js')

# ---------- icon
ic = Image.new('RGBA', (256, 256), (28, 31, 38, 255)); d = ImageDraw.Draw(ic)
for x in range(0, 256, 32): d.line([(x, 0), (x, 256)], fill=(38, 42, 50)); d.line([(0, x), (256, x)], fill=(38, 42, 50))
h = Image.open('/data/vg2/out/full_howl.png').resize((192, 192), Image.NEAREST); ic.alpha_composite(h, (32, 14))
F = ImageFont.truetype('/usr/share/fonts/liberation-sans/LiberationSans-Bold.ttf', 30)
d.rectangle([0, 206, 256, 256], fill=(232, 184, 46)); d.text((128, 231), 'VANGUARD 2.0', font=F, fill=(25, 25, 30), anchor='mm')
ic.convert('RGB').save(f'{ROOT}/icon.png')
print('mod built')
