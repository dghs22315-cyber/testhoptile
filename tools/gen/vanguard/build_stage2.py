"""Build Vanguard Arsenal 2.0.0-alpha2 = stage 1 build + stage 2 content (BKM, engineers, cores, bay, JS)."""
src = open('/data/vg2/build_mod.py').read().replace("V = '2.0.0-alpha1'", "V = '2.0.0-alpha2'")
exec(compile(src, 'build_mod.py', 'exec'))
os.makedirs(f'{ROOT}/content/units', exist_ok=True)

# ---------------- units
def blue_bolt():
    return {'type': 'BasicBulletType', 'speed': 5.2, 'damage': 42, 'lifetime': 34, 'width': 8, 'height': 13,
            'frontColor': 'e6f6ff', 'backColor': '6ab8ff', 'trailColor': '6ab8ff', 'trailLength': 6, 'trailWidth': 1.8,
            'hitColor': '6ab8ff', 'lightColor': '6ab8ff', 'buildingDamageMultiplier': 0.6,
            'shootEffect': flash('e6f6ff', '6ab8ff', 0.8), 'hitEffect': boom('6ab8ff', 10), 'despawnEffect': boom('6ab8ff', 8)}
W('units/acu-uef', {
    'type': 'mech', 'speed': 0.5, 'hitSize': 14, 'health': 1400, 'armor': 6, 'rotateSpeed': 3.2,
    'canBoost': True, 'boostMultiplier': 1.5, 'riseSpeed': 0.06, 'mechLandShake': 2.5, 'mechStepParticles': True, 'mechStride': 6.5,
    'buildSpeed': 1.6, 'mineTier': 3, 'mineSpeed': 6.5, 'itemCapacity': 80, 'buildBeamOffset': 6,
    'deathSound': 'acu-death', 'deathExplosionEffect': 'reactorExplosion', 'lightColor': '6ab8ff',
    'research': 'vg-core-uef',
    'weapons': [
        {'name': 'acu-uef-cannon', 'x': 6, 'y': 0.5, 'top': False, 'mirror': False, 'reload': 24, 'recoil': 1.5, 'shootY': 5.2,
         'shake': 0.8, 'heatColor': '6ab8ff', 'cooldownTime': 30, 'shootSound': 'acu-uef-shot', 'bullet': blue_bolt()},
        {'name': 'acu-uef-launcher', 'x': -6, 'y': 0.5, 'top': False, 'mirror': False, 'reload': 150, 'recoil': 1, 'shootY': 2.4,
         'inaccuracy': 6, 'velocityRnd': 0.1, 'shootSound': 'acu-missile', 'shoot': {'shots': 2, 'shotDelay': 8},
         'bullet': {'type': 'MissileBulletType', 'speed': 3.4, 'damage': 14, 'splashDamage': 60, 'splashDamageRadius': 22, 'lifetime': 68,
                    'width': 7, 'height': 10, 'homingPower': 0.08, 'homingRange': 60, 'frontColor': 'fff4d6', 'backColor': 'ffb347',
                    'trailColor': 'b8b8b8', 'hitShake': 1.5, 'hitSound': 'explosion', 'hitEffect': boom('ffb347', 22)}}]})
W('units/acu-cybran', {
    'type': 'mech', 'speed': 0.6, 'hitSize': 13, 'health': 1200, 'armor': 4, 'rotateSpeed': 3.6,
    'canBoost': True, 'boostMultiplier': 1.6, 'riseSpeed': 0.07, 'mechLandShake': 2, 'mechStepParticles': True, 'mechStride': 6.2,
    'buildSpeed': 1.5, 'mineTier': 3, 'mineSpeed': 6, 'itemCapacity': 70, 'buildBeamOffset': 6,
    'deathSound': 'acu-death', 'deathExplosionEffect': 'reactorExplosion', 'lightColor': 'ff3355',
    'research': 'vg-core-cybran',
    'weapons': [
        {'name': 'acu-cybran-laser', 'x': 5.75, 'y': 0.75, 'top': False, 'mirror': False, 'reload': 50, 'recoil': 1, 'shootY': 5.4,
         'shake': 1, 'heatColor': 'ff3355', 'cooldownTime': 40, 'shootSound': 'acu-cybran-laser',
         'bullet': {'type': 'LaserBulletType', 'length': 150, 'damage': 70, 'width': 12, 'colors': ['ff335566', 'ff3355', 'ffd6dd'],
                    'hitColor': 'ff3355', 'lightColor': 'ff3355', 'buildingDamageMultiplier': 0.5, 'hitEffect': flash('ff8899', 'ff3355', 0.7)}},
        {'name': 'acu-cybran-emp', 'x': -5.75, 'y': 0.75, 'top': False, 'mirror': False, 'reload': 70, 'recoil': 0.8, 'shootY': 3.6,
         'heatColor': 'ff3355', 'shootSound': 'acu-cybran-emp',
         'bullet': {'type': 'LightningBulletType', 'damage': 20, 'lightningLength': 14, 'lightningLengthRand': 6,
                    'lightningColor': 'ff5577', 'status': 'shocked', 'statusDuration': 120}}]})
W('units/engineer', {
    'type': 'flying', 'flying': True, 'lowAltitude': True, 'speed': 2.2, 'accel': 0.09, 'drag': 0.05, 'hitSize': 8, 'health': 280, 'armor': 1,
    'rotateSpeed': 8, 'buildSpeed': 0.9, 'mineTier': 2, 'mineSpeed': 5, 'itemCapacity': 40, 'buildBeamOffset': 3.4,
    'engineSize': 1.6, 'engineOffset': 6, 'research': 'vg-engineering-bay', 'weapons': []})

