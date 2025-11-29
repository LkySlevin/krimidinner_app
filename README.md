# Krimidinner

Ein lokaler Flask-Webserver für ein Krimidinner mit 10 Spielern und 3 NPCs.

## Installation

1. **Python installieren** (falls noch nicht vorhanden)

   - Version 3.7 oder höher erforderlich

2. **Flask installieren**
   ```bash
   pip install flask
   ```

## Programm starten

1. Im Terminal zum Projektordner navigieren:

   ```bash
   cd /Users/stefanweigl/krimidinner_app
   ```

2. Programm starten:

   ```bash
   python app.py
   ```

3. Der Server läuft nun auf:
   - **Lokal:** http://localhost:9000
   - **Im Netzwerk:** http://[DEINE-IP]:9000

## WLAN-Hotspot einrichten

### Auf macOS:

1. Systemeinstellungen → Allgemein → Freigaben
2. "Internetfreigabe" aktivieren
3. Deine IP-Adresse findest du in den Netzwerkeinstellungen

### Auf Windows:

1. Einstellungen → Netzwerk & Internet → Mobiler Hotspot
2. Hotspot aktivieren
3. IP-Adresse mit `ipconfig` im Terminal finden

## Spielablauf

### 1. Admin-Seite (http://localhost:9000/admin)

- Wähle aus:
  - Wer war zuerst am Klo?
  - Wer hat zuerst in der Küche geholfen?
  - Wer hat als erstes Alkohol getrunken?
- Klicke auf "Rollen generieren & Spiel starten"
- Das System wählt automatisch:
  - Einen zufälligen Mörder
  - Das passende Opfer basierend auf deinen Eingaben

### 2. Opfer-Logik

- **Küchenhilfe vorhanden** → Opfer: Jonas Reber (Koch)
- **Sonst: Klo-Gänger vorhanden** → Opfer: Viktor Bergmann (Hotelier)
- **Sonst: Alkohol-Trinker vorhanden** → Opfer: Dimitri Volkov (Investor)

### 3. QR-Codes & Links verteilen

- Gehe zu http://localhost:9000/qr-codes
- Zeige jedem Spieler seinen Link oder erstelle QR-Codes
- Empfohlener QR-Code-Generator: https://www.qr-code-generator.com

### 4. Spieler sehen ihre Rolle

- Jeder Spieler öffnet seinen individuellen Link
- Er sieht:
  - Ob er der Mörder ist oder nicht
  - Informationen über das Opfer
  - Sein Nachtverhalten (Phase 3)
  - Seine Alibi-Aussage

## Anpassungen

### Charakternamen ändern

In [app.py](app.py) Zeile 21-32:

```python
CHARACTERS = [
    {"id": 1, "name": "Dein Name hier"},
    ...
]
```

### Phase-3-Texte anpassen

In [app.py](app.py) Zeile 43-84:

```python
PHASE3_TEXTS = {
    1: {
        "nacht": "Dein individueller Text...",
        "alibi": "Deine Alibi-Aussage..."
    },
    ...
}
```

### NPC-Informationen ändern

In [app.py](app.py) Zeile 35-39:

```python
NPCS = {
    "kueche": {"name": "Jonas Reber", "role": "Koch", "location": "Küche"},
    ...
}
```

## Spiel zurücksetzen

Auf der Admin-Seite gibt es einen "Spiel zurücksetzen" Button, um eine neue Runde zu starten.

## Troubleshooting

### Port bereits belegt?

In [app.py](app.py) Zeile 289 den Port ändern:

```python
app.run(host='0.0.0.0', port=5000, debug=True)  # Statt 9000
```

### Firewall-Problem?

Stelle sicher, dass der Port in deiner Firewall freigegeben ist.

### Spieler können nicht zugreifen?

- Prüfe, ob alle im gleichen WLAN sind
- Verwende deine lokale IP statt localhost
- Beispiel: http://192.168.1.100:9000

## Projektstruktur

```
krimidinner_app/
├── app.py                    # Hauptprogramm
├── templates/                # HTML-Templates
│   ├── base.html            # Basis-Template mit CSS
│   ├── index.html           # Startseite
│   ├── admin.html           # Admin-Panel
│   ├── player.html          # Spieler-Ansicht
│   ├── error.html           # Fehlerseite
│   └── qr_codes.html        # QR-Code-Übersicht
└── README.md                # Diese Datei
```

## Funktionen

- ✅ 10 Spielercharaktere
- ✅ 3 NPCs als mögliche Opfer
- ✅ Automatische Mörder-Auswahl
- ✅ Dynamische Opfer-Bestimmung
- ✅ Individuelle Token für jeden Spieler
- ✅ Phase-3-Texte (Nachtverhalten & Alibis)
- ✅ Admin-Panel zur Spielkonfiguration
- ✅ QR-Code-freundliche Links
- ✅ Responsive Design für Mobilgeräte

## Viel Erfolg beim Krimidinner! 🕵️‍♀️🔪
