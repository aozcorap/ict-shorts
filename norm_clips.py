#!/usr/bin/env python3
"""Lautstaerke aller Sprech-WAVs eines Ordners auf denselben Wert (Standard -19.9 LUFS) bringen.
  python3 norm_clips.py EIN_ORDNER AUS_ORDNER [ZIEL_LUFS]
Grund: ElevenLabs erzeugt Zeile fuer Zeile, einzelne Zeilen kamen 5-8 dB zu laut (Ausrufezeichen)."""
import glob, os, re, subprocess, sys
src, dst = sys.argv[1], sys.argv[2]; target = float(sys.argv[3]) if len(sys.argv) > 3 else -19.9
os.makedirs(dst, exist_ok=True)
for f in sorted(glob.glob(os.path.join(src, "*.wav"))):
    o = subprocess.run(["ffmpeg", "-nostats", "-i", f, "-af", "ebur128", "-f", "null", "-"], capture_output=True, text=True).stderr
    I = float(re.findall(r"I:\s+(-?[\d.]+) LUFS", o)[-1])
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", f, "-af", f"volume={target - I:.2f}dB,alimiter=limit=0.89", "-ar", "44100",
                    os.path.join(dst, os.path.basename(f))], check=True)
print("ok")
