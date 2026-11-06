#!/usr/bin/env python3
"""Erzeugt eine ruhige, eigene Hintergrundmusik (Pad + leichte Zupfnoten), Tonart a-Moll, 90 BPM. Keine Fremdlizenz.

  python3 make_music.py DAUER_SEKUNDEN AUSGABE.wav [rhythm]
Mit "rhythm": zusaetzlich leiser Beat (Kick auf 1 und 3, Snare auf 2 und 4, Hi-Hat auf den Achteln).
"""
import sys, numpy as np, soundfile as sf
from scipy.signal import lfilter

sr = 48000
dur = float(sys.argv[1])
rng = np.random.default_rng(7)
N = int(sr * (dur + 3))
t = np.arange(N) / sr
beat = 60 / 90
bar = 4 * beat
chords = [[57, 60, 64], [57, 60, 65], [55, 60, 64], [55, 59, 62]]  # Am, F, C, G (enge Lagen)
hz = lambda m: 440.0 * 2 ** ((m - 69) / 12)


def saw(f, tt, ph):
    return 2 * ((f * tt + ph) % 1.0) - 1


def lowpass(x, fc):
    a = np.exp(-2 * np.pi * fc / sr)
    return lfilter([1 - a], [1, -a], x)


L = np.zeros(N); R = np.zeros(N)
nbars = int(np.ceil((dur + 3) / bar)) + 1
for b in range(nbars):
    ch = chords[b % 4]
    t0 = b * bar
    i0 = int(t0 * sr); i1 = min(N, int((t0 + bar + 1.2) * sr))
    if i0 >= N: break
    tt = np.arange(i1 - i0) / sr
    env = np.minimum(1, tt / 0.7) * np.exp(-np.maximum(0, tt - bar) / 0.5)
    for m in ch:
        for det, side in ((-7, 0), (0, 2), (7, 1)):
            f = hz(m) * 2 ** (det / 1200)
            v = saw(f, tt, rng.random()) * 0.06 * env
            if side in (0, 2): L[i0:i1] += v
            if side in (1, 2): R[i0:i1] += v
    sub = np.sin(2 * np.pi * hz(ch[0] - 12) * tt) * 0.05 * env
    L[i0:i1] += sub; R[i0:i1] += sub
L = lowpass(L, 1100); R = lowpass(R, 1100)
# leichte Zupfnoten, Achtel, Muster 0-1-2-1, eine Oktave hoeher
pl = np.zeros(N)
step = beat / 2
k = 0
while k * step < dur + 2.5:
    ch = chords[int(k * step // bar) % 4]
    m = ch[[0, 1, 2, 1][k % 4]] + 12
    i0 = int(k * step * sr)
    tt = np.arange(int(0.6 * sr)) / sr
    f = hz(m)
    v = (np.sin(2 * np.pi * f * tt) + 0.35 * np.sin(2 * np.pi * 2 * f * tt)) * np.exp(-tt / 0.16) * 0.05
    e = min(N, i0 + len(v)); pl[i0:e] += v[:e - i0]
    k += 1
d1 = int(0.75 * beat * sr)
echo = np.zeros(N); echo[d1:] += 0.4 * pl[:-d1]
pl = pl + echo
L += pl * 0.9; R += pl * 1.1
if len(sys.argv) > 3 and sys.argv[3] == "rhythm":
    dr = np.zeros(N)
    def put(i0, v):
        e = min(N, i0 + len(v))
        if i0 < N: dr[i0:e] += v[: e - i0]
    kt = np.arange(int(0.35 * sr)) / sr
    kick = np.sin(2 * np.pi * (45 * kt + 75 * (1 - np.exp(-kt * 28)) / 28)) * np.exp(-kt / 0.11) * 0.30
    st = np.arange(int(0.25 * sr)) / sr
    snare = (rng.standard_normal(len(st)) * 0.5 + np.sin(2 * np.pi * 190 * st)) * np.exp(-st / 0.07) * 0.07
    snare = lowpass(snare, 5000) - lowpass(snare, 300)
    ht = np.arange(int(0.08 * sr)) / sr
    hat = rng.standard_normal(len(ht)); hat = hat - lowpass(hat, 6000)
    hat = hat * np.exp(-ht / 0.018) * 0.12
    n8 = 0
    while n8 * step < dur + 2.5:
        tt0 = n8 * step; i0 = int(tt0 * sr); pos = n8 % 8
        if pos in (0, 4): put(i0, kick)
        if pos in (2, 6): put(i0, snare)
        if n8 % 2 == 1: put(i0, hat * 0.8)
        elif pos not in (0, 4): put(i0, hat * 0.5)
        n8 += 1
    L += dr; R += dr
y = np.stack([L, R], 1)[: int(sr * dur)]
fade = np.ones(len(y)); n1 = int(sr * 1.5); n2 = int(sr * 2.5)
fade[:n1] = np.linspace(0, 1, n1); fade[-n2:] = np.linspace(1, 0, n2)
y *= fade[:, None]
y /= np.abs(y).max() / 0.7
sf.write(sys.argv[2], y.astype(np.float32), sr, subtype="PCM_16")
print("ok", len(y) / sr, "s")
