"""Build Vanguard Arsenal 2.0.0-alpha3 = stage 1 + stage 2 + stage 3 (T2-T3: resources, heat, industry, turrets, defence)."""
import os
exec(compile(open('/data/vg2/build_stage2.py').read(), 'build_stage2.py', 'exec'))
V = '2.0.0-alpha3'
os.makedirs(f'{ROOT}/content/liquids', exist_ok=True)

# ---------------- items, ores, liquid
ITEMS3 = {'bauxite': {'color': 'bd6a2c', 'hardness': 3, 'cost': 0.9, 'research': 'vg-ferrolite'},
          'cobaltite': {'color': '3f76c2', 'hardness': 3, 'cost': 1.0, 'research': 'vg-ferrolite'},
          'wolframite': {'color': '555965', 'hardness': 4, 'cost': 1.3, 'research': 'vg-cobaltite'},
          'neodymite': {'color': 'ba58a0', 'hardness': 4, 'cost': 1.3, 'research': 'vg-wolframite'},
          'aluminum': {'color': 'bcc6d0', 'cost': 1.1, 'research': 'vg-bauxite'},
          'cobalt-alloy': {'color': '4470bb', 'cost': 1.6, 'research': 'vg-cobaltite'},
          'tungsten-core': {'color': '4b5059', 'cost': 2.0, 'research': 'vg-wolframite'},
          'magnet': {'color': '735b8b', 'cost': 1.8, 'charge': 0.3, 'research': 'vg-neodymite'}}
for k, v in ITEMS3.items(): W(f'items/{k}', v)
for k in ('bauxite', 'cobaltite', 'wolframite', 'neodymite'): W(f'blocks/ore-{k}', {'type': 'OreBlock', 'itemDrop': k, 'variants': 3})
W('liquids/chlorine', {'color': '74d45a', 'gasColor': 'a8e88f', 'barColor': '74d45a', 'gas': True, 'temperature': 0.4, 'viscosity': 0.2,
                       'flammability': 0, 'effect': 'corroded', 'coolant': False, 'research': 'vg-aluminum'})

# ---------------- industry
W('blocks/mass-separator-2', {'type': 'Separator', 'category': 'crafting', 'size': 3, 'health': 700, 'research': 'vg-mass-separator',
   'requirements': ['copper/160', 'lead/120', 'graphite/80', 'titanium/60', 'steel/60'],
   'results': ['bauxite/4', 'cobaltite/4', 'wolframite/3', 'neodymite/2'], 'craftTime': 32,
   'consumes': {'power': 2.2, 'liquid': {'liquid': 'slag', 'amount': 0.1}}, 'ambientSound': 'separator-loop', 'ambientSoundVolume': 0.12,
   'drawer': {'type': 'DrawMulti', 'drawers': [{'type': 'DrawRegion', 'suffix': '-bottom'}, {'type': 'DrawLiquidTile', 'drawLiquid': 'slag'},
              {'type': 'DrawRegion', 'suffix': '-spinner', 'spinSprite': True, 'rotateSpeed': 3.2}, {'type': 'DrawDefault'},
              {'type': 'DrawGlowRegion', 'color': '6ab8ff', 'alpha': 0.75}]}})
W('blocks/electrolyzer', {'type': 'GenericCrafter', 'category': 'crafting', 'size': 2, 'health': 420, 'research': 'vg-mass-separator-2',
   'requirements': ['copper/90', 'lead/70', 'silicon/50', 'steel/40'], 'outputItem': 'aluminum/1', 'craftTime': 60,
   'outputLiquid': {'liquid': 'chlorine', 'amount': 0.1}, 'ignoreLiquidFullness': True, 'liquidCapacity': 30,
   'consumes': {'items': {'items': ['bauxite/2']}, 'power': 1.6}, 'craftEffect': 'smeltsmoke',
   'ambientSound': 'electrolyzer-loop', 'ambientSoundVolume': 0.08,
   'drawer': {'type': 'DrawMulti', 'drawers': [{'type': 'DrawRegion', 'suffix': '-bottom'}, {'type': 'DrawLiquidTile', 'drawLiquid': 'chlorine'},
              {'type': 'DrawDefault'}, {'type': 'DrawGlowRegion', 'color': '74d45a', 'alpha': 0.8, 'glowScale': 5, 'glowIntensity': 0.3}]}})
