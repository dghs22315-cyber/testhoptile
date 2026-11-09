"""Build Vanguard Arsenal 2.5.0-alpha1 = 2.0 (stages 1-3 + hero artillery) + T4 tier."""
import os, json, glob
exec(compile(open('/data/vg2/build_stage3.py').read(), 'build_stage3.py', 'exec'))
V = '2.5.0-alpha1'
os.makedirs(f'{ROOT}/content/liquids', exist_ok=True)
SP = json.load(open('/data/vg2/out/spec6.json'))
SY = {k: round(v[0]*8, 1) for k, v in SP.items()}

# ---------------- T4 resources
ITEMS4 = {'iridite': {'color': '9aa2c8', 'hardness': 5, 'cost': 1.8, 'research': 'vg-mass-separator-2'},
          'tritium-ice': {'color': '8fe3ff', 'hardness': 3, 'cost': 1.4, 'radioactivity': 0.3, 'explosiveness': 0.2, 'research': 'vg-mass-separator-2'},
          'iridium': {'color': 'c9cfe6', 'cost': 2.6, 'research': 'vg-iridite'},
          'superconductor': {'color': 'e6b45a', 'cost': 2.4, 'charge': 0.6, 'research': 'vg-magnet'}}
for k, v in ITEMS4.items(): W(f'items/{k}', v)
W('liquids/liquid-nitrogen', {'color': 'bfe9ff', 'barColor': 'bfe9ff', 'temperature': 0.05, 'heatCapacity': 0.9, 'viscosity': 0.3,
                              'flammability': 0, 'effect': 'freezing', 'coolant': True, 'research': 'vg-cryocondenser'})
# Mass Separator II now also yields the T4 raw resources
p = glob.glob(f'{ROOT}/content/blocks/mass-separator-2.json')[0]
j = json.load(open(p)); j['results'] = j['results'] + ['iridite/1', 'tritium-ice/1']
open(p, 'w').write(json.dumps(j, indent=1, ensure_ascii=False))

# ---------------- T4 industry
W('blocks/cryocondenser', {'type': 'GenericCrafter', 'category': 'crafting', 'size': 2, 'health': 480, 'research': 'vg-electrolyzer',
   'requirements': ['copper/120', 'lead/100', 'silicon/80', 'titanium/60', 'aluminum/60'], 'craftTime': 60,
   'outputLiquid': {'liquid': 'liquid-nitrogen', 'amount': 0.12}, 'liquidCapacity': 40,
   'consumes': {'liquid': {'liquid': 'water', 'amount': 0.2}, 'power': 2.5}, 'ambientSound': 'cryo-loop', 'ambientSoundVolume': 0.08,
   'drawer': {'type': 'DrawMulti', 'drawers': [{'type': 'DrawRegion', 'suffix': '-bottom'}, {'type': 'DrawLiquidTile', 'drawLiquid': 'liquid-nitrogen'},
              {'type': 'DrawDefault'}, {'type': 'DrawGlowRegion', 'color': '9fe6ff', 'alpha': 0.8}]}})
W('blocks/iridium-smelter', {'type': 'HeatCrafter', 'category': 'crafting', 'size': 3, 'health': 1400, 'research': 'vg-tungsten-forge',
   'requirements': ['copper/300', 'lead/200', 'silicon/200', 'titanium/150', 'plastanium/80', 'cobalt-alloy/120', 'tungsten-core/60'],
   'outputItem': 'iridium/1', 'craftTime': 120, 'heatRequirement': 15, 'maxEfficiency': 2,
   'consumes': {'items': {'items': ['iridite/2', 'cobalt-alloy/1', 'plastanium/1']}, 'power': 4},
   'craftEffect': 'smeltsmoke', 'ambientSound': 'forge-loop', 'ambientSoundVolume': 0.14,
   'drawer': {'type': 'DrawMulti', 'drawers': [{'type': 'DrawDefault'}, {'type': 'DrawHeatInput'}, {'type': 'DrawGlowRegion', 'color': 'dfe6ff', 'alpha': 0.9}]}})
