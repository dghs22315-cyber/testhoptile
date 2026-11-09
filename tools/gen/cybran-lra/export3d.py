"""Export the procedural model to GLB (glTF 2.0, rigged hierarchy) and OBJ/MTL."""
import numpy as np, json, struct, math, os
from model import build, MATS, MID, ELEV, PIVOT
from render import RAMP, tri_normals

OUT = '/data/cybran/out/model'
os.makedirs(OUT, exist_ok=True)
M = build()

def yup(P):
    P = np.asarray(P, float)
    return np.stack([P[..., 0], P[..., 2], -P[..., 1]], -1)

def srgb2lin(c):
    c = np.asarray(c)/255.0
    return np.where(c <= 0.04045, c/12.92, ((c+0.055)/1.055)**2.4)

PBR = {  # metallic, roughness, emissive
 'hull_dark': (0.55, 0.62, None), 'hull_mid': (0.55, 0.55, None), 'hull_light': (0.6, 0.45, None),
 'red_armor': (0.35, 0.45, None), 'metal': (0.9, 0.32, None), 'metal_light': (0.95, 0.25, None),
 'cable': (0.1, 0.8, None), 'vent': (0.4, 0.8, None), 'bore': (0.2, 0.9, None),
 'coil': (0.5, 0.4, (0.55, 0.04, 0.07)), 'heat': (0.3, 0.6, (0.45, 0.03, 0.05)),
 'glow': (0.0, 0.3, (1.0, 0.10, 0.17)),
}
NICE = {'hull_dark':'Cybran_Hull_Dark','hull_mid':'Cybran_Hull','hull_light':'Cybran_Hull_Light',
        'red_armor':'Cybran_Red_Armor','metal':'Gunmetal','metal_light':'Steel_Bright','cable':'Cable_Rubber',
        'vent':'Vent_Recess','bore':'Bore_Black','coil':'Accelerator_Coil','heat':'Heat_Vent','glow':'Cybran_Glow'}

parts = {
  'Base': M.parts['base'], 'Body': M.parts['body'], 'Wing_L': M.parts['wingl'],
  'Wing_R': M.parts['wingr'], 'Barrel': M.parts['barrel_local'],
}
used = [m for m in MATS if any(mm == m for L in parts.values() for _, mm in L)]
mat_index = {m: i for i, m in enumerate(used)}

# ---------------- GLB
buf = bytearray(); views = []; accs = []; meshes = []
def push(arr, target):
    global buf
    while len(buf) % 4: buf.append(0)
    off = len(buf); b = arr.tobytes(); buf += b
    v = {'buffer': 0, 'byteOffset': off, 'byteLength': len(b)}
    if target: v['target'] = target
    views.append(v)
    return len(views)-1

for pname, L in parts.items():
    prims = []
    by = {}
    for T, m in L: by.setdefault(m, []).append(T)
    for m, Ts in by.items():
        T = np.concatenate(Ts)
        n = tri_normals(T)
        P = yup(T.reshape(-1, 3)).astype(np.float32)
        N = yup(np.repeat(n, 3, 0)).astype(np.float32)
        vp = push(P, 34962); vn = push(N, 34962)
        accs.append({'bufferView': vp, 'componentType': 5126, 'count': len(P), 'type': 'VEC3',
                     'min': P.min(0).tolist(), 'max': P.max(0).tolist()})
        ap = len(accs)-1
        accs.append({'bufferView': vn, 'componentType': 5126, 'count': len(N), 'type': 'VEC3'})
        an = len(accs)-1
        prims.append({'attributes': {'POSITION': ap, 'NORMAL': an}, 'material': mat_index[m], 'mode': 4})
    meshes.append({'name': pname, 'primitives': prims})

