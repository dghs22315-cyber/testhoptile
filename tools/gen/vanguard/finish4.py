src = open('/data/vg2/finish3.py').read()
T4 = [('monolith-full', 'Монолит · T4 страт. арта'), ('bastion-full', 'Бастион · T4 рельса'), ('suppressor-full', 'Подавитель · T4 ЭМИ'),
      ('citadel-full', 'Цитадель · T4 щит'), ('fusion-reactor-full', 'Термоядерный реактор'),
      ('iridium-smelter-full', 'Иридиевая плавильня'), ('superconductor-chamber-full', 'Камера сверхпроводн.'),
      ('plasma-heater-full', 'Плазменный нагреватель'), ('cryocondenser-full', 'Криоконденсатор'),
      ('iridite', 'Иридит'), ('tritium-ice', 'Тритиевый лёд'), ('iridium', 'Иридий'),
      ('superconductor', 'Сверхпроводник'), ('liquid-nitrogen', 'Жидкий азот')]
TB = ['-base', '', '-outline', '-barrel', '-barrel-outline', '-barrel-heat', '-full']
NEED4 = {'monolith': TB, 'bastion': TB, 'suppressor': ['-base', '', '-outline', '-heat', '-full'], 'citadel': ['', '-top', '-full'],
         'cryocondenser': ['-bottom', '', '-glow', '-full'], 'iridium-smelter': ['', '-glow', '-heat', '-full'],
         'superconductor-chamber': ['', '-glow', '-full'], 'plasma-heater': ['', '-glow', '-top1', '-top2', '-heat', '-full'],
         'fusion-reactor': ['', '-glow', '-full']}
REP = [("V = '2.0.0-alpha3'", "V = '2.5.0-alpha1'"),
       ("for k, v in need.items(): EXP[k]", "need.update(NEED4)\nfor k, v in need.items(): EXP[k]"),
       ("EXP['items-3'] = [", "EXP['items-4'] = ['iridite', 'tritium-ice', 'iridium', 'superconductor', 'liquid-nitrogen']\nEXP['items-3'] = ["),
       ("T = [(", "T = T4; _T3 = [("),
       ("/data/vg2/out/stage3-contact.png", "/data/vg2/out/t4-contact.png"),
       ("этап 3: T1–T3 турели, щиты, ресурсы, тепло", "версия 2.5, этап 1: ярус T4"),
       ("/data/vg2/report3.md", "/data/vg2/report5.md")]
for a, b in REP:
    assert a in src, a
    src = src.replace(a, b)
exec(compile(src, 'finish4', 'exec'))
