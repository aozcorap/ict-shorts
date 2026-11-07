# Übergabe (Stand: Ende der ersten Sitzung)

## Ziel
Kurze Erklärvideos (hochkant, 1080x1920) zu Smart-Money-/ICT-Konzepten, **automatisiert** aus Text-Specs erzeugt: Chart-Animation, Sprecherstimme, Musik. Aus Kursmaterial "Core 03" (nicht öffentlich, Transkript liegt NICHT im Repo). Hinweis im Bild: "Lehrbeispiel, keine Anlageberatung".

## Stand
- 13 Einzelfolgen (`specs/liq01-13.json`) wurden zu **6 längeren Videos** (v01-v06) zusammengelegt, Sprechtext neu geschrieben (fließend, direkt, kein "laut ICT").
- Alles ist auf `main` gepusht (Branch `claude/stoic-knuth-lw9zjw` identisch). Kein PR offen.
- **Fertige Videos (Beispiele):**
  - `videos_v7/v01_handy_klar_musik_beat_leise.mp4`: v01 mit der ECHTEN Stimme des Nutzers (eigene Handy-Aufnahme, Hall verringert) + Musik Fassung 3. Beste Fassung bisher.
  - `videos_v8/v02..v06.mp4`: Klon-Stimme (Chatterbox) + Musik Fassung 3.
  - `videos_v3/v01..v06.mp4`: Standardstimme Piper (Thorsten-medium), Fließtext.

## Übersicht: was ist aktuell, was veraltet (alles auf `main`)

**Fertige Videos (Stand Ende Sitzung 1):**

| Ordner | Inhalt | Status |
|---|---|---|
| `videos_v7/` | v01 mit ECHTER Stimme des Nutzers (Handy-Aufnahme), vier Fassungen | `v01_handy_klar_musik_beat_leise.mp4` = **beste Fassung** (Musik Fassung 3) |
| `videos_v8/` | v02-v06 mit Klon-Stimme + Musik Fassung 3 | **aktuellster Stand**, Stimme dem Nutzer nicht gut genug |
| `videos_v3/` | v01-v06, Standardstimme Piper, Fließtext, ohne Musik | brauchbare Vergleichsbasis |
| `videos_v6_handy/`, `videos_v5_clone/` | Zwischenstände v01 | überholt |
| `videos_v2/`, `videos_v2_clone/`, `videos_v3_clone/`, `videos_v4_clone/` | ältere Testfassungen | überholt |
| `videos/` | ursprüngliche 13 Einzelfolgen ohne Ton | überholt |

**Layout / Optik (aktuell):** `engine_v2.html`, gerendert mit `render_v2.js`.
- Oben ein Fenster "…chart" mit Titel, Kapitel-Tag und Kerzenchart (Zonen, Linien, Ringe, Labels).
- Darunter ein Fenster "erklaerung.log" (Konsole) mit kurzen Stichworten, getippt, Schlüsselwort markiert; Schrittzähler unten.
- Titelkarte am Anfang (ca. 3,8 s, mit gesprochenem Titel), Abschlusskarte "Welches Thema als Nächstes?" am Ende.
- Fußzeile "Lehrbeispiel, keine Anlageberatung", oben Platzhalter `@kanalname` (Kanalname noch offen).
- Der alte Look (`engine.html`) ist überholt. Kein Screenshot im Repo, nur der Code; ein Standbild lässt sich mit `render_v2.js` erzeugen.

**Specs (Inhalt je Video):** v01 `specs_v7/v01.json`, v02-v06 `specs_v8f/*.json` (Videos bestehen aus Teilen `vNN_K`). Sprechtexte: `sprechzettel/`. Ausgangsmaterial: `specs/liq01-13.json`, Contentplan `plan/`.

**Audio:** `audio_v7/` (Clips aus der Nutzer-Aufnahme für v01), `audio_v8/` (Klon-Zeilen v02-v06), weitere `audio_*` sind Testvarianten. **Musik:** `music/ruhig_beat_63s.m4a` (Fassung 3 Basis), Erzeugung `make_music.py`.

**Nicht im Repo:** Stimmprobe und Roh-Aufnahmen des Nutzers (`voice_ref/`, nur lokal), Python-venv für den Klon, Zwischenordner `videos_teile*/`, `fr_*/`, `_*.html`, `s_*.png` (alle gitignored, werden beim Rendern neu erzeugt).

