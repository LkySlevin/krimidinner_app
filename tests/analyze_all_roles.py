#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Analysiert alle Rollen über alle möglichen Seed-Kombinationen:
- Mörder-Wahrscheinlichkeiten
- Opfer-Wahrscheinlichkeiten
- Awakener-Wahrscheinlichkeiten
- Intrigant & Intrigant-Ziel Wahrscheinlichkeiten
- Desperate-Person Wahrscheinlichkeiten
- Lover-Paare Wahrscheinlichkeiten

Durchläuft alle (event1, event2, event3, weekday) Kombinationen.
"""

import sys
import os
from collections import defaultdict, Counter
import matplotlib.pyplot as plt
import matplotlib
import numpy as np

matplotlib.use('Agg')  # Backend für nicht-interaktive Plots

# Füge den Parent-Ordner zum Pfad hinzu, um app.py zu importieren
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import (
    CHARACTERS, NPCS,
    select_murder_, select_random_victim,
    select_awakeners, select_special_roles
)


def analyze_all_scenarios(num_players=10):
    """
    Durchläuft alle Seed-Kombinationen und sammelt Statistiken über alle Rollen.
    """

    print("\n" + "=" * 80)
    print(f"🎲 ROLLEN-ANALYSE über alle möglichen Szenarien ({num_players} Spieler)")
    print("=" * 80)
    print()

    # Statistiken sammeln
    murderer_count = Counter()
    victim_count = Counter()
    awakener_count = Counter()
    intrigant_count = Counter()
    intrigant_target_count = Counter()
    desperate_count = Counter()
    lover_count = Counter()

    # Ereignis-Kombinationen (None + char IDs 1-10)
    events = [None] + [char["id"] for char in CHARACTERS]  # 11 Optionen
    weekdays = list(range(1, 8))  # 7 Wochentage

    total_scenarios = 0

    # Verwende alle 10 Charaktere für die Analyse
    active_chars = CHARACTERS[:num_players]

    print(f"Aktive Charaktere: {', '.join([c['name'] for c in active_chars])}")
    print(f"\nBerechne {len(events) ** 3 * len(weekdays):,} Szenarien (11³ × 7)...\n")

    # Durchlaufe alle Kombinationen
    for event1 in events:
        for event2 in events:
            for event3 in events:
                for weekday in weekdays:
                    seed_tuple = (event1, event2, event3, weekday)
                    total_scenarios += 1

                    # 1. Opfer bestimmen
                    victim = select_random_victim(seed_tuple)
                    victim_count[victim['name']] += 1

                    # 2. Mörder bestimmen
                    murderer_id = select_murder_(active_chars, seed_tuple, victim)
                    murderer = next(c for c in active_chars if c['id'] == murderer_id)
                    murderer_count[murderer['name']] += 1

                    # 3. Awakeners bestimmen
                    awakeners = select_awakeners(active_chars, murderer_id)
                    for awakener_id in awakeners:
                        awakener = next(c for c in active_chars if c['id'] == awakener_id)
                        awakener_count[awakener['name']] += 1

                    # 4. Spezielle Rollen bestimmen
                    # Hinweis: Diese sind nicht-deterministisch, daher müssen wir mehrere Samples nehmen
                    # Wir machen 10 Samples pro Szenario für bessere Statistik
                    for _ in range(10):
                        intrigant_id, target_id, desperate_id, lovers = select_special_roles(
                            active_chars, murderer_id
                        )

                        if intrigant_id:
                            intrigant = next(c for c in active_chars if c['id'] == intrigant_id)
                            intrigant_count[intrigant['name']] += 1

                        if target_id:
                            target = next(c for c in active_chars if c['id'] == target_id)
                            intrigant_target_count[target['name']] += 1

                        if desperate_id:
                            desperate = next(c for c in active_chars if c['id'] == desperate_id)
                            desperate_count[desperate['name']] += 1

                        if lovers:
                            for lover_id in lovers:
                                lover = next(c for c in active_chars if c['id'] == lover_id)
                                lover_count[lover['name']] += 1

    # Fortschritt
    if total_scenarios % 1000 == 0:
        print(f"Progress: {total_scenarios} Szenarien berechnet...", end='\r')

    print(f"\n✅ {total_scenarios} Szenarien analysiert!\n")

    # === AUSGABE DER ERGEBNISSE ===

    print("\n" + "=" * 80)
    print("📊 MÖRDER-WAHRSCHEINLICHKEITEN")
    print("=" * 80)
    print(f"Gesamt-Szenarien: {total_scenarios}\n")

    for char in active_chars:
        count = murderer_count[char['name']]
        prob = (count / total_scenarios) * 100
        bar = '█' * int(prob * 0.5)
        print(f"  [{char['letter']}] {char['name']:<30} │ {count:6} │ {prob:6.2f}% │ {bar}")

    print("\n" + "=" * 80)
    print("🎯 OPFER-WAHRSCHEINLICHKEITEN")
    print("=" * 80)
    print()

    for npc_name in victim_count.keys():
        count = victim_count[npc_name]
        prob = (count / total_scenarios) * 100
        bar = '█' * int(prob * 0.5)
        print(f"  {npc_name:<30} │ {count:6} │ {prob:6.2f}% │ {bar}")

    print("\n" + "=" * 80)
    print("⏰ AWAKENER-WAHRSCHEINLICHKEITEN")
    print("=" * 80)
    print("(Wahrscheinlichkeit, beim ersten Schrei aufzuwachen)\n")

    # Awakener-Statistik ist anders: Jedes Szenario hat 2-3 Awakeners
    total_awakener_slots = sum(awakener_count.values())

    for char in active_chars:
        count = awakener_count[char['name']]
        # Wahrscheinlichkeit dass dieser Charakter Awakener ist
        prob = (count / total_scenarios) * 100
        bar = '█' * int(prob * 0.3)
        print(f"  [{char['letter']}] {char['name']:<30} │ {count:6} │ {prob:6.2f}% │ {bar}")

    print("\n" + "=" * 80)
    print("🎭 INTRIGANT-WAHRSCHEINLICHKEITEN")
    print("=" * 80)
    print("(Wer wird mit welcher Chance zum Intriganten?)\n")

    # Intrigant: 10 Samples pro Szenario
    total_intrigant_samples = total_scenarios * 10

    for char in active_chars:
        count = intrigant_count[char['name']]
        prob = (count / total_intrigant_samples) * 100
        bar = '█' * int(prob * 0.5)
        print(f"  [{char['letter']}] {char['name']:<30} │ {count:6} │ {prob:6.2f}% │ {bar}")

    print("\n" + "=" * 80)
    print("🎯 INTRIGANT-ZIEL-WAHRSCHEINLICHKEITEN")
    print("=" * 80)
    print("(Wem wird mit welcher Chance der Mord angehängt?)\n")

    for char in active_chars:
        count = intrigant_target_count[char['name']]
        prob = (count / total_intrigant_samples) * 100
        bar = '█' * int(prob * 0.5)
        print(f"  [{char['letter']}] {char['name']:<30} │ {count:6} │ {prob:6.2f}% │ {bar}")

    print("\n" + "=" * 80)
    print("😔 DESPERATE-PERSON-WAHRSCHEINLICHKEITEN")
    print("=" * 80)
    print("(Wer wird mit welcher Chance verzweifelt?)\n")

    for char in active_chars:
        count = desperate_count[char['name']]
        prob = (count / total_intrigant_samples) * 100
        bar = '█' * int(prob * 0.5)
        print(f"  [{char['letter']}] {char['name']:<30} │ {count:6} │ {prob:6.2f}% │ {bar}")

    print("\n" + "=" * 80)
    print("💕 LOVER-WAHRSCHEINLICHKEITEN")
    print("=" * 80)
    print("(Wer wird mit welcher Chance Teil eines verliebten Paares?)\n")

    for char in active_chars:
        count = lover_count[char['name']]
        prob = (count / total_intrigant_samples) * 100
        bar = '█' * int(prob * 0.5)
        print(f"  [{char['letter']}] {char['name']:<30} │ {count:6} │ {prob:6.2f}% │ {bar}")

    print("\n" + "=" * 80)
    print("✅ ANALYSE ABGESCHLOSSEN")
    print("=" * 80)
    print()

    # Rückgabe der Statistiken für Visualisierung
    return {
        'total_scenarios': total_scenarios,
        'active_chars': active_chars,
        'murderer_count': murderer_count,
        'victim_count': victim_count,
        'awakener_count': awakener_count,
        'intrigant_count': intrigant_count,
        'intrigant_target_count': intrigant_target_count,
        'desperate_count': desperate_count,
        'lover_count': lover_count,
        'total_intrigant_samples': total_intrigant_samples
    }


def create_role_distribution_chart(stats):
    """
    Erstellt eine visuelle Darstellung der Rollenverteilung über alle Szenarien.
    """
    print("\n" + "=" * 80)
    print("📊 Erstelle Rollen-Verteilungs-Grafiken...")
    print("=" * 80)

    # Erstelle Ergebnisordner falls nicht vorhanden
    results_dir = os.path.join(os.path.dirname(__file__), 'results')
    os.makedirs(results_dir, exist_ok=True)

    active_chars = stats['active_chars']
    char_names = [c['name'].split()[0] for c in active_chars]  # Nur Vornamen

    # === GRAFIK 1: Mörder-Wahrscheinlichkeiten ===
    fig, ax = plt.subplots(figsize=(12, 6))

    murderer_probs = [(stats['murderer_count'][c['name']] / stats['total_scenarios']) * 100
                      for c in active_chars]

    bars = ax.bar(char_names, murderer_probs, color='darkred', alpha=0.7, edgecolor='black')

    ax.set_xlabel('Charakter', fontsize=12, fontweight='bold')
    ax.set_ylabel('Wahrscheinlichkeit (%)', fontsize=12, fontweight='bold')
    ax.set_title(f'Mörder-Wahrscheinlichkeiten über {stats["total_scenarios"]:,} Szenarien',
                 fontsize=14, fontweight='bold', pad=20)
    ax.set_ylim(0, max(murderer_probs) * 1.2)
    ax.grid(axis='y', alpha=0.3)

    # Werte auf Balken anzeigen
    for i, (bar, prob) in enumerate(zip(bars, murderer_probs)):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{prob:.1f}%',
                ha='center', va='bottom', fontweight='bold', fontsize=9)

    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()

    output_path = os.path.join(results_dir, 'murderer_distribution.png')
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✅ Mörder-Verteilung gespeichert: {output_path}")

    # === GRAFIK 2: Alle Rollen im Vergleich ===
    fig, axes = plt.subplots(2, 3, figsize=(18, 10))
    fig.suptitle('Rollenverteilung über alle Szenarien', fontsize=16, fontweight='bold')

    # 2.1 Mörder
    ax = axes[0, 0]
    murderer_probs = [(stats['murderer_count'][c['name']] / stats['total_scenarios']) * 100
                      for c in active_chars]
    ax.barh(char_names, murderer_probs, color='darkred', alpha=0.7)
    ax.set_xlabel('Wahrscheinlichkeit (%)')
    ax.set_title('🔪 Mörder', fontweight='bold')
    ax.grid(axis='x', alpha=0.3)

    # 2.2 Awakener
    ax = axes[0, 1]
    awakener_probs = [(stats['awakener_count'][c['name']] / stats['total_scenarios']) * 100
                      for c in active_chars]
    ax.barh(char_names, awakener_probs, color='orange', alpha=0.7)
    ax.set_xlabel('Wahrscheinlichkeit (%)')
    ax.set_title('⏰ Awakener', fontweight='bold')
    ax.grid(axis='x', alpha=0.3)

    # 2.3 Intrigant
    ax = axes[0, 2]
    intrigant_probs = [(stats['intrigant_count'][c['name']] / stats['total_intrigant_samples']) * 100
                       for c in active_chars]
    ax.barh(char_names, intrigant_probs, color='purple', alpha=0.7)
    ax.set_xlabel('Wahrscheinlichkeit (%)')
    ax.set_title('🎭 Intrigant', fontweight='bold')
    ax.grid(axis='x', alpha=0.3)

    # 2.4 Intrigant-Ziel
    ax = axes[1, 0]
    target_probs = [(stats['intrigant_target_count'][c['name']] / stats['total_intrigant_samples']) * 100
                    for c in active_chars]
    ax.barh(char_names, target_probs, color='darkviolet', alpha=0.7)
    ax.set_xlabel('Wahrscheinlichkeit (%)')
    ax.set_title('🎯 Intrigant-Ziel', fontweight='bold')
    ax.grid(axis='x', alpha=0.3)

    # 2.5 Desperate Person
    ax = axes[1, 1]
    desperate_probs = [(stats['desperate_count'][c['name']] / stats['total_intrigant_samples']) * 100
                       for c in active_chars]
    ax.barh(char_names, desperate_probs, color='navy', alpha=0.7)
    ax.set_xlabel('Wahrscheinlichkeit (%)')
    ax.set_title('😔 Desperate', fontweight='bold')
    ax.grid(axis='x', alpha=0.3)

    # 2.6 Lover
    ax = axes[1, 2]
    lover_probs = [(stats['lover_count'][c['name']] / stats['total_intrigant_samples']) * 100
                   for c in active_chars]
    ax.barh(char_names, lover_probs, color='hotpink', alpha=0.7)
    ax.set_xlabel('Wahrscheinlichkeit (%)')
    ax.set_title('💕 Lover', fontweight='bold')
    ax.grid(axis='x', alpha=0.3)

    plt.tight_layout()

    output_path = os.path.join(results_dir, 'all_roles_comparison.png')
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✅ Rollen-Vergleich gespeichert: {output_path}")

    # === GRAFIK 3: Opfer-Verteilung ===
    fig, ax = plt.subplots(figsize=(10, 6))

    victim_names = list(stats['victim_count'].keys())
    victim_probs = [(stats['victim_count'][name] / stats['total_scenarios']) * 100
                    for name in victim_names]

    bars = ax.bar(victim_names, victim_probs, color='darkgreen', alpha=0.7, edgecolor='black')

    ax.set_xlabel('NPC (Opfer)', fontsize=12, fontweight='bold')
    ax.set_ylabel('Wahrscheinlichkeit (%)', fontsize=12, fontweight='bold')
    ax.set_title('Opfer-Wahrscheinlichkeiten (NPCs)', fontsize=14, fontweight='bold', pad=20)
    ax.set_ylim(0, max(victim_probs) * 1.2)
    ax.grid(axis='y', alpha=0.3)

    for bar, prob in zip(bars, victim_probs):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{prob:.1f}%',
                ha='center', va='bottom', fontweight='bold', fontsize=10)

    plt.xticks(rotation=15, ha='right')
    plt.tight_layout()

    output_path = os.path.join(results_dir, 'victim_distribution.png')
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✅ Opfer-Verteilung gespeichert: {output_path}")

    print("\n" + "=" * 80)
    print("✅ ALLE GRAFIKEN ERSTELLT")
    print("=" * 80)
    print()


def main():
    stats = analyze_all_scenarios(num_players=10)
    create_role_distribution_chart(stats)


if __name__ == "__main__":
    main()
