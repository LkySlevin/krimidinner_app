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

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)  # Für Session-Management

# ============================================================================
# DATENSTRUKTUREN - HIER KÖNNEN DIE TEXTE ANGEPASST WERDEN
# ============================================================================

# 10 Spielercharaktere mit Buchstaben-IDs
CHARACTERS = [
    {"id": 1, "letter": "A", "name": "Vincent Dubois", "url_slug": "spieler-a"},
    {"id": 2, "letter": "B", "name": "Alexa Steinberg", "url_slug": "spieler-b"},
    {"id": 3, "letter": "C", "name": "Viktoria Lang", "url_slug": "spieler-c"},
    {"id": 4, "letter": "D", "name": "Pater Antonio Benedetti", "url_slug": "spieler-d"},
    {"id": 5, "letter": "E", "name": "Jazz Monroe", "url_slug": "spieler-e"},
    {"id": 6, "letter": "F", "name": "Dr. Sarah Chen", "url_slug": "spieler-f"},
    {"id": 7, "letter": "G", "name": "Luna Silbermann", "url_slug": "spieler-g"},
    {"id": 8, "letter": "H", "name": "Maximilian 'Max' Gold", "url_slug": "spieler-h"},
    {"id": 9, "letter": "I", "name": "Tom Greenwood", "url_slug": "spieler-i"},
    {"id": 10, "letter": "J", "name": "Maria Gonzalez", "url_slug": "spieler-j"}
]

# 3 NPCs (mögliche Opfer)
NPCS = {
    "kueche": {"name": "Jonas Reber", "role": "Koch", "location": "Die alte Eiche"},
    "klo": {"name": "Viktor Bergmann", "role": "Hotelier", "location": "Die alte Eiche"},
    "alkohol": {"name": "Dimitri Volkov", "role": "Investor", "location": "Die alte Eiche"}
}

NPC_PLACEHOLDER_MAP = {
    "H": {"name": "Der Koch", "tag": "NPC"},
    "I": {"name": "Die Hausdame", "tag": "NPC"},
    "J": {"name": "Viktor Bergmann", "tag": "Hotelier"}
}

