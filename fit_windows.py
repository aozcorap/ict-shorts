#!/usr/bin/env python3
"""Passt die Zeitfenster der Specs an die tatsaechliche Laenge der erzeugten WAVs an (fuer die Klon-Stimme).

  python3 fit_windows.py --spec-dir specs_v2 --audio-dir audio_v2_clone --out-dir specs_v2c vNN_K ...
Ist eine Zeile laenger als ihr Fenster, wird das Fenster verlaengert und ALLES danach (Zeilen, Kerzen, Marker)
um dieselbe Zeit nach hinten geschoben. Jede Aenderung wird ausgegeben; die Quell-Specs bleiben unveraendert.
"""
import argparse, json, wave
from pathlib import Path

DELAY = 0.2
MARGIN = 0.15  # Luft zwischen Zeilenende und naechstem Fenster

ap = argparse.ArgumentParser()
ap.add_argument("--spec-dir", required=True)
ap.add_argument("--audio-dir", required=True)
ap.add_argument("--out-dir", required=True)
ap.add_argument("slugs", nargs="+")
a = ap.parse_args()
root = Path(__file__).resolve().parent
(root / a.out_dir).mkdir(exist_ok=True)


def dur(p):
    with wave.open(str(p)) as w:
        return w.getnframes() / w.getframerate()


def shift_after(spec, t, d):
    """alles ab Zeitpunkt t um d nach hinten"""
    spec["reveal"] = [[i0, i1, (t0 + d if t0 >= t else t0), dt] for i0, i1, t0, dt in spec["reveal"]]
    for e in spec.get("elements", []):
        if e["at"] >= t:
            e["at"] += d
        if "until" in e and e["until"] >= t:
            e["until"] += d
    if "countdown" in spec:
        spec["countdown"] = [x + d if x >= t else x for x in spec["countdown"]]


for slug in a.slugs:
    spec = json.load(open(root / a.spec_dir / f"{slug}.json", encoding="utf8"))
    has_intro = "intro" in spec
    n = 0
    log = []
    if has_intro:
        n += 1
        d = dur(root / a.audio_dir / f"{slug}_{n}.wav")
        need = spec["intro"]["a"] + DELAY + d + MARGIN - spec["intro"]["b"]
        if need > 0:
            need = round(need, 2)
            spec["intro"]["b"] = round(spec["intro"]["b"] + need, 2)
            for c in spec["caps"]:
                c[0] = round(c[0] + need, 2); c[1] = round(c[1] + need, 2)
            shift_after(spec, 0, need)
            log.append(f"Intro +{need}s (alles danach um {need}s verschoben)")
    for k, c in enumerate(spec["caps"]):
        n += 1
        d = dur(root / a.audio_dir / f"{slug}_{n}.wav")
        need = c[0] + DELAY + d + MARGIN - c[1]
        if need > 0:
            need = round(need, 2)
            old_b = c[1]
            c[1] = round(c[1] + need, 2)
            for c2 in spec["caps"][k + 1:]:
                c2[0] = round(c2[0] + need, 2); c2[1] = round(c2[1] + need, 2)
            shift_after(spec, old_b, need)
            log.append(f"Zeile {n} ({c[2][:40]}...) Fenster +{need}s, Rest +{need}s")
    json.dump(spec, open(root / a.out_dir / f"{slug}.json", "w", encoding="utf8"), ensure_ascii=False, indent=1)
    print(slug, "|", "; ".join(log) if log else "keine Aenderung")
