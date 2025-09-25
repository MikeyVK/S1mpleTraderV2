# backlog_to_github.py
"""
Reads a product_backlog.csv file and creates GitHub issues for each entry
using the GitHub CLI (`gh`). It automatically creates labels if they don't exist.

@layer: Tool
@dependencies:
    - GitHub CLI (must be installed and authenticated)
@responsibilities:
    - Parses a CSV file with backlog items.
    - Ensures required labels exist in the GitHub repository.
    - Constructs and executes `gh issue create` commands.
@inputs:
    - A `product_backlog.csv` file in the same directory.
@outputs:
    - Creates GitHub issues in the repository associated with the current directory.
"""

import csv
import subprocess
import shutil
import sys
import json
import random

# --- Constants ---
BACKLOG_FILE = 'product_backlog.csv'

# --- Global Cache ---
# A set to store the names of labels that are confirmed to exist in the repo.
EXISTING_LABELS = set()

def check_gh_cli():
    """Checks if the GitHub CLI tool 'gh' is installed and accessible."""
    if not shutil.which("gh"):
        print("❌ FOUT: De GitHub CLI ('gh') is niet geïnstalleerd of niet gevonden in je PATH.")
        print("   Installeer het via: https://cli.github.com/")
        return False
    return True

def populate_existing_labels_cache():
    """
    Fetches all existing labels from the repository once and stores them in the
    global cache to minimize API calls.
    """
    global EXISTING_LABELS
    print("Labels in de repository controleren...", end='', flush=True)
    try:
        command = ["gh", "label", "list", "--json", "name"]
        result = subprocess.run(command, check=True, capture_output=True, text=True, encoding='utf-8')
        labels = json.loads(result.stdout)
        EXISTING_LABELS = {label['name'] for label in labels}
        print(f" ✅ {len(EXISTING_LABELS)} labels gevonden.")
    except (subprocess.CalledProcessError, json.JSONDecodeError) as e:
        print(f"\n⚠️ Waarschuwing: Kon bestaande labels niet ophalen: {e}.")
        print("   Het script zal proberen de labels aan te maken, dit kan mislukken als ze al bestaan.")
        EXISTING_LABELS = set()

def ensure_label_exists(label_name):
    """
    Checks if a label exists locally, and if not, creates it via the GitHub CLI.
    """
    # Check against the cache first.
    if label_name in EXISTING_LABELS:
        return

    # If not in cache, create it.
    print(f"   Label '{label_name}' niet gevonden, wordt aangemaakt...", end='', flush=True)
    
    # Generate a random color for better visual distinction.
    color = f'{random.randint(0, 0xFFFFFF):06x}'
    
    command = [
        "gh", "label", "create", label_name,
        "--color", color,
        "--description", "Automatisch aangemaakt door backlog script."
    ]
    
    try:
        subprocess.run(command, check=True, capture_output=True, text=True, encoding='utf-8')
        print(" ✅")
        # Add the newly created label to the cache to avoid re-creating it.
        EXISTING_LABELS.add(label_name)
    except subprocess.CalledProcessError as e:
        # Handle the case where the label might already exist but wasn't in our initial fetch.
        if "already exists" in e.stderr:
            print(" ⚠️  Bestond al.")
            EXISTING_LABELS.add(label_name)
        else:
            print(" ❌ Fout!")
            print(f"      Error bij aanmaken van label: {e.stderr.strip()}")

def create_github_issue(title, release, fase, issue_type):
    """Creates a single GitHub issue with appropriate labels."""
    # Define the desired labels
    release_label = f"Release: {release}"
    fase_label = f"Fase: {fase}"
    type_label = f"Type: {issue_type}"
    
    # Ensure all labels exist before creating the issue
    ensure_label_exists(release_label)
    ensure_label_exists(fase_label)
    ensure_label_exists(type_label)

    # Construct the issue creation command
    command = [
        "gh", "issue", "create",
        "--title", title,
        "--body", f"Automatisch aangemaakt vanuit de product backlog voor **Release {release}**.",
        "--label", release_label,
        "--label", fase_label,
        "--label", type_label
    ]

    try:
        print(f"Issue aanmaken voor: '{title}'...", end='', flush=True)
        result = subprocess.run(command, check=True, capture_output=True, text=True, encoding='utf-8')
        print(f" ✅ Gelukt! ({result.stdout.strip()})")
    except subprocess.CalledProcessError as e:
        print(" ❌ Fout!")
        print(f"   Error bij het aanmaken van issue: {e.stderr.strip()}")

def main():
    """Main function to read the backlog and create all issues."""
    if not check_gh_cli():
        return

    print("🚀 Starten met het aanmaken van GitHub issues vanuit de backlog...")
    print("-" * 60)

    # 1. Fetch existing labels once at the beginning
    populate_existing_labels_cache()
    
    # 2. Process the CSV file
    try:
        with open(BACKLOG_FILE, mode='r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile, delimiter=';')
            for row in reader:
                create_github_issue(
                    title=row['User Story'],
                    release=row['Release'],
                    fase=row['Fase'],
                    issue_type=row['Type']
                )
    except FileNotFoundError:
        print(f"❌ FOUT: Het bestand '{BACKLOG_FILE}' niet gevonden in de huidige map.")
        return
    except KeyError as e:
        print(f"❌ FOUT: Een verwachte kolom ontbreekt in je CSV-bestand: {e}")
        return

    print("-" * 60)
    print("✅ Alle items uit de backlog zijn verwerkt.")

if __name__ == "__main__":
    main()