materials = []
for m in used:
    met, rough, emi = PBR[m]
    base = srgb2lin(RAMP[MID[m], 3]).tolist() + [1.0]
    d = {'name': NICE[m], 'doubleSided': True,
         'pbrMetallicRoughness': {'baseColorFactor': base, 'metallicFactor': met, 'roughnessFactor': rough}}
    if emi: d['emissiveFactor'] = list(emi)
    materials.append(d)

# ---- charge-glow shell: coil rings inflated radially, scaled up from the barrel axis while charging
glowT = np.concatenate([T for T, m in parts['Barrel'] if m == 'coil']).copy()
glowT[..., 0] *= 1.045; glowT[..., 2] *= 1.045
n = tri_normals(glowT)
P = yup(glowT.reshape(-1, 3)).astype(np.float32); N = yup(np.repeat(n, 3, 0)).astype(np.float32)
vp = push(P, 34962); vn = push(N, 34962)
accs.append({'bufferView': vp, 'componentType': 5126, 'count': len(P), 'type': 'VEC3',
             'min': P.min(0).tolist(), 'max': P.max(0).tolist()})
accs.append({'bufferView': vn, 'componentType': 5126, 'count': len(N), 'type': 'VEC3'})
materials.append({'name': 'Charge_Glow', 'doubleSided': True,
                  'pbrMetallicRoughness': {'baseColorFactor': [1.0, 0.08, 0.15, 1.0], 'metallicFactor': 0.0,
                                           'roughnessFactor': 0.3},
                  'emissiveFactor': [1.0, 0.12, 0.2],
                  'extensions': {'KHR_materials_emissive_strength': {'emissiveStrength': 4.0}}})
meshes.append({'name': 'Charge_Glow', 'primitives': [{'attributes': {'POSITION': len(accs)-2, 'NORMAL': len(accs)-1},
                                                      'material': len(materials)-1, 'mode': 4}]})

def quat_x(d): a = math.radians(d)/2; return [math.sin(a), 0.0, 0.0, math.cos(a)]
def quat_y(d): a = math.radians(d)/2; return [0.0, math.sin(a), 0.0, math.cos(a)]

nodes = [
 {'name': 'Cybran_LongRangeArtillery', 'children': [1, 2]},
 {'name': 'Base', 'mesh': 0},
 {'name': 'Turret_Yaw', 'children': [3], 'extras': {'note': 'rotate around Y to aim'}},
 {'name': 'Turret_Recoil', 'children': [4, 5, 6, 7], 'extras': {'note': 'whole-turret kick along local +Z on firing'}},
 {'name': 'Body', 'mesh': 1},
 {'name': 'Wing_L', 'mesh': 2, 'extras': {'note': 'slides outward on deploy'}},
 {'name': 'Wing_R', 'mesh': 3, 'extras': {'note': 'slides outward on deploy'}},
 {'name': 'Barrel_Pitch', 'translation': yup(PIVOT).tolist(), 'rotation': quat_x(ELEV), 'children': [8],
  'extras': {'note': 'pitch around X'}},
 {'name': 'Barrel', 'mesh': 4, 'children': [9], 'extras': {'note': 'recoils along local +Z'}},
 {'name': 'Charge_Glow', 'mesh': 5, 'scale': [1e-4, 1e-4, 1.0],
  'extras': {'note': 'accelerator charge glow, scaled radially 0->1 by the Fire animation'}},
]

# ---------------- animations (sampled at 30 fps, LINEAR)
WING, WING_BACK, RECOIL, KICK, PU = 0.15, 0.0625, 0.34, 0.07, 42.0
SHOT = 40/60  # charge time = firstShotDelay 40 ticks
def smooth(x): x = min(max(x, 0.0), 1.0); return x*x*(3-2*x)
def ease(x): x = min(max(x, 0.0), 1.0); return 1-(1-x)**3
def st(**k):
    s = dict(yaw=0.0, pitch=ELEV, wing=0.0, recoil=0.0, kick=0.0, glow=0.0); s.update(k); return s