## Kernproblem für die nächste Sitzung
Der Nutzer will **vollautomatisch, ohne Aufwand** (später z. B. 40 Videos). Ergebnis bisher:
- Standardstimme (Piper) klingt künstlich/emotionslos, englische Begriffe (ICT, Sell-Side, Raid, Chart) werden deutsch gelesen.
- Klon (Chatterbox, Stimme des Nutzers): gefällt dem Nutzer nicht gut genug, Fachwörter oft verhaspelt, wenig Ausdruck.
- Echte Aufnahme klingt gut, ist aber manuell und damit nicht das Ziel.
**Zu klären:** Welche Stimm-Lösung ist automatisierbar UND gut genug? Optionen (ungetestet, Vermutung): kommerzieller TTS-/Klon-Dienst (z. B. ElevenLabs; braucht freigegebenen Host + Credential über `request_credential`, Stimme läge beim Anbieter), eine lokale Stimme auf Nutzerdaten feinjustieren (braucht viel Aufnahmematerial), oder Textstil/Prosodie gezielt auf die gewählte Stimme zuschneiden. Außerdem: Plattform (TikTok + YouTube Shorts empfohlen), Kanalname (offen, Vorschläge: Chartlogik, Smart Money Kompakt), Thumbnails/Profil/Banner (Platzhalter "@kanalname" im Bild).

## Entscheidungen des Nutzers (beachten)
- Kein "laut ICT" / "ICT behauptet" im Sprechtext; ICT/Smart Money ist die Grundlage des Kanals. Vorsichtig formulieren ("oft", "manchmal"), keine Gewinnversprechen.
- Kein Quiz/Countdown/A-oder-B und kein Layout vom Original-TikTok kopieren (Abmahnrisiko). Das Originalvideo wurde aus dem Repo entfernt (steckt noch in der Git-Historie: Commits `08d26bc`, `f0ccff7`).
- Intro-Titelkarte vorn, offener Kommentar-Aufruf hinten ("Welches Thema soll als Nächstes kommen?").
- Videos immer als Anhang im Chat schicken (`SendUserFile`), der Nutzer hat am Handy keinen GitHub-Zugriff.
- Musik: eigene Musik (`make_music.py`, keine Fremdlizenz), Fassung 3 = Beat, −38 LUFS, beim Sprechen abgesenkt, bis zum Ende.
- Antworten kurz, auf Deutsch, unbequeme Wahrheit zuerst, Gesichertes von Vermutung trennen, nichts stillschweigend ändern, Zeilen die ihr Fenster sprengen melden.

## Pipeline (Skripte)
- `engine_v2.html` + `render_v2.js`: rendert eine Spec zu MP4 (Playwright/Chromium + ffmpeg). `SPECDIR=<ordner> node render_v2.js <slug>`; Ergebnis `<slug>.mp4` im Root (Zwischendatei, nicht einchecken).
- `tts_all.py`: Ton pro Zeile + Mix + Einbau. Engines: `piper` (Standardstimme, englische Begriffe per Lautschrift `[[ ... ]]`), `clone` (Chatterbox via `clone_tts.py`), `recorded` (vorhandene WAVs).
- `fit_windows.py`, `retime_rec.py`, `build_v3.py retime`: Zeitfenster an tatsächliche Sprechlänge anpassen, Chart-Ereignisse mitziehen.
- `build_v3.py`: Texte und Aufbau für v02-v06 (Teile, Titelkarte, Kommentar-Aufruf); Ordner per Umgebungsvariablen.
- `make_series.py`: ältere Zusammenlegung (v2).
- `make_music.py`: eigene Hintergrundmusik, optional `rhythm`.
- Spec-Formate: `specs/` (Original 13 Folgen), `specs_v3/` bis `specs_v8f/` (Varianten, "f" = angepasste Zeiten). Caps: `[von, bis, "Bildtext mit *Schlüsselwort*", {"voice": "Sprechtext"}]`.

## Umgebung (flüchtig, bei neuer Sitzung neu aufsetzen)
- Node, Playwright, ffmpeg vorhanden. `cd fonts && npm install`.
- `pip install piper-tts faster-whisper nara_wpe scipy soundfile`; Piper-Stimme von `huggingface.co/rhasspy/piper-voices` (Host `us.aws.cdn.hf.co` muss freigegeben sein).
- Klon: eigene venv mit `chatterbox-tts` und `setuptools<81`; in `clone_tts.py` wird der Chinesisch-Segmenter abgeschaltet (GitHub-Download nicht nötig). Modell lädt von hf.co. Läuft nur auf CPU, ca. 35 s pro Zeile.
- Stimmprobe des Nutzers liegt nur lokal in `voice_ref/` (gitignored) und ist nach Sitzungsende weg. Die bereinigte Aufnahme war Variante C (WPE-Hallreduktion + Tiefmitten −2 dB bei 250 Hz + Expander + `afftdn` + `loudnorm`).
- Spracherkennung `faster-whisper` (small) dient nur als grober Test, kann Englisch/Aussprache nicht sicher beurteilen. **Nichts davon wurde vom Assistenten gehört.**

