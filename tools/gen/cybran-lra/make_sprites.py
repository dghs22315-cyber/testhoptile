import numpy as np, os, sys, time
from PIL import Image
from model import build, MID, ELEV, PIVOT
from render import *

OUT = '/data/cybran/out/sprites'
os.makedirs(OUT, exist_ok=True)
NAME = 'cybran-lra'
t0 = time.time()
M = build()

def heat_body(mp, X, Y, g):
    return np.isin(mp, [MID['coil'], MID['heat']]).astype(float)

def heat_barrel(mp, X, Y, g):
    h = np.isin(mp, [MID['coil']]).astype(float)
    hot = np.isin(mp, [MID['metal'], MID['hull_dark'], MID['hull_mid'], MID['bore']])
    grad = np.clip((Y-2.3)/1.05, 0, 1)*0.8
    return np.maximum(h, np.where(hot, grad, 0))

SS = 4
C = 224
base, _ = render_layer(M, ['base'], ['base'], 96, SS)
body, hb = render_layer(M, ['body'], ['body', 'barrel'], C, SS, heat_body)
wingl, _ = render_layer(M, ['wingl'], ['wingl', 'body'], C, SS)
wingr, _ = render_layer(M, ['wingr'], ['wingr', 'body'], C, SS)
barrel, hbar = render_layer(M, ['barrel'], ['barrel'], C, SS, heat_barrel)
print('render', time.time()-t0)

def save(a, n): Image.fromarray(a).save(f'{OUT}/{n}.png')
save(base, f'{NAME}-base')
save(body, NAME)
save(outline(body), f'{NAME}-outline')
save(heat_sprite(hb), f'{NAME}-heat')
save(barrel, f'{NAME}-barrel')
save(outline(barrel), f'{NAME}-barrel-outline')
save(heat_sprite(hbar), f'{NAME}-barrel-heat')
for nm, w in (('wingl', wingl), ('wingr', wingr)):
    save(w, f'{NAME}-{nm}')
    save(outline(w), f'{NAME}-{nm}-outline')

# preview: head assembled (wings, body, barrel) with outlines, as the game would stack it
head = np.zeros((C, C, 4), np.uint8)
for w in (wingl, wingr): head = over(head, outline(w))
for w in (wingl, wingr): head = over(head, w)
head = over(head, outline(body)); head = over(head, body)
head = over(head, outline(barrel)); head = over(head, barrel)
save(head, f'{NAME}-preview')
full = np.zeros((C, C, 4), np.uint8)
full = over(full, base, (C-96)//2, (C-96)//2)
full = over(full, head)
save(full, f'{NAME}-full')
np.save('/data/cybran/out/heat_body.npy', hb); np.save('/data/cybran/out/heat_barrel.npy', hbar)
print('done', time.time()-t0)