W('blocks/alloy-furnace', {'type': 'GenericCrafter', 'category': 'crafting', 'size': 3, 'health': 800, 'research': 'vg-steel-smelter',
   'requirements': ['copper/160', 'lead/110', 'graphite/80', 'titanium/70', 'steel/80'], 'outputItem': 'cobalt-alloy/1', 'craftTime': 90,
   'consumes': {'items': {'items': ['cobaltite/2', 'steel/1', 'titanium/1']}, 'liquid': {'liquid': 'slag', 'amount': 0.06}, 'power': 3},
   'craftEffect': 'smeltsmoke', 'ambientSound': 'furnace-loop', 'ambientSoundVolume': 0.12,
   'drawer': {'type': 'DrawMulti', 'drawers': [{'type': 'DrawDefault'}, {'type': 'DrawGlowRegion', 'color': 'ff7a2a', 'alpha': 0.9, 'glowScale': 6, 'glowIntensity': 0.35}]}})
W('blocks/heater', {'type': 'HeatProducer', 'category': 'crafting', 'size': 2, 'health': 380, 'research': 'vg-alloy-furnace', 'rotate': True,
   'requirements': ['copper/60', 'lead/50', 'graphite/40', 'steel/30'], 'heatOutput': 6, 'craftTime': 120,
   'consumes': {'items': {'items': ['charge/1']}}, 'ambientSound': 'heater-loop', 'ambientSoundVolume': 0.08,
   'drawer': {'type': 'DrawMulti', 'drawers': [{'type': 'DrawDefault'}, {'type': 'DrawHeatOutput'}]}})
W('blocks/heat-conduit', {'type': 'HeatConductor', 'category': 'crafting', 'size': 1, 'health': 120, 'research': 'vg-heater',
   'requirements': ['copper/10', 'graphite/8', 'steel/6'],
   'drawer': {'type': 'DrawMulti', 'drawers': [{'type': 'DrawDefault'}, {'type': 'DrawHeatOutput'}, {'type': 'DrawHeatInput', 'suffix': '-heat'}]}})
W('blocks/tungsten-forge', {'type': 'HeatCrafter', 'category': 'crafting', 'size': 3, 'health': 900, 'research': 'vg-heater',
   'requirements': ['copper/200', 'lead/120', 'silicon/90', 'titanium/80', 'cobalt-alloy/40'], 'outputItem': 'tungsten-core/1', 'craftTime': 120,
   'heatRequirement': 6, 'maxEfficiency': 2, 'consumes': {'items': {'items': ['wolframite/2', 'graphite/1']}, 'power': 2.5},
   'craftEffect': 'smeltsmoke', 'ambientSound': 'forge-loop', 'ambientSoundVolume': 0.12,
   'drawer': {'type': 'DrawMulti', 'drawers': [{'type': 'DrawDefault'}, {'type': 'DrawHeatInput'}, {'type': 'DrawGlowRegion', 'color': 'ff9a3a', 'alpha': 0.85}]}})
W('blocks/magnet-factory', {'type': 'GenericCrafter', 'category': 'crafting', 'size': 2, 'health': 420, 'research': 'vg-electrolyzer',
   'requirements': ['copper/90', 'lead/80', 'silicon/70', 'aluminum/40'], 'outputItem': 'magnet/1', 'craftTime': 75,
   'consumes': {'items': {'items': ['neodymite/2', 'silicon/1']}, 'liquid': {'liquid': 'chlorine', 'amount': 0.08}, 'power': 1.8},
   'craftEffect': 'pulverizeMedium', 'ambientSound': 'press-loop', 'ambientSoundVolume': 0.08,
   'drawer': {'type': 'DrawMulti', 'drawers': [{'type': 'DrawRegion', 'suffix': '-bottom'},
              {'type': 'DrawRegion', 'suffix': '-spinner', 'spinSprite': True, 'rotateSpeed': 4}, {'type': 'DrawDefault'},
              {'type': 'DrawGlowRegion', 'color': 'c77dff', 'alpha': 0.8}]}})
W('blocks/impact-drill', {'type': 'Drill', 'category': 'production', 'size': 3, 'health': 760, 'research': 'laser-drill',
   'requirements': ['copper/90', 'graphite/60', 'silicon/50', 'titanium/50', 'aluminum/40'], 'tier': 4, 'drillTime': 300,
   'rotateSpeed': 4, 'drillEffect': 'mineHuge', 'updateEffect': 'pulverizeMedium', 'updateEffectChance': 0.03,
   'consumes': {'power': 2.6}, 'ambientSound': 'drill-loop', 'ambientSoundVolume': 0.1})

