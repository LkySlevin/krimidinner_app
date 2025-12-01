#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Krimidinner - Datenstrukturen
Enthält alle Charaktere, NPCs, Motive und Clues
"""

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
    "H": {"name": "Jonas, der Koch,", "tag": "Koch"},
    "I": {"name": "Helga, die Hausdame,", "tag": "Hausdame"},
    "J": {"name": "Viktor Bergmann, der Hotelier", "tag": "Hotelier"}
}

# Motiv-Matrix: Wer hat gegen wen ein Motiv
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
        "Jonas Reber": "Jonas' Filme können dich, wenn sie online gehen, kompromittieren oder lächerlich darstellen. Der Herr wird es verstehen."
    },
    5: {
        "Viktor Bergmann": "Viktor bezahlt dich nicht fair für Promo und hat dich ausgenutzt. Du zeigst ihm, was du davon hältst.",
        "Jonas Reber": "Jonas hat versucht dir Follower abzuluchsen - das muss er mit dem Leben bezahlen."
    },
    6: {
        "Jonas Reber": "Jonas hat dir heute schon wieder den Vorwurf gemacht, am Tod seines Vaters schuld gewesen zu sein. Genug ist genug.",
    },
    7: {
        "Viktor Bergmann": "Du siehst ihn in der Verantwortung für den Tod deines Vaters und deiner Tante damals im Jahr 1991.",
        "Jonas Reber": "Jonas kocht zu selten mit Bio-Zutaten und zu wenige vegetarische Gerichte. Mit Leuten wie ihm geht die Welt den Bach runter."
    },
    8: {
        "Viktor Bergmann": "Viktor interessiert sich nicht nur nicht für deinen Golfplatz - er hat sich auch lächerlich über deine Abschlagweite gemacht. Mal sehen was er von diesem Schlag hält!",
        "Dimitri Volkov": "Du schuldest ihm immer noch eine Menge Geld, die du ihm wohl nie zurückzahlen kannst."
    },
    9: {
        "Jonas Reber": "Jonas Müll (z.B. Fritteuse) im Wald verärgert dich massiv. Solche Leute gehören bestraft.",
        "Dimitri Volkov": "Dimitri steht für große Eingriffe in Naturschutzgebiete. Er muss gestoppt werden."
    },
    10: {
        "Dimitri Volkov": "Er weiß über den KGB von deinen Machenschaften. Ein Geheimnis, das er mit ins Grab nehmen wird.",
        "Viktor Bergmann": "Du hast noch einmal recherchiert, Viktor hat mehr Dreck am Stecken als gedacht. Zeit, dass jemand ihm eine Lektion erteilt."
    }
}

DEFAULT_MOTIVE_TEXT = (
    "Man hat dich gesehen, du weißt nicht was du tun sollst, kurz schaut ihr euch starr vor Schreck in die Augen. "
    "Dann übernehmen deine Instinkte und du schlägst mit voller Wucht zu."
)

# Mörder-Hinweise für zusätzliche Erinnerungen in Phase 4
MURDER_CLUES = [
    {
        "id": 1,
        "observation": "hat nur Fleisch gegessen",
        "detail": "Ich bemerkte, dass {subject_name} beim Hauptgang ausschließlich von den goldenen Schüsseln gegessen hat (Fleisch und Fisch). Die Schüsseln mit Gemüse hat {subject_name} komplett ignoriert."
    },
    {
        "id": 3,
        "observation": "ließ Gemüseschüssel fallen",
        "detail": "Als ich {subject_name} eine Schüssel mit Gemüse reichen wollte, ließ {subject_name} sie fallen wie eine heiße Kartoffel. {subject_name} murmelte eine Entschuldigung und orderte Personal zum Aufräumen herbei."
    },
    {
        "id": 4,
        "observation": "eigenes Besteck mitgebracht",
        "detail": "Ich sah, dass {subject_name} sein eigenes Besteck mitgebracht hatte. Auf meine Frage warum, meinte {subject_name}, ob ich nicht wüsste, wie häufig Keime über dreckiges Hotelbesteck verteilt werden."
    },
    {
        "id": 5,
        "observation": "war ungewöhnlich blass",
        "detail": "{subject_name} sah sehr blass aus, nachdem er die Suppe gegessen hatte. Ich fragte, ob es {subject_name} gut geht, aber {subject_name} meinte nur er sei gegen etwas in der Suppe allergisch."
    },
    {
        "id": 6,
        "observation": "hatte erweiterte Pupillen",
        "detail": "Als ich mit {subject_name} sprach, fielen mir die seltsam erweiterten Pupillen auf. Der Blick war irgendwie glasig und leer, so als hätte {subject_name} etwas eingenommen. War {subject_name} noch zurechnungsfähig?"
    },
    {
        "id": 7,
        "observation": "reagierte nervös auf Nachthimmel-Erwähnung",
        "detail": "Als jemand den schönen, sternenklaren Nachthimmel erwähnte, wurde {subject_name} plötzlich sehr still und angespannt."
    },
    {
        "id": 8,
        "observation": "schwitzte stark",
        "detail": "{subject_name} schwitzte ungewöhnlich stark, obwohl es im Raum eher kühl war. {subject_name} tupfte sich ständig die Stirn ab."
    },
    {
        "id": 9,
        "observation": "Kein Spaziergang",
        "detail": "Als jemand eine Nachtwanderung vorschlug, lehnte {subject_name} vehement ab, weil das viel zu kindisch sei. Hat {subject_name} Angst im Dunkeln?"
    }
]

# Opferbezogene falsche Fährten (Red Herrings) pro Charakter und Motiv-Opfer
# Für jedes Motiv-Opfer gibt es zwei mögliche Red-Herring-Beobachtungen.
RED_HERRING_MATRIX = {
    1: {  # Vincent -> Dimitri
        "Dimitri Volkov": [
            {
                "id": 101,
                "detail": "{subject_firstname} hat Dimitri noch spät in der Lobby abgepasst und bestand darauf, dass sie dringend unter vier Augen reden müssen."
            },
            {
                "id": 102,
                "detail": "Aus der Bar hörte ich, wie {subject_name} Dimitri laut vorwarf, seine Betrügereien aufzudecken – kurz bevor beide auseinander gingen."
            },
        ]
    },
    2: {  # Alexa -> Viktor
        "Viktor Bergmann": [
            {
                "id": 201,
                "detail": "Ich sah, wie {subject_firstname} Viktor im Büro abpasste und ihm wütend Akten unter die Nase hielt – das klang nicht nach einem höflichen Gespräch."
            },
            {
                "id": 202,
                "detail": "{subject_name} stürmte hinter Viktor her und rief ihm nach, dass er „endlich zahlen soll, was er versprochen hat“."
            },
        ]
    },
    3: {  # Viktoria -> Dimitri
        "Dimitri Volkov": [
            {
                "id": 301,
                "detail": "Dimitri und {subject_firstname} flüsterten lange auf dem Balkon. Als ich näher kam, hörte ich, wie {subject_firstname} „das Geld“ erwähnte."
            },
            {
                "id": 302,
                "detail": "{subject_name} nahm Dimitri beiseite und warnte ihn, dass er „damit nicht durchkommt“. Dimitri wirkte sichtlich nervös."
            },
        ]
    },
    4: {  # Pater Benedetti -> Jonas
        "Jonas Reber": [
            {
                "id": 401,
                "detail": "In der Küche redete {subject_firstname} mit Jonas auffallend streng und schien ihm eine letzte Warnung zu geben."
            },
            {
                "id": 402,
                "detail": "Ich sah Jonas und {subject_firstname} hinter der Tür zur Vorratskammer diskutieren; Jonas wirkte kleinlaut und nickte nur."
            },
        ]
    },
    5: {  # Jazz -> Viktor und Jonas
        "Viktor Bergmann": [
            {
                "id": 501,
                "detail": "{subject_firstname} stellte Viktor in der Lounge zur Rede, weil er einen Deal nicht eingehalten habe. Die Stimmung war eisig."
            },
            {
                "id": 502,
                "detail": "Viktor kam aus dem Büro, und {subject_name} zischte ihm hinterher, er solle ihre Zeit nicht verschwenden – das klang nach Ärger."
            },
        ],
        "Jonas Reber": [
            {
                "id": 503,
                "detail": "Am Buffet nörgelte {subject_firstname} lautstark an Jonas’ Menü herum und beschuldigte ihn, ihre Rezepte kopiert zu haben."
            },
            {
                "id": 504,
                "detail": "{subject_name} schnappte Jonas am Ärmel und verlangte, dass er endlich zugibt, ihre Follower mit Fake-Accounts abzuwerben."
            },
        ]
    },
    6: {  # Dr. Chen -> Jonas
        "Jonas Reber": [
            {
                "id": 601,
                "detail": "Ich hörte, wie {subject_firstname} Jonas scharf fragte, ob er sie wieder für den Tod ihres Vaters verantwortlich machen wolle."
            },
            {
                "id": 602,
                "detail": "{subject_name} stand dicht vor Jonas und erklärte mit eiskalter Stimme, dass seine Anschuldigungen Konsequenzen haben werden."
            },
        ]
    },
    7: {  # Luna -> Viktor und Jonas
        "Viktor Bergmann": [
            {
                "id": 701,
                "detail": "Auf der Treppe stellte {subject_firstname} Viktor wütend zur Rede – sie machte ihn für alte Schuld verantwortlich und drohte, „es allen zu erzählen“."
            },
            {
                "id": 702,
                "detail": "Im Flur hörte ich {subject_name}, wie sie Viktor vorwarf, ihre Familie ruiniert zu haben. Viktor wich keinen Schritt zurück."
            },
        ],
        "Jonas Reber": [
            {
                "id": 703,
                "detail": "{subject_firstname} beschuldigte Jonas, die Umwelt zu ruinieren, und sagte, jemand müsse ihn stoppen, bevor es schlimmer wird."
            },
            {
                "id": 704,
                "detail": "Beim Dessert stritten {subject_firstname} und Jonas laut über Bio-Zutaten. Jonas winkte ab, aber {subject_firstname} wurde richtig wütend."
            },
        ]
    },
    8: {  # Max -> Viktor und Dimitri
        "Viktor Bergmann": [
            {
                "id": 801,
                "detail": "{subject_firstname} zog Viktor beiseite und prahlte erst – dann hörte ich, wie er Viktor vorwarf, seinen Golfplatz lächerlich gemacht zu haben."
            },
            {
                "id": 802,
                "detail": "Viktor lachte über einen Spruch, und {subject_name} wurde rot vor Wut. Er murmelte, Viktor solle das noch bereuen."
            },
        ],
        "Dimitri Volkov": [
            {
                "id": 803,
                "detail": "Im Foyer drängte {subject_firstname} Dimitri, endlich das Geld zu überweisen. Dimitri winkte ab, was {subject_firstname} noch wütender machte."
            },
            {
                "id": 804,
                "detail": "{subject_name} folgte Dimitri bis zum Aufzug und sagte, sie würden „die Schulden heute Nacht klären“. Dimitri sah genervt aus."
            },
        ]
    },
    9: {  # Tom -> Jonas und Dimitri
        "Jonas Reber": [
            {
                "id": 901,
                "detail": "Draußen vor der Tür stritt {subject_firstname} mit Jonas über Müll im Wald. {subject_firstname} sagte, er werde das nicht mehr dulden."
            },
            {
                "id": 902,
                "detail": "{subject_name} kam aufgebracht herein und murmelte, Jonas sei ein Umweltverbrecher – Jonas rollte nur mit den Augen."
            },
        ],
        "Dimitri Volkov": [
            {
                "id": 903,
                "detail": "Ich sah {subject_firstname} mit einer Karte im Foyer stehen und Dimitri anfahren, dass er Naturschutz nicht mit Geld aufwiegen könne."
            },
            {
                "id": 904,
                "detail": "{subject_name} knallte Dimitri einen Flyer über Naturschutz hin und sagte, er werde „gegen ihn vorgehen, egal wie reich er ist“."
            },
        ]
    },
    10: {  # Maria -> Dimitri und Viktor
        "Dimitri Volkov": [
            {
                "id": 1001,
                "detail": "{subject_firstname} flüsterte Dimitri zu, dass sie seine Geheimnisse kenne und bereit sei, sie zu nutzen, falls er nicht kooperiert."
            },
            {
                "id": 1002,
                "detail": "Dimitri verließ hastig den Wintergarten, nachdem {subject_name} ihm sagte, „der KGB hört alles“ – das klang nicht nach Spaß."
            },
        ],
        "Viktor Bergmann": [
            {
                "id": 1003,
                "detail": "Später hörte ich, wie {subject_firstname} Viktor drohte, seine Machenschaften öffentlich zu machen, wenn er sie weiter unterschätzt."
            },
            {
                "id": 1004,
                "detail": "{subject_name} stellte Viktor in der Lobby zur Rede und sagte, sie habe „dreckige Details“ über ihn gesammelt."
            },
        ]
    },
}
