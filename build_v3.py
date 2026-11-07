#!/usr/bin/env python3
"""v3: fliessende Sprechtexte (voice) + kurze Stichworte im Bild (screen), Chart-Ereignisse mitgezogen.

  python3 build_v3.py spec     -> specs_v3/vNN_K.json (Texte; Zeiten noch alt)
  (dann Ton erzeugen: tts_all.py --no-mux --spec-dir specs_v3 --audio-dir audio_v3 ...)
  python3 build_v3.py retime   -> specs_v3f/vNN_K.json (Fenster = Sprachlaenge + Atempause, Chart-Zeiten linear umgerechnet)
  python3 build_v3.py concat   -> videos_teile_v3/vNN_K.mp4 -> videos_v3/vNN.mp4
Quelle der Fakten: die Zeilen in specs/liqNN.json; nichts Neues behauptet, nur verbunden und angesprochen.
"""
import copy, json, subprocess, sys, wave
from pathlib import Path
import os

ROOT = Path(__file__).resolve().parent
PAUSE = 0.45   # Atempause nach jeder Zeile
LEAD = 0.2     # Verzoegerung Zeilenstart (wie tts_all.DELAY)
CTA_VOICE = "Welches Thema soll als Nächstes kommen? Schreib es in die Kommentare."
CTA_SCREEN = "Welches *Thema* soll als Nächstes kommen?"

