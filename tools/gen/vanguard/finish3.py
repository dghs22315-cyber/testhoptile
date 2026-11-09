import json, os, re, glob, subprocess, math
from PIL import Image, ImageDraw, ImageFont
ROOT = '/data/vg2/mod/vg'; V = '2.0.0-alpha3'
ZIP = f'/data/vg2/vanguard-arsenal-{V}.zip'
paths = {os.path.basename(p)[:-4]: p for p in glob.glob(f'{ROOT}/sprites/**/*.png', recursive=True)}
sprites = set(paths)
sounds = {os.path.basename(p)[:-4] for p in glob.glob(f'{ROOT}/sounds/*.ogg')}
src2 = open('/data/vg2/finish2.py').read()
exec(src2[src2.index('EXP = {'):src2.index('rows = []')])
need = {'redoubt': ['-base', '', '-outline', '-barrel', '-barrel-outline', '-barrel-heat', '-full'],
        'mantis': ['-base', '', '-outline', '-barrel', '-barrel-outline', '-barrel-heat', '-full'],
        'electrolyzer': ['-bottom', '', '-glow', '-full'], 'alloy-furnace': ['', '-glow', '-full'], 'tungsten-forge': ['', '-glow', '-heat', '-full'],
        'magnet-factory': ['-bottom', '-spinner', '', '-glow', '-full'], 'mass-separator-2': ['-bottom', '-spinner', '', '-glow', '-full'],
        'heater': ['', '-glow', '-top1', '-top2', '-heat', '-full'], 'heat-conduit': ['', '-top1', '-top2', '-heat', '-full'],
        'impact-drill': ['', '-rotator', '-top', '-full'], 'radar': ['-base', '', '-glow', '-full'], 'ed-shield': ['', '-top', '-full'],
        'pulse-shield': ['', '-top', '-full'], 'nanite-repairer': ['', '-top', '-full'], 'decoy': ['', '-full'],
        'tungsten-wall': ['', '-full'], 'tungsten-wall-large': ['', '-full']}
for t in ('lash', 'hydra', 'wasp', 'rivet', 'sparrow'): need[t] = ['-base', '', '-outline', '-heat', '-full']
for o in ('bauxite', 'cobaltite', 'wolframite', 'neodymite'): need['ore-' + o] = ['1', '2', '3']
for k, v in need.items(): EXP[k] = [k + s for s in v]
EXP['items-3'] = ['bauxite', 'cobaltite', 'wolframite', 'neodymite', 'aluminum', 'cobalt-alloy', 'tungsten-core', 'magnet', 'chlorine']
rows = []; ok_all = True
_r = subprocess.run(['node', '--check', f'{ROOT}/scripts/main.js'], capture_output=True, text=True)
JS = 'OK' if _r.returncode == 0 else 'ОШИБКА ' + _r.stderr[:300]
ok_all &= _r.returncode == 0
for k, lst in EXP.items():
    miss = [s for s in lst if s not in sprites]; ok_all &= not miss
    rows.append(f'| {k} | {len(lst)-len(miss)}/{len(lst)} | {"OK" if not miss else "НЕТ: " + ", ".join(miss)} |')
ref = set(); nfiles = 0
for p in glob.glob(f'{ROOT}/content/**/*.*json', recursive=True):
    txt = open(p).read(); nfiles += 1
    if p.endswith('.json'): json.loads(txt)
    else: assert txt.count('{') == txt.count('}') and txt.count('[') == txt.count(']'), p
    ref |= set(re.findall(r'[Ss]ound"?\s*:\s*"?([a-z0-9-]+)', txt))
js = open(f'{ROOT}/scripts/main.js').read()
ref |= set(re.findall(r'S\(\s*"([a-z0-9-]+)"', js)) | set(re.findall(r'whistle: "([a-z0-9-]+)"', js))
ref = {r for r in ref if '-' in r}
miss_snd = sorted(r for r in ref if r not in sounds); ok_all &= not miss_snd
# content ids referenced in requirements / ammo / research must exist (mod or vanilla)
mod_ids = {os.path.basename(p).split('.')[0] for p in glob.glob(f'{ROOT}/content/**/*.*json', recursive=True)}
VAN = set('copper lead metaglass graphite sand coal titanium thorium scrap silicon plastanium phase-fabric surge-alloy spore-pod blast-compound pyratite '
          'water slag oil cryofluid hail duo scatter lancer laser-drill mender titanium-wall ground-factory core-shard melter ripple'.split())
bad_ref = set()
for p in glob.glob(f'{ROOT}/content/**/*.json', recursive=True):
    o = json.load(open(p))
    for r in o.get('requirements', []): n = r.split('/')[0]; (n in mod_ids or n in VAN) or bad_ref.add(n)
    for n in o.get('ammoTypes', {}): (n in mod_ids or n in VAN) or bad_ref.add(n)
    rs = o.get('research');
    if rs: n = rs[3:] if rs.startswith('vg-') else rs; (n in mod_ids or n in VAN) or bad_ref.add(rs)
