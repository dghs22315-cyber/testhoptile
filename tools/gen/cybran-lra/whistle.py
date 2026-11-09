"""Incoming-shell whistle (classic artillery cue), 1.25 s, descending pitch."""
import numpy as np, wave, subprocess
OUT = '/data/cybran/out/sounds'; name = 'cybran-lra-whistle'
SR = 44100; d = 1.25
t = np.arange(int(SR*d))/SR
f = 1650*np.exp(np.log(560/1650)*(t/d)**1.3) * (1 + 0.006*np.sin(2*np.pi*6.5*t))
ph = 2*np.pi*np.cumsum(f)/SR
x = np.sin(ph) + 0.22*np.sin(2*ph + 0.3) + 0.08*np.sin(3*ph)
n = np.random.default_rng(1).normal(size=t.size)
air = n - np.convolve(n, np.ones(9)/9, 'same')
env = (t/d)**1.7
env *= 1 - np.clip((t - (d - 0.035))/0.035, 0, 1)
env *= np.clip(t/0.01, 0, 1)
y = (x*0.85 + air*0.18*(0.4 + 0.6*t/d))*env
y = y/np.max(np.abs(y))*0.72
w = wave.open(f'{OUT}/{name}.wav', 'wb'); w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
w.writeframes((y*32767).astype(np.int16).tobytes()); w.close()
subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', f'{OUT}/{name}.wav', '-c:a', 'libvorbis', '-q:a', '5', f'{OUT}/{name}.ogg'], check=True)
print('whistle ok')