# Phase-3-Texte für jeden Charakter (Nachtverhalten + Alibi)
# HIER KÖNNEN DIE TEXTE INDIVIDUELL ANGEPASST WERDEN
# Buchstaben A-J entsprechen den Charakteren 1-10
PHASE3_TEXTS = {
    1: {  # A  "Frühes Zurückziehen"
        "nacht": "Du fühlst dich vom Tag erschöpft und gehst früh in dein Zimmer. Du räumst noch kurz etwas auf, sortierst deine Sachen und legst dich nach einem schnellen Blick aus dem Fenster ins Bett. Zum Einschlafen hörst du noch eine Folge der Drei Fragezeichen ??? 87 auf Spotify.",
        "alibi": "Auf dem Flur, kurz bevor du dein Zimmer erreichst, siehst du [B] gerade aus dem Bad kommend. Wenige Sekunden später begegnet dir [C] mit einer Wasserflasche in der Hand Richtung Treppe gehend."
    },
    2: {  # B "Kurzes Fenster-Ritual"
        "nacht": "Du kommst gerade aus dem Gemeinschaftsbad. Bevor du ins Bett gehst, bleibst du einen Moment am Fenster stehen, beobachtest die Wolken und holst tief Luft. Danach gehst du auf dein Zimmer. Um besser einschlafen zu können, hörst du dir noch eine Folge der Drei Fragezeichen ??? 69 auf Spotify an.",
        "alibi": "Auf dem Weg siehst du [A] gerade im Zimmer verschwindend. Als du die Treppe erreichst, begegnet dir [D] die Stufen hinaufgehend."
    },
    3: {  # C "Zu viel gegessen"
        "nacht": "Du hast beim Dinner wohl etwas übertrieben und fühlst dich schwer. Im Zimmer schaltest du den Fernseher kurz ein, zappst durch, doch deine Augen fallen schnell zu.",
        "alibi": "Im Flur siehst du [A] die Tür hinter sich schließend. Kurz darauf kommt dir [F] entgegen, etwas in der Hand tragend – vielleicht ein Snack."
    },
    4: {  # D "Nachttee in der Lounge"
        "nacht": "Du nimmst dir in der Lounge noch einen Tee oder ein Wasser und genießt einen Moment Ruhe. Danach gehst du Richtung Zimmer, stellst dir auf Spotify noch die Drei Fragezeichenfolge ??? 43 an und schläfst sofort ein.",
        "alibi": "An der Treppe siehst du [B] gerade zum Fenster schauend. Als du oben im Flur ankommst, läuft [G] an dir vorbei und öffnet eine Zimmertür."
    },
    5: {  # E "Arbeiten im Zimmer"
        "nacht": "Du verbringst den späten Abend damit, Dinge zu sortieren, Mails zu beantworten oder Dateien zu ordnen. Gegen Mitternacht wirst du müde und legst dich hin. Noch schnell die Drei Fragezeichen ??? Folge 86 angemacht und sofort schläfst du ein.",
        "alibi": "Bevor du in dein Zimmer gehst, siehst du [G] mit nassen Haaren die Treppe hochkommend. Kurz danach läuft [J] an dir vorbei, sich dabei die Schuhe ausziehend."
    },
    6: {  # F - "Letzter Smalltalk"
        "nacht": "Du triffst auf dem Weg ins Zimmer noch jemanden, wechselst ein paar Worte und gehst dann weiter. Schließlich verschwindest du in deinem Zimmer.",
        "alibi": "Du siehst [C] schläfrig aufs Zimmer zusteuernd. Außerdem kommt dir [H] entgegen, Notizen unter dem Arm tragend."
    },
    7: {  # G - "Badezimmer-Selfie-Session"
        "nacht": "Du verbringst noch etwas Zeit im Bad oder vor dem Spiegel, filmst dich oder machst Fotos. Danach gehst du zurück Richtung Zimmer.",
        "alibi": "Auf dem Rückweg begegnet dir [D] gerade die Zimmertür aufschließend. Vor der Treppe siehst du [E] mit müdem Blick hochgehend."
    },
    8: {  # H - "Arbeiten an Notizen"
        "nacht": "Im Zimmer schreibst du ein paar Gedanken auf, sortierst deine Ideen und bereitest dich mental auf den nächsten Tag vor.",
        "alibi": "Auf dem Flur siehst du [F] gerade den Gang entlanggehend. Kurz darauf kommt dir [I] entgegen, still vor sich hin summend."
    },
    9: {  # I - "Glas Wein & Ritual"
        "nacht": "Du gönnst dir ein Glas Wein oder Tee, legst ein kleines Schmuckstück oder Erinnerungsstück auf das Bett und versinkst in deinen Gedanken.",
        "alibi": "Auf dem Weg zurück zum Zimmer begegnest du [H] noch Notizen in der Hand haltend. Kurz darauf kommt dir [J] entgegen, die Treppe hochsteigend."
    },
    10: {  # J - "Musik & Handy-Scrollen"
        "nacht": "Du hörst Musik, scrollst durch dein Handy und siehst dir die Aufnahmen des Abends an. Schließlich wirst du müde und legst dich hin. Noch schnell die Drei Fragezeichen ??? Folge 62 angemacht und schon schläfst du ein.",
        "alibi": "An der Treppe siehst du [E] müde die Stufen nehmend. Im Flur siehst du [I] leise summend ins Zimmer gehend."
    }
}