## Offene Punkte / Risiken
- Transkript "Core 03" fehlt: Reihenfolge und Inhalte der Zeilen sind nicht gegen die Quelle geprüft. Aussagen in v02 (Teil "Bessere Level") und v06 (Übung) laut Contentplan vor Veröffentlichung prüfen.
- Rechtliches vor Veröffentlichung klären: Plattformregeln für Finanzinhalte, Erlaubnispflicht Anlageberatung, Nutzungsrechte am Kursmaterial, KI-Kennzeichnung bei synthetischen Stimmen. Chatterbox setzt ein unhörbares Wasserzeichen.
- "ICT" nicht in den Kanalnamen (Marke), Handles auf TikTok/YouTube sind nicht geprüft.
- Repo ist durch viele Testvarianten aufgebläht (`.git` ca. 320 MB, viele `audio_*`/`videos_*`/`specs_*`-Ordner). Vorschlag: Endstand festlegen, Rest aufräumen oder in ein Archiv verschieben.
- Bekannte Bildschwächen aus der README (Beschriftungen über Kerzen) teils offen.

## Sitzung 2: Pilot-Fassung v9 (Piper, kostenlos)
- Aenderung nach Rueckmeldung: v06 gestrichen, stumme A/B-Fassungen gestrichen. `videos_v9/v01-v05` alle mit Piper-Stimme (Thorsten) + Musik. Fehler behoben: Bei Teilen mit Titelkarte ueberlappte der Titel-Sprechtext mit der ersten Zeile (zwei Stimmen); jetzt per `build_v3.py retime` (Specs aus specs_v8, Zeiten in `specs_v9/`) ohne Ueberlappung.
- Urspruenglicher Plan: Pilot mit Posts von Hand, 3 pro Woche.
- Texte: v01 aus `specs_v7`, v02-v06 aus `specs_v8` (Zeiten per `fit_windows.py` an Piper angepasst -> `specs_v9/`). Bau: `finish_v9.py` (Teile zusammenfuegen, Ton ueber die Gesamtlaenge, Musik). Die Mischung von "Fassung 3" war nicht als Skript vorhanden; Werte in `finish_v9.py` sind rekonstruiert (Sprecher -16 LUFS, Musik -38 LUFS, abgesenkt beim Sprechen; stumm: Musik -24 LUFS).
- Nicht gehoert vom Assistenten: nur Lautstaerke und Bild geprueft. Aussprache englischer Begriffe (Lautschrift) ungeprueft.
- Kein ElevenLabs/Klon eingerichtet. Kein Host/Zugang ausser pip/npm/huggingface (Piper-Modell) genutzt.

## Sitzung 2, Stand v11 (aktuell): ElevenLabs-Klon der eigenen Stimme
- `videos_v11/v01-v05`: Stimme = ElevenLabs Instant Voice Clone des Nutzers (Stimmen-ID im Chat gegeben, kein Geheimnis; Modell `eleven_multilingual_v2`, Stabilitaet 0.5, Aehnlichkeit 0.75, Stil 0), Musik darunter. Specs: `specs_v11/`. Kommentar-Aufruf am Ende bei jedem Video gesprochen.
- Erzeugung: Zeilen per ElevenLabs-API (Skript lag nur lokal, `gen_el.py`: POST /v1/text-to-speech/<ID>, Header xi-api-key; Key NIE ins Repo), Zeiten `build_v3.py retime` (jetzt inkl. v01), Zusammenbau `finish_v9.py`.
- Gratis-Konto war ueber die Schnittstelle wegen Proxy-Erkennung gesperrt; nach Bezahlplan ging es von der Cloud-Sitzung aus.
- v06 gestrichen. Chatterbox-Klon verworfen (klang hallig). `dereverb.py` vorhanden, falls noetig.
- Der verwendete API-Key stand im Chatverlauf: bei ElevenLabs loeschen und neuen erzeugen.
