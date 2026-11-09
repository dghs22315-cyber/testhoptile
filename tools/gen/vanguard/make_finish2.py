"""Derive finish2.py (self-check, report, zip) for 2.0.0-alpha2 from finish.py."""
s = open('/data/vg2/finish.py').read()
s = s.replace("V = '2.0.0-alpha1'", "V = '2.0.0-alpha2'")
s = s.replace(" 'items': ['ferrolite', 'saltpeter', 'steel', 'charge']}", """ 'items': ['ferrolite', 'saltpeter', 'steel', 'charge'],
 'acu-uef': ['acu-uef', 'acu-uef-leg', 'acu-uef-base', 'acu-uef-cell', 'acu-uef-outline', 'acu-uef-full', 'acu-uef-cannon', 'acu-uef-cannon-outline', 'acu-uef-cannon-heat', 'acu-uef-launcher', 'acu-uef-launcher-outline'],
 'acu-cybran': ['acu-cybran', 'acu-cybran-leg', 'acu-cybran-base', 'acu-cybran-cell', 'acu-cybran-outline', 'acu-cybran-full', 'acu-cybran-laser', 'acu-cybran-laser-heat', 'acu-cybran-emp', 'acu-cybran-emp-heat'],
 'engineer': ['engineer', 'engineer-cell', 'engineer-outline', 'engineer-full'],
 'core-uef': ['core-uef', 'core-uef-team', 'core-uef-full'], 'core-cybran': ['core-cybran', 'core-cybran-team', 'core-cybran-full'],
 'engineering-bay': ['engineering-bay', 'engineering-bay-top', 'engineering-bay-out', 'engineering-bay-full']}""")
s = s.replace("sheet.save('/data/vg2/vanguard-2.0-stage1-sheet.png')\nsheet.resize((sheet.width//2, sheet.height//2)).save('/data/vg2/sheet_qa.jpg', quality=80)\n", "")
a = s.index("rep = f'''"); b = s.index("open(f'{ROOT}/REWORK-REPORT.md'")
rep = open('/data/vg2/report2.md').read()
s = s[:a] + "rep = open('/data/vg2/report2.md').read().replace('{V}', V)\n" + s[b:]
s = s.replace("- JSON-файлы парсятся: OK;", "- JS (scripts/main.js) синтаксис: {JS}\n- JSON-файлы парсятся: OK;")
s = s.replace("rows = []; ok_all = True", "rows = []; ok_all = True\n_r = subprocess.run(['node', '--check', f'{ROOT}/scripts/main.js'], capture_output=True, text=True)\nJS = 'OK' if _r.returncode == 0 else 'ОШИБКА ' + _r.stderr[:300]\nok_all &= _r.returncode == 0")
open('/data/vg2/finish2.py', 'w').write(s)
print('finish2 ready')
