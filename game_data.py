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
    "H": {"name": "Der Koch", "tag": "NPC"},
    "I": {"name": "Die Hausdame", "tag": "NPC"},
    "J": {"name": "Viktor Bergmann", "tag": "Hotelier"}
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
        "detail": "Ich habe bemerkt, dass {subject_name} ausschließlich von den goldenen Schüsseln gegessen hat (Fleisch und Fisch). Die Schüsseln mit Gemüse und Suppe hat {subject_name} komplett ignoriert."
    },
    {
        "id": 3,
        "observation": "ließ Gemüseschüssel fallen",
        "detail": "Als ich {subject_name} eine Schüssel mit Gemüse reichen wollte, ließ {subject_name} sie fallen wie eine heiße Kartoffel. {subject_name} murmelte eine Entschuldigung und orderte Personal zum Aufräumen herbei."
    },
    {
        "id": 4,
        "observation": "vermied Silberbesteck",
        "detail": "Ich sah, dass {subject_name} das Silberbesteck auf dem Tisch vermieden hat und stattdessen mit den Händen oder eigenem Besteck aß."
    },
    {
        "id": 5,
        "observation": "war ungewöhnlich blass",
        "detail": "{subject_name} sah sehr blass und krank aus während des Abendessens. Ich fragte, ob es {subject_name} gut geht, aber {subject_name} wich der Frage aus."
    },
    {
        "id": 6,
        "observation": "hatte erweiterte Pupillen",
        "detail": "Als ich mit {subject_name} sprach, fielen mir die seltsam erweiterten Pupillen auf. Der Blick war irgendwie glasig und leer."
    },
    {
        "id": 7,
        "observation": "reagierte nervös auf Nachthimmel-Erwähnung",
        "detail": "Als jemand den schönen, sternenklaren Nachthimmel erwähnte, zuckte {subject_name} zusammen und wurde plötzlich sehr still und angespannt."
    },
    {
        "id": 8,
        "observation": "schwitzte stark",
        "detail": "{subject_name} schwitzte ungewöhnlich stark, obwohl es im Raum eher kühl war. {subject_name} tupfte sich ständig die Stirn ab."
    }
]

# Falsche Fährten (Red Herrings) für Erinnerungen
RED_HERRING_CLUES = [
    {
        "id": 1,
        "observation": "telefonierte lange",
        "detail": "{subject_name} hat sich nach dem Essen für einen langen Anruf zurückgezogen."
    },
    {
        "id": 2,
        "observation": "hatte tränende Augen",
        "detail": "Die Augen von {subject_name} waren gerötet und tränten."
    },
    {
        "id": 3,
        "observation": "roch nach Rauch",
        "detail": "Mir ist ein leichter Rauchgeruch an {subject_name} aufgefallen."
    },
    {
        "id": 4,
        "observation": "zählte ständig Besteck",
        "detail": "{subject_name} hat während des Dinners mehrfach das Besteck gezählt."
    },
    {
        "id": 5,
        "observation": "fragte nach WLAN",
        "detail": "{subject_name} wollte unbedingt das WLAN-Passwort und war dauernd am Handy."
    },
    {
        "id": 6,
        "observation": "war extrem müde",
        "detail": "{subject_name} hat ständig gegähnt und wirkte völlig übermüdet."
    },
    {
        "id": 7,
        "observation": "musste oft aufs Klo",
        "detail": "{subject_name} war dauernd auf der Toilette."
    },
    {
        "id": 8,
        "observation": "polierte Besteck",
        "detail": "Ich sah, wie {subject_name} mehrfach das eigene Besteck polierte."
    },
    {
        "id": 9,
        "observation": "starrte ins Leere",
        "detail": "{subject_name} starrte häufiger gedankenverloren in die Leere."
    },
    {
        "id": 10,
        "observation": "wechselte ständig Plätze",
        "detail": "{subject_name} hat während des Abends mehrmals den Sitzplatz gewechselt."
    }
]
