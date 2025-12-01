#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Krimidinner - Textbausteine
Enthält alle Templates, Traum-Texte und spezielle Rollen-Texte
"""

# Phase-3-Texte pro Buchstabe (Nachtverhalten + Alibi)
# HIER KÖNNEN DIE TEXTE INDIVIDUELL ANGEPASST WERDEN
# Buchstaben A-J bilden die festen Rollen, die zufällig auf Charaktere gemappt werden
PHASE3_TEXTS = {
    "A": {  # "Frühes Zurückziehen"
        "nacht": "Du fühlst dich vom Tag erschöpft und gehst früh in dein Zimmer. Du räumst noch kurz etwas auf, sortierst deine Sachen und legst dich nach einem schnellen Blick aus dem Fenster ins Bett. Zum Einschlafen hörst du noch eine Folge der Drei Fragezeichen ???, die Nummer 87, die du so gern magst, auf Spotify.",
        "alibi": "Auf dem Flur, kurz bevor du dein Zimmer erreichst, siehst du [B] gerade aus dem Bad kommend. Wenige Sekunden später begegnet dir [C] mit einer Wasserflasche in der Hand in Richtung der Treppe gehend."
    },
    "B": {  # "Kurzes Fenster-Ritual"
        "nacht": "Du kommst gerade aus dem Gemeinschaftsbad. Bevor du ins Bett gehst, bleibst du einen Moment am Fenster stehen, beobachtest wie die Wolken ziehen und holst tief Luft. Danach gehst du auf dein Zimmer. Um besser einschlafen zu können, hörst du dir noch eine Folge der Drei Fragezeichen ??? 69 auf Spotify an.",
        "alibi": "Auf dem Weg in dein Zimmer siehst du [A] gerade im Zimmer verschwindend. Als du die Treppe erreichst, begegnet dir [D] die Stufen hinaufgehend."
    },
    "C": {  # "Zu viel gegessen"
        "nacht": "Du hast beim Dinner wohl etwas übertrieben und fühlst dich schwer. Im Zimmer schaltest du den Fernseher kurz ein, zappst durch, doch deine Augen fallen schnell zu.",
        "alibi": "Im Flur siehst du [A] die Tür hinter sich schließend. Kurz darauf kommt dir [F] entgegen, etwas in der Hand tragend – vielleicht ein Snack."
    },
    "D": {  # "Nachttee in der Lounge"
        "nacht": "Du nippst am Tee aus der Loung, der eine gute Idee war, und genießt einen Moment Ruhe. Danach gehst du ins Bett und stellst dir auf Spotify noch die Drei Fragezeichenfolge ??? 43, The Mystery of the Creep-Show Crooks, an und schläfst sofort ein.",
        "alibi": "An der Treppe zu deinem Zimmerstockwerk siehst du [B] mit einem Handtuch über der Schulter aus dem Fenster schauend die Schneeflocken beobachten. Als du oben im Flur ankommst, läuft [G] an dir vorbei und öffnet eine Zimmertür."
    },
    "E": {  # "Arbeiten im Zimmer"
        "nacht": "Du verbringst den späten Abend damit, Dinge zu sortieren, Mails zu beantworten und Dateien zu ordnen. Gegen Mitternacht wirst du müde und legst dich hin. Noch schnell die Drei Fragezeichen ??? Folge 86, deine Lieblingsfolge, angemacht und sofort schläfst du ein.",
        "alibi": "Bevor du in dein Zimmer gehst, siehst du [G] mit nassen Haaren die Treppe hochkommend. Kurz danach läuft [J] an dir vorbei, schon aus der Puste vom Treppensteigen."
    },
    "F": {  # "Letzter Smalltalk"
        "nacht": "Du triffst auf dem Weg ins Zimmer noch jemanden, wechselst ein paar Worte und gehst dann weiter. Schließlich verschwindest du in deinem Zimmer.",
        "alibi": "Du siehst [C] schläfrig aufs Zimmer mit einer Flasche in der Hand zusteuernd als du selbst in Richtung deines Zimmers gehst. Außerdem kommt dir [H] entgegen, Notizen unter dem Arm tragend."
    },
    "G": {  # "Badezimmer-Selfie-Session"
        "nacht": "Du verbringst noch etwas Zeit im Bad vor dem Spiegel, filmst dich oder machst Fotos. Danach gehst du zurück Richtung Zimmer.",
        "alibi": "Auf dem Rückweg zum Zimmer begegnet dir [D] gerade die Zimmertür aufschließend. Vor der Treppe siehst du [E] mit müdem Blick hochgehend."
    },
    "H": {  # "Arbeiten an Notizen"
        "nacht": "Im Zimmer schreibst du ein paar Gedanken auf, sortierst deine Ideen und bereitest dich mental auf den nächsten Tag vor.",
        "alibi": "Du machst dich zu deinen Schlafgemächern auf. Auf dem Flur siehst du [F] gerade den Gang entlanggehend mit einem Schokoriegel. Kurz darauf kommt dir [I] entgegen, still vor sich hin summend."
    },
    "I": {  # "Glas Wein & Ritual"
        "nacht": "Du gönnst dir ein Glas Wein, legst ein kleines Erinnerungsstück auf das Bett und versinkst in deinen Gedanken.",
        "alibi": "Auf dem Weg zurück zum Zimmer begegnest du [H] noch Notizen in der Hand haltend. Kurz darauf kommt dir [J] entgegen, die Treppe hochsteigend."
    },
    "J": {  # "Musik & Handy-Scrollen"
        "nacht": "Du hörst Musik, scrollst durch dein Handy und siehst dir die Aufnahmen des Abends an. Schließlich wirst du müde und legst dich hin. Noch schnell die Drei Fragezeichen ??? Folge 62 angemacht und schon schläfst du ein.",
        "alibi": "Du bist gerade auf dem Weg in dein Zimmer. An der Treppe siehst du [E] müde die Stufen nehmend. Im Flur siehst du [I] leise summend ins Zimmer gehend."
    }
}

# Texte für Mörder
MURDER_TEXT_TEMPLATE = """
<div class="innocent-info">
    <h2>⚠️ Deine Rolle</h2>

    <div style="margin-top: 20px;">
        {abendverlauf}
    </div>

    <div style="margin-top: 20px; padding: 15px; background: #2c3e50; border-radius: 5px;">
        <p><strong style="color: #e74c3c;">Du bist der Mörder.</strong></p>

        <p>Du wusstest es bereits seit deiner Einladung, du kennst jedes dieser Daten auswendig und doch hast du die Einladung angenommen. 
        Du hättest auch bei der Wahl des Zimmers darauf achten können oder die Vorhänge zuziehen als du dich ins Bett gelegt hast - 
        hast du aber nicht und das obwohl es genau hier vor 3 Jahren schonmal passiert ist. Auch wenn du damals kein Hotelgast warst.</p>

        <p>Den ganzen Abend über hast du schon leichte Veränderungen gespürt in deinem Körper, verstärkter Geruchssinn und Hitzewallungen - und überall dieses verdammte Silber.</p>
        
        <p>Während du schläfst, trifft ein kurzer Moment des klaren Vollmondlichts durch das leichte Schneetreiben dein Zimmer. Es reicht – dein Körper verändert sich.</p>

        <p>Du stehst auf und trittst auf den Balkon, da passiert es, du verwandelst dich und merkst wie du teilweise nicht mehr Herr deiner Sinne bist. Deine Brust, Hände und Füße schwellen an. Du wirst zum Werwolf!</p>

        <p>Dieses Wesen ist schnell, stark und tödlich – aber nur solange der Mond dich direkt trifft.</p>

        <p>Der Mond beleuchtet die Szenerie vor dir. Schneetreiben, der Bach und der Wald dahinter der sich meilenweit erstreckt. 
        Du legst deine nun zu kleine Kleidung ab und springst vom Balkon im ersten Stock in den Schnee und gehst Richtung Wald. Du willst eigentlich niemandem ein Leid zufügen.
        Doch plötzlich triffst du auf <strong>{victim_name}</strong>.</p>

        {motive_text}

        <p>Das Opfer schreit laut auf als es sein Schicksal als besiegelt sieht. Der Mord geschieht in einem einzigen, brutalen Augenblick:</p>

        <p style="text-align: center; font-weight: bold; margin: 15px 0;">ein extrem starker stumpfer Schlag gegen die Brust</p>

        <p>Ein lautes Knacken verrät dir das der Brustkorb zerschmettert wurde als der Körper gegen den Baumstamm kracht.<br>
        In deinem Rausch wirfst du den leblosen Körper nach oben – er landet über einem Ast in zwei Metern Höhe, wo er hängen bleibt.</p>

        <p>Du keuchst. Es ist schon wieder passiert - kurz kommt dein menschliches Wesen in dir zurück und dir wird klar, den Schrei muss jemand gehört haben. 
        Du musst unbemerkt zurück in dein Zimmer, ohne zu viele Spuren zu hinterlassen und so schnell wie möglich.
        Du bewegst dich mit übermenschlicher Geschwindigkeit:</p>

        <ul style="margin-left: 20px;">
            <li>deine riesigen, barfüßigen Abdrücke (Schuhgröße 49) führen bis zum Bach</li>
            <li>dort verlieren sie sich am/im Wasser</li>
            <li>du rennst stromabwärts, Richtung Straße</li>
            <li>und gelangst über die Hotelfassade auf den 2. Balkon deiner Suite der zu einer anderen Himmelsrichtung zeigt. Für einen Mensch wäre die Kletteraktion aber unmöglich.</li>
        </ul>

        <p>In diesem Moment hörst du einen weiteren Schrei der Hausdame, aber aus Richtung des Foyers – sie hat die Leiche bereits gefunden.</p>

        <p>Sobald du das Innere erreichst, verschwindet die Verwandlung – glücklicherweise ziehen gerade die Wolken auf und verdecken den Mond. Du hast heute wohl keine weitere Verwandlung mehr zu befürchten.</p>

        <p>Du vernimmst bereits aufgeregte Stimmen im Flur als sich alle Richtung Foyer bewegen. Auch du ziehst dich schnell wieder an und bewegst dich aus dem Zimmer mit den restlichen Leuten ins Foyer.</p>

        <p style="font-weight: bold; margin-top: 20px;">Niemand hat dich gesehen.<br>
        Niemand weiß, dass du es warst. Du warst schnell genug wieder im Zimmer.<br>
        Bestreite immer alles - es gibt keine eindeutigen Beweise! Oder doch?</p>
    </div>
</div>
"""

# Texte für Unschuldige
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

    <p style="color: #ffb3d9; font-style: italic;">Hinweis: Suche heute Nacht nach Gelegenheiten, mit {lover_name} zu sprechen. Ein Blick, eine Geste – ihr werdet euch verstehen.</p>
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