# ---------------- turrets
AL = ('bcc6d0', 'ffffff')
W('blocks/redoubt', {
    'type': 'ItemTurret', 'category': 'turret', 'size': 3, 'health': 2400, 'armor': 6, 'research': 'vg-howl',
    'requirements': ['copper/220', 'graphite/140', 'titanium/100', 'steel/120', 'aluminum/60'],
    'targetAir': False, 'range': 440, 'minRange': 80, 'reload': 150, 'rotateSpeed': 2.2, 'inaccuracy': 2, 'velocityRnd': 0.06,
    'recoil': 0, 'shake': 3, 'shootY': 21.9, 'shootSound': 'redoubt-shoot', 'ammoUseEffect': 'casing3', 'heatColor': 'ffb050', 'cooldownTime': 90,
    'maxAmmo': 30, 'shoot': {'shots': 3, 'shotDelay': 6}, 'consumes': {'coolant': {'amount': 0.25}},
    'drawer': {'type': 'DrawTurret', 'parts': [{'type': 'RegionPart', 'suffix': '-barrel', 'progress': 'recoil', 'moveY': -4.0, 'heatColor': 'ff9a3a'}]},
    'ammoTypes': {
        'charge': shell(speed=3.6, lifetime=130, width=13, height=15, hittable=False, reflectable=False, splashDamage=130, splashDamageRadius=32,
                        ammoMultiplier=2, backColor='d9a441', frontColor='ffe8a0', trailColor='d9a44199', status='blasted', hitShake=3.5,
                        hitEffect=boom('ffd27a', 32)),
        'pyratite': shell(speed=3.6, lifetime=130, width=13, height=15, hittable=False, reflectable=False, splashDamage=70, splashDamageRadius=34,
                          backColor='ff7a1e', frontColor='ffcf8a', trailColor='ff7a1e99', status='burning', statusDuration=420,
                          makeFire=True, incendAmount=7, incendSpread=22, incendChance=0.85, hitSound='howl-fire', hitEffect=boom('ff9a3a', 34, FIRE)),
        'aluminum': shell(speed=3.6, lifetime=130, width=13, height=15, hittable=False, reflectable=False, splashDamage=40, splashDamageRadius=20,
                          backColor=AL[0], frontColor=AL[1], trailColor='bcc6d099', hitSound='cluster-hit', hitEffect=boom('e8eef5', 20),
                          fragBullets=7, fragVelocityMin=0.5, fragVelocityMax=1.1, fragRandomSpread=360,
                          fragBullet={'type': 'ArtilleryBulletType', 'speed': 1.7, 'lifetime': 24, 'width': 6, 'height': 6, 'splashDamage': 38,
                                      'splashDamageRadius': 18, 'hittable': False, 'backColor': AL[0], 'frontColor': AL[1], 'hitSound': 'none',
                                      'hitShake': 0.6, 'trailLength': 3, 'trailWidth': 1, 'trailColor': 'bcc6d077', 'hitEffect': boom('e8eef5', 14)}),
    }})
