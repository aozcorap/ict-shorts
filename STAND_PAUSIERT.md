# Stand: pausiert (7. November 2026)

Der Nutzer hat das Projekt vorerst gestoppt ("zu aufwendig, ich muss mich grundsaetzlich anders aufstellen"). Moeglicherweise in ein paar Wochen wieder aufnehmen. Dieses Dokument ist der Einstieg, `UEBERGABE.md` ist die aeltere, laengere Chronik (teils ueberholt).

## Ziel
Erklaervideos (hochkant 1080x1920) zu Smart-Money-/ICT-Konzepten **vollautomatisch aus Text-Specs**, Stimme ohne Einsprechen, am Ende auch automatisch posten (TikTok + YouTube Shorts) mit Dashboard (Postplan, Views/Kommentare).

## Was fertig ist
- **Pipeline Spec -> Video:** `engine_v2.html` + `render_v2.js` (Chart-Animation), `build_v3.py retime` (Zeiten an Sprechlaenge), `finish_v9.py` (Teile zusammenfuegen, Ton, Musik), `make_music.py` (ruhig, unter Stimme), `make_music2.py` (energischer: `drive`, `lift`), `norm_clips.py` (Lautstaerke angleichen), `gen_el.py` (Zeilen per ElevenLabs-API), `dereverb.py` (Hallreduktion), `fit_windows.py`.
- **Posting-Set (Pilot):** `videos_final/` = v01, v03, v05 mit Stimme (ruhige Musik), v02, v04 ohne Stimme (Untertitel + Musik "drive"). Alle Fassungen: `videos_v11/` (mit Stimme), `videos_v11_stumm/` (ohne). Specs: `specs_v11/`. Sprechtexte stehen in den Specs (`caps[3].voice`, Titel: `intro.voice`).
- **Stimme:** ElevenLabs Instant Voice Clone der Stimme des Nutzers, Name "Stimme Smart Money Kompakt", **Stimmen-ID `6jMbC2DXHZpXFYNoOO5R`** (kein Geheimnis). Modell `eleven_multilingual_v2`, Stabilitaet 0.5, Aehnlichkeit 0.75, Stil 0, Speaker Boost an. Gute Ergebnisse brauchen den Satz davor/danach als Kontext (`previous_text`/`next_text`), sonst einzelne Zeilen zu laut/anders.
- **Webseiten fuer den TikTok-Antrag:** Repo `aozcorap/smart-money-kompakt` (oeffentlich, GitHub Pages): `https://aozcorap.github.io/smart-money-kompakt/` (+ `terms.html`, `privacy.html`, `impressum.html`). **Impressum ist nur ein Platzhalter.**
- **Antragsentwurf:** `tiktok_antrag/ANTRAG.md` (Beschreibung, Erklaertext, Demovideo-Ablauf, Risiken) und `app_icon_1024.png`.
- Pilotplan (nicht gestartet): 5 Videos, Mo/Mi/Fr 18:30 (Vermutung), 2 Wochen, von Hand posten, Auswertung: Aufrufe, Anteil bis zum Ende, Kommentare.

## Was nicht geklappt hat / Erkenntnisse
- **Piper (Thorsten):** klingt kuenstlich, englische Begriffe falsch. Verworfen.
- **Chatterbox-Klon:** mehrere Vorlagen (Jabra-Box, MacBook, hallfrei bearbeitet), klang jedes Mal hallig/komisch. Verworfen.
- **ElevenLabs Gratis-Konto ueber die Schnittstelle:** gesperrt ("unusual activity", vermutlich Proxy/VPN der Cloud-Sitzung). Mit Bezahlplan (Starter, Einfuehrungsangebot 1 $) funktionierte die Schnittstelle von der Cloud-Sitzung aus.
- **Vollautomatisches Posten:** TikTok Content Posting API braucht App-Pruefung (Demovideo, verifizierte URLs, Wartezeit, Ablehnung moeglich). Zusaetzlich ein laufendes Web-Tool (Login + Upload, Client Secret auf einem Server). Nicht umgesetzt. Alternative: bezahltes Planungs-Tool mit TikTok-Anbindung (Metricool/Buffer o. ae., ungeprueft).
- Karussell-/Foto-Format statt Video: laut Blogs (nicht belastbar) oft mehr Speicherungen bei Lernthemen; nicht gebaut.