def fire(u):
    if u < SHOT: return dict(glow=1.06*smooth(u/SHOT), recoil=0.0, kick=0.0)
    v = u-SHOT
    rec = v/0.04 if v < 0.04 else (1-min((v-0.04)/0.95, 1))**1.8
    kick = v/0.03 if v < 0.03 else (1-min((v-0.03)/0.35, 1))**2
    glow = 1.12 if v < 0.05 else 1.12*(1-min((v-0.05)/0.5, 1))**1.5
    return dict(glow=glow, recoil=rec, kick=kick)
CYCLE = 100/60
def demo(t):
    yaw = 35*smooth(t/1.2) if t < 6.4 else 35*(1-smooth((t-6.4)/1.4))
    if t < 5.2:
        w = ease((t-0.6)/1.0); p = ELEV+(PU-ELEV)*smooth((t-0.6)/1.0)
    else:
        w = 1-smooth((t-5.2)/1.0); p = PU-(PU-ELEV)*smooth((t-5.2)/1.0)
    s = st(yaw=yaw, pitch=p, wing=w)
    for c0 in (1.6, 1.6+CYCLE):
        if c0 <= t < c0+CYCLE: s.update(fire(t-c0))
    return s
CLIPS = [
    ('Idle_Scan', 6.0, lambda t: st(yaw=30*math.sin(2*math.pi*t/6))),
    ('Deploy', 1.0, lambda t: st(wing=ease(t), pitch=ELEV+(PU-ELEV)*smooth(t))),
    ('Fire', CYCLE, lambda t: st(wing=1.0, pitch=PU, **fire(t))),
    ('Undeploy', 1.0, lambda t: st(wing=1-smooth(t), pitch=PU-(PU-ELEV)*smooth(t))),
    ('Demo_Full', 8.4, demo),
]
animations = []
def add_acc(vals, typ, minmax=False):
    a = np.asarray(vals, np.float32)
    d = {'bufferView': push(a, None), 'componentType': 5126, 'count': len(vals), 'type': typ}
    if minmax: d['min'] = [float(a.min())]; d['max'] = [float(a.max())]
    accs.append(d); return len(accs)-1
for name, dur, f in CLIPS:
    ts = np.arange(0, dur+1e-6, 1/30)
    if ts[-1] < dur-1e-4: ts = np.append(ts, dur)
    S = [f(float(t)) for t in ts]
    ti = add_acc(ts, 'SCALAR', True)
    samplers, channels = [], []
    def ch(node, path, vals):
        samplers.append({'input': ti, 'output': add_acc(vals, 'VEC4' if path == 'rotation' else 'VEC3'),
                         'interpolation': 'LINEAR'})
        channels.append({'sampler': len(samplers)-1, 'target': {'node': node, 'path': path}})
    ch(2, 'rotation', [quat_y(s['yaw']) for s in S])
    ch(3, 'translation', [[0, 0, KICK*s['kick']] for s in S])
    ch(5, 'translation', [[-WING*s['wing'], 0, WING_BACK*s['wing']] for s in S])
    ch(6, 'translation', [[WING*s['wing'], 0, WING_BACK*s['wing']] for s in S])
    ch(7, 'rotation', [quat_x(s['pitch']) for s in S])
    ch(8, 'translation', [[0, 0, RECOIL*s['recoil']] for s in S])
    ch(9, 'scale', [[max(1e-4, s['glow']), max(1e-4, s['glow']), 1.0] for s in S])
    animations.append({'name': name, 'samplers': samplers, 'channels': channels})

gltf = {'asset': {'version': '2.0', 'generator': 'Cybran LRA procedural builder (python/numpy)',
                  'copyright': 'Fan-made, inspired by Supreme Commander 2 (Cybran Nation). Non-commercial.'},
        'extensionsUsed': ['KHR_materials_emissive_strength'],
        'scene': 0, 'scenes': [{'name': 'Scene', 'nodes': [0]}], 'nodes': nodes, 'meshes': meshes,
        'materials': materials, 'accessors': accs, 'bufferViews': views, 'animations': animations,
        'buffers': [{'byteLength': len(buf)}]}
