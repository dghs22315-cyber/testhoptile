import json, os, re, glob, subprocess, math
from PIL import Image, ImageDraw, ImageFont
ROOT = '/data/vg2/mod/vg'; V = '2.0.0-alpha2'
ZIP = f'/data/vg2/vanguard-arsenal-{V}.zip'
sprites = {os.path.basename(p)[:-4] for p in glob.glob(f'{ROOT}/sprites/**/*.png', recursive=True)}
sounds = {os.path.basename(p)[:-4] for p in glob.glob(f'{ROOT}/sounds/*.ogg')}
EXP = {
 'howl': ['howl', 'howl-base', 'howl-outline', 'howl-barrel', 'howl-barrel-outline', 'howl-barrel-heat', 'howl-full'],
 'scorpion': ['scorpion', 'scorpion-base', 'scorpion-barrel', 'scorpion-wingl', 'scorpion-wingr', 'scorpion-coil', 'scorpion-full'],
 'interceptor': ['interceptor', 'interceptor-base', 'interceptor-full'],
 'spotter-beacon': ['spotter-beacon', 'spotter-beacon-base', 'spotter-beacon-glow', 'spotter-beacon-full'],
 'shield-emitter': ['shield-emitter', 'shield-emitter-top', 'shield-emitter-full'],
 'mass-separator': ['mass-separator', 'mass-separator-bottom', 'mass-separator-spinner', 'mass-separator-glow', 'mass-separator-full'],
 'steel-smelter': ['steel-smelter', 'steel-smelter-glow', 'steel-smelter-full'],
 'propellant-press': ['propellant-press', 'propellant-press-bottom', 'propellant-press-piston', 'propellant-press-top', 'propellant-press-glow', 'propellant-press-full'],
 'steel-wall': ['steel-wall'], 'steel-wall-large': ['steel-wall-large'],
 'ore-ferrolite': ['ore-ferrolite1', 'ore-ferrolite2', 'ore-ferrolite3'], 'ore-saltpeter': ['ore-saltpeter1', 'ore-saltpeter2', 'ore-saltpeter3'],
 'items': ['ferrolite', 'saltpeter', 'steel', 'charge'],
 'acu-uef': ['acu-uef', 'acu-uef-leg', 'acu-uef-base', 'acu-uef-cell', 'acu-uef-outline', 'acu-uef-full', 'acu-uef-cannon', 'acu-uef-cannon-outline', 'acu-uef-cannon-heat', 'acu-uef-launcher', 'acu-uef-launcher-outline'],
 'acu-cybran': ['acu-cybran', 'acu-cybran-leg', 'acu-cybran-base', 'acu-cybran-cell', 'acu-cybran-outline', 'acu-cybran-full', 'acu-cybran-laser', 'acu-cybran-laser-heat', 'acu-cybran-emp', 'acu-cybran-emp-heat'],
 'engineer': ['engineer', 'engineer-cell', 'engineer-outline', 'engineer-full'],
 'core-uef': ['core-uef', 'core-uef-team', 'core-uef-full'], 'core-cybran': ['core-cybran', 'core-cybran-team', 'core-cybran-full'],
 'engineering-bay': ['engineering-bay', 'engineering-bay-top', 'engineering-bay-out', 'engineering-bay-full']}
rows = []; ok_all = True
_r = subprocess.run(['node', '--check', f'{ROOT}/scripts/main.js'], capture_output=True, text=True)
JS = 'OK' if _r.returncode == 0 else 'ОШИБКА ' + _r.stderr[:300]
ok_all &= _r.returncode == 0
for k, lst in EXP.items():
    miss = [s for s in lst if s not in sprites]; ok_all &= not miss
    rows.append(f'| {k} | {len(lst)-len(miss)}/{len(lst)} | {"OK" if not miss else "НЕТ: " + ", ".join(miss)} |')
# sounds referenced
ref = set()
for p in glob.glob(f'{ROOT}/content/**/*.*json', recursive=True):
    txt = open(p).read()
    if p.endswith('.json'): json.loads(txt)
    else: assert txt.count('{') == txt.count('}') and txt.count('[') == txt.count(']'), p
    ref |= set(re.findall(r'[Ss]ound"?\s*:\s*"?([a-z0-9-]+)', txt))
