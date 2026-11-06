#!/usr/bin/env python3
"""Zeiten fuer eigene Aufnahmen: Fenster = Verzoegerung + Aufnahmelaenge + kurze Pause.
Chart-Ereignisse werden linear von den alten Fenstern der Spec auf die neuen umgerechnet.

  python3 retime_rec.py --spec-dir specs_v5 --audio-dir audio_v6_handy --out-dir specs_v6 v01
"""
import argparse, json, wave
from pathlib import Path

LEAD, PAUSE = 0.2, 0.15
ap = argparse.ArgumentParser()
ap.add_argument("--spec-dir", required=True); ap.add_argument("--audio-dir", required=True); ap.add_argument("--out-dir", required=True)
ap.add_argument("slug")
a = ap.parse_args()
root = Path(__file__).resolve().parent
(root / a.out_dir).mkdir(exist_ok=True)
s = json.load(open(root / a.spec_dir / f"{a.slug}.json", encoding="utf8"))
dur = lambda n: (lambda w: w.getnframes() / w.getframerate())(wave.open(str(root / a.audio_dir / f"{a.slug}_{n}.wav")))
old = [(c[0], c[1]) for c in s["caps"]]
n = 0; t = 0.5
if "intro" in s:
    n = 1
    s["intro"]["b"] = round(max(3.8, 0.1 + LEAD + dur(1) + 0.3), 2)
    t = s["intro"]["b"]
new = []
for c in s["caps"]:
    n += 1
    L = LEAD + dur(n) + PAUSE
    new.append((round(t, 2), round(t + L, 2))); c[0], c[1] = new[-1]; t += L


def m(x):
    if x < old[0][0]:
        return max(0.0, new[0][0] + (x - old[0][0]))
    for (oa, ob), (na, nb) in zip(old, new):
        if x <= ob:
            return na + (x - oa) * (nb - na) / (ob - oa)
    return new[-1][1] + (x - old[-1][1])


def ratio(x):
    for (oa, ob), (na, nb) in zip(old, new):
        if x <= ob:
            return (nb - na) / (ob - oa)
    return 1.0


s["reveal"] = [[i0, i1, round(m(t0), 2), round(dt * ratio(t0), 2)] for i0, i1, t0, dt in s["reveal"]]
for e in s["elements"]:
    if "until" in e:
        e["until"] = round(m(e["until"]), 2)
    e["at"] = round(m(e["at"]), 2)
json.dump(s, open(root / a.out_dir / f"{a.slug}.json", "w", encoding="utf8"), ensure_ascii=False, indent=1)
print("neue Fenster:", [(round(x, 1), round(y, 1)) for x, y in new])