# Texte für Werwolf und Unschuldige
WEREWOLF_TEXT_TEMPLATE = """
<div class="innocent-info">
    <h2>⚠️ Deine Rolle</h2>

    <div style="margin-top: 20px;">
        {abendverlauf}
    </div>

    <div style="margin-top: 20px; padding: 15px; background: #2c3e50; border-radius: 5px;">
        <p><strong style="color: #e74c3c;">Du bist der Werwolf.</strong></p>

        <p>Du wusstest es bereits seit deiner Einladung, du kennst jedes dieser Daten auswendig und doch hast du die Einladung angenommen. Du hättest auch bei der Wahl des Zimmers darauf achten können oder die Vorhänge zuziehen als du dich ins Bett gelegt hast - hast du aber nicht und das obwohl es genau hier vor 3 Jahren schonmal passiert ist.</p>

        <p>Während du schläfst, trifft ein kurzer Moment des klaren Vollmondlichts durch das leichte Schneetreiben dein Zimmer. Es reicht – dein Körper verändert sich.</p>

        <p>Du stehst auf und trittst auf den Balkon, da passiert es, du verwandelst dich und merkst wie du teilweise nicht mehr Herr deiner Sinne bist. Du wirst zum Werwolf!</p>

        <p>Dieses Wesen ist schnell, stark und tödlich – aber nur solange der Mond dich direkt trifft.</p>

        <p>Der Mond beleuchtet die Szenerie vor dir. Schneetreiben, der Bach und der Wald dahinter der sich meilenweit erstreckt. Du springst vom Balkon im ersten Stock in den Schnee und gehst Richtung Wald. Doch plötzlich triffst du auf <strong>{victim_name}</strong>.</p>

        {motive_text}

        <p>Das Opfer schreit laut auf als es sein Schicksal als besiegelt sieht. Der Mord geschieht in einem einzigen, brutalen Augenblick:</p>

        <p style="text-align: center; font-weight: bold; margin: 15px 0;">ein extrem starker stumpfer Schlag gegen die Brust</p>

        <p>Rippen brechen, eine davon durchstößt das Herz, der Tod tritt sofort ein.<br>
        In deinem Rausch wirfst du den leblosen Körper nach oben – er landet über einem Ast in zwei Metern Höhe, wo er hängen bleibt.</p>

        <p>Es ist schon wieder passiert - kurz kommt dein menschliches Wesen in dir zurück und dir wird klar, den Schrei muss jemand gehört. Du musst unbemerkt in dein Zimmer - so schnell wie möglich. Du bewegst dich mit übermenschlicher Geschwindigkeit zurück:</p>

        <ul style="margin-left: 20px;">
            <li>deine gigantischen, barfüßigen Abdrücke (Schuhgröße 49) führen bis zum Bach</li>
            <li>dort verlieren sie sich am/im Wasser</li>
            <li>du rennst stromabwärfs, Richtung Straße</li>
            <li>und gelangst über die Hotelfassade wieder auf deinen 2. Balkon der in eine andere Himmelsrichtung zeigt - zum Glück hast du die Executive Suite bekommen ;)</li>
        </ul>

        <p>In diesem Moment hörst du einen weiteren Schrei draußen – die Hausdame hat die Leiche gefunden.</p>

        <p>Sobald du das Innere erreichst, verschwindet die Verwandlung – glücklicherweise ziehen gerade die Wolken auf und verdecken den Mond. Du hast heute keine weitere Verwandlung mehr zu befürchten.</p>

        <p>Nun nochmal Geschrei und aufgeregte Stimmen im Flur als sich alle Richtung Foyer bewegen auch du ziehst dich schnell an und bewegst dich aus dem Zimmer mit den restlichen Leuten ins Foyer.</p>

        <p style="font-weight: bold; margin-top: 20px;">Niemand hat dich gesehen.<br>
        Niemand weiß, dass du es warst.<br>
        Bestreite immer alles - es gibt keine klaren Beweise! Oder doch?</p>
    </div>
</div>
"""

INNOCENT_TEXT_TEMPLATE = """
<div class="innocent-info">
    <h2>✓ Deine Rolle</h2>

    <div style="margin-top: 20px;">
        {abendverlauf}
    </div>

    <div style="margin-top: 20px; padding: 15px; background: #2c3e50; border-radius: 5px;">
        <p>Du schläfst fest, während draußen der Schneesturm stärker wird.<br>
        Den ersten Schrei bekommst du nicht mit – der Wind ist zu laut, der Schlaf zu tief.</p>

        <p>Doch du hast einen seltsamen Traum:</p>

        <div style="background: #34495e; padding: 15px; margin: 15px 0; border-left: 4px solid #3498db; font-style: italic;">
            {dream_text}
        </div>

        <p>Erst als ein zweiter, panischer Schrei aus der Nähe der Empfangshalle ertönt, reißt es dich aus dem Schlaf.<br>
        Du fühlst dich merkwürdig unruhig, als hättest du schlecht geträumt - hast du ja auch.</p>

        <p>Ohne weiter nachzudenken ziehst du dich schnell an und machst dich auf den Weg nach unten, um herauszufinden, was passiert ist.</p>
    </div>
</div>
"""

