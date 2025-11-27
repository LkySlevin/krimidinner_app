#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Krimidinner / Werwolf-Spiel - Flask Webserver
Autor: Erstellt für Stefan Weigl
"""

from flask import Flask, render_template, request, redirect, url_for, session
import random
import secrets
import os

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)  # Für Session-Management

# ============================================================================
# DATENSTRUKTUREN - HIER KÖNNEN DIE TEXTE ANGEPASST WERDEN
# ============================================================================

# 10 Spielercharaktere mit Buchstaben-IDs
CHARACTERS = [
    {"id": 1, "letter": "A", "name": "Anna Schneider", "url_slug": "spieler-a"},
    {"id": 2, "letter": "B", "name": "Michael Weber", "url_slug": "spieler-b"},
    {"id": 3, "letter": "C", "name": "Sophie Hoffmann", "url_slug": "spieler-c"},
    {"id": 4, "letter": "D", "name": "Thomas Becker", "url_slug": "spieler-d"},
    {"id": 5, "letter": "E", "name": "Laura Müller", "url_slug": "spieler-e"},
    {"id": 6, "letter": "F", "name": "David Schmidt", "url_slug": "spieler-f"},
    {"id": 7, "letter": "G", "name": "Emma Wagner", "url_slug": "spieler-g"},
    {"id": 8, "letter": "H", "name": "Lukas Fischer", "url_slug": "spieler-h"},
    {"id": 9, "letter": "I", "name": "Nina Braun", "url_slug": "spieler-i"},
    {"id": 10, "letter": "J", "name": "Felix Zimmermann", "url_slug": "spieler-j"}
]

# 3 NPCs (mögliche Opfer)
NPCS = {
    "kueche": {"name": "Jonas Reber", "role": "Koch", "location": "Küche"},
    "klo": {"name": "Viktor Bergmann", "role": "Hotelier", "location": "Flur vor den Zimmern"},
    "alkohol": {"name": "Dimitri Volkov", "role": "Investor", "location": "Terrasse/Schnee"}
}

# Phase-3-Texte für jeden Charakter (Nachtverhalten + Alibi)
# HIER KÖNNEN DIE TEXTE INDIVIDUELL ANGEPASST WERDEN
PHASE3_TEXTS = {
    1: {  # Anna Schneider
        "nacht": "Du gehst gegen 22:30 Uhr in dein Zimmer, nachdem du zu viel gegessen hast. Du fühlst dich unwohl und versuchst zu schlafen, wachst aber mehrmals auf.",
        "alibi": "Auf dem Weg zu deinem Zimmer siehst du Michael Weber im Flur, der nervös hin- und herläuft."
    },
    2: {  # Michael Weber
        "nacht": "Du bist unruhig und kannst nicht schlafen. Du gehst mehrmals auf den Flur und rauchst eine Zigarette an der Hintertür.",
        "alibi": "Du kannst bestätigen, dass Sophie Hoffmann kurz vor 23:00 Uhr noch in der Lounge war und Tee getrunken hat."
    },
    3: {  # Sophie Hoffmann
        "nacht": "Du entspannst dich nach dem Essen in der Lounge mit einem Kräutertee und liest ein Buch. Gegen 23:30 gehst du ins Bett.",
        "alibi": "Du hast Thomas Becker gegen 23:15 Uhr im Treppenhaus gesehen, als er nach oben ging."
    },
    4: {  # Thomas Becker
        "nacht": "Du telefonierst auf deinem Zimmer mit deiner Familie bis ca. 23:45 Uhr, dann versuchst du einzuschlafen.",
        "alibi": "Als du gegen 23:15 Uhr auf dein Zimmer gehst, siehst du Laura Müller, die gerade aus der Bibliothek kommt."
    },
    5: {  # Laura Müller
        "nacht": "Du verbringst Zeit in der Bibliothek und blätterst durch alte Fotobücher des Hotels. Gegen 23:20 gehst du schlafen.",
        "alibi": "Du hast David Schmidt gegen 22:45 Uhr am Kamin sitzen sehen, er wirkte nachdenklich."
    },
    6: {  # David Schmidt
        "nacht": "Du sitzt lange am Kamin in der Lounge und denkst über den Abend nach. Erst gegen Mitternacht gehst du ins Bett.",
        "alibi": "Du kannst bestätigen, dass Emma Wagner gegen 23:00 Uhr noch wach war und mit jemandem telefoniert hat - du hast ihre Stimme aus dem Nebenzimmer gehört."
    },
    7: {  # Emma Wagner
        "nacht": "Du bist gestresst und führst ein längeres Telefonat mit einem Geschäftspartner. Danach gehst du gegen 23:30 ins Bett.",
        "alibi": "Auf dem Weg zum Badezimmer siehst du Lukas Fischer, der gerade von draußen hereinkommt - seine Schuhe sind nass."
    },
    8: {  # Lukas Fischer
        "nacht": "Dir ist nach dem Essen heiß, und du gehst gegen 23:00 Uhr kurz nach draußen, um frische Luft zu schnappen. Du bleibst etwa 15 Minuten draußen.",
        "alibi": "Als du wieder reinkommst, siehst du Nina Braun in der Küche - sie scheint etwas zu suchen."
    },
    9: {  # Nina Braun
        "nacht": "Du hast Hunger und gehst gegen 23:20 Uhr in die Küche, um dir einen Snack zu holen. Danach gehst du direkt ins Bett.",
        "alibi": "In der Küche bemerkst du, dass Felix Zimmermann kurz vorher auch dort war - sein Glas steht noch auf der Theke."
    },
    10: {  # Felix Zimmermann
        "nacht": "Du holst dir gegen 23:00 Uhr noch ein Glas Wasser aus der Küche und gehst dann früh schlafen, da du müde bist.",
        "alibi": "Du hast Anna Schneider auf dem Flur getroffen, als du ins Bett gegangen bist - sie sah blass aus."
    }
}

# Texte für Werwolf und Unschuldige
WEREWOLF_TEXT = """
<div class="werewolf-alert">
    <h2>⚠️ DU BIST DER MÖRDER / DIE MÖRDERIN ⚠️</h2>
    <p>Du bist ein <strong>Werwolf</strong>.</p>
    <p>Du tötest in dieser Nacht um <strong>00:15 Uhr</strong> das Opfer, während draußen Vollmond ist.</p>
    <p>Du erinnerst dich nur an <em>Hitze, Kälte, Blut</em> und den Lauf durch den Schnee.</p>
    <p>Dein Ziel ist es, nicht entdeckt zu werden.</p>
