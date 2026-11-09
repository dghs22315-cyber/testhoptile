src = open('/data/cybran/render.py', encoding='utf-8').read()
src = src.replace('from model import MATS, MID', 'from mats import MATS, MID')
old_start = src.index('RAMPS = {')
old_end = src.index('}', old_start) + 1
ramps = '''RAMPS = {
 'hull_dark':  ['15191f','1d222b','272e3a','333c4b','424d5f','566276'],
 'hull_mid':   ['1b2029','262d39','343d4c','45505f','5a6678','748194'],
 'hull_light': ['272d37','363e4b','4b5566','636e81','7f8b9f','a1acbf'],
 'red_armor':  ['2a0b10','45121a','631923','88222f','ad2d3b','cf4252'],
 'metal':      ['24262c','373a42','50545f','6d717e','8e939f','b3b7c2'],
 'metal_light':['31343c','4a4e58','686d79','8b909c','adb2bd','d0d4dc'],
 'cable':      ['101216','191c22','23272f','2e333c','3a3f4a','484e5a'],
 'vent':       ['0b0c0f','111317','17191e','1e2026','25282f','2d3038'],
 'bore':       ['050607','08090b','0b0c0e','0f1013','131418','17191d'],
 'coil':       ['3a1406','5a1f08','7a2b0c','9a3810','ba4614','d85a1c'],
 'heat':       ['30140a','48200e','603012','784016','90501c','a86422'],
 'glow':       ['1b4f7a','2272b0','2f95e0','56b4f2','8fd0fa','cdeeff'],
 'ground':     ['2b2c33','34353d','3d3e47','474852','52535e','5e5f6b'],
 'yellow':     ['3b2d07','5c450b','846312','ad841a','d6a624','f5c84a'],
 'glass':      ['0e1c27','15293a','1e3b51','29506c','376a8b','4c87ab'],
 'copper':     ['3a1d10','5a2e18','7f4322','a65a2e','c9743e','e8955a'],
 'flame':      ['8a2a06','c2420a','f06414','ff8c2a','ffb45a','ffe0a0'],
 'ore_fer':    ['2a1410','46201a','663024','86402e','a6553c','c26e50'],
 'ore_salt':   ['5c5d5c','7c7d7a','9d9e99','bdbeb7','d9dad2','f2f2ec'],
 'steel':      ['2a3038','3f4752','58626f','76818f','98a3b0','c2cbd5'],
 'charge':     ['2a2812','433f1c','615b28','817936','a19946','c3ba5c'],
 'rglow':      ['a3132a','d81c38','ff2b45','ff4a60','ff7486','ff9eab'],
}'''
src = src[:old_start] + ramps + src[old_end:]
src = src.replace("UNLIT = {MID['glow']}", "UNLIT = {MID['glow'], MID['flame'], MID['rglow']}")
# treat flame/rglow like glow in sprite quantization
src = src.replace("cnt[..., MID['glow']] = (cnt[..., MID['glow']]*1.8).astype(int)",
  "for _g in ('glow','flame','rglow'): cnt[..., MID[_g]] = (cnt[..., MID[_g]]*1.8).astype(int)")
src = src.replace("gl = mode == MID['glow']", "gl = np.isin(mode, [MID['glow'], MID['flame'], MID['rglow']])")
# showcase emission colors configurable
src = src.replace("emi[gm] = hexc('ff3048')/255.0", "emi[gm] = hexc(EMI[0])/255.0")
src = src.replace("col[gm] = hexc('ff7a8a')/255.0", "col[gm] = hexc(EMI[1])/255.0")
src = src.replace("gm = m == MID['glow']", "gm = np.isin(m, [MID['glow'], MID['flame'], MID['rglow']])")
src = src.replace("LIGHT_TD = ", "EMI = ['3aa8ff', '9fdcff']\nLIGHT_TD = ")
src = src.replace("spec_k = np.isin(m, [MID['metal'], MID['metal_light'], MID['hull_light'], MID['red_armor']])",
  "spec_k = np.isin(m, [MID['metal'], MID['metal_light'], MID['hull_light'], MID['red_armor'], MID['steel'], MID['yellow'], MID['glass']])")
open('/data/vg2/rend.py', 'w', encoding='utf-8').write(src)
print('ok', 'EMI' in src)
