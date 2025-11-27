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
# Buchstaben A-J entsprechen den Charakteren 1-10
PHASE3_TEXTS = {
    1: {  # A - Anna Schneider - "Frühes Zurückziehen"
        "nacht": "Du fühlst dich vom Tag erschöpft und gehst früh in dein Zimmer. Du räumst noch kurz etwas auf, sortierst deine Sachen und legst dich nach einem schnellen Blick aus dem Fenster ins Bett.",
        "alibi": "Auf dem Flur siehst du Michael Weber [B], der gerade aus dem Bad kommt. Wenige Sekunden später begegnet dir Sophie Hoffmann [C], die eine Wasserflasche in der Hand hält."
    },
    2: {  # B - Michael Weber - "Kurzes Fenster-Ritual"
        "nacht": "Bevor du ins Bett gehst, bleibst du einen Moment am Fenster stehen. Du beobachtest den wechselnden Himmel und atmest die kalte Luft durch den Spalt ein. Danach machst du dich bettfertig.",
        "alibi": "Auf dem Weg ins Zimmer siehst du Thomas Becker [D], der die Treppe hinaufgeht. Außerdem kommt dir Laura Müller [E] entgegen, die sich müde über die Augen reibt."
    },
    3: {  # C - Sophie Hoffmann - "Zu viel gegessen"
        "nacht": "Du hast beim Dinner wohl etwas übertrieben und fühlst dich schwer. Im Zimmer schaltest du den Fernseher kurz ein, zappst durch Kanäle, merkst dann, wie dir die Augen zufallen.",
        "alibi": "Im Flur begegnest du David Schmidt [F], der etwas in der Hand trägt. Vor deinem Zimmer siehst du Emma Wagner [G], die gerade eine Tür schließt."
    },
    4: {  # D - Thomas Becker - "Nachttee in der Lounge"
        "nacht": "Du nimmst dir noch einen Tee oder Wasser aus der Lounge und genießt einen kurzen Moment Ruhe. Danach gehst du gemütlich Richtung Zimmer und machst dich fürs Bett fertig.",
        "alibi": "Am Ende der Treppe siehst du Lukas Fischer [H], der sein Zimmer betritt. Auf dem Flur läufst du an Nina Braun [I] vorbei, die still vor sich hin summt."
    },
    5: {  # E - Laura Müller - "Arbeiten im Zimmer"
        "nacht": "Du verbringst die Zeit zwischen 22:30 und Mitternacht damit, ein paar Dinge zu sortieren, Nachrichten zu beantworten oder Dateien zu ordnen. Irgendwann wirst du schläfrig und legst dich hin.",
        "alibi": "Bevor du dein Zimmer betrittst, läufst du an Felix Zimmermann [J] vorbei, der sich gerade die Schuhe auszieht. Kurz danach siehst du Anna Schneider [A], die mit einem Tablet unter dem Arm Richtung Zimmer geht."
    },
    6: {  # F - David Schmidt - "Letzter Smalltalk"
        "nacht": "Du führst auf dem Weg zu deinem Zimmer noch ein paar Worte mit einer Person, die zufällig denselben Weg hat. Danach verschwindest du in deinem Zimmer und bereitest dich auf die Nacht vor.",
        "alibi": "Du siehst Michael Weber [B], der mit einem leisen 'Gute Nacht' an dir vorbeigeht. Außerdem siehst du Sophie Hoffmann [C], die noch kurz am Fenster stehen bleibt."
    },
    7: {  # G - Emma Wagner - "Badezimmer-Selfie-Session"
        "nacht": "Du verbringst noch etwas Zeit im Badezimmer oder vor dem Spiegel, filmst oder fotografierst dich kurz oder redest leise mit dir selbst über die Ereignisse des Tages.",
        "alibi": "Auf dem Rückweg ins Zimmer begegnest du Thomas Becker [D], der gerade seine Zimmertür aufschließt. Vor dem Bad siehst du Laura Müller [E], die mit nassen Haaren die Treppe hinaufkommt."
    },
    8: {  # H - Lukas Fischer - "Arbeiten an Notizen"
        "nacht": "Du setzt dich im Zimmer an den kleinen Tisch und schreibst ein paar Notizen, sortierst deine Gedanken oder arbeitest an etwas, das du nicht vergessen möchtest.",
        "alibi": "Als du den Zimmertrakt betrittst, siehst du David Schmidt [F], der langsam den Gang entlanggeht. Kurz darauf kommt dir Emma Wagner [G] entgegen, die müde wirkt."
    },
    9: {  # I - Nina Braun - "Glas Wein und altes Ritual"
        "nacht": "Du gönnst dir in deinem Zimmer ein Glas Wein oder Tee, legst ein kleines Schmuckstück oder Erinnerungsstück neben das Bett und versinkst in deinen Gedanken, bevor du müde wirst.",
        "alibi": "Auf dem Flur siehst du Lukas Fischer [H], der mit einem leisen Lächeln an dir vorbeigeht. Kurz darauf begegnet dir Felix Zimmermann [J], der gerade die Treppe hochkommt."
    },
    10: {  # J - Felix Zimmermann - "Musik & Handy-Scrollen"
        "nacht": "Du hörst Musik, scrollst durch dein Handy und siehst dir Aufnahmen des Abends an. Danach legst du dich hin und lässt noch leise Musik laufen, bis du einschläfst.",
        "alibi": "An der Treppe läuft Anna Schneider [A] an dir vorbei und murmelt etwas von Müdigkeit. Im Flur siehst du Nina Braun [I], die sich gerade ins Zimmer zurückzieht."
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