W('blocks/superconductor-chamber', {'type': 'GenericCrafter', 'category': 'crafting', 'size': 3, 'health': 1200, 'research': 'vg-cryocondenser',
   'requirements': ['copper/250', 'lead/200', 'silicon/250', 'titanium/150', 'aluminum/120', 'magnet/80'],
   'outputItem': 'superconductor/1', 'craftTime': 90,
   'consumes': {'items': {'items': ['magnet/1', 'aluminum/2']}, 'liquid': {'liquid': 'liquid-nitrogen', 'amount': 0.12}, 'power': 5},
   'craftEffect': 'smeltsmoke', 'ambientSound': 'chamber-loop', 'ambientSoundVolume': 0.08,
   'drawer': {'type': 'DrawMulti', 'drawers': [{'type': 'DrawDefault'}, {'type': 'DrawGlowRegion', 'color': '7fd4ff', 'alpha': 0.85, 'glowScale': 5, 'glowIntensity': 0.3}]}})
W('blocks/plasma-heater', {'type': 'HeatProducer', 'category': 'crafting', 'size': 3, 'health': 1100, 'research': 'vg-heater', 'rotate': True,
   'requirements': ['copper/250', 'lead/180', 'silicon/150', 'titanium/120', 'cobalt-alloy/80', 'magnet/60'], 'heatOutput': 20, 'craftTime': 150,
   'consumes': {'items': {'items': ['tritium-ice/1']}, 'power': 4}, 'ambientSound': 'plasma-loop', 'ambientSoundVolume': 0.1,
   'drawer': {'type': 'DrawMulti', 'drawers': [{'type': 'DrawDefault'}, {'type': 'DrawHeatOutput'}]}})
W('blocks/fusion-reactor', {'type': 'ConsumeGenerator', 'category': 'power', 'size': 4, 'health': 2600, 'research': 'vg-plasma-heater',
   'requirements': ['lead/600', 'silicon/500', 'graphite/400', 'metaglass/200', 'titanium/300', 'cobalt-alloy/250', 'iridium/150', 'superconductor/200'],
   'powerProduction': 45, 'itemDuration': 300, 'warmupSpeed': 0.01, 'effectChance': 0.04, 'generateEffect': 'generatespark', 'generateEffectRange': 40,
   'consumes': {'items': {'items': ['tritium-ice/1']}, 'liquid': {'liquid': 'liquid-nitrogen', 'amount': 0.15}},
   'ambientSound': 'fusion-loop', 'ambientSoundVolume': 0.14,
   'drawer': {'type': 'DrawMulti', 'drawers': [{'type': 'DrawDefault'}, {'type': 'DrawGlowRegion', 'color': '7fd4ff', 'alpha': 0.95, 'glowScale': 4, 'glowIntensity': 0.4}]}})

# ---------------- T4 turrets
IR = ('c9cfe6', 'ffffff')
mono = dict(speed=5.2, lifetime=262, width=20, height=24, hittable=False, reflectable=False, hitShake=9, hitSound='monolith-hit', hitSoundVolume=1.0,
            trailLength=12, trailWidth=3.2)
W('blocks/monolith', {
    'type': 'ItemTurret', 'category': 'turret', 'size': 5, 'health': 9800, 'armor': 12, 'research': 'vg-mantis',
    'requirements': ['copper/1200', 'graphite/600', 'silicon/500', 'plastanium/250', 'surge-alloy/150', 'steel/600', 'tungsten-core/300',
                     'cobalt-alloy/300', 'iridium/350', 'superconductor/200'],
    'targetAir': False, 'range': 1360, 'minRange': 240, 'reload': 420, 'rotateSpeed': 0.9, 'inaccuracy': 1.2, 'velocityRnd': 0.03,
    'recoil': 0, 'shake': 7, 'shootY': SY['monolith'], 'shootSound': 'monolith-shoot', 'ammoUseEffect': 'casing3', 'heatColor': '7fd4ff',
    'cooldownTime': 200, 'maxAmmo': 12, 'heatRequirement': 20, 'maxHeatEfficiency': 2, 'consumes': {'coolant': {'amount': 0.5}},
    'drawer': {'type': 'DrawTurret', 'parts': [{'type': 'RegionPart', 'suffix': '-barrel', 'progress': 'recoil', 'moveY': -6, 'heatColor': '7fd4ff'}]},
    'ammoTypes': {
        'iridium': shell(**mono, splashDamage=1600, splashDamageRadius=64, buildingDamageMultiplier=1.2, backColor=IR[0], frontColor=IR[1],
                         trailColor='c9cfe699', status='blasted', hitEffect=boom('dfe6ff', 64),
                         fragBullets=8, fragVelocityMin=0.5, fragVelocityMax=1.2, fragRandomSpread=360,
                         fragBullet={'type': 'ArtilleryBulletType', 'speed': 2, 'lifetime': 26, 'width': 7, 'height': 7, 'splashDamage': 90,
                                     'splashDamageRadius': 22, 'hittable': False, 'backColor': IR[0], 'frontColor': IR[1], 'hitSound': 'none',
                                     'hitShake': 1, 'trailLength': 3, 'trailWidth': 1.2, 'trailColor': 'c9cfe677', 'hitEffect': boom('dfe6ff', 18)}),
        'tungsten-core': shell(**dict(mono, speed=5.6, lifetime=243, hitSound='ap-hit'), splashDamage=1100, splashDamageRadius=30, pierceArmor=True,
                               buildingDamageMultiplier=2.2, backColor='8a8f99', frontColor='e6e9ef', trailColor='8a8f9999', status='blasted',
                               hitEffect=boom('e6e9ef', 30)),
        'magnet': shell(**dict(mono, hitSound='emp-hit'), splashDamage=650, splashDamageRadius=72, backColor='ff3355', frontColor='ffd6dd',
                        trailColor='ff335599', status='electrified', statusDuration=240, lightning=8, lightningLength=14, lightningDamage=45,
                        lightningColor='ff8fa0', hitEffect=boom('ff8fa0', 72)),
    }})
