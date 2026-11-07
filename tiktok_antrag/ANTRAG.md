# TikTok-Antrag (Weg A): Entwurf zum Einkopieren

Stand: Entwurf, nicht abgeschickt. Nichts hier ist rechtlich geprüft. Quelle der Vorgaben: TikTok for Developers (Register Your App, App Review Guidelines, Content Posting API Upload).

## 1. Im Portal korrigieren / ausfüllen
- **App-Name:** `Smart Money Kompakt` (im Portal steht noch der Tippfehler "Smat").
- **App icon:** `app_icon_1024.png` (1024x1024, PNG, unter 5 MB).
- **Category:** passende Kategorie wählen (z. B. Bildung/Education, falls vorhanden). Welche Kategorien es gibt, habe ich nicht gesehen.
- **Description (max. 120 Zeichen, hier 103):**
  `Uploads our own educational chart videos to the creator's TikTok inbox as drafts for manual publishing.`
- **Terms of Service URL / Privacy Policy URL / Web-URL:** drei öffentliche Webadressen (siehe Abschnitt 4). Alle drei müssen über "URL properties" verifiziert werden.
- **Platforms:** nur "Web" ankreuzen.
- **Products:** Login Kit und Content Posting API.
- **Scopes:** nur `user.info.basic` und `video.upload`. Nichts anderes, sonst verzögert sich die Prüfung.

## 2. Erklärtext für "Explain how each product and scope works" (max. 1000 Zeichen, hier 718)
```
Smart Money Kompakt is a small tool used by the channel owner to upload the channel's own educational chart videos to TikTok. The creator signs in with TikTok (Login Kit, scope user.info.basic). The tool then sends a finished video file to the creator's TikTok inbox as a draft (Content Posting API, scope video.upload). Nothing is published automatically: the creator opens the TikTok app, reviews the draft and publishes it manually. The tool does not read the creator's videos, followers or messages, does not post comments, and stores only the access token needed for the upload. Videos are original, educational, and carry the note 'Lehrbeispiel, keine Anlageberatung' (educational example, not financial advice).
```

## 3. Demovideo (Bildschirmaufnahme, mp4/mov, max. 50 MB, bis 5 Dateien)
TikTok verlangt für neue Apps die **Sandbox** (Reiter "Sandbox" neben "Production"). Ablauf, der zu sehen sein muss:
1. Adresse der Web-Anwendung im Browser, die Domain stimmt mit der eingetragenen Web-URL überein.
2. Klick auf "Mit TikTok anmelden", TikTok-Zustimmungsseite mit beiden Rechten (Profil lesen, Video hochladen), zustimmen.
3. Videodatei wählen, "An TikTok senden" klicken, Erfolgsmeldung.
4. TikTok-App öffnen, Posteingang, das Video erscheint als Entwurf.
5. In der App auf "Posten" tippen, Video wird veröffentlicht (oder bewusst verworfen).

## 4. Webadressen (Hosting offen)
Drei Seiten brauchen eine **öffentliche Adresse**, die TikTok verifizieren kann:
- **Startseite:** Name, ein Satz, was das Tool macht, Link zu den beiden anderen Seiten.
- **Nutzungsbedingungen:** Nutzung nur für den Kanalbetreiber, keine Garantie, keine Anlageberatung, Kontakt.
- **Datenschutz:** Welche Daten (TikTok-Zugriffstoken, TikTok-Nutzername), wofür (Upload), wie lange (bis Widerruf), Löschung auf Anfrage, Kontakt.
- **Impressum:** Bei einer deutschen Webseite vermutlich nötig (Name, Anschrift, Kontakt). Das macht deine private Adresse öffentlich. Klären, bevor veröffentlicht wird (nicht rechtsgeprüft, kein Rechtsrat).

## 5. Technische Lücke, die der Antrag nicht löst
Für Login und Upload braucht es ein **laufendes Web-Tool** mit Anmeldung und serverseitigem Austausch des Zugriffstokens (das "Client Secret" darf nicht im Browser liegen). Eine reine statische Seite reicht nicht. Das Demovideo setzt dieses Tool voraus. Offen: wo es läuft (eigener Server, Cloud-Dienst) und was das kostet.

## 6. Risiken
- TikTok verlangt laut Dokumentation, dass die App "nicht auf Testanwendungen beschränkt ist". Ein Tool nur für ein eigenes Konto kann abgelehnt werden. Ich weiß nicht, wie streng das gehandhabt wird.
- Prüfdauer laut TikTok-FAQ (Drittquelle): Tage bis zwei Wochen.
- Bei Ablehnung steht im Portal ein Verlauf mit Kommentaren der Prüfer.
