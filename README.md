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
NODE_PATH=$(npm root -g) node render_all.js liq01 liq02 liq03 liq04 liq05 liq06 liq07 liq08 liq09 liq10 liq11 liq12 liq13
```
Voraussetzung: Node, Playwright (Chromium), ffmpeg. Schriften: Space Grotesk und IBM Plex Mono (per npm, nicht im Repo).

## Spec-Format (Kurz)
`candles` [open, close, high, low], `reveal` [[von, bis, startzeit, abstand]], `elements` (zone, line, ring, label mit `at`/`until`), `caps` [[von, bis, "Text mit *Schlüsselwort*"]], `next` (Abschlusskarte).

## Regeln
- Stand Neuaufbau (v3): kein "laut ICT" mehr im Sprechtext, das ICT/Smart-Money-Konzept ist die Grundlage des Kanals. Vorsichtig formulieren ("manchmal", "oft"), keine Gewinnversprechen.
- Nur eigene Worte und eigene Charts, kein Kursmaterial 1:1 übernehmen.
- Im Fuß jedes Videos: "Lehrbeispiel, keine Anlageberatung".

## Bekannte Schwächen (Stand erster Push)
- Einige Beschriftungen liegen noch über Kerzen (lesbar durch weißen Rand): liq01, liq04, liq12.
- Kein Ton.
- Folgen 11 und 13 enthalten Faustregeln aus dem Kursmaterial, vor Veröffentlichung prüfen.
