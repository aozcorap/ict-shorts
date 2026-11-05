#!/usr/bin/env python3
"""Deutsche Sprachspur fuer alle Folgen (Piper, offline).

Pro Untertitelzeile (caps) eine WAV in audio/<folge>_<n>.wav, Start = a + DELAY.
Danach pro Folge Mix (ffmpeg adelay/amix) und Einbau ins gerenderte Video (aac).
Aendert nichts an den Specs: Zeilen, die ihr Zeitfenster [a, b] sprengen, werden nur gemeldet.

Aufruf:  python3 tts_all.py --model PFAD/de_DE-thorsten-medium.onnx [--no-mux] [folgen...]
Video-Quelle: <folge>.mp4 im Repo-Root (Ausgabe von render_all.js), Ziel: videos/<folge>.mp4
"""
import argparse, json, re, subprocess, sys, wave
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DELAY = 0.2


# Aussprache nur fuer den Ton (im Bild bleibt der Originaltext). ICT wird englisch gesprochen: "ai si ti".
PRON = {"ICT": "Ei Si Ti"}


def clean(text):
    text = text.replace("*", "")
    for k, v in PRON.items():
        text = re.sub(rf"\b{k}\b", v, text)
    return text


def wav_len(p):
    with wave.open(str(p)) as w:
        return w.getnframes() / w.getframerate()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
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
    overruns = []
    for slug in slugs:
        spec = json.loads((ROOT / a.spec_dir / f"{slug}.json").read_text())
        inputs, filters = [], []
        for n, (t0, t1, text, *_) in enumerate(spec["caps"], 1):
            wav = AUD / f"{slug}_{n}.wav"
            subprocess.run([sys.executable, "-m", "piper", "-m", a.model, "-f", str(wav)],
                           input=clean(text).encode(), check=True, stderr=subprocess.DEVNULL)
            d = wav_len(wav)
            start = t0 + DELAY
            over = start + d - t1
            flag = f"  UEBERLAENGE +{over:.2f}s" if over > 0 else ""
            print(f"{slug} z{n}: Start {start:.2f}s, Dauer {d:.2f}s, Fenster bis {t1:.2f}s{flag}")
            if over > 0:
                overruns.append((slug, n, round(over, 2), clean(text)))
            inputs += ["-i", str(wav)]
            ms = int(round(start * 1000))
            filters.append(f"[{n-1}:a]adelay={ms}|{ms}[a{n-1}]")
        if a.no_mux:
            continue
        src = ROOT / f"{slug}.mp4"
        if not src.exists():
            print(f"{slug}: {src.name} fehlt, erst render_all.js laufen lassen", file=sys.stderr)
            continue
        k = len(spec["caps"])
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
