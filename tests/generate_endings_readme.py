#!/usr/bin/env python3
"""
Generiert eine Übersicht aller möglichen Schluss-Szenentexte und schreibt sie
bei jedem Lauf in tests/ENDINGS_README.md (Datei wird neu erstellt).
"""

import os
import sys
import types
from typing import List, Optional
import textwrap

# Projektwurzel zum Pfad hinzufügen
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Stubs, falls Abhängigkeiten (Flask, qrcode, PIL) lokal nicht installiert sind
try:
    import flask  # type: ignore
except ModuleNotFoundError:
    class _DummyFlask:
        def __init__(self, *args, **kwargs):
            pass

        def route(self, *args, **kwargs):
            def decorator(func):
                return func
            return decorator

    def _nop(*args, **kwargs):
        return None

    flask = types.SimpleNamespace(  # type: ignore
        Flask=_DummyFlask,
        render_template=_nop,
        request=None,
        redirect=_nop,
        url_for=lambda *a, **k: "",
        session={},
        send_from_directory=_nop,
        abort=_nop,
    )
    sys.modules["flask"] = flask

try:
    import qrcode  # type: ignore
except ModuleNotFoundError:
    class _DummyQR:
        def __init__(self, *a, **k):
            pass

        def add_data(self, *a, **k):
            pass

        def make(self, *a, **k):
            pass

        def make_image(self, *a, **k):
            class _Img:
                def save(self, *a, **k):
                    pass
            return _Img()

    qrcode = types.SimpleNamespace(QRCode=_DummyQR)  # type: ignore
    sys.modules["qrcode"] = qrcode

try:
    from PIL import Image, ImageDraw, ImageFont  # type: ignore
except ModuleNotFoundError:
    class _DummyImage:
        def __init__(self, *a, **k):
            pass

        def convert(self, *a, **k):
            return self

        def save(self, *a, **k):
            pass

        @staticmethod
        def new(*a, **k):
            return _DummyImage()

    class _DummyDraw:
        def __init__(self, *a, **k):
            pass

        def textbbox(self, *a, **k):
            return (0, 0, 10, 10)

        def text(self, *a, **k):
            pass

    class _DummyFont:
        @staticmethod
        def truetype(*a, **k):
            raise OSError()

        @staticmethod
        def load_default():
            return None

    Image = _DummyImage  # type: ignore
    ImageDraw = types.SimpleNamespace(Draw=lambda *a, **k: _DummyDraw())  # type: ignore
    ImageFont = _DummyFont  # type: ignore
    sys.modules["PIL"] = types.SimpleNamespace(Image=Image, ImageDraw=ImageDraw, ImageFont=ImageFont)  # type: ignore
    sys.modules["PIL.Image"] = Image  # type: ignore
    sys.modules["PIL.ImageDraw"] = ImageDraw  # type: ignore
    sys.modules["PIL.ImageFont"] = ImageFont  # type: ignore

from app import (  # type: ignore
    CHARACTERS,
    NPCS,
    build_phase5_outcome_text,
    get_character_by_id,
)


OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "ENDINGS_README.md")


def identity_letter_mapping():
    """Erstellt ein Letter-Mapping A-J -> A-J entsprechend der CHARACTERS-Liste."""
    return {char["id"]: char["letter"] for char in CHARACTERS}


def render_outcome(
    title: str,
    accused_id: int,
    is_correct: bool,
    lovers: Optional[List[int]] = None,
    desperate_id: Optional[int] = None,
    intrigant_id: Optional[int] = None,
    intrigant_target_id: Optional[int] = None,
) -> str:
    """Baut den HTML-Ausgangstext für ein Szenario."""
    letter_mapping = identity_letter_mapping()
    victim = NPCS["kueche"]  # beliebiges Opfer genügt für den Text
    accused_char = get_character_by_id(accused_id)

    game_state = {
        "lovers": lovers or [],
        "desperate_id": desperate_id,
        "intrigant_id": intrigant_id,
        "intrigant_target_id": intrigant_target_id,
    }

    html = build_phase5_outcome_text(
        accused_char=accused_char,
        letter_mapping=letter_mapping,
        is_correct=is_correct,
        victim=victim,
        game_state=game_state,
    )
    clean_html = textwrap.dedent(html).strip()
    # Entferne führende Spaces pro Zeile, damit Markdown es nicht als Codeblock rendert
    clean_html = "\n".join(line.lstrip() for line in clean_html.splitlines())
    return f"## {title}\n\n{clean_html}\n\n"


