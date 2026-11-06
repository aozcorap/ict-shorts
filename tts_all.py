#!/usr/bin/env python3
"""Deutsche Sprachspur fuer alle Folgen (offline): Piper-Standardstimme oder eigene Stimme (Klon, Chatterbox).

Pro Untertitelzeile (caps) eine WAV in audio/<folge>_<n>.wav, Start = a + DELAY.
Danach pro Folge Mix (ffmpeg adelay/amix) und Einbau ins gerenderte Video (aac).
Aendert nichts an den Specs: Zeilen, die ihr Zeitfenster [a, b] sprengen, werden nur gemeldet.

Aufruf Piper: python3 tts_all.py --model PFAD/de_DE-thorsten-medium.onnx [--no-mux] [folgen...]
Aufruf Klon:  python3 tts_all.py --engine clone --ref STIMMPROBE.wav --clone-python PFAD/venv/bin/python [--reuse] [folgen...]
  (Stimmprobe: eigene Aufnahme, sauber, 10-30 s, wav; nicht ins Repo legen. --reuse ueberspringt vorhandene WAVs.)
Video-Quelle: <folge>.mp4 im Repo-Root (Ausgabe von render_all.js), Ziel: videos/<folge>.mp4
"""
import argparse, json, re, subprocess, sys, wave
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DELAY = 0.2


# Aussprache nur fuer den Ton (im Bild bleibt der Originaltext).
# Piper: englische Begriffe in Lautschrift [[ ... ]] (die Stimme kennt die englischen Laute).
# Hinweis: direkt vor Satzzeichen KEIN Leerzeichen lassen, sonst verhaspelt sich Piper.
PRON_PIPER = [
    (r"Buy-Side", "[[ baɪ saɪd ]]"), (r"Sell-Side", "[[ sɛl saɪd ]]"),
    (r"Equal Highs", "[[ iːkwəl haɪz ]]"), (r"Equal Lows", "[[ iːkwəl loʊz ]]"),
    (r"Equal High", "[[ iːkwəl haɪ ]]"),
    (r"Liquidity Raid", "[[ lɪkwɪdɪti ɹeɪd ]]"), (r"Raid", "[[ ɹeɪd ]]"),
    (r"Stop Hunt", "[[ stɒp hʌnt ]]"), (r"Stop-Loss-Orders", "[[ stɒp lɒs ɔːdɐz ]]"), (r"Stop-Loss", "[[ stɒp lɒs ]]"),
    (r"Limit-Order", "[[ lɪmɪt ɔːdɐ ]]"), (r"Order Pairing", "[[ ɔːdɐ pɛəɹɪŋ ]]"),
    (r"FOMO", "[[ fɔmoʊ ]]"), (r"Range", "[[ ɹeɪndʒ ]]"), (r"Retest", "[[ ɹiːtɛst ]]"),
    (r"Retail", "[[ ɹiːteɪl ]]"), (r"Short-Händler", "[[ ʃɔːt ]]-Händler"),
    (r"Trader", "[[ tɹeɪdɐ ]]"), (r"ICT", "[[ aɪ siː tiː ]]"),
    (r"Chart", "Tschart"),
]
# Klon (Chatterbox) versteht keine Lautschrift: nur Schreibweisen.
PRON_CLONE = [(r"ICT", "Ei Si Ti")]


def clean(text, engine="piper"):
    text = text.replace("*", "")
    for k, v in (PRON_PIPER if engine == "piper" else PRON_CLONE):
        text = re.sub(rf"(?<![A-Za-zÄÖÜäöü]){k}", v, text)
    return text


def wav_len(p):
    with wave.open(str(p)) as w:
        return w.getnframes() / w.getframerate()


def clips_of(spec):
    intro = [(spec["intro"]["a"], spec["intro"]["b"], spec["intro"]["voice"])] if "intro" in spec else []
    return intro + [(c[0], c[1], c[3]["voice"] if len(c) > 3 and "voice" in c[3] else c[2]) for c in spec["caps"]]


