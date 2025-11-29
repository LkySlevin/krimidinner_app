# Krimidinner - Test-Simulation

## Übersicht

Dieses Testprogramm simuliert **alle möglichen Kombinationen** von Events und analysiert, wie oft jeder Charakter als Mörder oder Opfer ausgewählt wird.

## Ausführung

```bash
# Virtual Environment aktivieren
source venv/bin/activate

# Simulation starten
python tests/simulate_all_combinations.py
```

## Was wird getestet?

Das Programm simuliert:
- **11³ × 7 = 9.317 Kombinationen** (11 Event-Optionen pro Event × 3 Events × 7 Wochentage)
- Alle möglichen Werte für Event1, Event2, Event3 (None oder Charakter 1-10)
- Alle Wochentage (Montag bis Sonntag)
- Zufällige Mörder-Auswahl mit Motiv-Gewichtung

## Ergebnisse

Die Simulation erstellt folgende Ausgaben:

### 1. Konsolen-Statistiken

- **Mörder-Häufigkeit**: Wie oft wird jeder Charakter zum Mörder?
- **Opfer-Häufigkeit**: Wie oft wird welches NPC zum Opfer?
- **Motiv-Analyse**: Einfluss von Motiven auf die Mörder-Auswahl

### 2. Visualisierungen (PNG-Dateien)

Alle Grafiken werden im Ordner `tests/results/` gespeichert:

1. **murderer_frequency.png**
   - Balkendiagramm der Mörder-Häufigkeit
   - Zeigt, wie oft jeder Charakter zum Mörder wird

2. **victim_frequency.png**
   - Balkendiagramm der Opfer-Häufigkeit
   - Zeigt, wie oft jedes NPC zum Opfer wird

3. **murderer_victim_heatmap.png**
   - Heatmap: Welcher Charakter wird bei welchem Opfer zum Mörder?
   - Matrix zeigt die Verteilung

4. **motive_influence.png**
   - Vergleich: Mit vs. ohne Motiv
   - Zeigt den Einfluss der Motiv-Gewichtung

## Interpretation der Ergebnisse

### Wichtige Erkenntnisse:

1. **Opfer-Verteilung**:
   - Jonas Reber (Koch) wird am häufigsten Opfer (~91%)
   - Viktor Bergmann (Hotelier) wird seltener Opfer (~8%)
   - Dimitri Volkov (Investor) wird sehr selten Opfer (~1%)
   - **Grund**: Event2 (Küchenhilfe) führt immer zu Jonas Reber

2. **Mörder-Verteilung**:
   - **Jazz Monroe** und **Pater Antonio Benedetti** werden am häufigsten Mörder (~15%)
   - **Tom Greenwood** wird ebenfalls häufig Mörder (~14%)
   - **Grund**: Diese Charaktere haben Motive für Jonas Reber

3. **Motiv-Gewichtung funktioniert**:
   - Charaktere mit Motiven werden **2x häufiger** als Mörder ausgewählt
   - Jazz Monroe: 99.8% ihrer Mörder-Auswahlen haben ein Motiv
   - Tom Greenwood: 100% seiner Mörder-Auswahlen haben ein Motiv
   - Pater Antonio: 97% seiner Mörder-Auswahlen haben ein Motiv

## Technische Details

- **Programmiersprache**: Python 3
- **Abhängigkeiten**: matplotlib, numpy
- **Laufzeit**: ~10-30 Sekunden (abhängig vom System)
- **Speicherverbrauch**: gering (~50 MB)

## Anpassungen

Um andere Szenarien zu testen, kannst du folgende Variablen in `app.py` anpassen:
- `MOTIVE_MATRIX`: Ändere die Motive zwischen Charakteren und Opfern
- `NPCS`: Ändere die Opfer-Definitionen
- `determine_victim()`: Ändere die Opfer-Logik

Nach Änderungen einfach die Simulation erneut ausführen!