W('blocks/mantis', {
    'type': 'ItemTurret', 'category': 'turret', 'size': 4, 'health': 5200, 'armor': 9, 'research': 'vg-scorpion',
    'requirements': ['copper/500', 'graphite/300', 'titanium/220', 'silicon/200', 'steel/220', 'cobalt-alloy/120', 'tungsten-core/60'],
    'targetAir': False, 'range': 760, 'minRange': 140, 'reload': 210, 'rotateSpeed': 1.6, 'inaccuracy': 1.5, 'velocityRnd': 0.05,
    'recoil': 0, 'shake': 4, 'shootY': 26.8, 'shootSound': 'mantis-shoot', 'ammoUseEffect': 'casing3', 'heatColor': 'ff3355', 'cooldownTime': 120,
    'maxAmmo': 40, 'shoot': {'type': 'ShootSpread', 'shots': 6, 'spread': 5.5, 'shotDelay': 5}, 'consumes': {'coolant': {'amount': 0.4}},
    'drawer': {'type': 'DrawTurret', 'parts': [{'type': 'RegionPart', 'suffix': '-barrel', 'progress': 'recoil', 'moveY': -4.5, 'heatColor': 'ff3355'}]},
    'ammoTypes': {
        'charge': shell(speed=4.2, lifetime=185, width=15, height=17, hittable=False, reflectable=False, splashDamage=170, splashDamageRadius=40,
                        ammoMultiplier=2, backColor='ff3355', frontColor='ffd6dd', trailColor='ff335599', status='blasted', hitShake=4,
                        hitSound='howl-hit', hitEffect=boom('ff5577', 40)),
        'tungsten-core': shell(speed=4.6, lifetime=170, width=12, height=18, hittable=False, reflectable=False, splashDamage=140, splashDamageRadius=22,
                               pierceArmor=True, buildingDamageMultiplier=1.8, backColor='8a8f99', frontColor='e6e9ef', trailColor='8a8f9999',
                               hitSound='ap-hit', hitShake=4, hitEffect=boom('e6e9ef', 24),
                               fragBullets=3, fragVelocityMin=0.7, fragBullet={'type': 'BasicBulletType', 'speed': 3.4, 'damage': 40, 'lifetime': 9,
                               'width': 4, 'height': 9, 'pierce': True, 'pierceArmor': True, 'backColor': '8a8f99', 'frontColor': 'e6e9ef',
                               'collidesAir': False, 'hitEffect': 'hitBulletSmall', 'despawnEffect': 'hitBulletSmall'}),
        'magnet': shell(speed=4.2, lifetime=185, width=15, height=17, hittable=False, reflectable=False, splashDamage=90, splashDamageRadius=40,
                        backColor='4aa8ff', frontColor='d6f0ff', trailColor='4aa8ff99', status='electrified', statusDuration=240,
                        lightning=5, lightningLength=9, lightningDamage=20, lightningColor='8fd0fa', hitSound='emp-hit',
                        hitEffect=boom('8fd0fa', 40)),
    }})
W('blocks/lash', {
    'type': 'PowerTurret', 'category': 'turret', 'size': 2, 'health': 1100, 'armor': 3, 'research': 'lancer',
    'requirements': ['copper/100', 'silicon/70', 'titanium/50', 'aluminum/35'],
    'range': 160, 'reload': 14, 'rotateSpeed': 8, 'recoil': 1.2, 'shake': 0.4, 'shootY': 9, 'heatColor': 'ff3355', 'cooldownTime': 24,
    'shootSound': 'lash-shoot', 'shoot': {'type': 'ShootAlternate', 'barrels': 2, 'spread': 5.5}, 'consumes': {'power': 3.5},
    'shootType': {'type': 'LaserBoltBulletType', 'speed': 6, 'damage': 24, 'lifetime': 28, 'width': 2.6, 'height': 9,
                  'frontColor': 'ffd6dd', 'backColor': 'ff3355', 'lightColor': 'ff3355', 'buildingDamageMultiplier': 0.5,
                  'hitEffect': 'hitLaser', 'despawnEffect': 'hitLaser', 'shootEffect': flash('ffd6dd', 'ff3355', 0.5)}})
def missile(dmg, spl, r, c1, c2, **kw):
    b = {'type': 'MissileBulletType', 'speed': 3.6, 'damage': dmg, 'splashDamage': spl, 'splashDamageRadius': r, 'lifetime': 72,
         'width': 7, 'height': 10, 'homingPower': 0.12, 'homingRange': 80, 'frontColor': c1, 'backColor': c2, 'trailColor': 'b8b8b8',
         'hitShake': 1, 'hitSound': 'explosion', 'hitEffect': boom(c2, r), 'shootEffect': flash(c1, c2, 0.6)}
    b.update(kw); return b