def clone_all(a, slugs, AUD):
    jobs = []
    for slug in slugs:
        spec = json.loads((ROOT / a.spec_dir / f"{slug}.json").read_text())
        for n, (_, _, text) in enumerate(clips_of(spec), 1):
            wav = AUD / f"{slug}_{n}.wav"
            if not (a.reuse and wav.exists()):
                jobs.append({"text": clean(text, "clone"), "out": str(wav)})
    if not jobs:
        return
    jf = AUD / "_clone_jobs.json"
    jf.write_text(json.dumps(jobs, ensure_ascii=False))
    ex, cfg, tmp = a.clone_style.split(",")
    subprocess.run([a.clone_python, str(ROOT / "clone_tts.py"), "--ref", a.ref, "--exaggeration", ex,
                    "--cfg-weight", cfg, "--temperature", tmp, str(jf)], check=True)
    jf.unlink()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--engine", choices=["piper", "clone", "recorded"], default="piper")
    ap.add_argument("--model")
    ap.add_argument("--ref")
    ap.add_argument("--clone-python")
    ap.add_argument("--reuse", action="store_true")
    ap.add_argument("--clone-style", default="0.35,0.3,0.6", help="Klon: exaggeration,cfg_weight,temperature (Standard = Variante B, ruhiger)")
    ap.add_argument("--no-mux", action="store_true")
    ap.add_argument("--spec-dir", default="specs")
    ap.add_argument("--audio-dir", default="audio")
    ap.add_argument("--out-dir", default="videos")
    ap.add_argument("slugs", nargs="*")
    a = ap.parse_args()
    slugs = a.slugs or [f"liq{i:02d}" for i in range(1, 14)]
    AUD, OUT = ROOT / a.audio_dir, ROOT / a.out_dir
    AUD.mkdir(exist_ok=True)
    OUT.mkdir(exist_ok=True)
    if a.engine == "recorded":
        pass  # WAVs liegen bereits im audio-dir (eigene Aufnahmen), nichts synthetisieren
    if a.engine == "piper" and not a.model:
        ap.error("--model fehlt (Piper)")
    if a.engine == "clone":
        if not (a.ref and a.clone_python):
            ap.error("--ref und --clone-python fehlen (Klon)")
        clone_all(a, slugs, AUD)
    overruns = []
    for slug in slugs:
        spec = json.loads((ROOT / a.spec_dir / f"{slug}.json").read_text())
        inputs, filters = [], []
        clips = clips_of(spec)
        for n, (t0, t1, text) in enumerate(clips, 1):
            wav = AUD / f"{slug}_{n}.wav"
            if a.engine == "piper" and not (a.reuse and wav.exists()):
                subprocess.run([sys.executable, "-m", "piper", "-m", a.model, "-f", str(wav)],
                               input=clean(text).encode(), check=True, stderr=subprocess.DEVNULL)
            d = wav_len(wav)
            start = t0 + DELAY
            over = start + d - t1
            flag = f"  UEBERLAENGE +{over:.2f}s" if over > 0 else ""
            print(f"{slug} z{n}: Start {start:.2f}s, Dauer {d:.2f}s, Fenster bis {t1:.2f}s{flag}")
            if over > 0:
                overruns.append((slug, n, round(over, 2), clean(text, a.engine)))
            inputs += ["-i", str(wav)]
            ms = int(round(start * 1000))
            filters.append(f"[{n-1}:a]adelay={ms}|{ms}[a{n-1}]")
        if a.no_mux:
            continue
        src = ROOT / f"{slug}.mp4"
        if not src.exists():
            print(f"{slug}: {src.name} fehlt, erst render_all.js laufen lassen", file=sys.stderr)
            continue
        k = len(clips)
        graph = ";".join(filters) + ";" + "".join(f"[a{i}]" for i in range(k)) + \
            f"amix=inputs={k}:normalize=0:dropout_transition=0[m]"
        mix = AUD / f"{slug}_mix.wav"
        subprocess.run(["ffmpeg", "-v", "error", "-y", *inputs, "-filter_complex", graph,
                        "-map", "[m]", str(mix)], check=True)
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(src), "-i", str(mix),
                        "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "160k",
                        str(OUT / f"{slug}.mp4")], check=True)
        print(f"{slug}: {a.out_dir}/{slug}.mp4 fertig")
    print("\nUEBERLAENGEN:" if overruns else "\nKeine Ueberlaengen.")
    for s, n, o, t in overruns:
        print(f"  {s} Zeile {n}: +{o}s  \"{t}\"")


main()