RAIL = dict(type='RailBulletType', length=384, pointEffect='railTrail', pointEffectSpace=20, pierceEffect='railHit', endEffect='railHit',
            hitEffect='hitBulletBig', shootEffect='railShoot', smokeEffect='shootBigSmoke')
W('blocks/bastion', {
    'type': 'ItemTurret', 'category': 'turret', 'size': 4, 'health': 6800, 'armor': 10, 'research': 'vg-lash',
    'requirements': ['copper/800', 'graphite/400', 'silicon/450', 'titanium/400', 'plastanium/150', 'steel/400', 'cobalt-alloy/250',
                     'iridium/200', 'superconductor/250'],
    'targetAir': True, 'range': 384, 'reload': 150, 'rotateSpeed': 2.2, 'recoil': 0, 'shake': 5, 'shootY': SY['bastion'],
    'shootSound': 'bastion-shoot', 'heatColor': '7fd4ff', 'cooldownTime': 110, 'maxAmmo': 20, 'minWarmup': 0.9, 'shootWarmupSpeed': 0.06,
    'consumes': {'power': 9, 'coolant': {'amount': 0.4}},
    'drawer': {'type': 'DrawTurret', 'parts': [{'type': 'RegionPart', 'suffix': '-barrel', 'progress': 'recoil', 'moveY': -5, 'heatColor': '7fd4ff'}]},
    'ammoTypes': {
        'iridium': dict(RAIL, damage=1400, pierceDamageFactor=0.5, hitColor='c9e6ff', ammoMultiplier=1),
        'tungsten-core': dict(RAIL, damage=900, pierceDamageFactor=0.35, hitColor='e6e9ef', pierceArmor=True, ammoMultiplier=2),
    }})
W('blocks/suppressor', {
    'type': 'PowerTurret', 'category': 'turret', 'size': 3, 'health': 2800, 'armor': 6, 'research': 'vg-radar',
    'requirements': ['copper/400', 'lead/300', 'silicon/400', 'titanium/250', 'steel/200', 'cobalt-alloy/150', 'magnet/150', 'superconductor/120'],
    'range': 240, 'reload': 300, 'rotateSpeed': 4, 'recoil': 2, 'shake': 3, 'heatColor': 'ff3355', 'cooldownTime': 120,
    'shootSound': 'suppressor-shoot', 'consumes': {'power': 7},
    'shootType': {'type': 'EmpBulletType', 'speed': 6, 'lifetime': 40, 'width': 14, 'height': 18, 'damage': 60, 'splashDamage': 120,
                  'splashDamageRadius': 64, 'radius': 64, 'timeIncrease': 1, 'timeDuration': 240, 'powerDamageScl': 1.5, 'powerSclDecrease': 0.4,
                  'hitUnits': True, 'unitDamageScl': 1, 'status': 'electrified', 'statusDuration': 240, 'backColor': 'ff3355', 'frontColor': 'ffd6dd',
                  'hitColor': 'ff3355', 'trailColor': 'ff3355', 'trailLength': 8, 'trailWidth': 2.5, 'lightColor': 'ff3355', 'hitSound': 'emp-hit',
                  'hitShake': 3, 'shootEffect': 'shootBig', 'smokeEffect': 'shootBigSmoke', 'hitEffect': boom('ff8fa0', 64), 'scaleLife': True,
                  'despawnHit': True}})