W('blocks/hydra', {
    'type': 'ItemTurret', 'category': 'turret', 'size': 3, 'health': 2200, 'armor': 5, 'research': 'vg-lash',
    'requirements': ['copper/200', 'graphite/120', 'silicon/120', 'titanium/80', 'aluminum/60', 'cobalt-alloy/40'],
    'range': 256, 'reload': 120, 'rotateSpeed': 4, 'inaccuracy': 7, 'velocityRnd': 0.12, 'recoil': 1.5, 'shake': 1, 'shootY': 8,
    'heatColor': 'ff3355', 'cooldownTime': 60, 'shootSound': 'hydra-launch', 'maxAmmo': 32,
    'shoot': {'type': 'ShootAlternate', 'barrels': 2, 'spread': 10, 'shots': 8, 'shotDelay': 4}, 'consumes': {'coolant': {'amount': 0.2}},
    'ammoTypes': {
        'charge': missile(20, 42, 20, 'ffd6dd', 'ff3355', ammoMultiplier=2),
        'blast-compound': missile(22, 70, 26, 'ffcf8a', 'ff7a1e', status='blasted', reloadMultiplier=0.85),
        'magnet': missile(18, 30, 22, 'd6f0ff', '4aa8ff', lightning=2, lightningLength=7, lightningDamage=14, lightningColor='8fd0fa',
                          status='electrified', statusDuration=180, hitSound='emp-hit'),
    }})
W('blocks/wasp', {
    'type': 'ItemTurret', 'category': 'turret', 'size': 3, 'health': 1900, 'armor': 4, 'research': 'vg-sparrow',
    'requirements': ['copper/180', 'graphite/90', 'silicon/120', 'titanium/70', 'aluminum/60'],
    'targetGround': False, 'range': 360, 'reload': 70, 'rotateSpeed': 6, 'inaccuracy': 4, 'recoil': 1.2, 'shootY': 8,
    'heatColor': 'ffb050', 'cooldownTime': 40, 'shootSound': 'wasp-launch', 'maxAmmo': 30,
    'shoot': {'type': 'ShootAlternate', 'barrels': 2, 'spread': 9, 'shots': 4, 'shotDelay': 5},
    'ammoTypes': {
        'silicon': missile(45, 30, 18, 'fff4d6', 'ffb347', speed=5, lifetime=74, homingPower=0.2, homingRange=120, collidesGround=False),
        'blast-compound': missile(40, 55, 26, 'ffcf8a', 'ff7a1e', speed=5, lifetime=74, homingPower=0.18, homingRange=120, collidesGround=False, status='blasted'),
        'magnet': missile(38, 30, 22, 'd6f0ff', '4aa8ff', speed=5, lifetime=74, homingPower=0.2, homingRange=120, collidesGround=False,
                          status='electrified', statusDuration=180, lightning=2, lightningLength=6, lightningColor='8fd0fa', hitSound='emp-hit'),
    }})
def mg(dmg, c1, c2, **kw):
    b = {'type': 'BasicBulletType', 'speed': 6, 'damage': dmg, 'lifetime': 34, 'width': 6, 'height': 10, 'frontColor': c1, 'backColor': c2,
         'hitEffect': 'hitBulletSmall', 'despawnEffect': 'hitBulletSmall', 'shootEffect': 'shootSmall', 'smokeEffect': 'shootSmallSmoke'}
    b.update(kw); return b
W('blocks/rivet', {
    'type': 'ItemTurret', 'category': 'turret', 'size': 2, 'health': 800, 'armor': 2, 'research': 'duo',
    'requirements': ['copper/70', 'lead/40', 'graphite/25', 'steel/20'],
    'range': 200, 'reload': 7, 'rotateSpeed': 10, 'inaccuracy': 2, 'recoil': 1, 'shootY': 7, 'heatColor': 'ffb050', 'cooldownTime': 18,
    'shootSound': 'rivet-shoot', 'ammoUseEffect': 'casing1', 'maxAmmo': 60, 'shoot': {'type': 'ShootAlternate', 'barrels': 2, 'spread': 4.5},
    'ammoTypes': {'copper': mg(11, 'fff0c8', 'd99d73', ammoMultiplier=2), 'graphite': mg(16, 'e6e6e6', '8a8a8a'),
                  'steel': mg(19, 'eef3f8', '98a3b0', pierceArmor=True), 'silicon': mg(13, 'fff4d6', 'ffb347', homingPower=0.06, reloadMultiplier=1.3)}})
def flak(spl, r, c1, c2, **kw):
    b = {'type': 'FlakBulletType', 'speed': 4.2, 'lifetime': 60, 'splashDamage': spl, 'splashDamageRadius': r, 'explodeRange': 26,
         'width': 6, 'height': 8, 'frontColor': c1, 'backColor': c2, 'collidesGround': False, 'hitEffect': 'flakExplosion',
         'shootEffect': 'shootSmall'}
    b.update(kw); return b
