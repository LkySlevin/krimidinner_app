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
        "nacht": "Du fühlst dich vom Tag erschöpft und gehst früh in dein Zimmer. Du räumst noch kurz etwas auf, sortierst deine Sachen und legst dich nach einem schnellen Blick aus dem Fenster ins Bett. Zum Einschlafen hörst du noch eine Folge der Drei Fragezeichen ???, die Nummer 87, die du so gern magst, auf Spotify.",
        "alibi": "Auf dem Flur, kurz bevor du dein Zimmer erreichst, siehst du [B] gerade aus dem Bad kommend. Wenige Sekunden später begegnet dir [C] mit einer Wasserflasche in der Hand Richtung Treppe gehend."
    },
    2: {  # B "Kurzes Fenster-Ritual"
        "nacht": "Du kommst gerade aus dem Gemeinschaftsbad. Bevor du ins Bett gehst, bleibst du einen Moment am Fenster stehen, beobachtest wie die Wolken ziehen und holst tief Luft. Danach gehst du auf dein Zimmer. Um besser einschlafen zu können, hörst du dir noch eine Folge der Drei Fragezeichen ??? 69 auf Spotify an.",
        "alibi": "Auf dem Weg siehst du [A] gerade im Zimmer verschwindend. Als du die Treppe erreichst, begegnet dir [D] die Stufen hinaufgehend."
    },
    3: {  # C "Zu viel gegessen"
        "nacht": "Du hast beim Dinner wohl etwas übertrieben und fühlst dich schwer. Im Zimmer schaltest du den Fernseher kurz ein, zappst durch, doch deine Augen fallen schnell zu.",
        "alibi": "Im Flur siehst du [A] die Tür hinter sich schließend. Kurz darauf kommt dir [F] entgegen, etwas in der Hand tragend – vielleicht ein Snack."
    },
    4: {  # D "Nachttee in der Lounge"
        "nacht": "Du nimmst dir in der Lounge noch einen Tee  und genießt einen Moment Ruhe. Danach gehst du Richtung Zimmer, stellst dir auf Spotify noch die Drei Fragezeichenfolge ??? 43, The Mystery of the Creep-Show Crooks, an und schläfst sofort ein.",
        "alibi": "An der Treppe siehst du [B] gerade zum Fenster schauend. Als du oben im Flur ankommst, läuft [G] an dir vorbei und öffnet eine Zimmertür."
    },
    5: {  # E "Arbeiten im Zimmer"
        "nacht": "Du verbringst den späten Abend damit, Dinge zu sortieren, Mails zu beantworten und Dateien zu ordnen. Gegen Mitternacht wirst du müde und legst dich hin. Noch schnell die Drei Fragezeichen ??? Folge 86, deine Lieblingsfolge, angemacht und sofort schläfst du ein.",
        "alibi": "Bevor du in dein Zimmer gehst, siehst du [G] mit nassen Haaren die Treppe hochkommend. Kurz danach läuft [J] an dir vorbei, sich dabei die Schuhe ausziehend."
    },
    6: {  # F - "Letzter Smalltalk"
        "nacht": "Du triffst auf dem Weg ins Zimmer noch jemanden, wechselst ein paar Worte und gehst dann weiter. Schließlich verschwindest du in deinem Zimmer.",
        "alibi": "Du siehst [C] schläfrig aufs Zimmer zusteuernd. Außerdem kommt dir [H] entgegen, Notizen unter dem Arm tragend."
    },
    7: {  # G - "Badezimmer-Selfie-Session"
        "nacht": "Du verbringst noch etwas Zeit im Bad vor dem Spiegel, filmst dich oder machst Fotos. Danach gehst du zurück Richtung Zimmer.",
        "alibi": "Auf dem Rückweg begegnet dir [D] gerade die Zimmertür aufschließend. Vor der Treppe siehst du [E] mit müdem Blick hochgehend."
    },
    8: {  # H - "Arbeiten an Notizen"
        "nacht": "Im Zimmer schreibst du ein paar Gedanken auf, sortierst deine Ideen und bereitest dich mental auf den nächsten Tag vor.",
        "alibi": "Auf dem Flur siehst du [F] gerade den Gang entlanggehend. Kurz darauf kommt dir [I] entgegen, still vor sich hin summend."
    },
    9: {  # I - "Glas Wein & Ritual"
        "nacht": "Du gönnst dir ein Glas Wein, legst ein kleines Erinnerungsstück auf das Bett und versinkst in deinen Gedanken.",
        "alibi": "Auf dem Weg zurück zum Zimmer begegnest du [H] noch Notizen in der Hand haltend. Kurz darauf kommt dir [J] entgegen, die Treppe hochsteigend."
    },
    10: {  # J - "Musik & Handy-Scrollen"
        "nacht": "Du hörst Musik, scrollst durch dein Handy und siehst dir die Aufnahmen des Abends an. Schließlich wirst du müde und legst dich hin. Noch schnell die Drei Fragezeichen ??? Folge 62 angemacht und schon schläfst du ein.",
        "alibi": "An der Treppe siehst du [E] müde die Stufen nehmend. Im Flur siehst du [I] leise summend ins Zimmer gehend."
    }
}