def main():
    # Datei zurücksetzen
    if os.path.exists(OUTPUT_PATH):
        os.remove(OUTPUT_PATH)

    style_block = """
<style>
.phase5-outcome, .phase5-outcome * {
  background: #f7f7f7 !important;
  color: #111 !important;
}
</style>
"""

    # Basis-IDs für Beispiele
    lover_a, lover_b = 3, 7  # Viktoria Lang, Luna Silbermann
    intrigant = 5  # Jazz Monroe
    target = 2  # Alexa Steinberg
    desperate = 9  # Tom Greenwood
    accused = 4  # Pater Antonio Benedetti

    base_args = {
        "lovers": [lover_a, lover_b],
        "desperate_id": desperate,
        "intrigant_id": intrigant,
        "intrigant_target_id": target,
    }

    scenario_defs = [
        # Richtiges Urteil (Intrigant scheitert standardmäßig)
        {"title": "Richtiges Urteil – Liebender stirbt", "is_correct": True, "args": {"accused_id": lover_a}},
        {"title": "Richtiges Urteil – Liebespaar überlebt", "is_correct": True, "args": {}},
        {"title": "Richtiges Urteil – Intrigant erfolgreich", "is_correct": True, "args": {"accused_id": target}},
        {"title": "Richtiges Urteil – Intrigant scheitert", "is_correct": True, "args": {}},
        # Falsches Urteil (Intrigant scheitert standardmäßig)
        {"title": "Falsches Urteil – Liebender stirbt", "is_correct": False, "args": {"accused_id": lover_b}},
        {"title": "Falsches Urteil – Liebespaar überlebt", "is_correct": False, "args": {}},
        {"title": "Falsches Urteil – Verzweifelte Person stirbt", "is_correct": False, "args": {"accused_id": desperate}},
        {"title": "Falsches Urteil – Verzweifelte Person überlebt", "is_correct": False, "args": {}},
        {"title": "Falsches Urteil – Intrigant erfolgreich", "is_correct": False, "args": {"accused_id": target}},
        {"title": "Falsches Urteil – Intrigant scheitert", "is_correct": False, "args": {}},
    ]

    # Tabellenkopf
    table_lines = ["| Szenario | Urteil korrekt? | Besonderheiten |", "| --- | --- | --- |"]
    scenario_sections = []

    logic_tree = """
<details>
<summary><strong>Logikbaum der Enden</strong></summary>

- Urteil korrekt (Mörder erwischt)
  - Liebender angeklagt? → Partner bricht beim Schuss zusammen
  - sonst: beide Liebenden leben → schleichen zusammen aufs Zimmer
  - Intrigant: Ziel getroffen? → zufrieden-grinsendes Gute Nacht; sonst Humbug-Kommentar vor Schlussabsatz
  - Verzweifelte Person: nicht möglich als Mörder
- Urteil falsch (Unschuldiger gehängt)
  - Liebender angeklagt? → Partner bricht beim Strick zusammen
  - sonst: beide Liebenden leben → schleichen zusammen aufs Zimmer
  - Intrigant: Ziel gehängt? → zufrieden-grinsendes Gute Nacht; sonst Humbug-Kommentar vor Schlussabsatz
  - Verzweifelte Person gehängt? → lächelnd; sonst geht sie mit hängendem Kopf ins Zimmer
</details>
"""

    for s in scenario_defs:
        title = s["title"]
        is_correct = "Ja" if s["is_correct"] else "Nein"
        specials = []
        args = {**base_args, **s["args"]}
        if args.get("lovers"):
            specials.append("Liebespaar")
        if "desperate_id" in args:
            specials.append("Verzweifelte Person")
        if args.get("intrigant_id"):
            specials.append("Intrigant")
        table_lines.append(f"| {title} | {is_correct} | {', '.join(specials) if specials else '-'} |")
        scenario_sections.append(
            render_outcome(
                title,
                accused_id=args.get("accused_id", accused),
                is_correct=s["is_correct"],
                lovers=args.get("lovers"),
                desperate_id=args.get("desperate_id"),
                intrigant_id=args.get("intrigant_id"),
                intrigant_target_id=args.get("intrigant_target_id"),
            )
        )

    content = "# Schluss-Szenen Übersicht\n\n" + logic_tree + "\n\n" + "\n".join(table_lines) + "\n\n" + style_block + "\n" + "".join(scenario_sections)

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"README generiert: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