# ---------------- T4 defence
W('blocks/citadel', {'type': 'ForceProjector', 'category': 'effect', 'size': 4, 'health': 3600, 'research': 'vg-pulse-shield',
   'requirements': ['lead/600', 'silicon/450', 'titanium/300', 'cobalt-alloy/200', 'magnet/120', 'iridium/120', 'superconductor/150'],
   'radius': 144, 'shieldHealth': 9000, 'cooldownNormal': 5.5, 'cooldownLiquid': 1.6, 'cooldownBrokenBase': 0.9, 'consumes': {'power': 12},
   'ambientSound': 'citadel-hum', 'ambientSoundVolume': 0.12})

# ---------------- names / bundles
NAMES.update({
 'item.vg-iridite': ('Iridite', 'Иридит', 'Dense platinum-group ore from Mass Separator II.', 'Плотная руда платиновой группы. Даёт масс-сепаратор II.'),
 'item.vg-tritium-ice': ('Tritium Ice', 'Тритиевый лёд', 'Frozen fusion fuel. Slightly radioactive.', 'Замороженное термоядерное топливо. Слабо радиоактивен.'),
 'item.vg-iridium': ('Iridium', 'Иридий', 'T4 super-heavy metal. Monolith and Bastion ammo.', 'Т4 сверхтяжёлый металл. Снаряды «Монолита» и «Бастиона».'),
 'item.vg-superconductor': ('Superconductor', 'Сверхпроводник', 'Cryo-cooled conductor for T4 tech.', 'Криоохлаждаемый проводник для Т4 техники.'),
 'liquid.vg-liquid-nitrogen': ('Liquid Nitrogen', 'Жидкий азот', 'Extreme coolant. Needed for superconductors and fusion.', 'Сверххладагент. Нужен для сверхпроводников и термояда.'),
 'status.vg-disarmed': ('Disarmed', 'Разоружён', 'Weapons offline, 40% slower.', 'Оружие отключено, скорость −40%.'),
 'block.vg-monolith': ('Monolith', 'Монолит',
    'T4 UEF strategic artillery. 170 tiles, 1600 damage in an 8-tile radius. Fires only with 20 heat (twice as fast at 40). Iridium cluster / tungsten AP / magnet EMP (disarms). Shells ignore point defence.',
    'Т4 стратегическая артиллерия UEF. 170 клеток, 1600 урона в радиусе 8 клеток. Стреляет только при 20 ед. тепла (при 40 — вдвое быстрее). Иридиевый кассетный / вольфрамовый бронебойный / магнитный ЭМИ (разоружает). Не сбивается ПРО.'),
 'block.vg-bastion': ('Bastion', 'Бастион',
    'T4 UEF railgun. 48 tiles, 1400 damage, pierces everything in line, hits air.', 'Т4 рельсотрон UEF. 48 клеток, 1400 урона, прошивает всё на линии, бьёт по воздуху.'),
 'block.vg-suppressor': ('Suppressor', 'Подавитель',
    'T4 Cybran EMP projector. 30 tiles, EMP radius 8 tiles: enemy units disarmed for 4 s, enemy buildings slowed and damaged.',
    'Т4 кибранский ЭМИ-проектор. 30 клеток, ЭМИ радиусом 8 клеток: вражеские юниты 4 с без оружия, постройки замедлены и повреждены.'),
 'block.vg-citadel': ('Citadel', 'Цитадель', 'T4 shield dome: radius 18 tiles, 9000 HP. Holds Monolith-class shells.', 'Т4 купол-щит: радиус 18 клеток, 9000 ед. прочности. Держит снаряды класса «Монолит».'),
 'block.vg-cryocondenser': ('Cryocondenser', 'Криоконденсатор', 'Turns water and power into liquid nitrogen.', 'Превращает воду и энергию в жидкий азот.'),
 'block.vg-iridium-smelter': ('Iridium Smelter', 'Иридиевая плавильня', 'Heat crafter (15 heat): iridite + cobalt alloy + plastanium → iridium.', 'Тепловой завод (15 тепла): иридит + кобальтовый сплав + пластаний → иридий.'),
 'block.vg-superconductor-chamber': ('Superconductor Chamber', 'Камера сверхпроводников', 'Magnet + aluminium in liquid nitrogen → superconductor.', 'Магнит + алюминий в жидком азоте → сверхпроводник.'),
 'block.vg-plasma-heater': ('Plasma Heater', 'Плазменный нагреватель', 'Burns tritium ice: 20 heat. Powers the Monolith and the iridium smelter.', 'Сжигает тритиевый лёд: 20 ед. тепла. Питает «Монолит» и иридиевую плавильню.'),
 'block.vg-fusion-reactor': ('Fusion Reactor', 'Термоядерный реактор', 'T4 tokamak: 2700 power/s from tritium ice + liquid nitrogen.', 'Т4 токамак: 2700 энергии/с из тритиевого льда и жидкого азота.'),
})
for lang, i in (('bundle', 0), ('bundle_ru', 1)):
    L = []
    for k, v in NAMES.items():
        L.append(f'{k}.name = {v[i]}')
        if v[2+i]: L.append(f'{k}.description = {v[2+i]}')
    L += EXTRA[lang]
    open(f'{ROOT}/bundles/{lang}.properties', 'w', encoding='utf-8').write('\n'.join(L)+'\n')