W('blocks/sparrow', {
    'type': 'ItemTurret', 'category': 'turret', 'size': 2, 'health': 760, 'armor': 2, 'research': 'scatter',
    'requirements': ['copper/80', 'lead/50', 'graphite/30', 'steel/25'],
    'targetGround': False, 'range': 240, 'reload': 18, 'rotateSpeed': 12, 'inaccuracy': 6, 'recoil': 1, 'shootY': 7,
    'heatColor': 'ffb050', 'cooldownTime': 20, 'shootSound': 'sparrow-shoot', 'maxAmmo': 40,
    'shoot': {'type': 'ShootAlternate', 'barrels': 2, 'spread': 6},
    'ammoTypes': {'steel': flak(30, 22, 'eef3f8', '98a3b0', ammoMultiplier=3), 'metaglass': flak(24, 26, 'ffffff', 'd8f0f6', ammoMultiplier=4),
                  'charge': flak(45, 30, 'fff1b0', 'c7b35a', status='blasted', hitEffect='flakExplosionBig')}})

# ---------------- defence
W('blocks/decoy', {'type': 'Wall', 'category': 'defense', 'size': 2, 'health': 4000, 'armor': 8, 'priority': 3, 'research': 'vg-steel-wall-large',
   'requirements': ['steel/50', 'lead/40', 'aluminum/30', 'silicon/20']})
W('blocks/tungsten-wall', {'type': 'Wall', 'category': 'defense', 'size': 1, 'health': 1800, 'armor': 15, 'research': 'vg-steel-wall',
   'requirements': ['tungsten-core/6', 'steel/2']})
W('blocks/tungsten-wall-large', {'type': 'Wall', 'category': 'defense', 'size': 2, 'health': 7200, 'armor': 15, 'research': 'vg-tungsten-wall',
   'requirements': ['tungsten-core/24', 'steel/8']})
W('blocks/radar', {'type': 'Radar', 'category': 'effect', 'size': 3, 'health': 900, 'research': 'vg-spotter-beacon', 'buildVisibility': 'shown',
   'requirements': ['copper/120', 'lead/90', 'silicon/80', 'aluminum/60', 'magnet/30'], 'fogRadius': 60, 'discoveryTime': 480,
   'rotateSpeed': 1.2, 'glowColor': 'ff3355', 'consumes': {'power': 1.2}, 'ambientSound': 'radar-loop', 'ambientSoundVolume': 0.06})
W('blocks/ed-shield', {'type': 'ForceProjector', 'category': 'effect', 'size': 2, 'health': 900, 'research': 'vg-shield-emitter',
   'requirements': ['lead/120', 'silicon/90', 'steel/60', 'aluminum/40'], 'radius': 72, 'shieldHealth': 1000, 'cooldownNormal': 2.0,
   'cooldownLiquid': 1.4, 'cooldownBrokenBase': 1.2, 'consumes': {'power': 2.5}, 'ambientSound': 'shield-hum', 'ambientSoundVolume': 0.08})
W('blocks/pulse-shield', {'type': 'ForceProjector', 'category': 'effect', 'size': 3, 'health': 1800, 'research': 'vg-ed-shield',
   'requirements': ['lead/240', 'silicon/180', 'titanium/120', 'cobalt-alloy/80', 'magnet/40'], 'radius': 112, 'shieldHealth': 3500,
   'cooldownNormal': 3.2, 'cooldownLiquid': 1.5, 'cooldownBrokenBase': 0.8, 'consumes': {'power': 5},
   'ambientSound': 'shield-hum', 'ambientSoundVolume': 0.1})
W('blocks/nanite-repairer', {'type': 'MendProjector', 'category': 'effect', 'size': 2, 'health': 520, 'research': 'mender',
   'requirements': ['lead/90', 'silicon/70', 'titanium/40', 'aluminum/40'], 'reload': 200, 'range': 90, 'healPercent': 14,
   'baseColor': '84f491', 'consumes': {'power': 1.5}, 'ambientSound': 'nanite-loop', 'ambientSoundVolume': 0.05})

