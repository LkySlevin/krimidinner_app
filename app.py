#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Krimidinner - das alptraumhafte Alpenhotel Aurora
Autor: Erstellt von Stefan Weigl, Claude, Codex und ChatGPT
"""

from flask import Flask, render_template, request, redirect, url_for, session, send_from_directory, abort
import random
import secrets
from datetime import datetime
import os
import qrcode
from PIL import Image, ImageDraw, ImageFont
import hashlib

# Import von Datenstrukturen und Textbausteinen
from game_data import (
    CHARACTERS, NPCS, NPC_PLACEHOLDER_MAP,
    MOTIVE_MATRIX, DEFAULT_MOTIVE_TEXT,
    MURDER_CLUES, RED_HERRING_CLUES
)
from game_texts import (
    PHASE3_TEXTS, MURDER_TEXT_TEMPLATE, INNOCENT_TEXT_TEMPLATE,
    DREAM_TEXTS, DESPERATE_DREAM_SUFFIX, INTRIGANT_DREAM_TEMPLATE,
    LOVER_DREAM_TEMPLATE, AWAKENING_TEXT_TEMPLATE
)

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)  # Für Session-Management

# ============================================================================
# SPIELZUSTAND (wird im Session gespeichert oder als globale Variable)
# ============================================================================

game_state = {
    "murder_id": None,           # ID des Mörders
    "victim": None,              # Dict mit Opfer-Informationen
    "num_players": None,         # Anzahl der aktiven Spieler (7-10)
    "active_characters": [],     # Liste der aktiven Charaktere (manuell/zufällig ausgewählt)
    "letter_mapping": {},        # Mapping: char_id -> zugewiesener Buchstabe (A-J)
    "awakeners": [],             # IDs der 2-3 Personen, die beim ersten Schrei aufwachen
    "event1_name": None,         # Name für Ereignis 1 (Standard: "Klo")
    "event2_name": None,         # Name für Ereignis 2 (Standard: "Küchenhilfe")
    "event3_name": None,         # Name für Ereignis 3 (Standard: "Alkohol")
    "first_event1": None,        # ID für Ereignis 1
    "first_event2": None,        # ID für Ereignis 2
    "first_event3": None,        # ID für Ereignis 3
    "setup_phase": 0,            # Setup-Phase: 0=nicht gestartet, 1=Charaktere gewählt, 2=Events konfiguriert
    "current_phase": 0,          # Spielphase für Spieler (0=warten, 3-5=Phasen)
    "game_started": False,
    "final_accused_id": None,    # Phase-5-Verdacht (nach Abstimmung)
    "final_verdict_correct": None,
    "votes": {},                 # Phase 5: Abstimmungen {char_id: voted_for_char_id}
    "intrigant_id": None,        # ID des Intriganten (will jemandem den Mord anhängen)
    "intrigant_target_id": None, # ID der Person, die der Intrigant belasten will
    "desperate_id": None,        # ID der verzweifelten Person (will als Mörder identifiziert werden)
    "lovers": [],                # Liste mit 2 IDs des verliebten Paars
    "voting_complete": False,    # Phase 5: True wenn alle abgestimmt haben
    "runoff_active": False,      # True wenn Stichwahl läuft
    "runoff_candidates": [],     # IDs der Kandidaten in der Stichwahl
    "runoff_round": 0            # Stichwahl-Runde (0=normal, 1=erste Stichwahl, 2=zweite, etc.)
}

# ============================================================================
# HILFSFUNKTIONEN
# ============================================================================

def get_character_by_slug(slug):
    """Gibt den Charakter anhand des URL-Slugs zurück."""
    # Unterstütze /player/spieler-1, /player/spieler-2, etc. (ID-basiert)
    if slug.startswith("spieler-"):
        try:
            char_id = int(slug.split("spieler-", 1)[1])
            for char in CHARACTERS:
                if char["id"] == char_id:
                    return char
        except (ValueError, IndexError):
            pass

    # Fallback: Alter URL-Slug (für Abwärtskompatibilität)
    for char in CHARACTERS:
        if char["url_slug"] == slug:
            return char

    return None

def select_random_characters(num_players):
    """Wählt zufällig num_players Charaktere aus der Liste aus"""
    return random.sample(CHARACTERS, num_players)

def assign_random_letters(characters):
    """
    Weist jedem Charakter zufällig einen Buchstaben zu.
    Bei 7 Spielern: A-G (zufällig verteilt), bei 8 Spielern: A-H (zufällig verteilt), etc.
    Gibt ein Dictionary zurück: {char_id: "A", ...}
    """
    available_letters = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J"]
    # Nimm nur die ersten N Buchstaben basierend auf der Anzahl der Spieler
    selected_letters = available_letters[:len(characters)]
    # Mische diese Buchstaben zufällig
    random.shuffle(selected_letters)

    letter_mapping = {}
    for i, char in enumerate(characters):
        letter_mapping[char["id"]] = selected_letters[i]

    return letter_mapping

def get_player_slug(character):
    """Ermittelt den passenden Player-Slug anhand der Charakter-ID."""
    return f"spieler-{character['id']}"

def reset_voting_state():
    """Setzt alle Voting-bezogenen Zustände zurück (z. B. beim Neustart oder neuer Phase 5)."""
    game_state["votes"] = {}
    game_state["voting_complete"] = False
    game_state["final_accused_id"] = None
    game_state["final_verdict_correct"] = None
    game_state["runoff_active"] = False
    game_state["runoff_candidates"] = []
    game_state["runoff_round"] = 0

def tally_votes_if_complete():
    """Wertet die abgegebenen Stimmen aus, sobald alle Spieler abgestimmt haben."""
    active_chars = game_state.get("active_characters", [])
    if not active_chars or len(game_state["votes"]) != len(active_chars):
        return

    vote_counts = {}
    for voted_for_id in game_state["votes"].values():
        vote_counts[voted_for_id] = vote_counts.get(voted_for_id, 0) + 1

    if not vote_counts:
        return

    max_votes = max(vote_counts.values())
    top_candidates = [char_id for char_id, count in vote_counts.items() if count == max_votes]

    if len(top_candidates) > 1:
        # Stichwahl erforderlich
        game_state["runoff_active"] = True
        game_state["runoff_candidates"] = top_candidates
        game_state["runoff_round"] = game_state.get("runoff_round", 0) + 1
        game_state["votes"] = {}
        game_state["voting_complete"] = False
        game_state["final_accused_id"] = None
        game_state["final_verdict_correct"] = None
    else:
        # Klarer Sieger
        winner_id = top_candidates[0]
        game_state["runoff_active"] = False
        game_state["runoff_candidates"] = []
        game_state["runoff_round"] = 0
        game_state["voting_complete"] = True
        game_state["final_accused_id"] = winner_id
        game_state["final_verdict_correct"] = (winner_id == game_state["murder_id"])

def add_label_to_qr_image(qr_image, label_text):
    """
    Fuegt dem QR-Code-Bild unten einen Text mit Namen und Buchstaben hinzu,
    damit beim Ausdruck sofort klar ist, zu wem der Code gehoert.
    """
    qr_image = qr_image.convert("RGB")

    # Versuche einen lesbaren Font zu verwenden, fallback auf Default
    base_font_size = max(24, qr_image.size[0] // 12)
    try:
        font = ImageFont.truetype("arial.ttf", base_font_size)
    except OSError:
        font = ImageFont.load_default()

    dummy_image = Image.new("RGB", (1, 1))
    dummy_draw = ImageDraw.Draw(dummy_image)
    text_bbox = dummy_draw.textbbox((0, 0), label_text, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]

    padding_x = 40
    padding_top = 20
    gap = 15
    total_width = max(qr_image.width + padding_x, text_width + padding_x)
    total_height = qr_image.height + padding_top + gap + text_height + padding_top

    canvas = Image.new("RGB", (total_width, total_height), "white")
    qr_x = (total_width - qr_image.width) // 2
    canvas.paste(qr_image, (qr_x, padding_top))

    draw = ImageDraw.Draw(canvas)
    text_x = (total_width - text_width) // 2
    text_y = padding_top + qr_image.height + gap
    draw.text((text_x, text_y), label_text, fill="black", font=font)

    return canvas

def replace_letter_placeholders(text, letter_mapping, active_characters):
    """
    Ersetzt Platzhalter wie [B] mit dem tatsächlichen Namen und Buchstaben.
    Z.B. [B] wird zu "Alexa Steinberg [F]" (wenn B -> F gemappt ist)
    """
    import re
    active_ids = {char["id"] for char in active_characters}

    def replace_match(match):
        original_letter = match.group(1)
        # Finde den Charakter mit diesem Original-Buchstaben
        char = next((c for c in CHARACTERS if c["letter"] == original_letter), None)
        if char and char["id"] in active_ids:
            # Gib nur den Namen ohne Buchstaben zurück
            return char['name']
        if original_letter in NPC_PLACEHOLDER_MAP:
            npc = NPC_PLACEHOLDER_MAP[original_letter]
            return npc['name']
        if char:
            return char["name"]

        return match.group(0)  # Keine Änderung, falls nichts gefunden

    # Ersetze alle [A], [B], etc.
    return re.sub(r'\[([A-J])\]', replace_match, text)

def select_murder(characters, seed_tuple, victim):
    """Wählt deterministisch-zufällig einen Mörder mit Gewichtung basierend auf Motiven"""
    # Besserer Seed mit SHA-256 für gleichmäßigere Verteilung
    seed_string = str(seed_tuple) + "_murder"
    seed_hash = hashlib.sha256(seed_string.encode()).hexdigest()
    seed_value = int(seed_hash, 16) % (2**32)
    random.seed(seed_value)

    # Gewichte berechnen basierend auf MOTIVE_MATRIX
    weights = []
    for char in characters:
        victim_name = victim.get("name") if isinstance(victim, dict) else str(victim)
        has_motive = victim_name in MOTIVE_MATRIX.get(char["id"], {})

        # Charaktere mit Motiv bekommen Gewicht 2, ohne Motiv Gewicht 1
        weights.append(2 if has_motive else 1)

    # Gewichtete Auswahl
    murder = random.choices(characters, weights=weights, k=1)[0]
    random.seed()  # Seed zurücksetzen
    return murder["id"]

def select_random_victim(seed_tuple):
    """Wählt deterministisch-zufällig eines der drei NPCs als Mordopfer basierend auf dem Event-Seed"""
    victims = list(NPCS.values())
    # Besserer Seed mit SHA-256 für gleichmäßigere Verteilung
    seed_string = str(seed_tuple) + "_victim"
    seed_hash = hashlib.sha256(seed_string.encode()).hexdigest()
    seed_value = int(seed_hash, 16) % (2**32)
    random.seed(seed_value)
    victim = random.choice(victims)
    random.seed()  # Seed zurücksetzen
    return victim

def select_awakeners(active_characters, murder_id):
    """
    Wählt zufällig 2-3 Personen aus, die beim ersten Schrei aufwachen.
    Der Mörder wird ausgeschlossen.
    """
    # Alle außer dem Mörder
    innocents = [char for char in active_characters if char["id"] != murder_id]

    # Zufällig 2 oder 3 auswählen (falls genug Spieler vorhanden)
    max_awakeners = min(3, len(innocents))
    min_awakeners = min(2, max_awakeners)
    num_awakeners = random.randint(min_awakeners, max_awakeners)
    awakeners = random.sample(innocents, num_awakeners)

    return [char["id"] for char in awakeners]

def select_special_roles(active_characters, murder_id):
    """
    Wählt ECHT-ZUFÄLLIG die speziellen Rollen (nicht deterministisch):
    - Intrigant (will jemandem den Mord anhängen)
    - Verzweifelte Person (will als Mörder identifiziert werden)
    - Verliebtes Paar (wollen gemeinsam überleben)

    Alle außer dem Mörder können diese Rollen bekommen.
    Der Intrigant darf aber jede beliebige Zielperson wählen – inklusive des Mörders.
    Die Auswahl ist nicht Seed-basiert, sondern bei jedem Spielstart neu zufällig.
    """
    # Alle außer dem Mörder
    innocents = [char for char in active_characters if char["id"] != murder_id]

    # Sicherstellen, dass genug Spieler vorhanden sind (mindestens 5 für alle Rollen)
    if len(innocents) < 5:
        return None, None, None, []

    # Mische die Unschuldigen (echt zufällig, kein Seed)
    available_innocents = innocents.copy()
    random.shuffle(available_innocents)

    # 1. Intrigant + Ziel auswählen
    intrigant = available_innocents.pop(0)

    # Ziel kann jede Person außer dem Intriganten sein (inkl. Mörder)
    target_pool = [char for char in active_characters if char["id"] != intrigant["id"]]
    random.shuffle(target_pool)
    intrigant_target = target_pool.pop(0)

    # 2. Verzweifelte Person auswählen
    desperate = available_innocents.pop(0)

    # 3. Verliebtes Paar auswählen (2 Personen)
    lover1 = available_innocents.pop(0)
    lover2 = available_innocents.pop(0)

    return intrigant["id"], intrigant_target["id"], desperate["id"], [lover1["id"], lover2["id"]]

def generate_all_memories(active_chars, murder_id, seed_tuple, special_role_ids):
    """
    Generiert Erinnerungen für ALLE Unschuldigen:
    - 2-3 bekommen Hinweise über den Mörder
    - Restliche bekommen Red Herrings über andere Spieler

    Args:
        active_chars: Liste aktiver Charaktere
        murder_id: ID des Mörders
        seed_tuple: Seed für Reproduzierbarkeit
        special_role_ids: Dict mit intrigant_id, desperate_id, lovers

    Returns:
        dict: {
            char_id: {
                "subject_id": int,      # Über wen ist die Erinnerung
                "clue_id": int,         # Welcher Hinweis
                "is_murderer": bool     # Ist subject der Mörder?
            }
        }
    """
    import random
    # Erweitere Seed mit "memories" Suffix für eindeutige Zufallsfolge
    memory_seed = hash(tuple(list(seed_tuple) + ["memories"]))
    rng = random.Random(memory_seed)

    # Sammle IDs die KEINE Erinnerungen bekommen
    excluded_from_memories = {murder_id}
    if special_role_ids.get("intrigant_id"):
        excluded_from_memories.add(special_role_ids["intrigant_id"])
    if special_role_ids.get("desperate_id"):
        excluded_from_memories.add(special_role_ids["desperate_id"])

    # Spieler die Erinnerungen bekommen
    memory_receivers = [c for c in active_chars if c['id'] not in excluded_from_memories]

    if len(memory_receivers) == 0:
        return {}

    # Anzahl echter Mörder-Hinweise begrenzen:
    # - bis inkl. 8 Spieler: 2
    # - ab 9 Spielern: 3
    target_true = 2 if len(active_chars) <= 8 else 3
    num_true_witnesses = min(target_true, len(memory_receivers))
    true_witnesses = rng.sample(memory_receivers, num_true_witnesses)
    true_witness_ids = [w['id'] for w in true_witnesses]

    # Restliche Spieler bekommen Red Herrings
    red_herring_receivers = [c for c in memory_receivers if c['id'] not in true_witness_ids]

    memories = {}
    lovers = special_role_ids.get("lovers", [])

    # 1. Vergebe echte Mörder-Hinweise
    used_clues_true = set()
    for witness in true_witnesses:
        # Wähle zufälligen Hinweis (ohne Wiederholung)
        available_clues = [i for i in range(1, len(MURDER_CLUES) + 1) if i not in used_clues_true]
        if not available_clues:
            used_clues_true.clear()  # Reset wenn alle verwendet
            available_clues = list(range(1, len(MURDER_CLUES) + 1))

        clue_id = rng.choice(available_clues)
        used_clues_true.add(clue_id)

        memories[witness['id']] = {
            "subject_id": murder_id,
            "clue_id": clue_id,
            "is_murderer": True,
            "clue_pool": "murder"
        }

    # 2. Vergebe Red Herring Hinweise
    used_clues_red = set()
    for receiver in red_herring_receivers:
        receiver_id = receiver['id']

        # Mögliche Subjekte: Alle AUSSER sich selbst, Partner (falls Lover), und ausgeschlossene
        possible_subjects = []
        for char in active_chars:
            # Ausschließen: sich selbst
            if char['id'] == receiver_id:
                continue

            # Ausschließen: eigener Partner (falls Lover)
            if receiver_id in lovers and char['id'] in lovers:
                # Beide sind Lover, also Partner
                continue

            possible_subjects.append(char['id'])

        if not possible_subjects:
            continue  # Keine verfügbaren Subjekte

        # Wähle zufälliges Subjekt
        subject_id = rng.choice(possible_subjects)

        # Wähle zufälligen Hinweis
        available_clues = [i for i in range(1, len(RED_HERRING_CLUES) + 1) if i not in used_clues_red]
        if not available_clues:
            used_clues_red.clear()
            available_clues = list(range(1, len(RED_HERRING_CLUES) + 1))

        clue_id = rng.choice(available_clues)
        used_clues_red.add(clue_id)

        memories[receiver_id] = {
            "subject_id": subject_id,
            "clue_id": clue_id,
            "is_murderer": (subject_id == murder_id),  # Könnte zufällig Mörder treffen
            "clue_pool": "red"
        }

    return memories


def build_memory_text(clue_id, subject_id, letter_mapping, clue_pool="murder"):
    """
    Erstellt den Erinnerungstext.

    Args:
        clue_id: ID des Hinweises
        subject_id: ID der Person über die der Hinweis ist
        letter_mapping: Letter-Mapping aus game_state
        clue_pool: "murder" oder "red" für den Hinweis-Pool

    Returns:
        str: Formatierter HTML-Text
    """
    # Wähle Pool
    pool = MURDER_CLUES if clue_pool == "murder" else RED_HERRING_CLUES

    # Finde Hinweis
    clue = next((c for c in pool if c['id'] == clue_id), None)
    if not clue:
        return ""

    # Finde Subjekt
    subject_char = next((c for c in CHARACTERS if c['id'] == subject_id), None)
    if not subject_char:
        return ""

    subject_name = subject_char['name']
    subject_firstname = subject_char["name"].split(" ")[0]

    # Ersetze Platzhalter
    detail_text = clue['detail'].format(
        subject_name=subject_name,
        subject_firstname=subject_firstname
    )

    return detail_text

def determine_victim(first_event2, first_event1, first_event3, seed_tuple):
    """
    Bestimmt das Opfer zufällig basierend auf dem Seed (Events + Wochentag).
    Alle drei NPCs haben die gleiche Chance, unabhängig davon welche Events stattfanden.
    """
    return select_random_victim(seed_tuple)

def get_character_by_id(char_id):
    """Gibt den Charakter mit der angegebenen ID zurück"""
    for char in CHARACTERS:
        if char["id"] == char_id:
            return char
    return None

def generate_motive_text(murder_id, victim):
    """Gibt den passenden Motivsatz für Mörder und Opfer zurück."""
    if not victim:
        return f"<p>{DEFAULT_MOTIVE_TEXT}</p>"

    victim_name = victim.get("name") if isinstance(victim, dict) else str(victim)
    motive_sentence = MOTIVE_MATRIX.get(murder_id or 0, {}).get(victim_name)

    if motive_sentence:
        return f"<p><strong>Motiv:</strong> {motive_sentence}</p>"

    return f"<p>{DEFAULT_MOTIVE_TEXT}</p>"

def build_phase5_intro_speech(victim):
    """Erstellt die einleitende Rede für Phase 5 (vor der Abstimmung)."""
    # Bestimme, wer die Abstimmung einfordert (Hotelbesitzer oder falls tot, der Investor)
    if victim and victim.get("name") == "Viktor Bergmann":
        speaker = "Dimitri"
    else:
        speaker = "Viktor Bergmann"
    speech = f'''
    <div class="phase5-intro" style="background: #2c3e50; padding: 20px; border-radius: 8px; margin-top: 25px;">
        <h3 style="margin-top: 0;">Phase 5 - Die Anklage</h3>
        <p><strong>{speaker} steht auf.</strong></p>
        <p>„Genug. Es reicht."</p>
        <p>Er lässt den Blick über die Runde wandern, als wolle er sich jeden Einzelnen genau einprägen.</p>
        <p>„Ich weiß nicht, was heute Nacht passiert ist… aber ich weiß eines: Hier drin sitzt jemand, der uns alle in Gefahr gebracht hat. Und ich werde nicht zulassen, dass das nochmal passiert."</p>
        <p>Er ballt die Hände, zwingt sich aber, die Stimme gleichmäßig zu halten.</p>
        <p>„Die Polizei rufen? Nein. Dafür ist es zu spät und außerdem kommt bei dem Wetter niemand hierher. Dafür ist zu viel auf dem Spiel. Dieser Ort darf nicht wieder in die Schlagzeilen. Nicht nach dem, was hier früher schon geschehen ist."</p>
        <p>Ein kurzes Schweigen.</p>
        <p>„Mir ist egal, wer es war. Mir ist egal, warum. Aber es endet heute Nacht. Hier. In diesem Raum."</p>
        <p>Er zeigt auf die Gruppe.</p>
        <p>„Ihr werdet jetzt abstimmen. Jede und jeder von euch weiß genug, um eine Entscheidung zu treffen. Wer von euch ist fähig gewesen, das zu tun?"</p>
        <p>Er tritt einen Schritt zurück, seine Stimme wird dunkler.</p>
        <p>„Ich verspreche euch: Ich kümmere mich danach persönlich um die Person, die ihr bestimmt. Auge um Auge. Zahn um Zahn."</p>
        <p>Noch ein tiefes Einatmen.</p>
        <p>„Wir stimmen geheim ab. Es wird Zeit, dass wir das Monster unter uns finden – bevor die Nacht noch jemanden verschlingt."</p>
    </div>
    '''
    return speech

def build_special_outcome_notes(accused_id, letter_mapping, game_state):
    """
    Baut Zusatztext für das Urteil, abhängig von Spezialrollen:
    - Liebespaar: Partner bricht zusammen, wenn einer stirbt (inline; Shot/Hang unterschiedlich); überleben beide, ziehen sie sich später zusammen zurück
    - Verzweifelte Person: stilles Lächeln am Galgen; sonst geht sie mit hängendem Kopf
    - Intrigant: Humbug-Kommentar bei Fehlurteil, zufrieden-gute-Nacht bei Erfolg
    """
    lover_inline_shot = ""
    lover_inline_hang = ""
    lover_survivor_note = ""
    inline_notes = []
    end_notes = []

    lovers = game_state.get("lovers", [])
    if accused_id in lovers and len(lovers) == 2:
        partner_id = lovers[0] if lovers[1] == accused_id else lovers[1]
        partner_char = get_character_by_id(partner_id)
        partner_letter = letter_mapping.get(partner_id, partner_char["letter"] if partner_char else "?")
        partner_name = partner_char["name"] if partner_char else "Unbekannt"
        lover_inline_shot = (
            f"Als der Schuss fällt, bricht {partner_name} [{partner_letter}] schluchzend zusammen "
            "und muss von den anderen zurückgehalten werden. Die große Liebe starb, bevor ein offenes Geständnis möglich war."
        )
        lover_inline_hang = (
            f"Als der Strick sich zuzieht, bricht {partner_name} [{partner_letter}] schluchzend zusammen "
            "und muss von den anderen zurückgehalten werden. Die große Liebe starb, bevor ein offenes Geständnis möglich war."
        )
    elif len(lovers) == 2:
        # Beide haben überlebt
        lover1 = get_character_by_id(lovers[0])
        lover2 = get_character_by_id(lovers[1])
        letter1 = letter_mapping.get(lovers[0], lover1["letter"] if lover1 else "?")
        letter2 = letter_mapping.get(lovers[1], lover2["letter"] if lover2 else "?")
        name1 = lover1["name"] if lover1 else "Unbekannt"
        name2 = lover2["name"] if lover2 else "Unbekannt"
        lover_survivor_note = (
            f"Später schleichen {name1} [{letter1}] und {name2} [{letter2}] leise auf dasselbe Zimmer, "
            "dankbar, dass sie die Nacht gemeinsam überstanden haben."
        )

    if accused_id == game_state.get("desperate_id"):
        end_notes.append(
            "Die Verzweifelte Person trägt im letzten Moment ein kaum merkliches, friedliches Lächeln – als wäre genau dieses Ende erwartet worden."
        )
    elif game_state.get("desperate_id"):
        desperate_char = get_character_by_id(game_state["desperate_id"])
        desperate_letter = letter_mapping.get(
            game_state["desperate_id"], desperate_char["letter"] if desperate_char else "?"
        )
        desperate_name = desperate_char["name"] if desperate_char else "Unbekannt"
        end_notes.append(
            f"{desperate_name} [{desperate_letter}] verlässt die Szene mit hängendem Kopf und schleppt sich wortlos in ihr Zimmer."
        )

    intrigant_id = game_state.get("intrigant_id")
    intrigant_target = game_state.get("intrigant_target_id")
    if intrigant_id and intrigant_id != accused_id:
        intrigant_char = get_character_by_id(intrigant_id)
        intrigant_letter = letter_mapping.get(intrigant_id, intrigant_char["letter"] if intrigant_char else "?")
        intrigant_name = intrigant_char["name"] if intrigant_char else "Unbekannt"
        if intrigant_target == accused_id:
            end_notes.append(
                f"{intrigant_name} [{intrigant_letter}] wünscht dem Rest mit einem zufriedenen Grinsen eine gute Nacht – der Plan ist aufgegangen."
            )
        else:
            inline_notes.append(
                f"{intrigant_name} [{intrigant_letter}] brummt enttäuscht: „Ach, ist doch alles Humbug“, und zieht sich zurück."
            )

    intr_success_flag = any("Plan ist aufgegangen" in n for n in end_notes)
    desp_success_flag = any("friedliches Lächeln" in n for n in end_notes)

    intr_success_text = next((n for n in end_notes if "Plan ist aufgegangen" in n), "")
    desp_success_text = next((n for n in end_notes if "friedliches Lächeln" in n), "")
    intr_fail_text = next((n for n in inline_notes if "Humbug" in n), "")
    desp_fail_text = next((n for n in end_notes if "hängendem Kopf" in n), "")

    intr_desp_success = ""
    intr_desp_fail = ""
    intr_success = ""
    desp_success = ""

    if intr_success_flag and desp_success_flag:
        parts = [p for p in [intr_success_text, desp_success_text] if p]
        intr_desp_success = "<p>" + "</p><p>".join(parts) + "</p>"
    elif intr_success_flag and not desp_success_flag:
        intr_success = f"<p>{intr_success_text}</p>" if intr_success_text else ""
    elif desp_success_flag and not intr_success_flag:
        desp_success = f"<p>{desp_success_text}</p>" if desp_success_text else ""
    else:
        fail_parts = [p for p in [intr_fail_text, desp_fail_text] if p]
        intr_desp_fail = "<p>" + "</p><p>".join(fail_parts) + "</p>" if fail_parts else ""

    return (
        lover_inline_shot,
        lover_inline_hang,
        lover_survivor_note,
        intr_desp_success,
        intr_desp_fail,
        intr_success,
        desp_success,
    )


def build_phase5_outcome_text(accused_char, letter_mapping, is_correct, victim, game_state):
    """Erstellt den Phase-5-Ergebnis-Text nach der Abstimmung (ohne die einleitende Rede)."""
    if not accused_char or is_correct is None:
        return None

    assigned_letter = letter_mapping.get(accused_char["id"], accused_char["letter"])
    accused_display = f"{accused_char['name']} [{assigned_letter}]"

    # Bestimme, wer die Abstimmung einfordert (Hotelbesitzer oder falls tot, der Investor)
    if victim and victim.get("name") == "Viktor Bergmann":
        speaker_lower = "der russische Investor"
    else:
        speaker_lower = "der Hotelbesitzer"


    (
        lover_inline_shot,
        lover_inline_hang,
        lover_survivor_note,
        intr_desp_success,
        intr_desp_fail,
        intr_success,
        desp_success,
    ) = build_special_outcome_notes(
        accused_char["id"], letter_mapping, game_state
    )

    if is_correct:
        outcome = f'''
        <p>Doch so leicht gibt <strong>{accused_display}</strong> nicht auf und ruft: "Denkt ihr Normalsterblichen, ihr könntet einen Werwolf einfach erhängen?".
        Doch noch bevor es zu einem weiteren Wort oder Tumult kommen kann, knallt es Ohrenbetäubend laut. Ein greller Blitz durchzuckt den Raum und ein markerschütternder Schrei erfüllt die Luft.
        Helga hält die Flinte noch in der Hand aus dessen Lauf es raucht. Die Flinte hatte Silberkugeln geladen.</p>
        {'<p>' + lover_inline_shot + '</p>' if lover_inline_shot else ''}
        {intr_desp_success or intr_success or intr_desp_fail}
        {desp_success if not intr_desp_success else ''}
        {'<p>' + lover_survivor_note + '</p>' if lover_survivor_note else ''}
        <p>Der Schrecken scheint endgültig besiegt und der Fluch des Hotels gebrochen. Alle nehmen das Geheimnis mit ins Grab und hoffen nun auf einen ruhigen Schlaf.</p>
        '''
    else:
        # Großschreibung für Satzanfang
        speaker_capitalized = speaker_lower.capitalize()
        outcome = f'''
        <p>{speaker_capitalized} schlägt <strong>{accused_display}</strong> mit einem Knüppel auf den Hinterkopf und zusammen mit den anderen Bediensteten wird <strong>{accused_display}</strong> mit einem Seil am selben Ast aufgehängt. 
        {' ' + lover_inline_hang if lover_inline_hang else ''} <strong>Nach wenigen Minuten ist alles vorbei.</strong></p>
        {intr_desp_success or intr_success or intr_desp_fail}
        {desp_success if not intr_desp_success else ''}
        {'<p>' + lover_survivor_note + '</p>' if lover_survivor_note else ''}
        <p>Völlig erschöpft gehen alle zu Bett und schlafen den Schlaf der Gerechten... bis die Wolken sich wieder verziehen und ein weiterer Schrei die vollmondhelle Nacht durchhallt.</p>
        '''

    html_content = f'''
    <div class="phase5-outcome" style="background: #2c3e50; padding: 20px; border-radius: 8px; margin-top: 25px;">
        <h3 style="margin-top: 0;">Phase 5 - Das Urteil</h3>
        <hr style="margin: 20px 0; border: none; border-top: 1px solid #34495e;">
        <p>Als die Entscheidung gefallen ist, wird <strong>{accused_display}</strong> unruhig und blickt die Umstehenden flehentlich an. Da schreit {speaker_lower} auf: 
        <em>„Alea iacta est. Die Entscheidung ist gefallen und nun muss <strong>{accused_display}</strong> sterben! "</em></p>
        {outcome}
    </div>
    '''

    return html_content


def get_personal_outcome(character_id, accused_id, murder_id, letter_mapping):
    """
    Erstellt eine personalisierte Erfolgsmeldung für einen Spieler basierend auf seinen Zielen.

    Mögliche Ziele:
    - Mörder: Nicht entdeckt werden
    - Intrigant: Das Intrigant-Ziel soll hingerichtet werden
    - Verzweifelte Person: Selbst hingerichtet werden
    - Verliebtes Paar: Beide müssen überleben (beide dürfen nicht hingerichtet werden)
    - Normale Unschuldige: Mörder muss hingerichtet werden

    Returns: (success: bool, message: str)
    """

    intrigant_id = game_state.get("intrigant_id")
    intrigant_target_id = game_state.get("intrigant_target_id")
    desperate_id = game_state.get("desperate_id")
    lovers = game_state.get("lovers", [])

    is_murderer = (character_id == murder_id)
    is_accused = (character_id == accused_id)
    is_intrigant = (character_id == intrigant_id)
    is_desperate = (character_id == desperate_id)
    is_lover = (character_id in lovers)

    # Sammle alle erreichten und verfehlten Ziele
    achieved_goals = []
    failed_goals = []

    # === MÖRDER ===
    if is_murderer:
        if not is_accused:
            achieved_goals.append("🎭 <strong>Mörder-Ziel erreicht:</strong> Du bist unentdeckt geblieben und hast dein Verbrechen vertuscht.")
        else:
            failed_goals.append("💀 <strong>Mörder-Ziel verfehlt:</strong> Du wurdest als Mörder entlarvt und hingerichtet.")

    # === INTRIGANT ===
    if is_intrigant:
        target_char = get_character_by_id(intrigant_target_id)
        if target_char:
            target_letter = letter_mapping.get(intrigant_target_id, target_char.get("letter", "?"))
            target_display = f"{target_char['name']} [{target_letter}]"

            if accused_id == intrigant_target_id:
                achieved_goals.append(f"🎯 <strong>Intrigant-Ziel erreicht:</strong> Du hast erfolgreich {target_display} den Mord angehängt!")
            else:
                failed_goals.append(f"🎯 <strong>Intrigant-Ziel verfehlt, du hast versagt:</strong> {target_display} wurde nicht hingerichtet.")

    # === VERZWEIFELTE PERSON ===
    if is_desperate:
        if is_accused:
            achieved_goals.append("😔 <strong>Verzweifeltes Ziel erreicht:</strong> Du hast dein Ende gefunden. Möge deine Seele nun Frieden finden.")
        else:
            failed_goals.append("😔 <strong>Du hast schon wieder versagt:</strong> Du lebst weiter, doch der innere Schmerz bleibt.")

    # === VERLIEBTES PAAR ===
    if is_lover:
        # Finde den/die Partner/in
        lover_partner_id = lovers[1] if lovers[0] == character_id else lovers[0]
        partner_char = get_character_by_id(lover_partner_id)

        if partner_char:
            partner_letter = letter_mapping.get(lover_partner_id, partner_char.get("letter", "?"))
            partner_display = f"{partner_char['name']} [{partner_letter}]"

            # Beide müssen überleben
            partner_survived = (lover_partner_id != accused_id)
            i_survived = not is_accused

            if partner_survived and i_survived:
                achieved_goals.append(f"💕 <strong>Liebespaar-Ziel erreicht:</strong> Du und {partner_display} habt beide überlebt und könnt gemeinsam in die Zukunft blicken!")
            elif not partner_survived and not i_survived:
                failed_goals.append(f"💕 <strong>Liebespaar-Ziel verfehlt:</strong> Ihr wurdet beide hingerichtet. Wenigstens seid ihr zusammen im Tod.")
            elif not partner_survived:
                failed_goals.append(f"💔 <strong>Liebespaar-Ziel verfehlt:</strong> {partner_display} wurde hingerichtet. Du bleibst allein zurück.")
            else:  # not i_survived
                failed_goals.append(f"💔 <strong>Liebespaar-Ziel verfehlt:</strong> Du wurdest hingerichtet und lässt {partner_display} allein zurück.")

    # === NORMALE UNSCHULDIGE (ohne spezielle Rolle) ===
    if not is_murderer and not is_intrigant and not is_desperate and not is_lover:
        murderer_caught = (accused_id == murder_id)

        if murderer_caught:
            achieved_goals.append("⚖️ <strong>Unschuldigen-Ziel erreicht:</strong> Der wahre Mörder wurde gefasst und die Gerechtigkeit siegt!")
        else:
            failed_goals.append("⚖️ <strong>Unschuldigen-Ziel verfehlt:</strong> Der Mörder ist noch frei. Die Unschuld wurde nicht gesühnt.")

    # Kombiniere alle Nachrichten
    all_messages = achieved_goals + failed_goals

    if not all_messages:
        return False, "<p>Keine speziellen Ziele.</p>"

    # Bestimme Gesamterfolg (mindestens ein Ziel erreicht)
    overall_success = len(achieved_goals) > 0

    messages_html = "<br>".join(all_messages)

    return overall_success, f"<div style='margin-top: 15px;'>{messages_html}</div>"


# ============================================================================
# ROUTEN
# ============================================================================

@app.route('/')
def index():
    """Startseite mit Links zu Admin und Spieler-Übersicht"""
    if game_state["game_started"]:
        characters = game_state.get("active_characters", CHARACTERS)
    else:
        characters = CHARACTERS

    return render_template('index.html',
                         game_started=game_state["game_started"],
                         characters=characters,
                         letter_mapping=game_state.get("letter_mapping", {}))

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    """Admin-Seite für Spielkonfiguration (mehrstufig)"""
    error = session.pop('admin_error', None)
    success = session.pop('admin_success', None)

    if request.method == 'POST':
        error = None
        success = None
        action = request.form.get('action')

        # PHASE 1: Charaktere auswählen und zu Phase 2 wechseln
        if action == 'select_characters':
            selected_char_ids = request.form.getlist('characters')
            selected_char_ids = [int(cid) for cid in selected_char_ids]

            if len(selected_char_ids) < 7 or len(selected_char_ids) > 10:
                error = "Fehler: Du musst zwischen 7 und 10 Charaktere auswählen!"
            else:
                # Charaktere speichern
                active_chars = [c for c in CHARACTERS if c["id"] in selected_char_ids]
                game_state["active_characters"] = active_chars
                game_state["num_players"] = len(active_chars)
                game_state["letter_mapping"] = assign_random_letters(active_chars)
                reset_voting_state()
                game_state["setup_phase"] = 1  # Zu Phase 2 (Event-Konfiguration)
                success = f"{len(active_chars)} Charaktere ausgewählt. Bitte konfiguriere jetzt die Ereignisse."

        # PHASE 2: Ereignisse konfigurieren und Spiel starten (Phase 3)
        elif action == 'configure_events':
            event1_name = request.form.get('event1_name', '').strip() or "Klo"
            event2_name = request.form.get('event2_name', '').strip() or "Küchenhilfe"
            event3_name = request.form.get('event3_name', '').strip() or "Alkohol"

            first_event1 = request.form.get('first_event1', type=int)
            first_event2 = request.form.get('first_event2', type=int)
            first_event3 = request.form.get('first_event3', type=int)

            # Event-Namen speichern
            game_state["event1_name"] = event1_name
            game_state["event2_name"] = event2_name
            game_state["event3_name"] = event3_name

            # Events speichern
            game_state["first_event1"] = first_event1
            game_state["first_event2"] = first_event2
            game_state["first_event3"] = first_event3

            # Seed-Tuple aus den Event-Charakteren + Wochentag erstellen (für deterministischen Zufall)
            weekday = datetime.now().weekday()  # 0=Montag, 1=Dienstag, ..., 6=Sonntag
            seed_tuple = (first_event1, first_event2, first_event3, weekday)

            # Opfer zuerst bestimmen (für gewichtete Mörder-Auswahl)
            active_chars = game_state["active_characters"]
            victim = determine_victim(first_event2, first_event1, first_event3, seed_tuple)
            game_state["victim"] = victim

            # Mörder mit Gewichtung basierend auf Motiv auswählen
            game_state["murder_id"] = select_murder(active_chars, seed_tuple, victim)
            game_state["awakeners"] = select_awakeners(active_chars, game_state["murder_id"])

            # Spezielle Rollen auswählen (Intrigant, Verzweifelte Person, Verliebtes Paar)
            intrigant_id, intrigant_target_id, desperate_id, lovers = select_special_roles(
                active_chars, game_state["murder_id"]
            )
            game_state["intrigant_id"] = intrigant_id
            game_state["intrigant_target_id"] = intrigant_target_id
            game_state["desperate_id"] = desperate_id
            game_state["lovers"] = lovers

            # Spiel ist jetzt bereit für Phase 3
            reset_voting_state()
            game_state["setup_phase"] = 2
            game_state["current_phase"] = 3  # Spieler können sich einloggen (Phase 3)
            game_state["game_started"] = True

            # QR-Codes automatisch generieren
            try:
                create_qr_codes_for_players()
                success = f"Phase 3 gestartet! QR-Codes wurden generiert. Spieler können sich jetzt einloggen."
            except Exception as e:
                print(f"Fehler beim Generieren der QR-Codes: {e}")
                success = f"Phase 3 gestartet! Achtung: QR-Codes konnten nicht automatisch generiert werden."

        # Phasen-Wechsel für Spieler (3->4->5)
        # Regel: Von Phase 3 nur zu Phase 4, von Phase 4 nur zu Phase 5
        elif action == 'change_phase':
            new_phase = request.form.get('phase', type=int)
            current_phase = game_state.get("current_phase", 0)

            # Validierung: nur erlaubte Übergänge
            valid_transition = False
            if current_phase == 3 and new_phase == 4:
                valid_transition = True
            elif current_phase == 4 and new_phase == 5:
                valid_transition = True

            if valid_transition:
                game_state["current_phase"] = new_phase
                if new_phase == 5:
                    reset_voting_state()
                success = f"Spielphase wurde auf {new_phase} geändert."
            else:
                error = f"Ungültiger Phasenwechsel! Von Phase {current_phase} kann nur zur nächsten Phase gewechselt werden."

        elif action == 'reveal_memories':
            # Prüfe ob bereits aktiviert
            if game_state.get("memories_revealed"):
                error = "Erinnerungen wurden bereits aktiviert."
            elif game_state.get("current_phase") != 4:
                error = "Erinnerungen können nur in Phase 4 aktiviert werden."
            else:
                # Generiere Erinnerungen
                murder_id = game_state.get("murder_id")
                active_chars = game_state.get("active_characters", [])
                seed_tuple = game_state.get("seed", (None, None, None, 1))

                special_role_ids = {
                    "intrigant_id": game_state.get("intrigant_id"),
                    "desperate_id": game_state.get("desperate_id"),
                    "lovers": game_state.get("lovers", [])
                }

                memories = generate_all_memories(active_chars, murder_id, seed_tuple, special_role_ids)

                game_state["memories_revealed"] = True
                game_state["memories"] = memories
                success = f"Zusätzliche Erinnerungen wurden für {len(memories)} Spieler aktiviert."

        if error:
            session['admin_error'] = error
        if success:
            session['admin_success'] = success
        return redirect(url_for('admin'))

    # Phase 5 Speech generieren, falls in Phase 5
    phase5_speech = None
    phase5_outcome_text = None

    if game_state.get("current_phase") == 5:
        phase5_speech = build_phase5_intro_speech(game_state.get("victim"))

        # Phase 5 Outcome Text generieren, wenn Abstimmung abgeschlossen
        if game_state.get("voting_complete", False) and game_state.get("final_accused_id"):
            accused_char = get_character_by_id(game_state["final_accused_id"])
            is_correct = game_state.get("final_verdict_correct", False)
            letter_mapping = game_state.get("letter_mapping", {})
            phase5_outcome_text = build_phase5_outcome_text(
                accused_char, letter_mapping, is_correct, game_state.get("victim"), game_state
            )

    return render_template('admin.html',
                         characters=CHARACTERS,
                         game_state=game_state,
                         error=error,
                         success=success,
                         phase5_speech=phase5_speech,
                         phase5_outcome_text=phase5_outcome_text)

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

    # Prüfen, ob dieser Charakter der Mörder ist
    is_murder = (character["id"] == game_state["murder_id"])

    # Prüfen, ob dieser Charakter beim ersten Schrei aufwacht
    is_awakener = character["id"] in game_state.get("awakeners", [])

    # Buchstaben-Mapping holen
    letter_mapping = game_state.get("letter_mapping", {})

    # Zugewiesenen Buchstaben für diesen Charakter holen
    assigned_letter = letter_mapping.get(character["id"], character["letter"])

    # Phase-3-Texte holen und Platzhalter ersetzen (nach zugewiesenem Buchstaben)
    phase3_raw = PHASE3_TEXTS.get(assigned_letter, {
        "nacht": "Keine Informationen verfügbar.",
        "alibi": "Keine Alibi-Information verfügbar."
    })

    active_chars = game_state.get("active_characters", [])

    phase3 = {
        "nacht": replace_letter_placeholders(phase3_raw["nacht"], letter_mapping, active_chars),
        "alibi": replace_letter_placeholders(phase3_raw["alibi"], letter_mapping, active_chars)
    }

    # Abendverlauf für alle erstellen (erst Alibi, dann Nacht)
    abendverlauf = f"<p><strong>Dein Abend:</strong></p><p>{phase3['alibi']}</p><p>{phase3['nacht']}</p>"

    # Mörder-Text mit Platzhaltern füllen
    murder_text = None
    innocent_text = None
    awakening_text = None

    if is_murder:
        # Motiv-Text generieren
        motive_text = generate_motive_text(
            game_state["murder_id"],
            game_state["victim"]
        )

        # Mörder-Text zusammensetzen
        murder_text = MURDER_TEXT_TEMPLATE.format(
            abendverlauf=abendverlauf,
            victim_name=game_state["victim"]["name"],
            motive_text=motive_text
        )
    else:
        # Unschuldigen-Text mit Traumsequenz
        base_dream_text = DREAM_TEXTS.get(character["id"], "Du hast einen seltsamen, wirren Traum.")
        # Liebespaar: Traum startet mit Gedanken an den Partner
        if character["id"] in game_state.get("lovers", []):
            lovers = game_state.get("lovers", [])
            other_lover_id = [lid for lid in lovers if lid != character["id"]][0]
            other_lover = get_character_by_id(other_lover_id)
            if other_lover:
                dream_intro = (
                    f"Obwohl der Abend turbulent begann, kreisen deine Gedanken um {other_lover['name']}. "
                    "Das Gefühl ist überraschend stark – fast so, als hättest du dich Hals über Kopf verliebt. "
                    f"Du fragst dich, ob {other_lover['name']} das genauso spürt. Doch plötzlich ändert sich die Szenerie... "
                )
                base_dream_text = dream_intro + base_dream_text

        # Spezielle Rollen-Zusätze
        special_role_text = ""

        # Prüfe ob Intrigant
        if character["id"] == game_state.get("intrigant_id"):
            target_char = get_character_by_id(game_state.get("intrigant_target_id"))
            if target_char:
                target_name = target_char["name"]
                special_role_text += INTRIGANT_DREAM_TEMPLATE.format(target_name=target_name)

        # Prüfe ob Verzweifelter
        if character["id"] == game_state.get("desperate_id"):
            special_role_text += DESPERATE_DREAM_SUFFIX

        # Prüfe ob Verliebter
        if character["id"] in game_state.get("lovers", []):
            lovers = game_state.get("lovers", [])
            other_lover_id = [lid for lid in lovers if lid != character["id"]][0]
            other_lover = get_character_by_id(other_lover_id)
            if other_lover:
                lover_name = other_lover["name"]
                special_role_text += LOVER_DREAM_TEMPLATE.format(lover_name=lover_name)

        combined_dream = base_dream_text + special_role_text

        if is_awakener:
            # Awakener: Verwende den Aufwach-Text als Haupttext, keine Doppelung
            innocent_text = AWAKENING_TEXT_TEMPLATE.format(dream_text=combined_dream)
            awakening_text = None
        else:
            innocent_text = INNOCENT_TEXT_TEMPLATE.format(
                abendverlauf=abendverlauf,
                dream_text=combined_dream
            )

    # Aufwach-Text wird nur einmal gezeigt (im Haupttext), daher hier kein separater Block mehr

    # Aktuelle Phase
    current_phase = game_state.get("current_phase", 0)

    # Phase 5: Prüfen ob dieser Spieler schon abgestimmt hat
    has_voted = character["id"] in game_state.get("votes", {})

    # Phase 5: Stichwahl-Informationen
    runoff_active = game_state.get("runoff_active", False)
    runoff_candidates = game_state.get("runoff_candidates", [])
    runoff_round = game_state.get("runoff_round", 0)

    # Prüfe ob dieser Charakter die verzweifelte Person ist
    is_desperate = (character["id"] == game_state.get("desperate_id"))

    # Phase-5-Intro-Rede (sofort bei Phase 5, vor der Abstimmung)
    phase5_intro_speech = None
    if current_phase == 5:
        phase5_intro_speech = build_phase5_intro_speech(game_state["victim"])

    # Phase-5-Outcome Text generieren wenn Abstimmung abgeschlossen
    phase5_outcome_text = None
    personal_outcome_success = None
    personal_outcome_message = None

    if game_state.get("voting_complete", False) and game_state.get("final_accused_id"):
        accused_char = get_character_by_id(game_state["final_accused_id"])
        is_correct = game_state.get("final_verdict_correct", False)
        phase5_outcome_text = build_phase5_outcome_text(
            accused_char, letter_mapping, is_correct, game_state["victim"], game_state
        )

        # Generiere persönliche Erfolgsmeldung für diesen Spieler
        personal_outcome_success, personal_outcome_message = get_personal_outcome(
            character["id"],
            game_state["final_accused_id"],
            game_state["murder_id"],
            letter_mapping
        )

    # Phase 4: Zusätzliche Erinnerungen
    additional_memory_text = None
    if current_phase >= 4 and game_state.get("memories_revealed"):
        memories = game_state.get("memories", {})
        char_id = character["id"]

        if char_id in memories:
            memory_data = memories[char_id]
            additional_memory_text = build_memory_text(
                clue_id=memory_data["clue_id"],
                subject_id=memory_data["subject_id"],
                letter_mapping=letter_mapping,
                clue_pool=memory_data.get("clue_pool", "murder")
            )

    return render_template('player.html',
                         character=character,
                         assigned_letter=assigned_letter,
                         is_murder=is_murder,
                         is_awakener=is_awakener,
                         is_desperate=is_desperate,
                         victim=game_state["victim"],
                         phase3=phase3,
                         awakening_text=awakening_text,
                         current_phase=current_phase,
                         murder_text=murder_text,
                         innocent_text=innocent_text,
                         has_voted=has_voted,
                         voting_complete=game_state.get("voting_complete", False),
                         runoff_active=runoff_active,
                         runoff_candidates=runoff_candidates,
                         runoff_round=runoff_round,
                         active_characters=active_chars,
                         letter_mapping=letter_mapping,
                         phase5_intro_speech=phase5_intro_speech,
                         phase5_outcome_text=phase5_outcome_text,
                         personal_outcome_success=personal_outcome_success,
                         personal_outcome_message=personal_outcome_message,
                         additional_memory=additional_memory_text)

@app.route('/victim-reveal')
def victim_reveal():
    """Seite für Spielleiter: Zeigt das Mordopfer (für Phase 4)"""
    if not game_state["game_started"]:
        return render_template('error.html',
                             message="Das Spiel wurde noch nicht gestartet.")

    if not game_state["victim"]:
        return render_template('error.html',
                             message="Kein Opfer wurde ausgewählt.")

    return render_template('victim_reveal.html',
                         victim=game_state["victim"])

@app.route('/vote', methods=['POST'])
def vote():
    """Spieler gibt seine Stimme in Phase 5 ab"""
    if not game_state["game_started"] or game_state["current_phase"] != 5:
        return redirect(url_for('index'))

    voter_id = request.form.get('voter_id', type=int)
    accused_id = request.form.get('accused_id', type=int)

    if not voter_id or not accused_id:
        return redirect(url_for('index'))

    # Prüfen ob Spieler aktiv ist
    active_ids = [char["id"] for char in game_state["active_characters"]]
    if voter_id not in active_ids:
        return redirect(url_for('index'))

    # Bei Stichwahl: Nur für Stichwahl-Kandidaten stimmen erlaubt
    if game_state.get("runoff_active", False):
        if accused_id not in game_state["runoff_candidates"]:
            return redirect(url_for('index'))
    else:
        if accused_id not in active_ids:
            return redirect(url_for('index'))

    # Stimme speichern (überschreibt alte Stimme falls vorhanden)
    game_state["votes"][voter_id] = accused_id

    tally_votes_if_complete()

    # Zurück zur Spielerseite
    voter_char = next((c for c in CHARACTERS if c["id"] == voter_id), None)
    if voter_char:
        slug = get_player_slug(voter_char)
        return redirect(url_for('player_view', slug=slug))

    return redirect(url_for('index'))

@app.route('/admin/random-votes', methods=['POST'])
def admin_random_votes():
    """Testing-Feature: Füllt alle fehlenden Stimmen zufällig aus"""
    if not game_state["game_started"] or game_state["current_phase"] != 5:
        return redirect(url_for('admin'))

    active_ids = [char["id"] for char in game_state["active_characters"]]

    # Für jeden Spieler der noch nicht abgestimmt hat
    for voter_id in active_ids:
        if voter_id not in game_state["votes"]:
            # Wähle zufällig einen anderen Spieler
            if game_state.get("runoff_active", False):
                possible_targets = [char_id for char_id in game_state["runoff_candidates"] if char_id != voter_id]
            else:
                possible_targets = [char_id for char_id in active_ids if char_id != voter_id]

            if possible_targets:
                accused_id = random.choice(possible_targets)
                game_state["votes"][voter_id] = accused_id

    tally_votes_if_complete()

    return redirect(url_for('admin'))

@app.route('/reset', methods=['POST'])
def reset_game():
    """Setzt das Spiel zurück (nur für Admin) und löscht alle QR-Codes"""
    # Spielzustand zurücksetzen
    game_state["murder_id"] = None
    game_state["victim"] = None
    game_state["num_players"] = None
    game_state["active_characters"] = []
    game_state["letter_mapping"] = {}
    game_state["awakeners"] = []
    game_state["event1_name"] = None
    game_state["event2_name"] = None
    game_state["event3_name"] = None
    game_state["first_event1"] = None
    game_state["first_event2"] = None
    game_state["first_event3"] = None
    game_state["setup_phase"] = 0
    game_state["current_phase"] = 0
    game_state["game_started"] = False
    reset_voting_state()

    # QR-Codes Ordner leeren
    qr_folder = os.path.join(os.path.dirname(__file__), 'qr_codes')
    if os.path.exists(qr_folder):
        try:
            # Lösche alle Dateien im Ordner
            for filename in os.listdir(qr_folder):
                file_path = os.path.join(qr_folder, filename)
                if os.path.isfile(file_path):
                    os.remove(file_path)
        except Exception as e:
            print(f"Fehler beim Löschen der QR-Codes: {e}")

    return redirect(url_for('admin'))

def get_local_ip():
    """Ermittelt die lokale Netzwerk-IP-Adresse"""
    import socket
    try:
        # Erstelle eine Socket-Verbindung zu einem externen Server (muss nicht erreichbar sein)
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception:
        # Fallback auf localhost
        return "127.0.0.1"

def create_qr_codes_for_players():
    """Helper-Funktion: Generiert QR-Codes für alle aktiven Spieler"""
    # QR-Code-Ordner erstellen
    qr_dir = os.path.join(os.getcwd(), 'qr_codes')
    os.makedirs(qr_dir, exist_ok=True)

    # Alte QR-Codes löschen bevor neue generiert werden
    if os.path.exists(qr_dir):
        try:
            for filename in os.listdir(qr_dir):
                file_path = os.path.join(qr_dir, filename)
                if os.path.isfile(file_path):
                    os.remove(file_path)
        except Exception as e:
            print(f"Fehler beim Löschen der alten QR-Codes: {e}")

    # Nur für aktive Charaktere QR-Codes generieren
    active_chars = game_state.get("active_characters", CHARACTERS)
    letter_mapping = game_state.get("letter_mapping", {})

    # Verwende die lokale Netzwerk-IP statt request.host_url
    local_ip = get_local_ip()
    base_url = f"http://{local_ip}:9000/"

    for char in active_chars:
        assigned_letter = letter_mapping.get(char["id"], char["letter"])
        slug = get_player_slug(char)
        url = base_url + "player/" + slug
        label_text = f"[{assigned_letter}] {char['name']}"

        # QR-Code mit hoher Aufloesung erstellen
        qr = qrcode.QRCode(
            version=1,
            box_size=20,  # Groessere Box-Size fuer hoehere Aufloesung
            border=4,
        )
        qr.add_data(url)
        qr.make(fit=True)

        # Bild erstellen und mit Schriftzug versehen
        img = qr.make_image(fill_color="black", back_color="white")
        labeled_img = add_label_to_qr_image(img, label_text)

        # Dateiname und Pfad erstellen
        safe_name = char['name'].replace(' ', '_').replace('"', '').replace('?', '').replace('"', '')
        filename = f"{assigned_letter}_{safe_name}.png"
        filepath = os.path.join(qr_dir, filename)

        # Als PNG speichern (Type-Checker-Warnung kann ignoriert werden)
        labeled_img.save(filepath)  # type: ignore

@app.route('/generate-qr-codes', methods=['POST'])
def generate_qr_codes():
    """Generiert QR-Codes als PNG-Dateien mit 300 DPI"""
    if not game_state["game_started"]:
        return redirect(url_for('admin'))

    create_qr_codes_for_players()
    return redirect(url_for('admin'))

@app.route('/qr-codes')
def qr_codes():
    """Zeigt alle QR-Code-Links für die Spieler (zur einfachen Verteilung)"""
    if not game_state["game_started"]:
        return render_template('error.html',
                             message="Das Spiel wurde noch nicht gestartet.")

    # Links nur für aktive Spieler erstellen mit lokaler Netzwerk-IP
    local_ip = get_local_ip()
    base_url = f"http://{local_ip}:9000/"
    qr_folder = os.path.join(os.path.dirname(__file__), 'qr_codes')

    active_chars = game_state.get("active_characters", CHARACTERS)
    letter_mapping = game_state.get("letter_mapping", {})
    player_links = []
    for char in active_chars:
        assigned_letter = letter_mapping.get(char["id"], char["letter"])
        slug = get_player_slug(char)
        safe_name = char['name'].replace(' ', '_').replace('"', '').replace('?', '').replace('"', '')
        filename = f"{assigned_letter}_{safe_name}.png"
        qr_path = os.path.join(qr_folder, filename)
        player_links.append({
            "character": char,
            "url": base_url + "player/" + slug,
            "assigned_letter": assigned_letter,
            "qr_url": url_for('qr_code_file', filename=filename) if os.path.isfile(qr_path) else None
        })

    return render_template('qr_codes.html', player_links=player_links)

@app.route('/qr-codes/files/<path:filename>')
def qr_code_file(filename):
    """Stellt generierte QR-Code-Bilder bereit."""
    qr_folder = os.path.join(os.path.dirname(__file__), 'qr_codes')
    file_path = os.path.join(qr_folder, filename)
    if not os.path.isfile(file_path):
        abort(404)
    return send_from_directory(qr_folder, filename)

# ============================================================================
# MAIN
# ============================================================================

if __name__ == '__main__':
    # Server starten (erreichbar im lokalen Netzwerk)
    app.run(host='0.0.0.0', port=9000, debug=True)