open(f'{ROOT}/scripts/main.js', 'w').write(''.join(open(f'/data/vg2/{n}').read() for n in ('main.js', 'main2.js', 'main3.js', 'main4.js')))
open(f'{ROOT}/mod.hjson', 'w').write(f'''name: vg
displayName: Vanguard Arsenal
author: Muse
version: "{V}"
minGameVersion: 146
java: false
description: "UEF/Cybran/Aeon/Seraphim-inspired artillery, defence and industry. 2.5 stage 1: T4 — Monolith strategic artillery (heat-fed), Bastion railgun, Suppressor EMP, Citadel shield; iridite, tritium ice, iridium, superconductor, liquid nitrogen; cryocondenser, iridium smelter, superconductor chamber, plasma heater, fusion reactor. 2.0: T1-T3 arsenal, BKM cores and ACUs."
''')

# ---------------- report
rep = open('/data/vg2/report4h.md').read()
old = '# Vanguard Arsenal {V} — отчёт этапа 3 (T1–T3)'
assert old in rep
rep = rep.replace(old, '# Vanguard Arsenal {V} — отчёт: версия 2.5, этап 1 (T4) + этапы 1–3')
rep += '''

## 2.5.0-alpha1 — ярус T4

Все модели T4 сделаны заново на уровне детализации «Скорпиона» (hero-пайплайн: скосы, вставки, болты, кабели, гидравлика, светящиеся элементы, многоступенчатые стволы).

| Блок | Размер | Роль | Ключевые цифры |
|---|---|---|---|
| Монолит | 5×5 | стратегическая арта UEF | 170 клеток, 1600 урона r8, 7 с перезарядка, нужно 20 тепла (40 → ×2) |
| Бастион | 4×4 | рельсотрон UEF | 48 клеток, 1400 урона, прошивает, бьёт воздух, 9 энергии/тик |
| Подавитель | 3×3 | ЭМИ Кибран | 30 клеток, ЭМИ r8: юниты разоружены 4 с, постройки замедлены |
| Цитадель | 4×4 | купол-щит | r18 клеток, 9000 прочности |
| Криоконденсатор | 2×2 | вода → жидкий азот | 0,12/тик |
| Иридиевая плавильня | 3×3 | тепловой завод | 15 тепла, иридит+сплав+пластаний → иридий |
| Камера сверхпроводников | 3×3 | завод | магнит+алюминий+азот → сверхпроводник |
| Плазменный нагреватель | 3×3 | источник тепла | 20 тепла из тритиевого льда |
| Термоядерный реактор | 4×4 | генератор | 2700 энергии/с |

**Новые ресурсы:** иридит, тритиевый лёд (из масс-сепаратора II), иридий, сверхпроводник, жидкий азот. Всё делается из ванильных ресурсов Serpulo + ресурсов 2.0.

**Статус «Разоружён»** (JS): оружие отключено, скорость −40%. Накладывают «Подавитель» и магнитные снаряды «Монолита»; магнитный снаряд ещё и замедляет вражеские постройки в радиусе 9 клеток на 5 с.

**Противодействие:** снаряды «Монолита» не сбиваются обычной ПРО (hittable=false) — их держат щиты, «Цитадель» рассчитана на 5–6 попаданий.

**9 новых звуков:** monolith-shoot, monolith-hit, bastion-shoot (заряд + щелчок), suppressor-shoot, citadel-hum, fusion-loop, cryo-loop, plasma-loop, chamber-loop.

**Цепочка:** масс-сепаратор II → иридит/тритий → плазменный нагреватель (тепло) → иридиевая плавильня → иридий; криоконденсатор → азот → камера → сверхпроводник; тритий + азот → термоядерный реактор.
'''
open('/data/vg2/report5.md', 'w').write(rep)
print('stage4 content added', V, len(NAMES), 'bundle keys', SY)
