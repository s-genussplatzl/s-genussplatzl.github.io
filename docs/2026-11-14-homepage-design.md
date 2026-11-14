# Homepage s-genussplatzl.at – Design (kurz)

Stand: 14.11.2026 · Freigabe: ausstehend (Michael)

## Wozu
Eine eigene, schlanke Homepage für das s`Genussplatz`l in Unterpurkla. Sie bündelt alle Wege – Google-Profil („Website“-Knopf, bisher steiermark.com), QR-Code im Bike-&-Spa-Schaukasten, künftige Flyer für Tourismusbüros/Hotels, Komoot, Instagram – an einem Ort.
Zielgruppe: Radfahrer, Wanderer und Ausflügler im Thermen- & Vulkanland, die überlegen, ob sie stehen bleiben oder herfahren.

## Ziele
- Stimmungsvolle Einladung in die Region: regional, historisch, Bezug zur Umgebung.
- Das Genussplatzl als Rastpunkt mittendrin, mit seiner Geschichte, Kunst und Genuss.
- Am Handy schnell und schön (die meisten Gäste kommen mobil).
- Leicht von Claude zu pflegen (Saisonstart, Fotos, Partner).

## Nicht-Ziele / Anti-Ziele
- Keine Betriebsdetails (kein „Selbstbedienung“, keine Hinweise zu Aufsicht/Personal, keine Events, keine Speisen).
- Kein Verkaufsshop; Kunst nur „bei Interesse sprechen Sie uns an“.
- Keine Cookies, kein Tracking, kein Google-Maps-Einbau (Datenschutz, keine Banner nötig).
- Sprachen: Deutsch (Hauptsprache, Wurzelverzeichnis), dazu Slowenisch, Englisch, Ungarisch unter /sl/, /en/, /hu/ (Entscheidung Michael, 14.11.2026). Texte in tools/lang/<sprache>.json und pages/<sprache>/. Ansprache immer höflich („Sie“, vikanje, Ön).
- Keine fremden Fotos ohne Zustimmung (Komoot-Fotos von Süwega/Günther erst nach Okay).

## Ansätze (betrachtet)
- **A – Eigene Seite, statisch, GitHub Pages (gewählt):** frei gestaltet, 0 € Hosting, schnell, keine Wartung; Änderungen über Claude.
- B – Baukasten (Wix/Jimdo): selbst editierbar, 10–20 €/Monat, Vorlagen-Look.
- C – WordPress beim Domain-Anbieter: editierbar, aber Updates/Sicherheitsrisiko, Hosting-Kosten.
Michael hat A gewählt.

## Aufbau (eine Seite)
1. **Kopf:** Abendbild (Titelbild aus Google-Profil), Logo, „Regional · Radeln · Relaxen“, Unterzeile „Ein Platzerl zum Ankommen im Herzen des Thermen- & Vulkanlands …“.
2. **Unsere Geschichte:** freigegebener Text (Freude/Begegnung; „ein Rastplatz, in dem Kupfer, Glas und Holz auf Natur treffen“; Nussbaum; Kunst „mit viel Liebe zum Detail von Hand geschmiedet“ – ohne Verkaufshinweis).
3. **Kunst im Garten:** Galerie der Figuren + „Die Kunstwerke sind Einzelstücke – bei Interesse sprechen Sie uns gerne an.“ Künstler vorerst ohne Namen.
4. **Genuss im Glas:** Winzer aus Tieschen und Klöch, Holunderspritzer, alkoholfreie Getränke, Snacks.
5. **Rundherum entdecken:** Karte (eigene, statische Illustration/SVG mit Punkten) + Kacheln mit Foto, Kurzgeschichte, Entfernung per Rad:
   Radbrücke über die Mur (Donnersdorf–Apače, 2006, 82,5 m) · Murauen / UNESCO-Biosphärenpark Mur-Drau-Donau · Murecker Schiffsmühle (1997 rekonstruiert) · Klöch / Traminer (1444, Vinothek & Weinbaumuseum, Burgruine) · Thermen & Bad Radkersburg (R12, 12-Thermen-Tour).
6. **Anfahrt & Radrouten:** Unterpurkla 28, 8484 Halbenrain; direkt am Gleichenberger Radweg R45 (Feldbach–Donnersdorf, Anschluss Murradweg R2), nahe R12. Hinweise E-Bike-Ladestation · WC · Schatten. Links Komoot-Highlight + Google Maps (Link, kein Einbau).
7. **Öffnungszeiten:** Saison März–Oktober, täglich 9–22 Uhr.
8. **Fußzeile:** Kontakt, Instagram, Impressum, Datenschutz (eigene Unterseiten).

## Gestaltung
Farben (Rebrand 14.11.2026, Entscheidung Michael): **Kupfer, Basalt, Kies**. Heller Grund wie der weiße Kies im Garten, Bänder in Anthrazit wie die Fassadenplatten (mit leichter Steinstruktur), Kupfer wie die Fassade als Akzent. Kein Grün mehr. Alle Farben stehen in tokens.css. Serifenschrift passend zum Logo für Überschriften, klare Schrift für Text. Großzügige Fotos, ruhige Gliederung, mobil zuerst.

## Technik (Claudes Entscheidungen)
- Reines HTML/CSS, minimal JS, keine Frameworks, keine externen Skripte/Fonts zur Laufzeit (Schriften lokal) → schnell, datenschutzfreundlich.
- Bilder als WebP/JPG in passenden Größen.
- Eigenes, kostenloses GitHub-Konto/-Organisation „s-genussplatzl“ (mit info@s-genussplatzl.at), getrennt von AVITECH; Repo mit GitHub Pages.
- Domain s-genussplatzl.at: beim Domain-Anbieter A-Records auf GitHub Pages + CNAME „www“; MX (Mail) bleibt unverändert. HTTPS über GitHub.
- Zweit-Domain **radeln-relaxen.at** (Slogan, für Flyer, Schilder, QR-Codes; Stand 14.11.2026 laut DNS vermutlich frei, verbindlich bei nic.at prüfen). Michael registriert sie selbst. Sie bekommt **keinen eigenen Inhalt**, sondern eine dauerhafte Weiterleitung (301) auf https://s-genussplatzl.at, damit Google nur eine Hauptadresse sieht. Umsetzung: Weiterleitung beim Domain-Anbieter (inkl. www und HTTPS); falls der Anbieter kein HTTPS-Forwarding kann, ein zweites GitHub-Repo „radeln-relaxen“ mit einer Weiterleitungsseite (meta refresh + canonical) als Ersatz.
- Kurzlinks über die Zweit-Domain für Drucksachen, z. B. radeln-relaxen.at → Startseite; Routen-Seiten bleiben unter s-genussplatzl.at/radrouten/….
- Impressum nach §5 ECG / §25 MedienG; Datenschutzerklärung (keine Cookies, Hosting GitHub, Kontakt per Mail).
- Entfernungen per Rad werden mit einem Routenplaner ermittelt (ca.-Angaben).

## Von Michael benötigt
- GitHub-Konto anlegen (selbst, mit info@) bzw. Freigabe dafür.
- Zugang/Anleitung beim Domain-Anbieter für die DNS-Einträge (macht Michael oder gibt frei).
- radeln-relaxen.at registrieren (optional zusätzlich genussplatzl.com als Schutz); prüfen, wem genussplatzl.at gehört.
- Optional später: Name des Schrottkünstlers, Zustimmung Komoot-Fotografen.

## Nach dem Start
- Google-Profil: Website-Link auf https://s-genussplatzl.at umstellen.
- QR-Code für Schaukasten/Flyer auf die Homepage.