# Traum-Texte für jeden Charakter (für alle Unschuldigen in Phase 3)
DREAM_TEXTS = {
    1: "Du träumst, dass du durch einen langen Hotelkorridor gehst. Hinter jeder Tür hörst du Stimmen deiner früheren Klienten, die deinen Namen flüstern. Je weiter du gehst, desto lauter werden sie. Am Ende öffnest du eine Tür – aber dahinter ist nur ein leerer, kalter Wald.",
    2: "Du siehst vor dir einen riesigen Serverraum, aber alle Bildschirme zeigen nur Schneerauschen. Zwischen den Regalen hörst du Schritte. Du rennst los, doch jedes Mal, wenn du eine Ecke erreichst, ist dein Weg blockiert – von nichts als dichter, grauer Nebel.",
    3: "Du sitzt bei einer Bürgerversammlung, aber alle Menschen haben verschwommene Gesichter. Jemand stellt dir eine Frage, doch du verstehst kein Wort. Die Menge rückt näher, lautlos, bis dich ein heller Lichtstrahl blendet und du allein in einem verschneiten Tal stehst.",
    4: "Du stehst in einer alten Kapelle. Kerzen brennen, doch keine spendet Wärme. Eine Orgel spielt leise Töne, die du nicht kennst. Als du näher trittst, siehst du einen geöffneten Beichtstuhl – darin sitzt niemand, aber die Tür schwingt langsam hin und her.",
    5: "Du stehst auf einer Bühne, aber der Saal ist komplett dunkel. Du hörst Applaus, doch jedes Mal, wenn du ins Licht trittst, verstummt er sofort. Als du ein letztes Mal die Hand hebst, bricht plötzlich ein kalter Wind durch den Raum und löscht alles aus.",
    6: "Du stehst in einem Behandlungszimmer, doch statt Patienten liegen dort verschneite Äste auf der Liege. Du willst sie berühren, aber sie zerfallen zu Frost. Aus der Ferne hörst du einen Herzmonitor, doch der Rhythmus ist unnatürlich schnell – bis er abrupt stoppt.",
    7: "Du wanderst über eine Mondlicht-helle Schneefläche. Über dir dreht sich ein riesiges, silbriges Rad wie eine Uhr. Die Zeit springt unregelmäßig, vor und zurück, und jedes Mal stehst du an einem anderen Ort – immer wieder vor derselben verschlossenen Holztür.",
    8: "Du stehst auf einem perfekten Golfplatz. Als du zum Abschlag ansetzt, verwandelt sich das Fairway plötzlich in eine endlose Schneelandschaft. Der Ball rollt weit weg, immer schneller, bis er in einem dunklen Loch verschwindet. Als du hineinsiehst, ist dort nur Leere.",
    9: "Du läufst durch einen stillen Wald. Der Schnee fällt lautlos und dämpft jeden Schritt. Doch plötzlich hörst du hinter dir knackende Äste, als würde etwas Großes durch das Unterholz streifen. Du drehst dich um – aber der Wald ist vollkommen leer.",
    10: "Du sitzt vor einer endlosen Reihe von Dokumenten, Sprachen mischen sich ineinander, Schriftzeichen flackern. Als du versuchst, einen Satz zu übersetzen, löst er sich in Schnee auf. Ein einzelnes Wort bleibt zurück, aber du kannst es nicht lesen."
}

MOTIVE_MATRIX = {
    1: {
        "Elise Montandon": "Reiche Witwe – perfektes Erpressungsopfer, möglicherweise gefährlich für Vincent.",
        "Dimitri Volkov": "Dimitri könnte Vincents Manipulation gegenüber Elise entdeckt haben."
    },
    2: {
        "Viktor Bergmann": "Wenn Viktor ihre KI-Pilotierung ablehnt, steht ihre Firma vor dem Aus.",
        "Dimitri Volkov": "Dimitri könnte verhindern, dass Investorengelder in ihr Unternehmen fließen."
    },
    3: {
        "Viktor Bergmann": "Viktor könnte ihre veruntreuten Gelder öffentlich machen.",
        "Elise Montandon": "Elise könnte gegen ihre Gemeindepolitik auftreten und ihr Image ruinieren.",
    },
    4: {
        "Elise Montandon": "Antonio könnte sie als Symbol für Dekadenz/Sünde sehen.",
        "Jonas Reber": "Jonas’ Filmen könnte Antonio kompromittieren oder lächerlich darstellen."
    },
    5: {
        "Viktor Bergmann": "Viktor bezahlt sie nicht fair für Promo oder nutzt sie aus.",
        "Elise Montandon": "Elise behandelt sie herablassend – starker emotionaler Trigger.",
        "Jonas Reber": "Jonas sabotiert ihre Aufnahmen oder konkurriert um Aufmerksamkeit."
    },
    6: {
        "Viktor Bergmann": "Verdacht, dass Viktor den Vorfall von vor 3 Jahren vertuschte.",
        "Helga Baumgartner": "Helga weiß mehr über den damaligen Todesfall und schweigt.",
        "Elise Montandon": "Verbindung der Montandon-Familie zu früheren Todesfällen im Hotel."
    },
    7: {
        "Viktor Bergmann": "Sie sieht ihn in Verantwortung für die ?dunkle Vergangenheit? des Hotels.",
        "Elise Montandon": "Lunas Familie macht Elise für die Tragödie von 1952 mitverantwortlich."
    },
    8: {
        "Viktor Bergmann": "Viktor könnte seinen geplanten Golfplatz stoppen.",
        "Dimitri Volkov": "Max könnte Dimitri Geld schulden oder sich bedroht fühlen."
    },
    9: {
        "Viktor Bergmann": "Hotelprojekte zerstören die Natur seines Reviers.",
        "Jonas Reber": "Jonas’ Müll (z.B. Fritteuse) im Wald verärgert Tom massiv.",
        "Dimitri Volkov": "Dimitri steht für große Eingriffe in Naturschutzgebiete."
    },
    10: {
        "Dimitri Volkov": "Maria könnte im Auftrag eines Geheimdienstes handeln.",
        "Viktor Bergmann": "Viktor könnte in fragwürdige Geschäfte verwickelt sein, die Maria kennt."
    }
}