# Texte für Mörder Unschuldige
MURDER_TEXT_TEMPLATE = """
<div class="innocent-info">
    <h2>⚠️ Deine Rolle</h2>

    <div style="margin-top: 20px;">
        {abendverlauf}
    </div>

    <div style="margin-top: 20px; padding: 15px; background: #2c3e50; border-radius: 5px;">
        <p><strong style="color: #e74c3c;">Du bist der Mörder.</strong></p>

        <p>Du wusstest es bereits seit deiner Einladung, du kennst jedes dieser Daten auswendig und doch hast du die Einladung angenommen. Du hättest auch bei der Wahl des Zimmers darauf achten können oder die Vorhänge zuziehen als du dich ins Bett gelegt hast - hast du aber nicht und das obwohl es genau hier vor 3 Jahren schonmal passiert ist.</p>

        <p>Während du schläfst, trifft ein kurzer Moment des klaren Vollmondlichts durch das leichte Schneetreiben dein Zimmer. Es reicht – dein Körper verändert sich.</p>

        <p>Du stehst auf und trittst auf den Balkon, da passiert es, du verwandelst dich und merkst wie du teilweise nicht mehr Herr deiner Sinne bist. Du wirst zum Werwolf!</p>

        <p>Dieses Wesen ist schnell, stark und tödlich – aber nur solange der Mond dich direkt trifft.</p>

        <p>Der Mond beleuchtet die Szenerie vor dir. Schneetreiben, der Bach und der Wald dahinter der sich meilenweit erstreckt. Du legst deine nun zu kleine Kleidung ab und springst vom Balkon im ersten Stock in den Schnee und gehst Richtung Wald. Doch plötzlich triffst du auf <strong>{victim_name}</strong>.</p>

        {motive_text}

        <p>Das Opfer schreit laut auf als es sein Schicksal als besiegelt sieht. Der Mord geschieht in einem einzigen, brutalen Augenblick:</p>

        <p style="text-align: center; font-weight: bold; margin: 15px 0;">ein extrem starker stumpfer Schlag gegen die Brust</p>

        <p>Rippen brechen, eine davon durchstößt das Herz, der Tod tritt sofort ein.<br>
        In deinem Rausch wirfst du den leblosen Körper nach oben – er landet über einem Ast in zwei Metern Höhe, wo er hängen bleibt.</p>

        <p>Es ist schon wieder passiert - kurz kommt dein menschliches Wesen in dir zurück und dir wird klar, den Schrei muss jemand gehört. Du musst unbemerkt in dein Zimmer - so schnell wie möglich. Du bewegst dich mit übermenschlicher Geschwindigkeit zurück:</p>

        <ul style="margin-left: 20px;">
            <li>deine gigantischen, barfüßigen Abdrücke (Schuhgröße 49) führen bis zum Bach</li>
            <li>dort verlieren sie sich am/im Wasser</li>
            <li>du rennst stromabwärts, Richtung Straße</li>
            <li>und gelangst über die Hotelfassade wieder auf deinen 2. Balkon der in eine andere Himmelsrichtung zeigt - zum Glück hast du die Executive Suite bekommen ;)</li>
        </ul>

        <p>In diesem Moment hörst du einen weiteren Schrei draußen – die Hausdame hat die Leiche gefunden.</p>

        <p>Sobald du das Innere erreichst, verschwindet die Verwandlung – glücklicherweise ziehen gerade die Wolken auf und verdecken den Mond. Du hast heute keine weitere Verwandlung mehr zu befürchten.</p>

        <p>Nun nochmal Geschrei und aufgeregte Stimmen im Flur als sich alle Richtung Foyer bewegen auch du ziehst dich schnell an und bewegst dich aus dem Zimmer mit den restlichen Leuten ins Foyer.</p>

        <p style="font-weight: bold; margin-top: 20px;">Niemand hat dich gesehen.<br>
        Niemand weiß, dass du es warst.<br>
        Bestreite immer alles - es gibt keine eindeutigen Beweise! Oder doch?</p>
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
        "Dimitri Volkov": "Dimitri könnte über Elise von deiner Betrugsmasche erfahren haben. Du gehst kein Risiko ein."
    },
    2: {
        "Viktor Bergmann": "Viktor hat deine KI-Pilotierung abgelehnt, deine Firma steht vor dem Aus. Dann muss er halt mit seinem Leben bezahlen.",
    },
    3: {
        "Dimitri Volkov": "Dimitri könnte deine veruntreuten Gelder öffentlich machen - er weiß zuviel.",
    },
    4: {
        "Jonas Reber": "Jonas Filme können dich wenn sie online gehen kompromittieren oder lächerlich darstellen. Der Herr wird es verstehen."
    },
    5: {
        "Viktor Bergmann": "Viktor bezahlt dich nicht fair für Promo und hat dich ausgenutzt. Du zeigst ihm, was du davon hältst.",
        "Jonas Reber": "Jonas hat versucht dir Follower abzuluchsen - das muss er mit dem Leben bezahlen."
    },
    6: {
        "Jonas Reber": "Jonas hat dir heute schon wieder den Vorwuf gemacht am Tod seines Vaters Schuld gehabt zu haben. Genug ist genug.",
    },
    7: {
        "Viktor Bergmann": "Du siehst ihn in Verantwortung für den Tod ihres Vaters und Tante damals im Jahr 1991.",
        "Jonas Reber": "Jonas kocht zu selten mit Bio-Zutaten und zu wenige vegetarische Gerichte. Mit Leuten wie ihm geht die Welt den Bach runter."
    },
    8: {
        "Viktor Bergmann": "Viktor interessiert sich nicht nur nicht für deinen Golfplatz - er hat sich auch lächerlich über deine Abschlagweite gemacht. Mal sehen was er von diesem Schlag hält!",
        "Dimitri Volkov": "Du schuldest ihm immernoch eine Menge Geld, was du ihm wohl nie zurückzahlen kannst."
    },
    9: {
        "Jonas Reber": "Jonas Müll (z.B. Fritteuse) im Wald verärgert dich massiv. Solche Leute gehören bestraft.",
        "Dimitri Volkov": "Dimitri steht für große Eingriffe in Naturschutzgebiete. Er muss gestoppt werden."
    },
    10: {
        "Dimitri Volkov": "Er weiß über den KGB über deine Machenschaften Bescheid. Ein Gehemnis das er mit ins Grab nehmen wird.",
        "Viktor Bergmann": "Du hast noch einmal recherchiert, Viktor hat mehr Dreck am Stecken als gedacht. Zeit, dass jemand ihm eine Lektion erteilt."
    }
}

DEFAULT_MOTIVE_TEXT = (
    "Man hat dich gesehen, du weißt nicht was du tun sollst, kurz schaut ihr euch starr vor Schreck in die Augen. "
    "Dann übernehmen deine Instinkte und du schlägst mit voller Wucht zu."
)

# Spezielle Traumtext-Suffixe für besondere Rollen
DESPERATE_DREAM_SUFFIX = """