ref |= set(re.findall(r'S\(\s*"([a-z0-9-]+)"', open(f'{ROOT}/scripts/main.js').read())) | set(re.findall(r'whistle: "([a-z0-9-]+)"', open(f'{ROOT}/scripts/main.js').read()))
ref = {r for r in ref if '-' in r}
miss_snd = sorted(r for r in ref if r not in sounds); ok_all &= not miss_snd
# contact sheet
F = ImageFont.truetype('/usr/share/fonts/liberation-sans/LiberationSans-Bold.ttf', 17)
Fs = ImageFont.truetype('/usr/share/fonts/liberation-sans/LiberationSans-Regular.ttf', 13)
T = [('howl', 'Вой · T1 мортира', 'blocks/turrets/howl-full'), ('scorpion', 'Скорпион · T2 арта', 'blocks/turrets/scorpion/scorpion-full'),
     ('interceptor', 'Перехватчик · ПРО', 'blocks/turrets/interceptor-full'), ('shield-emitter', 'Эмиттер щита · T1', 'blocks/defense/shield-emitter-full'),
     ('spotter-beacon', 'Маяк корректировщика', 'blocks/defense/spotter-beacon-full'), ('mass-separator', 'Масс-сепаратор I', 'blocks/crafting/mass-separator-full'),
     ('steel-smelter', 'Сталеплавильня', 'blocks/crafting/steel-smelter-full'), ('propellant-press', 'Пороховой пресс', 'blocks/crafting/propellant-press-full'),
     ('steel-wall-large', 'Стальные стены', 'blocks/walls/steel-wall-large'), ('steel-wall', 'Стальная стена 1×1', 'blocks/walls/steel-wall'),
     ('ferrolite', 'Феролит', 'items/ferrolite'), ('saltpeter', 'Селитра', 'items/saltpeter'), ('steel', 'Сталь', 'items/steel'), ('charge', 'Пороховой заряд', 'items/charge'),
     ('ore-ferrolite', 'Руда феролита', 'blocks/ores/ore-ferrolite1'), ('ore-saltpeter', 'Руда селитры', 'blocks/ores/ore-saltpeter1')]
C, CW, CH = 4, 250, 250
sheet = Image.new('RGB', (C*CW, 70+math.ceil(len(T)/C)*CH), (24, 26, 32)); d = ImageDraw.Draw(sheet)
d.text((16, 18), f'Vanguard Arsenal {V} — этап 1: модели, слои, иконки (3D-рендер, вид сверху)', font=F, fill=(232, 184, 46))
for i, (k, lab, p) in enumerate(T):
    x, y = (i % C)*CW, 70+(i//C)*CH
    d.rectangle([x+8, y+4, x+CW-8, y+CH-10], fill=(44, 47, 56))
    for gx in range(x+8, x+CW-8, 24): d.line([(gx, y+4), (gx, y+CH-40)], fill=(52, 56, 66))
    im = Image.open(f'{ROOT}/sprites/{p}.png').convert('RGBA')
    s = 176/max(im.width, im.height); im = im.resize((round(im.width*s), round(im.height*s)), Image.NEAREST)
    sheet.paste(im, (x+CW//2-im.width//2, y+16+(190-im.height)//2-8), im)
    d.text((x+CW//2, y+CH-26), lab, font=Fs, fill=(225, 228, 235), anchor='mm')
# reports
rep = open('/data/vg2/report2.md').read().replace('{V}', V)
open(f'{ROOT}/REWORK-REPORT.md', 'w').write(rep)
subprocess.run(f'cd {ROOT} && rm -f {ZIP} && zip -qr -9 {ZIP} . -x "*.DS_Store"', shell=True, check=True)
sz = os.path.getsize(ZIP)
chk = f'''# Vanguard Arsenal {V} — самопроверка

| Блок | Спрайты | Статус |
|---|---|---|
''' + '\n'.join(rows) + f'''

- JS (scripts/main.js) синтаксис: {JS}
- JSON-файлы парсятся: OK; hjson Скорпиона — скобки сбалансированы: OK
- Звуки, на которые есть ссылки ({len(ref)}): {"все на месте" if not miss_snd else "НЕТ: " + ", ".join(miss_snd)}
- Архив: {sz/1e6:.2f} МБ (лимит 10 МБ): {"OK" if sz < 10e6 else "ПРЕВЫШЕН"}
- Спрайтов: {len(sprites)}, звуков: {len(sounds)}
- Итог: {"ПРОЙДЕНО" if ok_all else "ЕСТЬ ОШИБКИ"}
'''
open(f'{ROOT}/REWORK-SELFCHECK.md', 'w').write(chk)
subprocess.run(f'cd {ROOT} && zip -q -9 {ZIP} REWORK-SELFCHECK.md', shell=True, check=True)
print(chk); print('size', os.path.getsize(ZIP))
