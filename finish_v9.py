#!/usr/bin/env python3
"""Fertigstellung v9: Teile -> ein Video pro Thema, Ton (Piper-WAVs) + eigene Musik darunter.

  python3 finish_v9.py --spec-dir specs_v9 --audio-dir AUDIO --parts-dir TEILE --out-dir videos_v9 \
      --voice v01 v03 v05 --silent v02 v04 v06

Voraussetzung: <parts-dir>/<slug>.mp4 (Ausgabe render_v2.js, ohne Ton) und <audio-dir>/<slug>_<n>.wav (tts_all.py --no-mux).
--voice:  Sprecher (Piper) auf -16 LUFS, Musik (Beat) auf -38 LUFS, beim Sprechen weiter abgesenkt.
--silent: ohne Sprecher, nur Musik (-24 LUFS), Bildtext traegt den Inhalt.
Hinweis: Die Mischung von "Fassung 3" war nicht als Skript im Repo; diese Werte sind eine Rekonstruktion aus UEBERGABE.md.
Der Ton wird ueber ALLE Teile zusammen auf die Gesamtlaenge gelegt (kein Versatz durch Teile-Enden).
"""
import argparse, json, subprocess, sys, wave
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DELAY = 0.2
FPS = 24


def probe(p):
    r = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=nb_frames",
                        "-of", "csv=p=0", str(p)], capture_output=True, text=True, check=True)
    return int(r.stdout.strip()) / FPS


def clips_of(spec):
    intro = [(spec["intro"]["a"], spec["intro"]["voice"])] if "intro" in spec else []
    return intro + [(c[0], None) for c in spec["caps"]]


def parts_of(vid, spec_dir):
    if (spec_dir / f"{vid}.json").exists():
        return [vid]
    return sorted(p.stem for p in spec_dir.glob(f"{vid}_*.json"))


def run(*cmd):
    subprocess.run([str(c) for c in cmd], check=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--spec-dir", required=True)
    ap.add_argument("--audio-dir", required=True)
    ap.add_argument("--parts-dir", required=True)
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--voice", nargs="*", default=[])
    ap.add_argument("--silent", nargs="*", default=[])
    ap.add_argument("--tmp", required=True)
    a = ap.parse_args()
    spec_dir, aud, parts, out, tmp = (Path(x) for x in (a.spec_dir, a.audio_dir, a.parts_dir, a.out_dir, a.tmp))
    spec_dir = spec_dir if spec_dir.is_absolute() else ROOT / spec_dir
    out = out if out.is_absolute() else ROOT / out
    out.mkdir(exist_ok=True)
    tmp.mkdir(parents=True, exist_ok=True)
    for vid, mode in [(v, "voice") for v in a.voice] + [(v, "silent") for v in a.silent]:
        slugs = parts_of(vid, spec_dir)
        durs = [probe(parts / f"{s}.mp4") for s in slugs]
        total = sum(durs)
        # 1) Video ohne Ton zusammenfuegen
        lst = tmp / f"_{vid}.txt"
        lst.write_text("".join(f"file '{(parts / (s + '.mp4')).resolve()}'\n" for s in slugs))
        vcat = tmp / f"{vid}_video.mp4"
        run("ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", "-an", vcat)
        # 2) Musik in Gesamtlaenge
        music = tmp / f"{vid}_music.wav"
        run(sys.executable, ROOT / "make_music.py", f"{total:.2f}", music, "rhythm")
        fade = f"afade=t=out:st={total - 1.5:.2f}:d=1.5"
        if mode == "silent":
            run("ffmpeg", "-v", "error", "-y", "-i", vcat, "-i", music, "-filter_complex",
                f"[1:a]loudnorm=I=-24:TP=-2:LRA=7,{fade},atrim=0:{total:.2f}[m]", "-map", "0:v", "-map", "[m]",
                "-c:v", "copy", "-c:a", "aac", "-b:a", "160k", "-t", f"{total:.2f}", out / f"{vid}.mp4")
            print(vid, "stumm fertig", f"{total:.1f}s")
            continue
        # 3) Sprecher: alle Zeilen aller Teile auf eine Zeitachse
        inputs, filt, n, off = [], [], 0, 0.0
        for s, d in zip(slugs, durs):
            spec = json.loads((spec_dir / f"{s}.json").read_text())
            for k, (t0, _) in enumerate(clips_of(spec), 1):
                wav = aud / f"{s}_{k}.wav"
                ms = int(round((off + t0 + DELAY) * 1000))
                inputs += ["-i", wav]
                filt.append(f"[{n}:a]adelay={ms}|{ms}[a{n}]")
                n += 1
            off += d
        voice = tmp / f"{vid}_voice.wav"
        g = ";".join(filt) + ";" + "".join(f"[a{i}]" for i in range(n)) + \
            f"amix=inputs={n}:normalize=0:dropout_transition=0,apad=whole_dur={total:.2f},atrim=0:{total:.2f}[m]"
        run("ffmpeg", "-v", "error", "-y", *inputs, "-filter_complex", g, "-map", "[m]", voice)
        # 4) Mischen: Musik -38 LUFS, beim Sprechen abgesenkt
        mixg = (f"[0:a]loudnorm=I=-16:TP=-1.5:LRA=7,aformat=sample_rates=48000:channel_layouts=stereo,asplit=2[vs][vm];"
                f"[1:a]loudnorm=I=-38:TP=-6:LRA=7,atrim=0:{total:.2f}[mu];"
                f"[mu][vs]sidechaincompress=threshold=0.02:ratio=4:attack=30:release=500[md];"
                f"[vm][md]amix=inputs=2:normalize=0,{fade},alimiter=limit=0.95[o]")
        mixed = tmp / f"{vid}_mix.wav"
        run("ffmpeg", "-v", "error", "-y", "-i", voice, "-i", music, "-filter_complex", mixg, "-map", "[o]", mixed)
        run("ffmpeg", "-v", "error", "-y", "-i", vcat, "-i", mixed, "-map", "0:v", "-map", "1:a",
            "-c:v", "copy", "-c:a", "aac", "-b:a", "160k", "-t", f"{total:.2f}", out / f"{vid}.mp4")
        print(vid, "mit Stimme fertig", f"{total:.1f}s")


main()