while len(buf) % 4: buf.append(0)
gltf['buffers'][0]['byteLength'] = len(buf)
js = json.dumps(gltf, separators=(',', ':')).encode()
while len(js) % 4: js += b' '
glb = struct.pack('<III', 0x46546C67, 2, 12+8+len(js)+8+len(buf))
glb += struct.pack('<II', len(js), 0x4E4F534A) + js + struct.pack('<II', len(buf), 0x004E4942) + bytes(buf)
open(f'{OUT}/cybran_lra.glb', 'wb').write(glb)

# ---------------- OBJ (assembled pose, Y-up, 1 unit = 1 tile)
from model import barrel_world
obj = ['# Cybran Long Range Artillery (fan model, inspired by Supreme Commander 2)', 'mtllib cybran_lra.mtl']
mtl = []
for m in used:
    met, rough, emi = PBR[m]
    c = RAMP[MID[m], 3]/255.0
    mtl += [f'newmtl {NICE[m]}', f'Kd {c[0]:.4f} {c[1]:.4f} {c[2]:.4f}', 'Ks 0.35 0.35 0.38',
            f'Ns {int((1-rough)*200)+10}', 'd 1.0', 'illum 2']
    if emi: mtl.append(f'Ke {emi[0]:.3f} {emi[1]:.3f} {emi[2]:.3f}')
    mtl.append('')
vi = 1
world = dict(parts); world['Barrel'] = [(barrel_world(T), m) for T, m in parts['Barrel']]
ntri = 0
for pname, L in world.items():
    obj.append(f'o {pname}')
    by = {}
    for T, m in L: by.setdefault(m, []).append(T)
    for m, Ts in by.items():
        T = np.concatenate(Ts); n = yup(tri_normals(T)); P = yup(T)
        obj.append(f'usemtl {NICE[m]}')
        for t in range(len(T)):
            for k in range(3): obj.append('v %.5f %.5f %.5f' % tuple(P[t, k]))
            obj.append('vn %.4f %.4f %.4f' % tuple(n[t]))
        for t in range(len(T)):
            a = vi + 3*t
            j = t+1+sum(0 for _ in ())
        base_vn = None
        # faces: each triangle uses its own normal; normals are written in order
        obj.append('# faces')
        ntri += len(T)
        vi += 3*len(T)
# rebuild with correct normal indices (simple, explicit)
lines = ['# Cybran Long Range Artillery (fan model, inspired by Supreme Commander 2)',
         '# Y-up, 1 unit = 1 Mindustry tile (8 world units). Turret faces -Z.', 'mtllib cybran_lra.mtl']
v_i = 1; n_i = 1
for pname, L in world.items():
    lines.append(f'o {pname}')
    by = {}
    for T, m in L: by.setdefault(m, []).append(T)
    for m, Ts in by.items():
        T = np.concatenate(Ts); n = yup(tri_normals(T)); P = yup(T)
        lines.append(f'usemtl {NICE[m]}')
        lines += ['v %.5f %.5f %.5f' % tuple(p) for p in P.reshape(-1, 3)]
        lines += ['vn %.4f %.4f %.4f' % tuple(x) for x in n]
        for t in range(len(T)):
            a = v_i+3*t; nn = n_i+t
            lines.append(f'f {a}//{nn} {a+1}//{nn} {a+2}//{nn}')
        v_i += 3*len(T); n_i += len(T)
open(f'{OUT}/cybran_lra.obj', 'w').write('\n'.join(lines)+'\n')
open(f'{OUT}/cybran_lra.mtl', 'w').write('\n'.join(mtl))
print('glb bytes', len(glb), 'tris', ntri, 'materials', len(used))
