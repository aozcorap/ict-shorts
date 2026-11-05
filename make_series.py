#!/usr/bin/env python3
"""Baut aus den 13 Einzelfolgen (specs/) 6 laengere Videos (Teile mit eigenem Chart, hintereinander).

  python3 make_series.py build    -> schreibt specs_v2/vNN_K.json (Teile)
  python3 make_series.py concat   -> fuegt videos_teile/vNN_K.mp4 zu videos_v2/vNN.mp4 zusammen
Zeilen und Reihenfolge bleiben wie in den Einzelfolgen. Neu sind nur: Titelkarte (Teil 1), Kommentar-Aufruf (letzter Teil).
"""
import copy, json, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
D = 3.0  # Laenge der Titelkarte
CTA = "Welches Thema soll als Nächstes kommen? Schreib es in die Kommentare."
VIDEOS = {
    "v01": dict(parts=["liq01", "liq02"], title="Liquidität", sub="was ist das und wo liegt sie?", voice="Liquidität. Was ist das, und wo liegt sie?"),
    "v02": dict(parts=["liq03", "liq10", "liq11"], title="Welche Level zählen?", sub="glatt, zackig, equal highs", voice="Welche Level zählen? Glatt, zackig und Equal Highs."),
    "v03": dict(parts=["liq04", "liq05", "liq08"], title="Stopps im Markt", sub="marktorder, raid, order pairing", voice="Stopps im Markt. Marktorder, Raid und Order Pairing."),
    "v04": dict(parts=["liq06", "liq07"], title="Wie Liquidität entsteht", sub="retail-muster und fomo", voice="Wie Liquidität entsteht. Retail-Muster und FOMO."),
    "v05": dict(parts=["liq09"], title="Der Ablauf", sub="fünf schritte im ict-modell", voice="Der Ablauf. Fünf Schritte im ICT-Modell."),
    "v06": dict(parts=["liq12", "liq13"], title="Risiko und Übung", sub="stop-loss und zehn tage training", voice="Risiko und Übung. Stop-Loss und zehn Tage Training."),
}


def build():
    out = ROOT / "specs_v2"
    out.mkdir(exist_ok=True)
    for vid, v in VIDEOS.items():
        n = len(v["parts"])
        for k, src in enumerate(v["parts"], 1):
            s = json.load(open(ROOT / "specs" / f"{src}.json", encoding="utf8"))
            p = copy.deepcopy(s)
            p["titleSize"] = min(s.get("titleSize", 104), 84)
            p["caps"] = [list(c[:3]) for c in s["caps"]]
            if k == 1:  # Titelkarte vorn, alles um D nach hinten
                p["intro"] = {"a": 0.1, "b": 3.8, "voice": v["voice"], "title": v["title"], "sub": v["sub"], "tag": "LIQUIDITÄT"}
                p["reveal"] = [[a, b, t + D, dt] for a, b, t, dt in s["reveal"]]
                for e in p["elements"]:
                    e["at"] += D
                    if "until" in e:
                        e["until"] += D
                p["caps"] = [[a + D, b + D, t] for a, b, t in p["caps"]]
            if k < n:
                p["noOutro"] = True
                p.pop("next", None)
            else:  # Kommentar-Aufruf am Ende
                last = p["caps"][-1][1]
                p["caps"].append([last, last + 6, CTA])
                p["next"] = {"ep": "in den kommentaren", "title": "Welches Thema<br>als Nächstes?"}
            json.dump(p, open(out / f"{vid}_{k}.json", "w", encoding="utf8"), ensure_ascii=False, indent=1)
    print("Specs geschrieben:", sum(len(v["parts"]) for v in VIDEOS.values()), "Teile")


def concat():
    (ROOT / "videos_v2").mkdir(exist_ok=True)
    for vid, v in VIDEOS.items():
        parts = [ROOT / "videos_teile" / f"{vid}_{k}.mp4" for k in range(1, len(v["parts"]) + 1)]
        lst = ROOT / "videos_teile" / f"_{vid}.txt"
        lst.write_text("".join(f"file '{p.resolve()}'\n" for p in parts))
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy",
                        str(ROOT / "videos_v2" / f"{vid}.mp4")], check=True)
        lst.unlink()
        print(vid, "fertig")


{"build": build, "concat": concat}[sys.argv[1]]()
