import numpy as np, sys, time, os
from PIL import Image
from model import build, MID
from geom import tf, rz
from render import render_view
from model import barrel_world

OUT = '/data/cybran/out'
M = build()

def assemble(yaw, elev=None):
    T = []; m = []; g = []
    for grp in ('base', 'body', 'wingl', 'wingr', 'barrel'):
        src = M.parts[grp] if (grp != 'barrel' or elev is None) else [(barrel_world(t, elev), mm) for t, mm in M.parts['barrel_local']]
        for tri, mat in src:
            if grp != 'base':
                tri = tf(tri, rz(yaw), np.zeros(3))
            T.append(tri); m += [MID[mat]]*len(tri); g += [grp]*len(tri)
    return np.concatenate(T), np.array(m), np.array(g)

which = sys.argv[1] if len(sys.argv) > 1 else 'hero'
t0 = time.time()
if which == 'hero':
    T, m, g = assemble(28, 38)
    im = render_view(T, m, g, cam=(1.35, -0.85, 1.05), light=(-0.35, -1.0, 1.35), W=1400, H=1000,
                     ss=2, ground=7.0, fit_tri=T, margin=0.08, glow_coils=0.55)
    im.save(f'{OUT}/hero.png')
elif which == 'front':
    T, m, g = assemble(-18, 38)
    im = render_view(T, m, g, cam=(-0.55, 1.35, 0.85), light=(0.6, 0.9, 1.4), W=900, H=700,
                     ss=2, ground=7.0, fit_tri=T, margin=0.08, glow_coils=0.25)
    im.save(f'{OUT}/front.png')
elif which == 'top':
    T, m, g = assemble(0)
    im = render_view(T, m, g, cam=(0.0001, -0.0001, 1), light=(-0.55, 0.38, 0.75), W=700, H=700,
                     ss=2, ground=7.0, fit_tri=T, margin=0.06)
    im.save(f'{OUT}/top.png')
print(which, time.time()-t0)