ok_all &= not bad_ref
# contact sheet (stage 3)
F = ImageFont.truetype('/usr/share/fonts/liberation-sans/LiberationSans-Bold.ttf', 17)
Fs = ImageFont.truetype('/usr/share/fonts/liberation-sans/LiberationSans-Regular.ttf', 13)
T = [('redoubt-full', 'Редут · T2 гаубица'), ('mantis-full', 'Богомол · T3 арта'), ('lash-full', 'Плеть · T2 лазер'), ('hydra-full', 'Гидра · T3 ракеты'),
     ('wasp-full', 'Оса · T3 ПВО'), ('rivet-full', 'Клёпка · T1 пулемёт'), ('sparrow-full', 'Воробей · T1 флак'), ('ed-shield-full', 'ЭД-щит · T2'),
     ('pulse-shield-full', 'Импульсный щит · T3'), ('radar-full', 'Радар · T3'), ('decoy-full', 'Ложная цель'), ('nanite-repairer-full', 'Нанитовый ремонтник'),
     ('tungsten-wall-large', 'Вольфрамовая стена 2×2'), ('tungsten-wall', 'Вольфрамовая стена 1×1'), ('electrolyzer-full', 'Электролизёр'),
     ('alloy-furnace-full', 'Сплавочная печь'), ('tungsten-forge-full', 'Вольфрамовый горн'), ('magnet-factory-full', 'Магнитная фабрика'),
     ('mass-separator-2-full', 'Масс-сепаратор II'), ('heater-full', 'Нагреватель'), ('heat-conduit-full', 'Тепловод'), ('impact-drill-full', 'Ударный бур T4'),
     ('bauxite', 'Боксит'), ('cobaltite', 'Кобальтит'), ('wolframite', 'Вольфрамит'), ('neodymite', 'Неодимит'), ('aluminum', 'Алюминий'),
     ('cobalt-alloy', 'Кобальтовый сплав'), ('tungsten-core', 'Вольфрамовый сердечник'), ('magnet', 'Неодимовый магнит'), ('chlorine', 'Хлор (газ)'),
     ('ore-bauxite1', 'Руда боксита'), ('ore-cobaltite1', 'Руда кобальтита'), ('ore-wolframite1', 'Руда вольфрамита'), ('ore-neodymite1', 'Руда неодимита')]
C, CW, CH = 5, 220, 220
sheet = Image.new('RGB', (C*CW, 70+math.ceil(len(T)/C)*CH), (24, 26, 32)); d = ImageDraw.Draw(sheet)
d.text((16, 18), f'Vanguard Arsenal {V} — этап 3: T1–T3 турели, щиты, ресурсы, тепло (3D-рендер, вид сверху)', font=F, fill=(232, 184, 46))
for i, (k, lab) in enumerate(T):
    x, y = (i % C)*CW, 70+(i//C)*CH
    d.rectangle([x+8, y+4, x+CW-8, y+CH-10], fill=(44, 47, 56))
    for gx in range(x+8, x+CW-8, 24): d.line([(gx, y+4), (gx, y+CH-40)], fill=(52, 56, 66))
    im = Image.open(paths[k]).convert('RGBA')
    s = min(150/max(im.width, im.height), 6); im = im.resize((round(im.width*s), round(im.height*s)), Image.NEAREST)
    sheet.paste(im, (x+CW//2-im.width//2, y+14+(170-im.height)//2-6), im)
    d.text((x+CW//2, y+CH-26), lab, font=Fs, fill=(225, 228, 235), anchor='mm')
sheet.save('/data/vg2/out/stage3-contact.png')
rep = open('/data/vg2/report3.md').read().replace('{V}', V)
open(f'{ROOT}/REWORK-REPORT.md', 'w').write(rep)
chk = f'''# Vanguard Arsenal {V} — самопроверка

| Блок | Спрайты | Статус |
|---|---|---|
''' + '\n'.join(rows) + f'''

- JS (scripts/main.js) синтаксис: {JS}
- Файлов контента: {nfiles}; JSON парсится, hjson Скорпиона — скобки сбалансированы: OK
- Ссылки на предметы/исследования (requirements, ammoTypes, research): {"все существуют" if not bad_ref else "НЕТ: " + ", ".join(sorted(bad_ref))}
- Звуки, на которые есть ссылки ({len(ref)}): {"все на месте" if not miss_snd else "НЕТ: " + ", ".join(miss_snd)}
- Спрайтов: {len(sprites)}, звуков: {len(sounds)}
'''
open(f'{ROOT}/REWORK-SELFCHECK.md', 'w').write(chk)
subprocess.run(f'cd {ROOT} && rm -f {ZIP} && zip -qr -9 {ZIP} . -x "*.DS_Store"', shell=True, check=True)
sz = os.path.getsize(ZIP); ok_all &= sz < 10e6
open(f'{ROOT}/REWORK-SELFCHECK.md', 'a').write(f'- Архив: {sz/1e6:.2f} МБ (лимит 10 МБ): {"OK" if sz < 10e6 else "ПРЕВЫШЕН"}\n- Итог: {"ПРОЙДЕНО" if ok_all else "ЕСТЬ ОШИБКИ"}\n')
subprocess.run(f'cd {ROOT} && zip -q -9 {ZIP} REWORK-SELFCHECK.md', shell=True, check=True)
print('rows', len(rows), 'files', nfiles, 'refs', len(ref), 'bad_ref', sorted(bad_ref), 'miss_snd', miss_snd, 'JS', JS)
print('zip MB', round(os.path.getsize(ZIP)/1e6, 2), 'ИТОГ', 'ПРОЙДЕНО' if ok_all else 'ЕСТЬ ОШИБКИ')
print([r for r in rows if 'НЕТ' in r])
