#!/usr/bin/env python3
"""Hilfsskript fuer tts_all.py --engine clone: erzeugt WAVs mit der eigenen Stimme (Chatterbox Multilingual, offline auf CPU).

Laeuft in einer eigenen Python-Umgebung mit chatterbox-tts (nicht im Repo), Aufruf durch tts_all.py:
  <python-mit-chatterbox> clone_tts.py --ref STIMMPROBE.wav JOBS.json
JOBS.json: [{"text": "...", "out": "pfad.wav"}, ...]. Das Modell wird einmal geladen.
Hinweis: Chatterbox bettet ein unhoerbares KI-Wasserzeichen (Perth) ein. Es bleibt aktiv.
"""
import argparse, json, random, time

import spacy_pkuseg
spacy_pkuseg.pkuseg = lambda *a, **k: None  # Chinesisch-Segmenter unnoetig (nur Deutsch), vermeidet GitHub-Download

import torch, torchaudio as ta
from chatterbox.mtl_tts import ChatterboxMultilingualTTS

ap = argparse.ArgumentParser()
ap.add_argument("--ref", required=True)
ap.add_argument("--seed", type=int, default=1)
ap.add_argument("jobs")
a = ap.parse_args()
jobs = json.load(open(a.jobs, encoding="utf8"))
m = ChatterboxMultilingualTTS.from_pretrained(device="cpu")
for j in jobs:
    t = time.time()
    random.seed(a.seed); torch.manual_seed(a.seed)
    w = m.generate(j["text"], language_id="de", audio_prompt_path=a.ref)
    ta.save(j["out"], w, m.sr, encoding="PCM_S", bits_per_sample=16)
    print(f"ok {j['out']} ({time.time()-t:.0f}s)", flush=True)