<div style="background: #8b0000; padding: 20px; margin: 20px 0; border-radius: 8px; border: 2px solid #ff0000;">
    <p style="color: #ffff00; font-weight: bold; font-size: 1.2em;">⚠️ TRIGGERWARNUNG: Suizidgedanken ⚠️</p>

    <p style="color: #ffffff;">Als du aus dem Traum erwachst, überkommt dich eine tiefe Verzweiflung. Dein ganzes Leben lang hattest du Pech – immer wieder Rückschläge, Enttäuschungen, verlorene Chancen. Und jetzt dieser Traum, der dir den letzten Lebenssinn nimmt.</p>

    <p style="color: #ffffff;">Ein dunkler Gedanke formt sich in deinem Kopf: <em>Was, wenn das die Gelegenheit ist, allem ein Ende zu setzen?</em></p>

    <p style="color: #ffffff; font-weight: bold;">🎯 DEIN GEHEIMES ZIEL: Du willst als Mörder identifiziert werden. Wenn die Gruppe dich beschuldigt, akzeptierst du es – es ist ein Ausweg, den du unbewusst suchst.</p>

    <div style="background: #ffffff; padding: 15px; margin-top: 20px; border-radius: 5px; color: #000000;">
        <p style="font-weight: bold; margin-bottom: 10px;">📞 WICHTIG - Wenn du selbst Hilfe brauchst:</p>
        <p style="margin: 5px 0;"><strong>Telefonseelsorge Deutschland:</strong></p>
        <p style="margin: 5px 0;">☎ 0800 / 111 0 111 (evangelisch)</p>
        <p style="margin: 5px 0;">☎ 0800 / 111 0 222 (katholisch)</p>
        <p style="margin: 5px 0;"><strong>24 Stunden erreichbar, kostenlos & anonym</strong></p>
        <p style="margin-top: 10px;"><strong>Schweiz:</strong> ☎ 143</p>
        <p style="margin: 5px 0;"><strong>Österreich:</strong> ☎ 142</p>
    </div>
