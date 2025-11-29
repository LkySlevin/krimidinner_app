#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Testsimulation für alle möglichen Kombinationen des Krimidinner-Spiels.
Simuliert alle Kombinationen von Events und analysiert die Häufigkeit von Mördern und Opfern.
"""

import sys
import os
from collections import defaultdict
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Backend für nicht-interaktive Plots

# Füge den Parent-Ordner zum Pfad hinzu, um app.py zu importieren
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import (
    CHARACTERS,
    NPCS,
    determine_victim,
    select_werewolf,
    MOTIVE_MATRIX
)

def simulate_all_combinations():
    """
    Simuliert alle möglichen Event-Kombinationen und zählt,
    wie oft jeder Charakter als Mörder oder Opfer ausgewählt wird.
    """

    # Zähler für Mörder und Opfer
    murderer_counts = defaultdict(int)
    victim_counts = defaultdict(lambda: defaultdict(int))

    # Alle 10 Spieler sind aktiv
    active_chars = CHARACTERS.copy()

    # Mögliche Werte für Events: None oder char_id (1-10)
    event_options = [None] + [char["id"] for char in CHARACTERS]

    total_combinations = 0
    results = []

    print("🎲 Starte Simulation aller Kombinationen...")
    print(f"📊 Anzahl möglicher Event-Kombinationen: {len(event_options)}³ × 7 Tage = {len(event_options)**3 * 7:,}")
    print()

    # Iteriere durch alle Kombinationen von Event1, Event2, Event3, Wochentag
    for event1 in event_options:
        for event2 in event_options:
            for event3 in event_options:
                for weekday in range(7):  # Alle Wochentage durchspielen
                    seed_tuple = (event1, event2, event3, weekday)

                    # Bestimme das Opfer
                    victim = determine_victim(event2, event1, event3, seed_tuple)

                    # Bestimme den Mörder (gewichtet nach Motiv)
                    murderer_id = select_werewolf(active_chars, seed_tuple, victim)

                    # Zähle
                    murderer_counts[murderer_id] += 1
                    victim_counts[victim["name"]][murderer_id] += 1

                    total_combinations += 1

                    # Speichere Details für spätere Analyse
                    results.append({
                        "event1": event1,
                        "event2": event2,
                        "event3": event3,
                        "weekday": weekday,
                        "victim": victim["name"],
                        "murderer_id": murderer_id
                    })

    print(f"✅ Simulation abgeschlossen!")
    print(f"📈 Insgesamt {total_combinations} Kombinationen simuliert")
    print()

    return murderer_counts, victim_counts, results, total_combinations


def print_statistics(murderer_counts, victim_counts, total_combinations):
    """Gibt detaillierte Statistiken aus"""

    print("="*80)
    print("📊 STATISTIK: Wie oft wird jeder Charakter zum Mörder?")
    print("="*80)
    print()

    # Sortiere nach Häufigkeit (absteigend)
    sorted_murderers = sorted(murderer_counts.items(), key=lambda x: x[1], reverse=True)

    for char_id, count in sorted_murderers:
        char = next(c for c in CHARACTERS if c["id"] == char_id)
        percentage = (count / total_combinations) * 100
        bar = "█" * int(percentage / 2)
        print(f"{char['letter']} {char['name']:30s} │ {count:6d} mal │ {percentage:5.2f}% │ {bar}")

    print()
    print("="*80)
    print("🔪 STATISTIK: Wie oft wird welches NPC zum Opfer?")
    print("="*80)
    print()

    for victim_name, murderer_dict in victim_counts.items():
        total_victim = sum(murderer_dict.values())
        percentage = (total_victim / total_combinations) * 100
        print(f"{victim_name:30s} │ {total_victim:6d} mal │ {percentage:5.2f}%")

    print()


def create_visualizations(murderer_counts, victim_counts, total_combinations):
    """Erstellt Grafiken zur Visualisierung der Ergebnisse"""

    # Erstelle Ausgabeordner
    output_dir = os.path.join(os.path.dirname(__file__), "results")
    os.makedirs(output_dir, exist_ok=True)

    # === GRAFIK 1: Mörder-Häufigkeit ===
    fig1, ax1 = plt.subplots(figsize=(14, 8))

    # Sortiere nach Häufigkeit
    sorted_murderers = sorted(murderer_counts.items(), key=lambda x: x[1], reverse=True)
    char_names = [next(c for c in CHARACTERS if c["id"] == char_id)["name"] for char_id, _ in sorted_murderers]
    char_letters = [next(c for c in CHARACTERS if c["id"] == char_id)["letter"] for char_id, _ in sorted_murderers]
    counts = [count for _, count in sorted_murderers]
    percentages = [(count / total_combinations) * 100 for count in counts]

    # Erstelle Labels mit Buchstaben
    labels = [f"[{letter}] {name}" for letter, name in zip(char_letters, char_names)]

    bars = ax1.barh(labels, counts, color='#e74c3c')
    ax1.set_xlabel('Anzahl als Mörder ausgewählt', fontsize=12, fontweight='bold')
    ax1.set_title(f'Mörder-Häufigkeit über {total_combinations:,} Simulationen', fontsize=14, fontweight='bold')
    ax1.grid(axis='x', alpha=0.3)

    # Füge Prozentangaben hinzu
    for i, (bar, pct) in enumerate(zip(bars, percentages)):
        width = bar.get_width()
        ax1.text(width, bar.get_y() + bar.get_height()/2,
                f' {pct:.1f}%',
                ha='left', va='center', fontweight='bold')

    plt.tight_layout()
    fig1.savefig(os.path.join(output_dir, 'murderer_frequency.png'), dpi=300, bbox_inches='tight')
    print(f"✅ Grafik gespeichert: {os.path.join(output_dir, 'murderer_frequency.png')}")

    # === GRAFIK 2: Opfer-Häufigkeit ===
    fig2, ax2 = plt.subplots(figsize=(10, 6))

    victim_names = list(victim_counts.keys())
    victim_totals = [sum(murderer_dict.values()) for murderer_dict in victim_counts.values()]
    victim_percentages = [(total / total_combinations) * 100 for total in victim_totals]

    bars2 = ax2.bar(victim_names, victim_totals, color=['#3498db', '#2ecc71', '#f39c12'])
    ax2.set_ylabel('Anzahl als Opfer ausgewählt', fontsize=12, fontweight='bold')
    ax2.set_title(f'Opfer-Häufigkeit über {total_combinations:,} Simulationen', fontsize=14, fontweight='bold')
    ax2.grid(axis='y', alpha=0.3)

    # Füge Prozentangaben hinzu
    for bar, pct in zip(bars2, victim_percentages):
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2, height,
                f'{pct:.1f}%',
                ha='center', va='bottom', fontweight='bold', fontsize=10)

    plt.xticks(rotation=15, ha='right')
    plt.tight_layout()
    fig2.savefig(os.path.join(output_dir, 'victim_frequency.png'), dpi=300, bbox_inches='tight')
    print(f"✅ Grafik gespeichert: {os.path.join(output_dir, 'victim_frequency.png')}")

    # === GRAFIK 3: Heatmap - Mörder pro Opfer ===
    fig3, ax3 = plt.subplots(figsize=(14, 10))

    # Erstelle Matrix: Zeilen = Charaktere, Spalten = Opfer
    matrix = []
    for char in CHARACTERS:
        row = []
        for victim_name in victim_names:
            count = victim_counts[victim_name].get(char["id"], 0)
            row.append(count)
        matrix.append(row)

    im = ax3.imshow(matrix, cmap='YlOrRd', aspect='auto')

    # Achsenbeschriftungen
    ax3.set_xticks(range(len(victim_names)))
    ax3.set_yticks(range(len(CHARACTERS)))
    ax3.set_xticklabels(victim_names, rotation=45, ha='right')
    ax3.set_yticklabels([f"[{c['letter']}] {c['name']}" for c in CHARACTERS])

    ax3.set_xlabel('Opfer (NPCs)', fontsize=12, fontweight='bold')
    ax3.set_ylabel('Mörder (Charaktere)', fontsize=12, fontweight='bold')
    ax3.set_title('Häufigkeit: Welcher Charakter wird bei welchem Opfer zum Mörder?', fontsize=14, fontweight='bold')

    # Füge Zahlen in Zellen ein
    for i in range(len(CHARACTERS)):
        for j in range(len(victim_names)):
            text = ax3.text(j, i, matrix[i][j],
                          ha="center", va="center", color="black", fontsize=8)

    # Colorbar
    cbar = plt.colorbar(im, ax=ax3)
    cbar.set_label('Anzahl', rotation=270, labelpad=20, fontweight='bold')

    plt.tight_layout()
    fig3.savefig(os.path.join(output_dir, 'murderer_victim_heatmap.png'), dpi=300, bbox_inches='tight')
    print(f"✅ Grafik gespeichert: {os.path.join(output_dir, 'murderer_victim_heatmap.png')}")

    # === GRAFIK 4: Motiv-Einfluss ===
    fig4, ax4 = plt.subplots(figsize=(12, 8))

    # Berechne für jeden Charakter den Anteil mit/ohne Motiv
    chars_with_motive = []
    chars_without_motive = []
    char_labels = []

    for char in CHARACTERS:
        char_labels.append(f"[{char['letter']}] {char['name']}")

        # Zähle wie oft dieser Charakter Mörder wurde, wenn er ein Motiv hatte
        with_motive = 0
        without_motive = 0

        for victim_name, murderer_dict in victim_counts.items():
            count = murderer_dict.get(char["id"], 0)

            # Prüfe ob Charakter ein Motiv für dieses Opfer hat
            has_motive = victim_name in MOTIVE_MATRIX.get(char["id"], {})

            if has_motive:
                with_motive += count
            else:
                without_motive += count

        chars_with_motive.append(with_motive)
        chars_without_motive.append(without_motive)

    x = range(len(CHARACTERS))
    width = 0.35

    bars1 = ax4.bar([i - width/2 for i in x], chars_with_motive, width,
                    label='Mit Motiv', color='#e74c3c', alpha=0.8)
    bars2 = ax4.bar([i + width/2 for i in x], chars_without_motive, width,
                    label='Ohne Motiv', color='#95a5a6', alpha=0.8)

    ax4.set_xlabel('Charakter', fontsize=12, fontweight='bold')
    ax4.set_ylabel('Anzahl als Mörder ausgewählt', fontsize=12, fontweight='bold')
    ax4.set_title('Einfluss von Motiven auf Mörder-Auswahl', fontsize=14, fontweight='bold')
    ax4.set_xticks(x)
    ax4.set_xticklabels(char_labels, rotation=45, ha='right')
    ax4.legend()
    ax4.grid(axis='y', alpha=0.3)

    plt.tight_layout()
    fig4.savefig(os.path.join(output_dir, 'motive_influence.png'), dpi=300, bbox_inches='tight')
    print(f"✅ Grafik gespeichert: {os.path.join(output_dir, 'motive_influence.png')}")

    print()
    print(f"📁 Alle Grafiken gespeichert in: {output_dir}")


def analyze_motive_impact(murderer_counts, victim_counts, total_combinations):
    """Analysiert den Einfluss von Motiven auf die Mörder-Auswahl"""

    print("="*80)
    print("🎯 ANALYSE: Einfluss von Motiven auf die Mörder-Auswahl")
    print("="*80)
    print()

    for char in CHARACTERS:
        # Zähle wie oft dieser Charakter Mörder wurde
        total_as_murderer = murderer_counts[char["id"]]

        # Zähle wie oft mit/ohne Motiv
        with_motive = 0
        without_motive = 0

        for victim_name, murderer_dict in victim_counts.items():
            count = murderer_dict.get(char["id"], 0)
            has_motive = victim_name in MOTIVE_MATRIX.get(char["id"], {})

            if has_motive:
                with_motive += count
            else:
                without_motive += count

        # Berechne Verhältnis
        if total_as_murderer > 0:
            motive_ratio = (with_motive / total_as_murderer) * 100
            print(f"{char['letter']} {char['name']:30s} │ Mit Motiv: {with_motive:6d} ({motive_ratio:5.1f}%) │ Ohne Motiv: {without_motive:6d}")

    print()


if __name__ == "__main__":
    print()
    print("="*80)
    print("🕵️ KRIMIDINNER - VOLLSTÄNDIGE SIMULATIONS-ANALYSE")
    print("="*80)
    print()

    # Führe Simulation durch
    murderer_counts, victim_counts, results, total_combinations = simulate_all_combinations()

    # Zeige Statistiken
    print_statistics(murderer_counts, victim_counts, total_combinations)

    # Analyse Motiv-Einfluss
    analyze_motive_impact(murderer_counts, victim_counts, total_combinations)

    # Erstelle Visualisierungen
    print("="*80)
    print("📊 Erstelle Visualisierungen...")
    print("="*80)
    print()
    create_visualizations(murderer_counts, victim_counts, total_combinations)

    print()
    print("="*80)
    print("✅ SIMULATION ABGESCHLOSSEN!")
    print("="*80)
    print()