DEFAULT_MOTIVE_TEXT = (
    "Man hat dich gesehen, du weißt nicht was du tun sollst, kurz schaut ihr euch starr vor Schreck in die Augen. "
    "Dann übernehmen deine Instinkte und du schlägst mit voller Wucht zu."
)


# Phase-4-Text für Aufwachende (die beim ersten Schrei aufwachen)
AWAKENING_TEXT_TEMPLATE = """
<div class="awakening-info" style="background: #34495e; padding: 20px; border-radius: 8px; margin: 20px 0;">
    <h2 style="color: #e74c3c;">🌙 Du wachst auf beim ersten Schrei</h2>
    <p>Während du schläfst, beginnt draußen der Wind stärker zu werden. Plötzlich – irgendwo in der Ferne – hörst du einen kurzen, erstickten Schrei, gefolgt von einem dumpfen Schlag.</p>

    <p>Durch das Schneetreiben ist das Geräusch schwer einzuordnen, und der Wind wirft es chaotisch gegen die Fassade. Du bist dir nicht sicher, ob du es dir eingebildet hast.</p>

    <p>Du drehst dich um, versuchst wieder einzuschlafen… aber du hast einen seltsamen Traum:</p>

    <div style="background: #2c3e50; padding: 15px; margin: 15px 0; border-left: 4px solid #e74c3c; font-style: italic;">
        {dream_text}
    </div>

    <p><strong>Nach wenigen Minuten hörst du erneut etwas:</strong> ein panischer, klarer Schrei aus der Nähe der Empfangshalle. Jetzt ist klar: irgendetwas ist passiert.</p>

    <p>Du stehst auf, ziehst dich hastig an und machst dich auf den Weg nach unten, um herauszufinden, was los ist.</p>
</div>
"""

# ============================================================================
# SPIELZUSTAND (wird im Session gespeichert oder als globale Variable)
# ============================================================================

game_state = {
    "werewolf_id": None,        # ID des Werwolfs
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
    "voting_complete": False,    # Phase 5: True wenn alle abgestimmt haben
    "runoff_active": False,      # True wenn Stichwahl läuft
    "runoff_candidates": [],     # IDs der Kandidaten in der Stichwahl
    "runoff_round": 0            # Stichwahl-Runde (0=normal, 1=erste Stichwahl, 2=zweite, etc.)
}

# ============================================================================
# HILFSFUNKTIONEN
# ============================================================================

def get_character_by_slug(slug):
    """Gibt den Charakter anhand des URL-Slugs oder des zugewiesenen Buchstabens zurück."""
    for char in CHARACTERS:
        if char["url_slug"] == slug:
            return char

    # Erlaube außerdem Zugriffe wie /player/spieler-c, wobei der Buchstabe zufällig zugewiesen wurde.
    letter_mapping = game_state.get("letter_mapping", {})
    if slug.startswith("spieler-"):
        letter_part = slug.split("spieler-", 1)[1].strip().upper()
        if len(letter_part) == 1:
            for char in CHARACTERS:
                if letter_mapping.get(char["id"]) == letter_part:
                    return char

    return None

def select_random_characters(num_players):
    """Wählt zufällig num_players Charaktere aus der Liste aus"""
    return random.sample(CHARACTERS, num_players)

def assign_random_letters(characters):
    """
    Weist jedem Charakter zufällig einen Buchstaben A-J zu.
    Gibt ein Dictionary zurück: {char_id: "A", ...}
    """
    available_letters = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J"]
    selected_letters = random.sample(available_letters, len(characters))

    letter_mapping = {}
    for i, char in enumerate(characters):
        letter_mapping[char["id"]] = selected_letters[i]

    return letter_mapping

def get_player_slug(character, letter_mapping):
    """Ermittelt den passenden Player-Slug anhand des zugewiesenen Buchstabens."""
    assigned_letter = letter_mapping.get(character["id"])
    if assigned_letter:
        return f"spieler-{assigned_letter.lower()}"
    return character["url_slug"]

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
        game_state["final_verdict_correct"] = (winner_id == game_state["werewolf_id"])

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