V = {
 "v02": dict(title="Welche Level zählen?", sub="glatt, zackig, equal highs", intro="Welche Level zählen? Glatt, zackig und Equal Highs.", parts=[
  ("liq03", [
   ("Wo ist der Markt *glatt*, wo *zackig*?", "Nicht jedes Level ist gleich viel wert. Schau mal: Wo ist der Markt glatt, und wo zackig?"),
   ("*Zackig*: oft berührt", "Zackig heißt: Der Preis war hier schon oft unterwegs."),
   ("*Glatt*: kaum berührt", "Glatt dagegen sind saubere Hochs, die kaum jemand angefasst hat."),
   ("Dort liegen oft noch viele *Stopps*.", "Und genau dort liegen oft noch viele Stopps."),
   ("Geholt: danach *zackig*", "Wird so ein Level geholt, ist es danach zackig."),
   ("Suche zuerst die *glatten* Level.", "Such dir deshalb zuerst die glatten Level.")]),
  ("liq10", [
   ("*Equal Highs*: zwei fast gleiche Hochs", "Ein Sonderfall sind Equal Highs: zwei Hochs auf fast gleicher Höhe."),
   ("Unten: *Equal Lows*", "Dasselbe unten heißt Equal Lows."),
   ("Stopps *knapp* darüber oder darunter", "Viele setzen ihre Stopps knapp darüber oder darunter."),
   ("Dort: *Ansammlung* von Orders", "So liegt dort eine ganze Ansammlung von Orders."),
   ("Der Preis wird oft *angezogen*", "Der Preis wird von dort oft regelrecht angezogen."),
   ("Eine *Beobachtung*, kein Gesetz", "Das ist eine Beobachtung, kein Gesetz.")]),
  ("liq11", [
   ("Nicht jedes *Equal High* zählt", "Aber Vorsicht: Nicht jedes Equal High ist gleich interessant."),
   ("Schon *abgeholt*", "Hier wurden die Hochs schon abgeholt."),
   ("Die Stopps sind *weg*", "Die Stopps darüber sind also weg."),
   ("Rechts: ein *tieferes Hoch*", "Hier dagegen liegt rechts ein tieferes Hoch."),
   ("Noch *unberührt*", "Diese Hochs sind noch unberührt."),
   ("*Faustregel*: selbst prüfen", "Das ist eine Faustregel. Prüf es immer selbst.")])]),
 "v03": dict(title="Stopps im Markt", sub="marktorder, raid, order pairing", intro="Stopps im Markt. Marktorder, Raid und Order Pairing.", parts=[
  ("liq04", [
   ("Ein Stopp ist erst mal nur eine *Wartestellung*.", "Was passiert eigentlich mit einem Stopp? Erst mal gar nichts: Er wartet nur."),
   ("Preis erreicht ihn: *Marktorder*", "Erreicht der Preis ihn, wird er zur Marktorder."),
   ("Marktorder: *sofort*", "Und eine Marktorder wird sofort ausgeführt."),
   ("Zum nächsten *verfügbaren* Preis", "Zum nächsten Preis, der gerade verfügbar ist."),
   ("*Limit-Order*: wartet", "Eine Limit-Order macht das anders: Sie wartet auf ihren Preis."),
   ("Stopps bringen *plötzlich* Handel", "Darum bringen Stopps plötzlich Handel in den Markt.")]),
  ("liq05", [
   ("Preis läuft über ein *altes Hoch*", "Jetzt wird es spannend: Der Preis läuft kurz über ein altes Hoch."),
   ("Dort: Stopps der *Verkäufer*", "Dort liegen die Stopps der Verkäufer."),
   ("Sie lösen aus: *Kauforders*", "Sie lösen aus und werden zu Kauforders."),
   ("Danach fällt der Preis oft *zurück*", "Und danach fällt der Preis oft wieder zurück."),
   ("*Stop Hunt*: Jagd auf Stopps", "Das nennt man Stop Hunt, die Jagd auf Stopps."),
   ("Ob *Raid*: erst hinterher", "Ob es ein Liquidity Raid war, siehst du erst hinterher.")]),
  ("liq08", [
   ("Große Orders brauchen eine *Gegenseite*", "Und warum passiert das alles? Große Orders brauchen eine Gegenseite."),
   ("Short-Händler: *Gewinn* mitnehmen", "Ein Short-Händler will später seinen Gewinn mitnehmen."),
   ("Jemand muss *verkaufen*", "Dafür muss ihm jemand etwas verkaufen."),
   ("Das liefern: Stopps der *Käufer*", "Genau das liefern die Stopps der Käufer."),
   ("*Order Pairing*", "Dieses Zusammenführen heißt Order Pairing."),
   ("Kein *bewiesener* Ablauf", "Ob es immer genau so abläuft, weiß niemand sicher.")])]),
 "v04": dict(title="Wie Liquidität entsteht", sub="retail-muster und fomo", intro="Wie Liquidität entsteht. Retail-Muster und FOMO.", parts=[
  ("liq06", [
   ("Viele Trader, dieselben *Chartmuster*", "Wie entsteht Liquidität eigentlich? Ganz einfach: Viele Trader nutzen dieselben Chartmuster."),
   ("Widerstand mehrfach *getestet*", "Ein Widerstand wird mehrfach getestet."),
   ("*Ausbruch*: viele steigen ein", "Dann kommt der Ausbruch, und viele steigen ein."),
   ("Manche warten auf den *Retest*", "Manche warten auf den Retest und kaufen dort."),
   ("Alle Stopps liegen *darunter*", "Und ihre Stopps liegen alle darunter."),
   ("Gleiche Muster: *Liquidität*", "So entsteht Liquidität durch gleiche Muster.")]),
  ("liq07", [
   ("Große *Kerzen* in eine Richtung", "Noch ein Klassiker: Plötzlich laufen große Kerzen in eine Richtung."),
   ("Da muss ich *dabei* sein!", "Und viele denken: Da muss ich dabei sein!"),
   ("*FOMO*: Angst, etwas zu verpassen", "Das nennt man FOMO, die Angst, etwas zu verpassen."),
   ("Spät rein, Stopps *nah*", "Sie steigen spät ein, und ihre Stopps liegen ganz nah."),
   ("Liquidität unter dem *Rücksetzer*", "So sammelt sich Liquidität unter dem Rücksetzer."),
   ("Ein Impuls ist oft ein *Köder*", "Darum ist ein schneller Impuls oft ein Köder.")])]),
 "v05": dict(title="Der Ablauf", sub="fünf schritte, ein ablauf", intro="Der Ablauf. Fünf Schritte, die du kennen solltest.", parts=[
  ("liq09", [
   ("1: Der Preis pendelt in einer *Range*.", "Fünf Schritte, und du erkennst Liquidität im Chart. Schritt eins: Der Preis pendelt in einer Range."),
   ("2: Ein *Impuls* bricht nach oben aus.", "Schritt zwei: Ein Impuls bricht nach oben aus."),
   ("3: Unter den Tiefs sammeln sich *Stopps*.", "Schritt drei: Unter den Tiefs sammeln sich Stopps."),
   ("4: Der Preis *kehrt* um.", "Schritt vier: Der Preis kehrt um."),
   ("5: Er läuft zu den *Stopps* zurück.", "Und Schritt fünf: Er läuft zu den Stopps zurück."),
   ("Keine *Garantie*, aber ein Rahmen", "Eine Garantie ist das nicht, aber ein guter Rahmen zum Beobachten.")])]),
 "v06": dict(title="Risiko und Übung", sub="stop-loss und zehn tage training", intro="Risiko und Übung. Stop-Loss und zehn Tage Training.", parts=[
  ("liq12", [
   ("Niemand kennt *alles*", "Und trotzdem gilt: Auch wer das Konzept kennt, kennt nicht alles."),
   ("Niemand weiß, wohin der Preis *wirklich* läuft", "Niemand weiß, wohin der Preis wirklich läuft."),
   ("*Stop-Loss* begrenzt den Verlust", "Ein Stop-Loss begrenzt, was du verlieren kannst."),
   ("Ohne Stopp: Fehler wird *teuer*", "Ohne Stopp kann ein einziger Fehler teuer werden."),
   ("Dort, wo die Idee *ungültig* ist", "Lege ihn dorthin, wo deine Idee ungültig ist."),
   ("*Risiko* zuerst, dann die Chance", "Risiko zuerst, dann die Chance.")]),
  ("liq13", [
   ("Übung: *10 Tage* Chart-Training", "Jetzt bist du dran: Zehn Tage Chart-Training."),
   ("Öffne den *1-Minuten-Chart*", "Öffne den Ein-Minuten-Chart eines Tages."),
   ("Markiere *glatte* und *zackige* Level", "Markiere die glatten und die zackigen Level."),
   ("Notiere die *Uhrzeit*", "Notiere die Uhrzeit, zu der ein Level geholt wurde."),
   ("Notiere *Hoch* und *Tief*", "Und notiere auch Hoch und Tief des Tages."),
   ("Nach 10 Tagen: *Muster*?", "Nach zehn Tagen siehst du Muster, oder eben nicht.")])]),
}