# ---------------- bundles
NAMES.update({
 'item.vg-bauxite': ('Bauxite', 'Боксит', 'Aluminium ore. Electrolysed into aluminium and chlorine.', 'Руда алюминия. Электролизом даёт алюминий и хлор.'),
 'item.vg-cobaltite': ('Cobaltite', 'Кобальтит', 'Blue cobalt ore for heat-resistant alloys.', 'Синяя кобальтовая руда для жаропрочных сплавов.'),
 'item.vg-wolframite': ('Wolframite', 'Вольфрамит', 'Dense tungsten ore. Needs heat to process.', 'Плотная вольфрамовая руда. Перерабатывается только с подводом тепла.'),
 'item.vg-neodymite': ('Neodymite', 'Неодимит', 'Rare-earth ore for permanent magnets.', 'Редкоземельная руда для постоянных магнитов.'),
 'item.vg-aluminum': ('Aluminium', 'Алюминий', 'Light metal. Cluster ammo for Redoubt.', 'Лёгкий металл. Кассетные снаряды для «Редута».'),
 'item.vg-cobalt-alloy': ('Cobalt Alloy', 'Кобальтовый сплав', 'Heat-resistant structural alloy for T3.', 'Жаропрочный сплав для построек Т3.'),
 'item.vg-tungsten-core': ('Tungsten Core', 'Вольфрамовый сердечник', 'Armour-piercing penetrator. AP ammo for Mantis, heavy walls.', 'Бронебойный сердечник. Бронебойные снаряды «Богомола», тяжёлые стены.'),
 'item.vg-magnet': ('Neodymium Magnet', 'Неодимовый магнит', 'EMP ammo: shocks units and slows enemy buildings.', 'ЭМИ-боеприпас: оглушает юнитов и замедляет вражеские постройки.'),
 'liquid.vg-chlorine': ('Chlorine', 'Хлор', 'Corrosive gas, by-product of electrolysis. Used for magnets.', 'Едкий газ, побочный продукт электролиза. Нужен для магнитов.'),
 'block.vg-ore-bauxite': ('Bauxite Ore', 'Бокситовая руда', '', ''),
 'block.vg-ore-cobaltite': ('Cobaltite Ore', 'Кобальтитовая руда', '', ''),
 'block.vg-ore-wolframite': ('Wolframite Ore', 'Вольфрамитовая руда', '', ''),
 'block.vg-ore-neodymite': ('Neodymite Ore', 'Неодимитовая руда', '', ''),
 'block.vg-mass-separator-2': ('Mass Separator II', 'Масс-сепаратор II', 'Separates slag into bauxite, cobaltite, wolframite and neodymite.', 'Разделяет шлак на боксит, кобальтит, вольфрамит и неодимит.'),
 'block.vg-electrolyzer': ('Electrolyzer', 'Электролизёр', 'Bauxite → aluminium + chlorine gas.', 'Боксит → алюминий + газ хлор.'),
 'block.vg-alloy-furnace': ('Alloy Furnace', 'Сплавочная печь', 'Cobaltite + steel + titanium + slag → cobalt alloy.', 'Кобальтит + сталь + титан + шлак → кобальтовый сплав.'),
 'block.vg-heater': ('Heater', 'Нагреватель', 'Burns propellant charges and outputs 6 heat forward.', 'Сжигает пороховые заряды и выдаёт вперёд 6 ед. тепла.'),
 'block.vg-heat-conduit': ('Heat Conduit', 'Тепловод', 'Carries heat forward.', 'Передаёт тепло вперёд.'),
 'block.vg-tungsten-forge': ('Tungsten Forge', 'Вольфрамовый горн', 'Wolframite + graphite → tungsten core. Needs 6 heat; up to ×2 with more.', 'Вольфрамит + графит → вольфрамовый сердечник. Нужно 6 тепла, при избытке — до ×2.'),
 'block.vg-magnet-factory': ('Magnet Factory', 'Магнитная фабрика', 'Neodymite + silicon + chlorine → neodymium magnet.', 'Неодимит + кремний + хлор → неодимовый магнит.'),
 'block.vg-impact-drill': ('Impact Drill', 'Ударный бур', 'T4 drill (3×3): mines thorium, wolframite and neodymite.', 'Бур Т4 (3×3): добывает торий, вольфрамит и неодимит.'),
 'block.vg-redoubt': ('Redoubt', 'Редут', 'T2 fortified howitzer (UEF). 55 tiles, 3-round salvo. HE / incendiary / cluster. Shells ignore point defence — stopped by shields.', 'Т2 укреплённая гаубица (UEF). 55 клеток, залп из 3 снарядов. Фугас / зажигательный / кассетный. Снаряды не сбиваются ПРО — их держат щиты.'),
 'block.vg-mantis': ('Mantis', 'Богомол', 'T3 Cybran heavy artillery (Scathis-style drum). 95 tiles, 6-shell fan. HE / armour-piercing / EMP. Ignores point defence.', 'Т3 тяжёлая артиллерия Кибран (барабан в духе Scathis). 95 клеток, веер из 6 снарядов. Фугас / бронебойный / ЭМИ. Не сбивается ПРО.'),
 'block.vg-lash': ('Lash', 'Плеть', 'T2 Cybran pulse laser. Fast twin bolts, ground and air.', 'Т2 импульсный лазер Кибран. Быстрые парные заряды по земле и воздуху.'),
 'block.vg-hydra': ('Hydra', 'Гидра', 'T3 missile battery: 8 homing missiles per salvo. Magnet ammo = EMP.', 'Т3 ракетная батарея: 8 самонаводящихся ракет за залп. Магниты = ЭМИ.'),
 'block.vg-wasp': ('Wasp', 'Оса', 'T3 anti-air missile battery. Air only.', 'Т3 зенитная ракетная батарея. Только воздух.'),
 'block.vg-rivet': ('Rivet', 'Клёпка', 'T1 twin machine gun. Steel rounds pierce armour.', 'Т1 спаренный пулемёт. Стальные пули пробивают броню.'),
 'block.vg-sparrow': ('Sparrow', 'Воробей', 'T1 flak gun. Air only.', 'Т1 зенитная пушка. Только воздух.'),
 'block.vg-decoy': ('Decoy', 'Ложная цель', 'Armoured dummy that enemy turrets and units prefer to target.', 'Бронированная обманка: вражеские турели и юниты бьют её в первую очередь.'),
 'block.vg-tungsten-wall': ('Tungsten Wall', 'Вольфрамовая стена', 'Armour 15: shrugs off light bullets.', 'Броня 15: лёгкие пули почти не наносят урона.'),
 'block.vg-tungsten-wall-large': ('Large Tungsten Wall', 'Большая вольфрамовая стена', 'Armour 15.', 'Броня 15.'),
 'block.vg-radar': ('Radar', 'Радар', 'T3 radar: reveals fog in a 60-tile radius.', 'Т3 радар: открывает туман в радиусе 60 клеток.'),
 'block.vg-ed-shield': ('ED Shield', 'ЭД-щит', 'T2 shield dome, radius 9 tiles, 1000 HP. Stops Redoubt and Scorpion shells.', 'Т2 купол-щит: радиус 9 клеток, 1000 ед. прочности. Держит снаряды «Редута» и «Скорпиона».'),
 'block.vg-pulse-shield': ('Pulse Shield', 'Импульсный щит', 'T3 shield dome, radius 14 tiles, 3500 HP.', 'Т3 купол-щит: радиус 14 клеток, 3500 ед. прочности.'),
 'block.vg-nanite-repairer': ('Nanite Repairer', 'Нанитовый ремонтник', 'Repairs 14% of block health every 3.3 s in an 11-tile radius.', 'Каждые 3,3 с чинит 14% прочности построек в радиусе 11 клеток.'),
})
for lang, i in (('bundle', 0), ('bundle_ru', 1)):
    L = []
    for k, v in NAMES.items():
        L.append(f'{k}.name = {v[i]}')
        if v[2+i]: L.append(f'{k}.description = {v[2+i]}')
    L += EXTRA[lang]
    open(f'{ROOT}/bundles/{lang}.properties', 'w', encoding='utf-8').write('\n'.join(L)+'\n')
open(f'{ROOT}/scripts/main.js', 'w').write(open('/data/vg2/main.js').read() + open('/data/vg2/main2.js').read() + open('/data/vg2/main3.js').read())
open(f'{ROOT}/mod.hjson', 'w').write(f'''name: vg
displayName: Vanguard Arsenal
author: Muse
version: "{V}"
minGameVersion: 146
java: false
description: "UEF/Cybran artillery, defence and industry. 2.0 stage 3: T2-T3 — Redoubt, Mantis, Lash, Hydra, Wasp, Rivet, Sparrow; ED/Pulse shields, radar, decoy, tungsten walls, nanite repairer; 4 ores, chlorine, heat industry. Stage 2: BKM cores and ACUs. Stage 1: Howl, Scorpion, interceptor, steel chain."
''')
print('stage3 content added', V, len(NAMES), 'bundle keys')