</div>
"""

INNOCENT_TEXT = """
<div class="innocent-info">
    <h2>✓ Du bist unschuldig</h2>
    <p>Du wirst in der Nacht von Schreien geweckt und erinnerst dich an eine Uhrzeit um ca. <strong>00:30 Uhr</strong>,
    gehst aber nicht nachsehen.</p>
    <p>Am nächsten Morgen erfährst du von dem schrecklichen Vorfall.</p>
</div>
"""

# ============================================================================
# SPIELZUSTAND (wird im Session gespeichert oder als globale Variable)
# ============================================================================

game_state = {
    "werewolf_id": None,        # ID des Werwolfs
    "victim": None,              # Dict mit Opfer-Informationen
    "first_toilet": None,        # ID des ersten Klo-Gängers
    "first_kitchen": None,       # ID des ersten Küchenhelfers
    "first_alcohol": None,       # ID des ersten Alkohol-Trinkers
    "game_started": False
}

# ============================================================================
# HILFSFUNKTIONEN
# ============================================================================

def get_character_by_slug(slug):
    """Gibt den Charakter mit dem angegebenen URL-Slug zurück"""
    for char in CHARACTERS:
        if char["url_slug"] == slug:
            return char
    return None

def select_werewolf(characters):
    """Wählt zufällig einen Werwolf aus der Charakterliste"""
    return random.choice(characters)["id"]

def determine_victim(first_kitchen, first_toilet, first_alcohol):
    """
    Bestimmt das Opfer basierend auf der Matrix:
    1. Erste Küchenhilfe → Jonas Reber (Koch)
    2. Sonst: Erster am Klo → Viktor Bergmann (Hotelier)
    3. Sonst: Erster Alkohol → Dimitri Volkov (Investor)
    """
    if first_kitchen is not None:
        return NPCS["kueche"]
    elif first_toilet is not None:
        return NPCS["klo"]
    elif first_alcohol is not None:
        return NPCS["alkohol"]
    else:
        return None

def get_character_by_id(char_id):
    """Gibt den Charakter mit der angegebenen ID zurück"""
    for char in CHARACTERS:
        if char["id"] == char_id:
            return char
    return None

# ============================================================================
# ROUTEN
# ============================================================================

@app.route('/')
def index():
    """Startseite mit Links zu Admin und Spieler-Übersicht"""
    return render_template('index.html',
                         game_started=game_state["game_started"],
                         characters=CHARACTERS)

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    """Admin-Seite für Spielkonfiguration"""
    error = None
    success = None

    if request.method == 'POST':
        # Eingaben aus dem Formular holen
        first_toilet = request.form.get('first_toilet', type=int)
        first_kitchen = request.form.get('first_kitchen', type=int)
        first_alcohol = request.form.get('first_alcohol', type=int)

        # Validierung: Mindestens eine Eingabe muss gesetzt sein
        if not any([first_toilet, first_kitchen, first_alcohol]):
            error = "Fehler: Du musst mindestens eine der drei Optionen auswählen!"
        else:
            # Spiel initialisieren
            game_state["first_toilet"] = first_toilet
            game_state["first_kitchen"] = first_kitchen
            game_state["first_alcohol"] = first_alcohol

            # Werwolf auswählen
            game_state["werewolf_id"] = select_werewolf(CHARACTERS)

            # Opfer bestimmen
            victim = determine_victim(first_kitchen, first_toilet, first_alcohol)
            if victim is None:
                error = "Fehler: Kein Opfer konnte bestimmt werden!"
            else:
                game_state["victim"] = victim
                game_state["game_started"] = True

                werewolf_name = get_character_by_id(game_state["werewolf_id"])["name"]
                success = f"Spiel erfolgreich gestartet! Werwolf: {werewolf_name}, Opfer: {victim['name']} ({victim['role']})"

    return render_template('admin.html',
                         characters=CHARACTERS,
                         game_state=game_state,
                         error=error,
                         success=success)

@app.route('/player/<slug>')
def player_view(slug):
    """Spieler-Ansicht: Zeigt Rolle und Phase-3-Informationen"""
    # Überprüfen, ob das Spiel gestartet wurde
    if not game_state["game_started"]:
        return render_template('error.html',
                             message="Das Spiel wurde noch nicht gestartet. Bitte warte auf den Spielleiter.")

    # Charakter anhand des URL-Slugs finden
    character = get_character_by_slug(slug)

    if not character:
        return render_template('error.html',
                             message="Ungültiger Spieler-Link. Bitte überprüfe die URL.")

    # Prüfen, ob dieser Charakter der Werwolf ist
    is_werewolf = (character["id"] == game_state["werewolf_id"])

    # Phase-3-Texte holen
    phase3 = PHASE3_TEXTS.get(character["id"], {
        "nacht": "Keine Informationen verfügbar.",
        "alibi": "Keine Alibi-Information verfügbar."
    })

    return render_template('player.html',
                         character=character,
                         is_werewolf=is_werewolf,
                         victim=game_state["victim"],
                         phase3=phase3,
                         werewolf_text=WEREWOLF_TEXT,
                         innocent_text=INNOCENT_TEXT)

@app.route('/reset', methods=['POST'])
def reset_game():
    """Setzt das Spiel zurück (nur für Admin)"""
    game_state["werewolf_id"] = None
    game_state["victim"] = None
    game_state["first_toilet"] = None
    game_state["first_kitchen"] = None
    game_state["first_alcohol"] = None
    game_state["game_started"] = False
    return redirect(url_for('admin'))

@app.route('/qr-codes')
def qr_codes():
    """Zeigt alle QR-Code-Links für die Spieler (zur einfachen Verteilung)"""
    if not game_state["game_started"]:
        return render_template('error.html',
                             message="Das Spiel wurde noch nicht gestartet.")

    # Links für jeden Spieler erstellen
    player_links = []
    for char in CHARACTERS:
        player_links.append({
            "character": char,
            "url": request.host_url + "player/" + char["url_slug"]
        })

    return render_template('qr_codes.html', player_links=player_links)

# ============================================================================
# MAIN
# ============================================================================

if __name__ == '__main__':
    # Server starten (erreichbar im lokalen Netzwerk)
    app.run(host='0.0.0.0', port=9000, debug=True)
