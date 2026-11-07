import json, os, re, subprocess, sys, urllib.request
from pathlib import Path
spec = json.load(open(sys.argv[1])); outdir = Path(sys.argv[2]); voice_id = sys.argv[3]; slug = sys.argv[4]
outdir.mkdir(parents=True, exist_ok=True)
clips = ([spec["intro"]["voice"]] if "intro" in spec else []) + [c[3]["voice"] if len(c) > 3 and "voice" in c[3] else c[2] for c in spec["caps"]]
for n, text in enumerate(clips, 1):
    text = text.replace("*", "")
    body = json.dumps({"text": text, "model_id": "eleven_multilingual_v2",
                       "voice_settings": {"stability": 0.5, "similarity_boost": 0.75, "style": 0.0, "use_speaker_boost": True}}).encode()
    req = urllib.request.Request(f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}?output_format=mp3_44100_128", body,
                                 {"xi-api-key": os.environ["EL_KEY"], "Content-Type": "application/json"})
    try:
        mp3 = urllib.request.urlopen(req, timeout=120).read()
    except urllib.error.HTTPError as e:
        print("FEHLER", e.code, e.read()[:300]); sys.exit(1)
    (outdir / f"{slug}_{n}.mp3").write_bytes(mp3)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(outdir / f"{slug}_{n}.mp3"), "-ar", "44100", "-ac", "1", str(outdir / f"{slug}_{n}.wav")], check=True)
    print(n, len(text), "Zeichen ok")