</div>
"""

INTRIGANT_DREAM_TEMPLATE = """

<div style="background: #2c2c2c; padding: 20px; margin: 20px 0; border-radius: 8px; border: 2px solid #ff8c00;">
    <p style="color: #ff8c00; font-weight: bold; font-size: 1.2em;">🎭 DEINE GEHEIME ROLLE: DER INTRIGANT</p>

    <p style="color: #ffffff;">Im Traum siehst du das Gesicht von <strong>{target_name}</strong> vor dir. Alle negativen Emotionen, die du jemals dieser Person gegenüber empfunden hast, kochen in diesem Moment hoch. Du kannst diese Person nicht leiden – vielleicht aus einem bestimmten Grund, vielleicht einfach nur so.</p>

    <p style="color: #ffffff;">Als du aufwachst, wird dir klar: <em>Bei der nächsten Gelegenheit schlage ich zu.</em></p>

    <p style="color: #ffffff; font-weight: bold;">🎯 DEIN GEHEIMES ZIEL: Hänge <strong>{target_name}</strong> den Mord an! Sammle Indizien, streue Gerüchte, lenke Verdächtigungen. Ob diese Person wirklich der Mörder ist oder nicht – es ist dir egal. Du willst {target_name} leiden sehen.</p>

    <p style="color: #cccccc; font-style: italic;">Hinweis: Falls {target_name} zufällig tatsächlich der Mörder ist, umso besser – dann erreichst du dein Ziel mit der Wahrheit.</p>
