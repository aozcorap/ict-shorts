#!/usr/bin/env python3
"""Hallreduktion fuer WAVs (WPE) + leichte Klangpflege. Aufruf: dereverb.py EIN_ORDNER AUS_ORDNER"""
import sys, subprocess
from pathlib import Path
import numpy as np, soundfile as sf
from nara_wpe.wpe import wpe
from nara_wpe.utils import stft, istft
src, dst = Path(sys.argv[1]), Path(sys.argv[2]); dst.mkdir(parents=True, exist_ok=True)
for f in sorted(src.glob("*.wav")):
    if f.stem.endswith("_mix"): continue
    x, sr = sf.read(f, dtype="float32")
    if x.ndim > 1: x = x[:, 0]
    Y = stft(x, size=512, shift=128).T[:, None, :]          # (F, 1, T)
    Z = wpe(Y, taps=10, delay=3, iterations=4)
    y = istft(Z[:, 0, :].T, size=512, shift=128)[: len(x)]
    y = y / max(1e-6, np.abs(y).max()) * 0.9
    tmp = dst / (f.stem + "_wpe.wav"); sf.write(tmp, y, sr, subtype="PCM_16")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(tmp), "-af",
                    "equalizer=f=250:t=q:w=1:g=-2,afftdn=nr=10:nf=-40,loudnorm=I=-18:TP=-2", "-ar", str(sr), str(dst / f.name)], check=True)
    tmp.unlink(); print("ok", f.name)