# ---------------- BKM cores + engineering bay
W('blocks/core-uef', {
    'type': 'CoreBlock', 'category': 'effect', 'size': 4, 'health': 4500, 'armor': 5, 'itemCapacity': 9000, 'unitCapModifier': 16,
    'unitType': 'vg-acu-uef', 'research': 'core-shard', 'ambientSound': 'core-hum', 'ambientSoundVolume': 0.07,
    'requirements': ['copper/3000', 'lead/3000', 'silicon/2000', 'steel/800']})
W('blocks/core-cybran', {
    'type': 'CoreBlock', 'category': 'effect', 'size': 4, 'health': 4000, 'armor': 4, 'itemCapacity': 9000, 'unitCapModifier': 18,
    'unitType': 'vg-acu-cybran', 'research': 'core-shard', 'ambientSound': 'core-hum', 'ambientSoundVolume': 0.07,
    'requirements': ['copper/3000', 'lead/2500', 'silicon/1500', 'graphite/1000', 'steel/800']})
W('blocks/engineering-bay', {
    'type': 'UnitFactory', 'category': 'units', 'size': 3, 'health': 900, 'research': 'ground-factory',
    'requirements': ['copper/120', 'lead/90', 'silicon/60', 'steel/40'],
    'plans': [{'unit': 'vg-engineer', 'time': 1500, 'requirements': ['silicon/30', 'steel/20', 'lead/20']}],
    'consumes': {'power': 1.2}, 'ambientSound': 'bay-loop', 'ambientSoundVolume': 0.05})

# ---------------- bundles
NAMES['block.vg-spotter-beacon'] = ('Spotter Beacon', 'Маяк корректировщика',
    'Reveals fog in a 25-tile radius and marks enemies inside it: marked targets take +25% damage. Needs power.',
    'Открывает туман в радиусе 25 клеток и помечает врагов: помеченные цели получают +25% урона. Нужна энергия.')
NAMES.update({
 'unit.vg-acu-uef': ('Guardian ACU', 'БКМ «Страж»', 'UEF Armoured Command Unit. Spawned by the UEF command complex. Builds and mines; plasma cannon and missile pod; jump jets (boost). Overloads with a huge blast on death.',
                     'Бронированный командный модуль UEF. Появляется из Командного комплекса. Строит и добывает; плазменная пушка и ракетная установка; прыжковые двигатели (буст). При гибели — мощный взрыв.'),
 'unit.vg-acu-cybran': ('Spectre ACU', 'БКМ «Призрак»', 'Cybran Armoured Command Unit. Faster and lighter: microwave laser and EMP prongs that shock targets. Overloads with a huge blast on death.',
                        'Бронированный командный модуль Кибран. Быстрее и легче: микроволновый лазер и ЭМИ-разрядник, оглушающий цели. При гибели — мощный взрыв.'),
 'unit.vg-engineer': ('Engineer', 'Инженер', 'Hover construction drone. Assists any construction nearby. Under a BKM core only ACUs and engineers can build.',
                      'Строительный дрон на воздушной подушке. Сам помогает строить рядом. При ядре БКМ строить могут только БКМ и инженеры.'),
 'block.vg-core-uef': ('UEF Command Complex', 'Командный комплекс UEF', 'BKM core (4×4). Place over a Shard. You play as the Guardian ACU. Team rule: only ACUs and engineers can build.',
                       'Ядро БКМ (4×4). Ставится поверх «Осколка». Вы играете за БКМ «Страж». Правило команды: строить могут только БКМ и инженеры.'),
 'block.vg-core-cybran': ('Cybran Nexus', 'Узел Кибран', 'BKM core (4×4). Place over a Shard. You play as the Spectre ACU. Team rule: only ACUs and engineers can build.',
                          'Ядро БКМ (4×4). Ставится поверх «Осколка». Вы играете за БКМ «Призрак». Правило команды: строить могут только БКМ и инженеры.'),
 'block.vg-engineering-bay': ('Engineering Bay', 'Инженерный цех', 'Produces engineers.', 'Производит инженеров.'),
 'status.vg-spotted': ('Spotted', 'Помечен', 'Marked by a spotter beacon: takes +25% damage.', 'Помечен маяком корректировщика: получает +25% урона.'),
})
EXTRA = {'bundle': ['vg.buildrule = Only ACUs and engineers can build (BKM core rule)'],
         'bundle_ru': ['vg.buildrule = Строить могут только БКМ и инженеры (правило ядра БКМ)']}
for lang, i in (('bundle', 0), ('bundle_ru', 1)):
    L = []
    for k, v in NAMES.items():
        L.append(f'{k}.name = {v[i]}')
        if v[2+i]: L.append(f'{k}.description = {v[2+i]}')
    L += EXTRA[lang]
    open(f'{ROOT}/bundles/{lang}.properties', 'w', encoding='utf-8').write('\n'.join(L)+'\n')
open(f'{ROOT}/scripts/main.js', 'w').write(open('/data/vg2/main.js').read() + open('/data/vg2/main2.js').read())
open(f'{ROOT}/mod.hjson', 'w').write(f'''name: vg
displayName: Vanguard Arsenal
author: Muse
version: "{V}"
minGameVersion: 146
java: false
description: "UEF/Cybran artillery, defence and industry. 2.0 stage 2: BKM cores (UEF Command Complex, Cybran Nexus) with Guardian/Spectre ACUs, hover engineers, SupCom build rule, spotter marking. Stage 1: Howl, Scorpion, interceptor, shield emitter, steel chain."
''')
print('stage2 content added', V)