</div>
"""

LOVER_DREAM_TEMPLATE = """

<div style="background: #4a0e4e; padding: 20px; margin: 20px 0; border-radius: 8px; border: 2px solid #ff1493;">
    <p style="color: #ff1493; font-weight: bold; font-size: 1.2em;">💕 DEINE GEHEIME ROLLE: DER/DIE VERLIEBTE</p>

    <p style="color: #ffffff;">In deinem Traum erscheint <strong>{lover_name}</strong> – nicht bedrohlich, sondern warm, vertraut, anziehend. Ihr begegnet euch in einer verschneiten Landschaft, und plötzlich spürst du eine tiefe Verbundenheit, die du dir vorher nicht erklären konntest.</p>

    <p style="color: #ffffff;">Als der Traum endet, bleibt dieses Gefühl. Du weißt intuitiv: <em>{lover_name} hat das Gleiche geträumt.</em></p>

    <p style="color: #ffffff; font-weight: bold;">🎯 DEIN GEHEIMES ZIEL: Ihr beide müsst überleben! Schützt euch gegenseitig, lenkt Verdächtigungen von {lover_name} ab, kommuniziert subtil. Ob einer von euch der Mörder ist oder nicht – spielt keine Rolle. Ihr gehört zusammen.</p>

    <p style="color: #ffb3d9; font-style: italic;">Hinweis: Suche heute Vormittag nach Gelegenheiten, mit {lover_name} zu sprechen. Ein Blick, eine Geste – ihr werdet euch verstehen.</p>
</div>
"""


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
    Die Auswahl ist nicht Seed-basiert, sondern bei jedem Spielstart neu zufällig.
    """
    # Alle außer dem Mörder
    innocents = [char for char in active_characters if char["id"] != murder_id]

    # Sicherstellen, dass genug Spieler vorhanden sind (mindestens 5 für alle Rollen)
    if len(innocents) < 5:
        return None, None, None, []

    # Mische die Unschuldigen (echt zufällig, kein Seed)
    available = innocents.copy()
    random.shuffle(available)

    # 1. Intrigant + Ziel auswählen
    intrigant = available.pop(0)
    intrigant_target = available.pop(0)

    # 2. Verzweifelte Person auswählen
    desperate = available.pop(0)

    # 3. Verliebtes Paar auswählen (2 Personen)
    lover1 = available.pop(0)
    lover2 = available.pop(0)

    return intrigant["id"], intrigant_target["id"], desperate["id"], [lover1["id"], lover2["id"]]

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
        speaker = "Der russische Investor"
    else:
        speaker = "Der langjährige Hotelbesitzer"

    speech = f'''
    <div class="phase5-intro" style="background: #2c3e50; padding: 20px; border-radius: 8px; margin-top: 25px;">
        <h3 style="margin-top: 0;">Phase 5 - Die Anklage</h3>
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
        <p>„Wir stimmen geheim ab. Es wird Zeit, dass wir das Monster unter uns finden – bevor die Nacht noch jemanden verschlingt."</p>
    </div>
    '''
    return speech