def select_werewolf(characters, seed_tuple, victim):
    """Wählt deterministisch-zufällig einen Werwolf mit Gewichtung basierend auf Motiven"""
    # Seed basierend auf Event-Charakteren setzen
    seed_value = hash(seed_tuple)
    random.seed(seed_value)

    # Gewichte berechnen basierend auf MOTIVE_MATRIX
    weights = []
    for char in characters:
        victim_name = victim.get("name") if isinstance(victim, dict) else str(victim)
        has_motive = victim_name in MOTIVE_MATRIX.get(char["id"], {})

        # Charaktere mit Motiv bekommen Gewicht 2, ohne Motiv Gewicht 1
        weights.append(2 if has_motive else 1)

    # Gewichtete Auswahl
    werewolf = random.choices(characters, weights=weights, k=1)[0]
    random.seed()  # Seed zurücksetzen
    return werewolf["id"]

def select_random_victim(seed_tuple):
    """Wählt deterministisch-zufällig eines der drei NPCs als Mordopfer basierend auf dem Event-Seed"""
    victims = list(NPCS.values())
    seed_value = hash(seed_tuple)
    random.seed(seed_value)
    victim = random.choice(victims)
    random.seed()  # Seed zurücksetzen
    return victim

def select_awakeners(active_characters, werewolf_id):
    """
    Wählt zufällig 2-3 Personen aus, die beim ersten Schrei aufwachen.
    Der Werwolf wird ausgeschlossen.
    """
    # Alle außer dem Werwolf
    innocents = [char for char in active_characters if char["id"] != werewolf_id]

    # Zufällig 2 oder 3 auswählen (falls genug Spieler vorhanden)
    max_awakeners = min(3, len(innocents))
    min_awakeners = min(2, max_awakeners)
    num_awakeners = random.randint(min_awakeners, max_awakeners)
    awakeners = random.sample(innocents, num_awakeners)

    return [char["id"] for char in awakeners]

def determine_victim(first_event2, first_event1, first_event3, seed_tuple):
    """
    Bestimmt das Opfer basierend auf der Matrix:
    1. Erstes Ereignis 2 (Küchenhilfe) → Jonas Reber (Koch)
    2. Sonst: Erstes Ereignis 1 (Klo) → Viktor Bergmann (Hotelier)
    3. Sonst: Erstes Ereignis 3 (Alkohol) → Dimitri Volkov (Investor)
    4. Sonst: Deterministisch-zufälliges Opfer basierend auf Event-Seed
    """
    if first_event2 is not None:
        return NPCS["kueche"]
    elif first_event1 is not None:
        return NPCS["klo"]
    elif first_event3 is not None:
        return NPCS["alkohol"]
    else:
        return select_random_victim(seed_tuple)

def get_character_by_id(char_id):
    """Gibt den Charakter mit der angegebenen ID zurück"""
    for char in CHARACTERS:
        if char["id"] == char_id:
            return char
    return None

def generate_motive_text(werewolf_id, victim):
    """Gibt den passenden Motivsatz f?r Werwolf und Opfer zur?ck."""
    if not victim:
        return f"<p>{DEFAULT_MOTIVE_TEXT}</p>"

    victim_name = victim.get("name") if isinstance(victim, dict) else str(victim)
    motive_sentence = MOTIVE_MATRIX.get(werewolf_id or 0, {}).get(victim_name)

    if motive_sentence:
        return f"<p><strong>Motiv:</strong> {motive_sentence}</p>"

    return f"<p>{DEFAULT_MOTIVE_TEXT}</p>"