## Offene Punkte (Reihenfolge nach Dringlichkeit)
**Sofort (Sicherheit/Kosten, bei dir):**
1. **ElevenLabs-API-Key loeschen** (Entwickler -> API-Schluessel). Er stand im Chatverlauf. Neuen Key nur ueber die Umgebungseinstellungen (Netzwerk-Geheimnis, Host `api.elevenlabs.io`, Header `xi-api-key`), nicht in den Chat.
2. **ElevenLabs-Abo kuendigen**, falls nicht weitergemacht wird (Einfuehrungsangebot "1 $" gilt vermutlich nur fuer den ersten Monat, danach Normalpreis; Bedingungen nicht geprueft).
3. **Oeffentliches Repo `smart-money-kompakt`:** Seiten sind live, Impressum ist Platzhalter. Entweder Repo/Pages loeschen oder auf privat stellen, oder Impressum fuellen (Anschrift wird oeffentlich). Nicht rechtsgeprueft.
4. **TikTok-Entwicklerportal:** Organisation "Smart Money Kompakt" und App-Entwurf existieren (Tippfehler im App-Namen "Smat" noch zu korrigieren). Nichts eingereicht. Bei Nichtnutzung loeschen.

**Inhalt/Recht vor jeder Veroeffentlichung:**
5. Quelle "Core 03" (Kursmaterial) liegt nicht im Repo; Aussagen in v02 (Teil "Bessere Level") nicht gegen die Quelle geprueft. Rechte am Kursmaterial, Plattformregeln fuer Finanzinhalte, Anlageberatung ungeklaert.
6. KI-Kennzeichnung (TikTok/YouTube) bei Stimme per Klon.
7. Kanalname "Smart Money Kompakt" festgelegt? Handles auf TikTok/YouTube ungeprueft. Im Bild steht der Platzhalter `@kanalname` (engine_v2.html). "ICT" nicht im Namen (Marke).

**Technik / Produkt:**
8. Aussprache englischer Begriffe mit ElevenLabs nur stichprobenartig geprueft (nur per Spracherkennung, nicht gehoert). Betonung schwankt zwischen Zeilen.
9. Videos 70+ s (v02, v03): evtl. zu lang; Stumm-Fassungen sind auf Sprechtempo getaktet.
10. Transkript -> Spec automatisch (bisher von Hand/durch den Assistenten in der Sitzung geschrieben): Eingang, Prompt, Pruefschritt (Ueberlappungen, Wortverbote wie "laut ICT", Gewinnversprechen) fehlen.
11. Ein-Aufruf-Skript (`pipeline`), Beschreibung/Hashtags pro Video, Kanal-Basis (Profilbild, Banner, Cover), Dashboard (Postplan + Kennzahlen), Posting-Automatik (siehe oben), YouTube Shorts.
12. Repo aufraeumen: viele Testordner (`audio_*`, `videos_*`, `specs_*`), `.git` ca. 320 MB; Historie enthaelt das entfernte Original-TikTok-Video (Commits `08d26bc`, `f0ccff7`).

## Regeln (weiter gueltig)
Kein "laut ICT" im Sprechtext, kein Quiz/Countdown/Layout vom Original-TikTok kopieren, "Lehrbeispiel, keine Anlageberatung" bleibt im Bild, keine Gewinnversprechen, keine Geheimnisse ins Repo, Videos immer als Anhang im Chat schicken (kein GitHub am Handy).

## So wuerde man neu starten
1. Umgebung: Node, ffmpeg, `cd fonts && npm install`, `pip install numpy scipy soundfile`; Playwright vorhanden.
2. ElevenLabs-Key als Netzwerk-Geheimnis oder Umgebungsvariable `EL_KEY` setzen (neuen Key erzeugen).
3. Zeilen erzeugen: `EL_KEY=... python3 gen_el.py SPEC.json AUDIO_ORDNER 6jMbC2DXHZpXFYNoOO5R SLUG`; ausserdem `previous_text/next_text` als Kontext (siehe Hinweis oben, im Chat entwickelte `regen.py` ist nicht im Repo).
4. `python3 norm_clips.py AUDIO AUDIO_NORM`; Zeiten `IN_SPECS=... OUT_SPECS=... AUDIO=... python3 build_v3.py retime`; Rendern `SPECDIR=... node render_v2.js <teil>`; Zusammenbau `python3 finish_v9.py --spec-dir ... --audio-dir ... --parts-dir ... --out-dir ... --tmp ... --voice vNN` bzw. `--silent vNN --silent-music drive`.