def build_phase5_outcome_text(accused_char, letter_mapping, is_correct, victim):
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


    if is_correct:
        outcome = f'''
        <p>Doch so leicht gibt <strong>{accused_display}</strong> nicht auf und ruft: "Denkt ihr normalsterblichen ihr könntet einen Werwolf einfach erhängen?".
        Doch noch bevor es zu einem weiteren Wort oder Tumult kommen kann, knallt es Ohrenbetäubend laut. Ein greller Blitz durchzuckt den Raum und ein markerschütternder Schrei erfüllt die Luft.
        Helga hält die Flinte noch in der Hand aus dessen Lauf es raucht. Die Flinte war mit Silberkugeln geladen gewesen.</p>
        <p>Der Schrecken scheint endgültig besiegt und der Fluch des Hotels gebrochen. Alle nehmen das Geheimnis mit ins Grab und hoffen nun auf einen ruhigen Schlaf.</p>
        '''
    else:
        # Großschreibung für Satzanfang
        speaker_capitalized = speaker_lower.capitalize()
        outcome = f'''
        <p>{speaker_capitalized} schlägt <strong>{accused_display}</strong> mit einem Knüppel auf den Hinterkopf und zusammen mit den anderen Bediensteten wird <strong>{accused_display}</strong> mit einem Seil am selben Ast aufgehängt. <strong>Nach wenigen Minuten ist alles vorbei.</strong></p>
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


def get_personal_outcome(character_id, accused_id, murderer_id, letter_mapping):
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

    is_murderer = (character_id == murderer_id)
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
                failed_goals.append(f"🎯 <strong>Intrigant-Ziel verfehlt:</strong> {target_display} wurde nicht hingerichtet.")

    # === VERZWEIFELTE PERSON ===
    if is_desperate:
        if is_accused:
            achieved_goals.append("😔 <strong>Verzweifeltes Ziel erreicht:</strong> Du hast dein Ende gefunden. Möge deine Seele nun Frieden finden.")
        else:
            failed_goals.append("😔 <strong>Verzweifeltes Ziel verfehlt:</strong> Du lebst weiter, doch der innere Schmerz bleibt.")

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
        murderer_caught = (accused_id == murderer_id)

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
                accused_char, letter_mapping, is_correct, game_state.get("victim")
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

    # Mörder-Text mit Platzhaltern füllen
    murder_text = None
    innocent_text = None

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
        dream_text = DREAM_TEXTS.get(character["id"], "Du hast einen seltsamen, wirren Traum.")

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

        innocent_text = INNOCENT_TEXT_TEMPLATE.format(
            abendverlauf=abendverlauf,
            dream_text=dream_text + special_role_text
        )

    # Aufwach-Text für Phase 4 erstellen (falls Aufwachender)
    awakening_text = None
    if is_awakener and not is_murder:
        dream_text = DREAM_TEXTS.get(character["id"], "Du hast einen seltsamen, wirren Traum.")

        # Spezielle Rollen-Zusätze auch für Awakeners
        special_role_text = ""

        if character["id"] == game_state.get("intrigant_id"):
            target_char = get_character_by_id(game_state.get("intrigant_target_id"))
            if target_char:
                target_name = target_char["name"]
                special_role_text += INTRIGANT_DREAM_TEMPLATE.format(target_name=target_name)

        if character["id"] == game_state.get("desperate_id"):
            special_role_text += DESPERATE_DREAM_SUFFIX

        if character["id"] in game_state.get("lovers", []):
            lovers = game_state.get("lovers", [])
            other_lover_id = [lid for lid in lovers if lid != character["id"]][0]
            other_lover = get_character_by_id(other_lover_id)
            if other_lover:
                lover_name = other_lover["name"]
                special_role_text += LOVER_DREAM_TEMPLATE.format(lover_name=lover_name)

        awakening_text = AWAKENING_TEXT_TEMPLATE.format(dream_text=dream_text + special_role_text)

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
            accused_char, letter_mapping, is_correct, game_state["victim"]
        )

        # Generiere persönliche Erfolgsmeldung für diesen Spieler
        personal_outcome_success, personal_outcome_message = get_personal_outcome(
            character["id"],
            game_state["final_accused_id"],
            game_state["murder_id"],
            letter_mapping
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
                         personal_outcome_message=personal_outcome_message)

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

    active_chars = game_state.get("active_characters", CHARACTERS)
    letter_mapping = game_state.get("letter_mapping", {})
    player_links = []
    for char in active_chars:
        assigned_letter = letter_mapping.get(char["id"], char["letter"])
        slug = get_player_slug(char)
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
