# Hero-artillery patch: new shootY/moveY for the remade barrels, version 2.0.0-alpha4, rebuild + self-check.
import re
def patch(path, pairs):
    s = open(path).read()
    for a, b in pairs:
        if a in s: s = s.replace(a, b)
    open(path, 'w').write(s)
patch('/data/vg2/build_mod.py', [("'shootY': 8, 'shootSound': 'howl-shoot'", "'shootY': 8.7, 'shootSound': 'howl-shoot'"), ("'moveY': -2.2", "'moveY': -2.4")])
patch('/data/vg2/build_stage3.py', [("'shootY': 14.8", "'shootY': 21.9"), ("'moveY': -3.2", "'moveY': -4.0"), ("'shootY': 17,", "'shootY': 26.8,"), ("'moveY': -3.6", "'moveY': -4.5")])
src = open('/data/vg2/build_stage3.py').read().replace("V = '2.0.0-alpha3'", "V = '2.0.0-alpha4'")
exec(compile(src, 'build_stage3.py', 'exec'))
rep = open('/data/vg2/report3.md').read() + '''

## 2.0.0-alpha4 — переделка моделей артиллерии до уровня «Скорпиона»

- Вой (2×2): UEF-миномёт, ствол под 30°, откатники, ящики с боеприпасами, радиатор, антенна; ~6 900 треугольников, голова 128 px.
- Редут (3×3): UEF-форт, 3 ствола с дульными тормозами, мантелет, открытый магазин с 6 снарядами, командирская башенка, радар; ~10 500 тр., 192 px.
- Богомол (4×4): кибранская тяжёлая арта + барабан Scathis на 6 стволов, катушечный ускоритель, крылья, реакторный барабан, паучьи опоры; ~12 200 тр., 256 px.
- shootY/откат подогнаны под новые стволы: Вой 8.7 / −2.4, Редут 21.9 / −4, Богомол 26.8 / −4.5.
- Набор деталей hero.py — основа для всех моделей T4–T6 (версия 2.5).
'''
open('/data/vg2/report4h.md', 'w').write(rep)
fs = open('/data/vg2/finish3.py').read().replace("V = '2.0.0-alpha3'", "V = '2.0.0-alpha4'").replace('report3.md', 'report4h.md').replace('/data/vg2/out/stage3-contact.png', '/data/vg2/out/hero-contact.png')
exec(compile(fs, 'finish3.py', 'exec'))