def spec_stage():
    out = ROOT / "specs_v3"
    out.mkdir(exist_ok=True)
    for vid, v in V.items():
        n = len(v["parts"])
        for k, (src, lines) in enumerate(v["parts"], 1):
            o = json.load(open(ROOT / "specs" / f"{src}.json", encoding="utf8"))
            assert len(lines) == len(o["caps"]) == 6, (vid, src)
            p = {k2: o[k2] for k2 in ("slug", "ep", "tag", "title", "sub", "pmin", "pmax", "candles")}
            p["titleSize"] = min(o.get("titleSize", 104), 84)
            p["reveal"] = o["reveal"]; p["elements"] = o.get("elements", [])
            p["_old"] = [[c[0], c[1]] for c in o["caps"]]
            p["caps"] = [[c[0], c[1], s, {"voice": vo}] for c, (s, vo) in zip(o["caps"], lines)]
            if k == 1:
                p["intro"] = {"a": 0.1, "b": 3.8, "voice": v["intro"], "title": v["title"], "sub": v["sub"], "tag": "LIQUIDITÄT"}
            if k < n:
                p["noOutro"] = True
            else:
                p["caps"].append([o["caps"][-1][1], o["caps"][-1][1] + 6, CTA_SCREEN, {"voice": CTA_VOICE}])
                p["next"] = {"ep": "in den kommentaren", "title": "Welches Thema<br>als Nächstes?"}
            json.dump(p, open(out / f"{vid}_{k}.json", "w", encoding="utf8"), ensure_ascii=False, indent=1)
    print("Specs:", sum(len(v["parts"]) for v in V.values()))


def dur(p):
    with wave.open(str(p)) as w:
        return w.getnframes() / w.getframerate()


def retime_stage():
    out = ROOT / os.environ.get("OUT_SPECS", "specs_v3f")
    out.mkdir(exist_ok=True)
    for f in sorted((ROOT / os.environ.get("IN_SPECS", "specs_v3")).glob("v0[1-6]*.json")):
        s = json.load(open(f, encoding="utf8"))
        slug = f.stem
        n = 0
        t = 0.5
        if "intro" in s:
            n = 1
            d = dur(ROOT / os.environ.get("AUDIO", "audio_v3") / f"{slug}_1.wav")
            s["intro"]["b"] = round(max(3.8, 0.1 + LEAD + d + 0.35), 2)
            t = s["intro"]["b"]
        old = s.pop("_old")
        newwin = []
        for k, c in enumerate(s["caps"]):
            n += 1
            L = LEAD + dur(ROOT / os.environ.get("AUDIO", "audio_v3") / f"{slug}_{n}.wav") + PAUSE
            newwin.append((round(t, 2), round(t + L, 2)))
            c[0], c[1] = newwin[-1]
            t += L
        ow = [tuple(x) for x in old]

        def m(x):
            if x < ow[0][0]:
                return max(0.0, newwin[0][0] + (x - ow[0][0]))
            for (oa, ob), (na, nb) in zip(ow, newwin):
                if x <= ob:
                    return na + (x - oa) * (nb - na) / (ob - oa)
            return newwin[5][1] + (x - ow[-1][1])

        def ratio(x):
            for (oa, ob), (na, nb) in zip(ow, newwin):
                if x <= ob:
                    return (nb - na) / (ob - oa)
            return 1.0

        s["reveal"] = [[i0, i1, round(m(t0), 2), round(dt * ratio(t0), 2)] for i0, i1, t0, dt in s["reveal"]]
        for e in s["elements"]:
            if "until" in e:
                e["until"] = round(m(e["until"]), 2)
            e["at"] = round(m(e["at"]), 2)
        json.dump(s, open(out / f"{slug}.json", "w", encoding="utf8"), ensure_ascii=False, indent=1)
    print("retimed")


def concat():
    (ROOT / os.environ.get("OUT_VIDEOS", "videos_v3")).mkdir(exist_ok=True)
    for vid, v in V.items():
        parts = [ROOT / os.environ.get("PARTS_DIR", "videos_teile_v3") / f"{vid}_{k}.mp4" for k in range(1, len(v["parts"]) + 1)]
        lst = ROOT / os.environ.get("PARTS_DIR", "videos_teile_v3") / f"_{vid}.txt"
        lst.write_text("".join(f"file '{p.resolve()}'\n" for p in parts))
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy",
                        str(ROOT / os.environ.get("OUT_VIDEOS", "videos_v3") / f"{vid}{os.environ.get('SUFFIX', '')}.mp4")], check=True)
        lst.unlink()
        print(vid, "fertig")


{"spec": spec_stage, "retime": retime_stage, "concat": concat}[sys.argv[1]]()
