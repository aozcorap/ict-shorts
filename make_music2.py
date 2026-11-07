#!/usr/bin/env python3
"""Energischere eigene Hintergrundmusik (keine Fremdlizenz), zwei Stile.

  python3 make_music2.py DAUER_SEKUNDEN AUSGABE.wav drive|lift
drive: 110 BPM, a-Moll (Am F C G), Kick auf jedem Schlag, Bass, Clap auf 2 und 4, Hi-Hat, Pad pumpt mit dem Kick.
lift:  118 BPM, d-Moll (Dm Bb F C), 16tel-Arpeggio mit Echo, Off-Beat-Hi-Hat, Bass, Pad pumpt mit dem Kick.
"""
import sys, numpy as np, soundfile as sf
from scipy.signal import lfilter

sr = 48000
dur = float(sys.argv[1]); style = sys.argv[3] if len(sys.argv) > 3 else "drive"
rng = np.random.default_rng(11)
N = int(sr * (dur + 3))
hz = lambda m: 440.0 * 2 ** ((m - 69) / 12)
if style == "drive":
    bpm = 110; chords = [[57, 60, 64], [53, 57, 60], [48, 55, 64], [55, 59, 62]]; roots = [45, 41, 36, 43]
else:
    bpm = 118; chords = [[62, 65, 69], [58, 62, 65], [53, 57, 60], [48, 55, 64]]; roots = [38, 34, 29, 36]
beat = 60 / bpm; bar = 4 * beat


def lowpass(x, fc):
    a = np.exp(-2 * np.pi * fc / sr)
    return lfilter([1 - a], [1, -a], x)


def put(buf, t, v):
    i = int(t * sr)
    if 0 <= i < len(buf):
        e = min(len(buf), i + len(v)); buf[i:e] += v[: e - i]


tt_all = np.arange(N) / sr
nb = int((dur + 3) / bar) + 2
# Kick-Zeiten (jeder Schlag)
kick_times = [k * beat for k in range(int((dur + 3) / beat) + 2)]
kt = np.arange(int(0.35 * sr)) / sr
kick = np.sin(2 * np.pi * (48 * kt + 80 * (1 - np.exp(-kt * 30)) / 30)) * np.exp(-kt / 0.12) * 0.55
dr = np.zeros(N)
for t in kick_times: put(dr, t, kick)
# Clap auf 2 und 4
ct = np.arange(int(0.22 * sr)) / sr
clap = rng.standard_normal(len(ct)); clap = lowpass(clap, 6000) - lowpass(clap, 700)
clap = clap * np.exp(-ct / 0.06) * 0.22
for k in range(1, int((dur + 3) / beat) + 2, 2): put(dr, k * beat, clap)
# Hi-Hat
ht = np.arange(int(0.07 * sr)) / sr
hat = rng.standard_normal(len(ht)); hat = hat - lowpass(hat, 7000)
hat_c = hat * np.exp(-ht / 0.015) * 0.10
ot = np.arange(int(0.18 * sr)) / sr
ohat = rng.standard_normal(len(ot)); ohat = (ohat - lowpass(ohat, 7000)) * np.exp(-ot / 0.06) * 0.08
step = beat / 2
for k in range(int((dur + 3) / step) + 2):
    if style == "drive": put(dr, k * step, hat_c if k % 2 == 0 else hat_c * 0.6)
    else:
        if k % 2 == 1: put(dr, k * step, ohat)
        else: put(dr, k * step, hat_c * 0.6)
# Bass: Achtel-Muster
bass = np.zeros(N)
pat = [1, 0, 0, 1, 1, 0, 1, 0] if style == "drive" else [1, 0, 1, 1, 0, 1, 0, 1]
for b in range(nb):
    r = roots[b % 4]
    for k in range(8):
        if pat[k]:
            n = int(0.28 * sr); tt = np.arange(n) / sr
            f = hz(r)
            v = (np.sin(2 * np.pi * f * tt) + 0.4 * (2 * ((f * tt) % 1.0) - 1)) * np.exp(-tt / 0.18) * 0.32
            put(bass, b * bar + k * step, lowpass(v, 400))
# Pad (L/R)
L = np.zeros(N); R = np.zeros(N)
for b in range(nb):
    t0 = b * bar; i0 = int(t0 * sr); i1 = min(N, int((t0 + bar + 0.8) * sr))
    if i0 >= N: break
    tt = np.arange(i1 - i0) / sr
    env = np.minimum(1, tt / 0.4) * np.exp(-np.maximum(0, tt - bar) / 0.4)
    for m in chords[b % 4]:
        for det, side in ((-8, 0), (0, 2), (8, 1)):
            f = hz(m) * 2 ** (det / 1200)
            v = (2 * ((f * tt + rng.random()) % 1.0) - 1) * 0.045 * env
            if side in (0, 2): L[i0:i1] += v
            if side in (1, 2): R[i0:i1] += v
L = lowpass(L, 1400); R = lowpass(R, 1400)
# Arpeggio / Zupfnoten
pl = np.zeros(N)
sub = beat / 4 if style == "lift" else beat / 2
k = 0
while k * sub < dur + 2.5:
    ch = chords[int(k * sub // bar) % 4]
    seq = [0, 1, 2, 1] if style == "drive" else [0, 2, 1, 2, 0, 1, 2, 1]
    m = ch[seq[k % len(seq)]] + 12
    tt = np.arange(int(0.45 * sr)) / sr
    f = hz(m)
    v = (np.sin(2 * np.pi * f * tt) + 0.35 * np.sin(2 * np.pi * 2 * f * tt)) * np.exp(-tt / (0.10 if style == "lift" else 0.14)) * 0.06
    put(pl, k * sub, v); k += 1
d1 = int(0.75 * beat * sr)
echo = np.zeros(N); echo[d1:] += 0.4 * pl[:-d1]
pl = pl + echo
L += pl * 0.9; R += pl * 1.1
# Pumpen: Pad/Arpeggio duckt kurz bei jedem Kick
duck = np.ones(N)
dt = np.arange(int(beat * sr)) / sr
curve = 1 - 0.55 * np.exp(-dt / 0.09)
for t in kick_times:
    i = int(t * sr)
    if i < N:
        e = min(N, i + len(curve)); duck[i:e] = np.minimum(duck[i:e], curve[: e - i])
L *= duck; R *= duck
L += dr + bass; R += dr + bass
y = np.stack([L, R], 1)[: int(sr * dur)]
fade = np.ones(len(y)); n1 = int(sr * 1.0); n2 = int(sr * 2.5)
fade[:n1] = np.linspace(0, 1, n1); fade[-n2:] = np.linspace(1, 0, n2)
y *= fade[:, None]
y /= np.abs(y).max() / 0.7
sf.write(sys.argv[2], y.astype(np.float32), sr, subtype="PCM_16")
print("ok", style, round(len(y) / sr, 1), "s", bpm, "BPM")
