"""
===============================================================================
PONY DIFFUSION STABILITY MATRIX PROMPT GENERATOR (INTERACTIVE)
===============================================================================

Version: 1.3.0
Date: 2025-12-26

Model Target: Pony Diffusion V6 XL

NEW IN v1.3.0
-------------
✔ Optional NSFW-safe toggle (uses `nsfw_tags` column if present)
✔ Fully commented logic for maintainability
✔ 100% backward compatible with older CSVs
"""

# =============================================================================
# STEP-BY-STEP SETUP (READ THIS!)
# =============================================================================
"""
1) INSTALL PYTHON
-----------------
https://www.python.org/downloads/
Use Python 3.8 or newer.

2) FOLDER STRUCTURE
-------------------
pony_matrix_prompt_generator/
├── pony_matrix_generator.py
├── prompts.txt (auto-created)
└── data/
    ├── characters.csv        (OPTIONAL column: nsfw_tags)
    ├── character_groups.csv
    ├── styles.csv
    ├── environments.csv
    ├── actions.csv
    ├── outfits.csv
    └── base_tags.csv

3) RUN
------
> python pony_matrix_generator.py
"""

# =============================================================================
# IMPORTS (STANDARD LIBRARY ONLY)
# =============================================================================

import csv
import random
from pathlib import Path
import os
import platform

# =============================================================================
# PATHS
# =============================================================================

DATA_DIR = Path("data")
OUTPUT_FILE = Path("prompts.txt")

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def clear_screen():
    """Clears the terminal for cleaner UI display."""
    os.system("cls" if platform.system() == "Windows" else "clear")

def print_header():
    """Prints fancy ASCII header."""
    print("╔════════════════════════════════════════════════════╗")
    print("║     🦄 Pony Diffusion Prompt Generator (v1.3)     ║")
    print("╚════════════════════════════════════════════════════╝\n")

def load_csv(filename):
    """
    Loads a CSV file from the /data directory.
    Returns a list of dictionaries (one per row).
    """
    with open(DATA_DIR / filename, "r", encoding="utf-8") as f:
        return list(csv.DictReader(f))

def parse_tags(tag_string):
    """
    Converts a pipe-separated tag string into a list.
    Example: "horn|wings|magic aura" → ["horn", "wings", "magic aura"]
    """
    return tag_string.split("|") if tag_string else []

def list_options(options, key="name"):
    """Displays a numbered list of selectable options."""
    print("╭───── OPTIONS ─────╮")
    for i, opt in enumerate(options, start=1):
        print(f"│ {i:2}) {opt[key]}")
    print("│  0) Random")
    print("╰───────────────────╯")

def select_option(options, label):
    """
    Prompts the user to select an option by number.
    Falls back to random on invalid input.
    """
    print(f"\n🔹 Select {label}:")
    list_options(options)
    try:
        choice = int(input("> "))
        if choice == 0:
            return random.choice(options)
        return options[choice - 1]
    except (ValueError, IndexError):
        print("⚠ Invalid input — using random.")
        return random.choice(options)

# =============================================================================
# LOAD ALL DATA FILES
# =============================================================================

characters = load_csv("characters.csv")
groups = load_csv("character_groups.csv")
styles = load_csv("styles.csv")
environments = load_csv("environments.csv")
actions = load_csv("actions.csv")
outfits = load_csv("outfits.csv")
base_tags = load_csv("base_tags.csv")

# =============================================================================
# BASE TAG EXTRACTION
# =============================================================================

positive_base = []
negative_base = []

for row in base_tags:
    if row["type"] == "positive":
        positive_base.extend(parse_tags(row["tags"]))
    elif row["type"] == "negative":
        negative_base.extend(parse_tags(row["tags"]))

# =============================================================================
# CHARACTER SELECTION
# =============================================================================

def choose_character():
    """
    Allows the user to choose between:
    - Solo character
    - Duo / Group combination
    """
    print("╔══════════════════════════════════════╗")
    print("║ Generate prompt for:                ║")
    print("║ 1) Solo Character                   ║")
    print("║ 2) Duo / Group                      ║")
    print("╚══════════════════════════════════════╝")
    mode = input("> ")

    if mode.strip() == "2":
        return select_option(groups, "Group"), True
    return select_option(characters, "Character"), False

# =============================================================================
# PROMPT GENERATION LOGIC
# =============================================================================

def generate_prompt(character, is_group, style, environment, action, outfit, include_nsfw):
    """
    Assembles the final positive and negative prompts.
    NSFW tags are appended ONLY if:
    - include_nsfw is True
    - character is solo
    - nsfw_tags column exists and is not empty
    """

    # Start with base quality / source tags
    pos_tags = list(positive_base)

    # Character tags
    pos_tags.extend(parse_tags(character["tags"]))

    # Optional NSFW tag injection (solo characters only)
    if (
        include_nsfw
        and not is_group
        and "nsfw_tags" in character
        and character.get("nsfw_tags")
    ):
        pos_tags.extend(parse_tags(character["nsfw_tags"]))

    # Remaining matrix components
    pos_tags.extend(parse_tags(style["tags"]))
    pos_tags.extend(parse_tags(environment["tags"]))
    pos_tags.extend(parse_tags(action["tags"]))
    pos_tags.extend(parse_tags(outfit["tags"]))

    # Final formatting
    pos_prompt = ", ".join(pos_tags)
    neg_prompt = ", ".join(negative_base)

    meta = (
        f"{character['name']} | "
        f"{style['name']} | "
        f"{environment['name']} | "
        f"{action['name']} | "
        f"{outfit['name']}"
    )

    return pos_prompt, neg_prompt, meta

# =============================================================================
# SAVE PROMPT TO FILE
# =============================================================================

def save_prompt(pos, neg, meta):
    """Appends a formatted prompt block to prompts.txt."""
    with open(OUTPUT_FILE, "a", encoding="utf-8") as f:
        f.write(f"# Prompt for: {meta}\n")
        f.write("Positive Prompt:\n```\n")
        f.write(pos + "\n```\n")
        f.write("Negative Prompt:\n```\n")
        f.write(neg + "\n```\n\n")

# =============================================================================
# MAIN FUNCTION
# =============================================================================

def main():
    clear_screen()
    print_header()

    # Global toggle for NSFW tags
    include_nsfw = input("🔞 Include NSFW tags (if available)? [y/N]: ").lower().startswith("y")

    # Character selection
    char, is_group = choose_character()
    clear_screen()
    print_header()

    # Matrix selections
    style = select_option(styles, "Style")
    clear_screen()
    print_header()

    environment = select_option(environments, "Environment")
    clear_screen()
    print_header()

    action = select_option(actions, "Action")
    clear_screen()
    print_header()

    outfit = select_option(outfits, "Outfit")
    clear_screen()
    print_header()

    # Prompt count
    try:
        count = int(input("🔸 How many prompts would you like to generate? > "))
    except ValueError:
        count = 1

    # Generate prompts
    for i in range(count):
        pos, neg, meta = generate_prompt(
            char,
            is_group,
            style,
            environment,
            action,
            outfit,
            include_nsfw
        )

        save_prompt(pos, neg, meta)

        print(f"\n✅ Prompt {i+1}/{count} for: {meta}")
        print("────────────────────────────")
        print("Positive Prompt:")
        print(pos)
        print("\nNegative Prompt:")
        print(neg)
        print("────────────────────────────")

    print(f"\n📁 All prompts saved to: {OUTPUT_FILE.resolve()}\n")

# =============================================================================
# RUN
# =============================================================================

if __name__ == "__main__":
    main()
