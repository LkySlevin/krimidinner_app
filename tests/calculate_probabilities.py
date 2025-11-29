#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Berechnet die theoretischen Wahrscheinlichkeiten für alle Mörder-Opfer-Kombinationen.
Berücksichtigt die Motiv-Gewichtung (2:1) und zeigt die Wahrscheinlichkeit für jedes Szenario.
"""

import sys
import os
import matplotlib.pyplot as plt
import matplotlib
import numpy as np

matplotlib.use('Agg')  # Backend für nicht-interaktive Plots

# Füge den Parent-Ordner zum Pfad hinzu, um app.py zu importieren
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import CHARACTERS, NPCS, MOTIVE_MATRIX


def calculate_murder_probabilities():
    """
    Berechnet für jede Opfer-Mörder-Kombination die theoretische Wahrscheinlichkeit.
    """

    print("=" * 80)
    print("🎲 THEORETISCHE WAHRSCHEINLICHKEITEN: Wer bringt wen mit welcher Chance um?")
    print("=" * 80)
    print()

    # Für jedes NPC (Opfer)
    for npc_key, npc in NPCS.items():
        victim_name = npc['name']

        print(f"\n{'═' * 80}")
        print(f"🔪 OPFER: {victim_name} ({npc['role']})")
        print(f"{'═' * 80}\n")

        # Berechne Gewichte für alle Charaktere bei diesem Opfer
        weights = []
        char_info = []

        for char in CHARACTERS:
            char_id = char['id']
            has_motive = victim_name in MOTIVE_MATRIX.get(char_id, {})
            weight = 2 if has_motive else 1

            weights.append(weight)
            char_info.append({
                'char': char,
                'has_motive': has_motive,
                'weight': weight,
                'motive_text': MOTIVE_MATRIX.get(char_id, {}).get(victim_name, None)
            })

        # Gesamtgewicht
        total_weight = sum(weights)

        # Berechne Wahrscheinlichkeiten
        print(f"📊 Wahrscheinlichkeitsverteilung (Gesamtgewicht: {total_weight}):\n")

        # Sortiere nach Wahrscheinlichkeit (höchste zuerst)
        char_info_sorted = sorted(char_info, key=lambda x: x['weight'], reverse=True)

        for info in char_info_sorted:
            char = info['char']
            weight = info['weight']
            probability = (weight / total_weight) * 100

            # Visuelle Balken
            bar_length = int(probability * 0.5)  # Skalierung für Darstellung
            bar = '█' * bar_length

            # Motiv-Marker
            motive_marker = "✓ MOTIV" if info['has_motive'] else "✗ kein Motiv"

            print(f"  [{char['letter']}] {char['name']:<30} │ {probability:6.2f}% │ {bar}")
            print(f"      Gewicht: {weight} │ {motive_marker}")

            if info['motive_text']:
                print(f"      → {info['motive_text']}")

            print()

        # Zusammenfassung
        chars_with_motive = [c for c in char_info if c['has_motive']]
        chars_without_motive = [c for c in char_info if not c['has_motive']]

        prob_with_motive = sum(c['weight'] for c in chars_with_motive) / total_weight * 100
        prob_without_motive = sum(c['weight'] for c in chars_without_motive) / total_weight * 100

        print(f"\n  📈 Zusammenfassung:")
        print(f"     • {len(chars_with_motive)} Charaktere MIT Motiv → {prob_with_motive:.2f}% Gesamtwahrscheinlichkeit")
        print(f"     • {len(chars_without_motive)} Charaktere OHNE Motiv → {prob_without_motive:.2f}% Gesamtwahrscheinlichkeit")


def calculate_victim_probabilities():
    """
    Berechnet die Wahrscheinlichkeit, dass jedes NPC Opfer wird.
    Da die Opferauswahl jetzt zufällig ist, ist jedes NPC gleich wahrscheinlich.
    """

    print("\n\n" + "=" * 80)
    print("🎯 OPFER-WAHRSCHEINLICHKEITEN")
    print("=" * 80)
    print()
    print("Da die Opferauswahl rein zufällig (basierend auf Seed) erfolgt,")
    print("hat jedes NPC die gleiche Chance, Opfer zu werden:\n")

    num_npcs = len(NPCS)
    probability = 100.0 / num_npcs

    for npc_key, npc in NPCS.items():
        bar_length = int(probability * 0.5)
        bar = '█' * bar_length
        print(f"  {npc['name']:<30} │ {probability:6.2f}% │ {bar}")

    print()


def calculate_overall_murderer_probabilities():
    """
    Berechnet die Gesamt-Wahrscheinlichkeit für jeden Charakter, Mörder zu werden.
    Berücksichtigt, dass jedes Opfer gleich wahrscheinlich ist (33.33% jeweils).
    """

    print("\n\n" + "=" * 80)
    print("🎲 GESAMT-WAHRSCHEINLICHKEITEN: Wer wird mit welcher Chance Mörder?")
    print("=" * 80)
    print()
    print("(Gewichtet über alle 3 möglichen Opfer, jeweils 33.33% Wahrscheinlichkeit)\n")

    # Für jeden Charakter die durchschnittliche Wahrscheinlichkeit berechnen
    overall_probs = {}

    for char in CHARACTERS:
        total_prob = 0.0

        # Für jedes mögliche Opfer
        for npc_key, npc in NPCS.items():
            victim_name = npc['name']

            # Berechne Gewichte für alle Charaktere bei diesem Opfer
            weights = []
            for c in CHARACTERS:
                has_motive = victim_name in MOTIVE_MATRIX.get(c['id'], {})
                weight = 2 if has_motive else 1
                weights.append(weight)

            total_weight = sum(weights)

            # Wahrscheinlichkeit für diesen Charakter bei diesem Opfer
            char_index = CHARACTERS.index(char)
            char_weight = weights[char_index]
            prob_for_this_victim = (char_weight / total_weight)

            # Gewichtet mit Opfer-Wahrscheinlichkeit (33.33%)
            total_prob += prob_for_this_victim * (1.0 / len(NPCS))

        overall_probs[char['name']] = total_prob * 100

    # Sortiere nach Wahrscheinlichkeit
    sorted_probs = sorted(overall_probs.items(), key=lambda x: x[1], reverse=True)

    for char_name, prob in sorted_probs:
        char = next(c for c in CHARACTERS if c['name'] == char_name)
        bar_length = int(prob * 0.5)
        bar = '█' * bar_length

        print(f"  [{char['letter']}] {char_name:<30} │ {prob:6.2f}% │ {bar}")

    print()


def create_probability_heatmap():
    """
    Erstellt eine Heatmap der theoretischen Wahrscheinlichkeiten für alle Mörder-Opfer-Kombinationen.
    """

    # Erstelle Ergebnisordner falls nicht vorhanden
    results_dir = os.path.join(os.path.dirname(__file__), 'results')
    os.makedirs(results_dir, exist_ok=True)

    # Matrix für Wahrscheinlichkeiten: Zeilen = Mörder, Spalten = Opfer
    num_chars = len(CHARACTERS)
    num_victims = len(NPCS)
    prob_matrix = np.zeros((num_chars, num_victims))

    # NPC-Namen für Spalten
    victim_names = [npc['name'].split()[0] for npc in NPCS.values()]  # Nur Vorname

    # Charakter-Namen für Zeilen
    char_labels = [f"[{char['letter']}] {char['name'].split()[0]}" for char in CHARACTERS]

    # Berechne Wahrscheinlichkeiten für jede Kombination
    for victim_idx, (npc_key, npc) in enumerate(NPCS.items()):
        victim_name = npc['name']

        # Berechne Gewichte für alle Charaktere bei diesem Opfer
        weights = []
        for char in CHARACTERS:
            char_id = char['id']
            has_motive = victim_name in MOTIVE_MATRIX.get(char_id, {})
            weight = 2 if has_motive else 1
            weights.append(weight)

        total_weight = sum(weights)

        # Setze Wahrscheinlichkeiten in Matrix
        for char_idx, char in enumerate(CHARACTERS):
            prob_matrix[char_idx, victim_idx] = (weights[char_idx] / total_weight) * 100

    # Erstelle Heatmap
    fig, ax = plt.subplots(figsize=(10, 14))

    # Heatmap mit roter Farbskala
    im = ax.imshow(prob_matrix, cmap='Reds', aspect='auto', vmin=0, vmax=16)

    # Achsenbeschriftungen
    ax.set_xticks(np.arange(num_victims))
    ax.set_yticks(np.arange(num_chars))
    ax.set_xticklabels(victim_names, fontsize=11, fontweight='bold')
    ax.set_yticklabels(char_labels, fontsize=10)

    # Achsentitel
    ax.set_xlabel('Opfer (NPCs)', fontsize=12, fontweight='bold')
    ax.set_ylabel('Mörder (Spieler-Charaktere)', fontsize=12, fontweight='bold')
    ax.set_title('Theoretische Wahrscheinlichkeiten: Wer bringt wen um?\n(Prozent-Wahrscheinlichkeit bei gegebenem Opfer)',
                 fontsize=13, fontweight='bold', pad=20)

    # Füge Prozentwerte in Zellen ein
    for i in range(num_chars):
        for j in range(num_victims):
            prob = prob_matrix[i, j]

            # Prüfe ob Motiv vorhanden
            victim_name = list(NPCS.values())[j]['name']
            char_id = CHARACTERS[i]['id']
            has_motive = victim_name in MOTIVE_MATRIX.get(char_id, {})

            # Text-Farbe abhängig von Wahrscheinlichkeit
            text_color = 'white' if prob > 10 else 'black'

            # Zeige Prozent und Motiv-Marker
            motive_marker = '★' if has_motive else ''
            text = ax.text(j, i, f'{prob:.1f}%\n{motive_marker}',
                          ha="center", va="center", color=text_color,
                          fontsize=9, fontweight='bold' if has_motive else 'normal')

    # Colorbar
    cbar = plt.colorbar(im, ax=ax)
    cbar.set_label('Wahrscheinlichkeit (%)', rotation=270, labelpad=20, fontsize=11)

    # Legende
    legend_text = '★ = Hat Motiv gegen dieses Opfer (Gewicht 2x)\nOhne Stern = Kein Motiv (Gewicht 1x)'
    fig.text(0.5, 0.01, legend_text, ha='center', fontsize=10,
             bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.3))

    plt.tight_layout(rect=[0, 0.03, 1, 1])

    # Speichern
    output_path = os.path.join(results_dir, 'probability_heatmap.png')
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()

    print(f"\n✅ Heatmap gespeichert: {output_path}")
    return output_path


def main():
    print("\n")

    # 1. Wahrscheinlichkeiten für jedes Opfer einzeln
    calculate_murder_probabilities()

    # 2. Opfer-Wahrscheinlichkeiten
    calculate_victim_probabilities()

    # 3. Gesamt-Mörder-Wahrscheinlichkeiten
    calculate_overall_murderer_probabilities()

    # 4. Erstelle Heatmap-Visualisierung
    print("\n" + "=" * 80)
    print("📊 Erstelle Wahrscheinlichkeits-Heatmap...")
    print("=" * 80)
    create_probability_heatmap()

    print("\n" + "=" * 80)
    print("✅ BERECHNUNG UND VISUALISIERUNG ABGESCHLOSSEN")
    print("=" * 80)
    print()


if __name__ == "__main__":
    main()
