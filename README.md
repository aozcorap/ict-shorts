# ict-shorts

Kurzvideos (1080x1920, ca. 25 s) zu ICT-Konzepten, vollautomatisch aus einer kleinen Datei pro Folge erzeugt.

## Aufbau
- `engine.html`: Vorlage (Editor-Look: Chart-Fenster oben, Konsole mit Tipp-Untertiteln unten)
- `specs/*.json`: eine Datei pro Folge (Kerzen, Markierungen, 6 Untertitelzeilen mit Zeiten)
- `render_all.js`: rendert Bilder mit Playwright und baut das MP4 mit ffmpeg
- `plan/`: Contentplan
- `videos/`: fertige Beispielfolgen (noch ohne Ton)

## Einrichten und Rendern
```bash
cd fonts && npm install && cd ..
NODE_PATH=$(npm root -g) node render_all.js liq01 liq02 liq03
```
Voraussetzung: Node, Playwright (Chromium), ffmpeg. Schriften: Space Grotesk und IBM Plex Mono (per npm, nicht im Repo).

## Spec-Format (Kurz)
`candles` [open, close, high, low], `reveal` [[von, bis, startzeit, abstand]], `elements` (zone, line, ring, label mit `at`/`until`), `caps` [[von, bis, "Text mit *Schlüsselwort*"]], `next` (Abschlusskarte).

## Regeln
- Aussagen aus dem ICT-Modell als "laut ICT" formulieren (Hypothese, kein belegter Fakt).
- Nur eigene Worte und eigene Charts, kein Kursmaterial 1:1 übernehmen.
- Im Fuß jedes Videos: "Lehrbeispiel, keine Anlageberatung".