def build_phase5_outcome_text(accused_char, letter_mapping, is_correct, victim):
    """Erstellt den Phase-5-Text basierend auf der Entscheidung."""
    if not accused_char or is_correct is None:
        return None

    assigned_letter = letter_mapping.get(accused_char["id"], accused_char["letter"])
    accused_display = f"{accused_char['name']} [{assigned_letter}]"

    # Bestimme, wer die Abstimmung einfordert (Hotelbesitzer oder falls tot, der Investor)
    if victim and victim.get("name") == "Viktor Bergmann":
        speaker = "Der russische Investor"
        speaker_lower = "der russische Investor"
    else:
        speaker = "Der Hotelbesitzer"
        speaker_lower = "der Hotelbesitzer"

    # Die dramatische Rede zur Abstimmung
    speech = f'''
    <p><strong>{speaker} steht auf.</strong></p>
    <p>„Genug. Es reicht."</p>
    <p>Er lässt den Blick über die Runde wandern, als wolle er sich jeden Einzelnen genau einprägen.</p>
    <p>„Ich weiß nicht, was heute Nacht passiert ist… aber ich weiß eines: Hier drin sitzt jemand, der uns alle in Gefahr gebracht hat. Und ich werde nicht zulassen, dass das nochmal passiert."</p>
    <p>Er ballt die Hände, zwingt sich aber, die Stimme gleichmäßig zu halten.</p>
    <p>„Die Polizei rufen? Nein. Dafür ist es zu spät und außerdem kommt bei dem Wetter niemand hierher. Dafür ist zu viel auf dem Spiel. Dieser Ort darf nicht wieder in die Schlagzeilen. Nicht nach dem, was hier früher schon geschehen ist."</p>
    <p>Ein kurzes Schweigen. Dann:</p>
    <p>„Mir ist egal, wer es war. Mir ist egal, warum. Aber es endet heute Nacht. Hier. In diesem Raum."</p>
    <p>Er zeigt auf die Gruppe.</p>
    <p>„Ihr werdet jetzt abstimmen. Jede und jeder von euch weiß genug, um eine Entscheidung zu treffen. Schaut euch an, hört einander zu – und entscheidet. Wer von euch ist fähig gewesen, das zu tun?"</p>
    <p>Er tritt einen Schritt zurück, seine Stimme wird dunkler.</p>
    <p>„Ich verspreche euch: Ich kümmere mich danach persönlich um die Person, die ihr bestimmt. Auge um Auge. Zahn um Zahn."</p>
    <p>Noch ein tiefes Einatmen.</p>
    <p>„Also… wer ist es? Es wird Zeit, dass wir das Monster unter uns finden – bevor die Nacht noch jemanden verschlingt."</p>
    <hr style="margin: 20px 0; border: none; border-top: 1px solid #34495e;">
    <p>Als die Entscheidung gefallen ist, wird <strong>{accused_display}</strong> unruhig und blickt die Umstehenden flehentlich an. Da schreit {speaker_lower} auf: <em>„Nun gut, wir haben demokratisch entschieden: HÄNGT DEN MÖRDER!"</em></p>
    '''

    if is_correct:
        outcome = '''
        <p><strong>Nach wenigen Minuten ist alles vorbei.</strong></p>
        <p>Der Schrecken scheint endgültig besiegt und der Fluch des Hotels gebrochen. Alle nehmen das Geheimnis mit ins Grab und hoffen auf einen ruhigen Schlaf.</p>
        '''
    else:
        outcome = '''
        <p><strong>Nach wenigen Minuten ist alles vorbei.</strong></p>
        <p>Doch es war die falsche Person. Trotzdem schlafen alle den Schlaf der Gerechten – bis ein weiterer Schrei die vollmondhelle Nacht durchhallt.</p>
        '''

    html_content = f'''
    <div class="phase5-outcome" style="background: #2c3e50; padding: 20px; border-radius: 8px; margin-top: 25px;">
        <h3 style="margin-top: 0;">Phase 5 - Das Urteil</h3>
        {speech}
        {outcome}
    </div>
    '''

    return html_content


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

            # Opfer zuerst bestimmen (für gewichtete Werwolf-Auswahl)
            active_chars = game_state["active_characters"]
            victim = determine_victim(first_event2, first_event1, first_event3, seed_tuple)
            game_state["victim"] = victim

            # Werwolf mit Gewichtung basierend auf Motiv auswählen
            game_state["werewolf_id"] = select_werewolf(active_chars, seed_tuple, victim)
            game_state["awakeners"] = select_awakeners(active_chars, game_state["werewolf_id"])

            # Spiel ist jetzt bereit für Phase 3
            reset_voting_state()
            game_state["setup_phase"] = 2
            game_state["current_phase"] = 3  # Spieler können sich einloggen (Phase 3)
            game_state["game_started"] = True

            success = f"Phase 3 gestartet! Spieler können sich jetzt einloggen und ihre Rollen sehen."

        # Phasen-Wechsel für Spieler (3->4->5)
        elif action == 'change_phase':
            new_phase = request.form.get('phase', type=int)
            if new_phase and 3 <= new_phase <= 5:
                previous_phase = game_state.get("current_phase", 0)
                game_state["current_phase"] = new_phase
                if new_phase == 5 and previous_phase != 5:
                    reset_voting_state()
                success = f"Spielphase wurde auf {new_phase} geändert."
            else:
                error = "Ungültige Phase!"

        if error:
            session['admin_error'] = error
        if success:
            session['admin_success'] = success
        return redirect(url_for('admin'))

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

    # Prüfen, ob dieser Charakter beim ersten Schrei aufwacht
    is_awakener = character["id"] in game_state.get("awakeners", [])

    # Buchstaben-Mapping holen
    letter_mapping = game_state.get("letter_mapping", {})

    # Zugewiesenen Buchstaben für diesen Charakter holen
    assigned_letter = letter_mapping.get(character["id"], character["letter"])

    # Phase-3-Texte holen und Platzhalter ersetzen
    phase3_raw = PHASE3_TEXTS.get(character["id"], {
        "nacht": "Keine Informationen verfügbar.",
        "alibi": "Keine Alibi-Information verfügbar."
    })

    active_chars = game_state.get("active_characters", [])

    phase3 = {
        "nacht": replace_letter_placeholders(phase3_raw["nacht"], letter_mapping, active_chars),
        "alibi": replace_letter_placeholders(phase3_raw["alibi"], letter_mapping, active_chars)
    }

    # Abendverlauf für alle erstellen
    abendverlauf = f"<p><strong>Dein Abend:</strong></p><p>{phase3['nacht']}</p><p>{phase3['alibi']}</p>"

    # Werwolf-Text mit Platzhaltern füllen
    werewolf_text = None
    innocent_text = None

    if is_werewolf:
        # Motiv-Text generieren
        motive_text = generate_motive_text(
            game_state["werewolf_id"],
            game_state["victim"]
        )

        # Werwolf-Text zusammensetzen
        werewolf_text = WEREWOLF_TEXT_TEMPLATE.format(
            abendverlauf=abendverlauf,
            victim_name=game_state["victim"]["name"],
            motive_text=motive_text
        )
    else:
        # Unschuldigen-Text mit Traumsequenz
        dream_text = DREAM_TEXTS.get(character["id"], "Du hast einen seltsamen, wirren Traum.")
        innocent_text = INNOCENT_TEXT_TEMPLATE.format(
            abendverlauf=abendverlauf,
            dream_text=dream_text
        )

    # Aufwach-Text für Phase 4 erstellen (falls Aufwachender)
    awakening_text = None
    if is_awakener and not is_werewolf:
        dream_text = DREAM_TEXTS.get(character["id"], "Du hast einen seltsamen, wirren Traum.")
        awakening_text = AWAKENING_TEXT_TEMPLATE.format(dream_text=dream_text)

    # Aktuelle Phase
    current_phase = game_state.get("current_phase", 0)

    # Phase 5: Prüfen ob dieser Spieler schon abgestimmt hat
    has_voted = character["id"] in game_state.get("votes", {})

    # Phase 5: Stichwahl-Informationen
    runoff_active = game_state.get("runoff_active", False)
    runoff_candidates = game_state.get("runoff_candidates", [])
    runoff_round = game_state.get("runoff_round", 0)

    return render_template('player.html',
                         character=character,
                         assigned_letter=assigned_letter,
                         is_werewolf=is_werewolf,
                         is_awakener=is_awakener,
                         victim=game_state["victim"],
                         phase3=phase3,
                         awakening_text=awakening_text,
                         current_phase=current_phase,
                         werewolf_text=werewolf_text,
                         innocent_text=innocent_text,
                         has_voted=has_voted,
                         voting_complete=game_state.get("voting_complete", False),
                         runoff_active=runoff_active,
                         runoff_candidates=runoff_candidates,
                         runoff_round=runoff_round,
                         active_characters=active_chars,
                         letter_mapping=letter_mapping)

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
        slug = get_player_slug(voter_char, game_state.get("letter_mapping", {}))
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
    game_state["werewolf_id"] = None
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

