import numpy as np, time
from PIL import Image
from models import *
from rend import *
t0 = time.time()
M = howl(); print('tris', M.ntri())
base, _ = render_layer(M, ['base'], ['base'], 64, 4)
body, hb = render_layer(M, ['body'], ['body', 'barrel'], 96, 4)
bar, hbar = render_layer(M, ['barrel'], ['barrel'], 96, 4, heat_howl_barrel)
print('t', time.time()-t0)
full = np.zeros((96, 96, 4), np.uint8)
full = over(full, base, 16, 16)
full = over(full, outline(body))
full = over(full, body)
full = over(full, outline(bar))
full = over(full, bar)
hs = heat_sprite(hbar)
for n, a in (('base', base), ('body', body), ('bar', bar), ('full', full), ('heat', hs)):
    Image.fromarray(a).save(f'/data/vg2/t_{n}.png')
big = Image.new('RGB', (96*4*3, 96*4), (40, 42, 48))
for i, a in enumerate((full, body, bar)):
    big.paste(Image.fromarray(a).resize((384, 384), Image.NEAREST), (i*384, 0), Image.fromarray(a).resize((384, 384), Image.NEAREST))
big.save('/data/vg2/t_howl.jpg', quality=85)