@app.route('/generate-qr-codes', methods=['POST'])
def generate_qr_codes():
    """Generiert QR-Codes als PNG-Dateien mit 300 DPI"""
    if not game_state["game_started"]:
        return redirect(url_for('admin'))

    # QR-Code-Ordner erstellen
    qr_dir = os.path.join(os.getcwd(), 'qr_codes')
    os.makedirs(qr_dir, exist_ok=True)

    # Nur f?r aktive Charaktere QR-Codes generieren
    active_chars = game_state.get("active_characters", CHARACTERS)
    letter_mapping = game_state.get("letter_mapping", {})

    # Verwende die lokale Netzwerk-IP statt request.host_url
    local_ip = get_local_ip()
    base_url = f"http://{local_ip}:9000/"

    for char in active_chars:
        assigned_letter = letter_mapping.get(char["id"], char["letter"])
        slug = get_player_slug(char, letter_mapping)
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

    active_chars = game_state.get("active_characters", CHARACTERS)
    letter_mapping = game_state.get("letter_mapping", {})
    player_links = []
    for char in active_chars:
        assigned_letter = letter_mapping.get(char["id"], char["letter"])
        slug = get_player_slug(char, letter_mapping)
        player_links.append({
            "character": char,
            "url": base_url + "player/" + slug,
            "assigned_letter": assigned_letter
        })

    return render_template('qr_codes.html', player_links=player_links)

# ============================================================================
# MAIN
# ============================================================================

if __name__ == '__main__':
    # Server starten (erreichbar im lokalen Netzwerk)
    app.run(host='0.0.0.0', port=9000, debug=True)
