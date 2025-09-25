# clear_github_issues.py
"""
Deletes all CLOSED issues in the current GitHub repository.
This is useful for cleaning up the 'Done' column in a project board after a bulk close.

@layer: Tool
@dependencies:
    - GitHub CLI (must be installed and authenticated)
@responsibilities:
    - Fetches all closed issue numbers.
    - Executes `gh issue delete` for each issue.
@inputs: None
@outputs:
    - Deletes issues in the GitHub repository.
"""

import subprocess
import json
import sys
import shutil

def check_gh_cli():
    """Checks if the GitHub CLI tool 'gh' is installed and accessible."""
    if not shutil.which("gh"):
        print("❌ FOUT: De GitHub CLI ('gh') is niet geïnstalleerd of niet gevonden in je PATH.")
        print("   Installeer het via: https://cli.github.com/")
        return False
    return True

def get_closed_issue_numbers() -> list[int]:
    """Fetches a list of all CLOSED issue numbers from the repository."""
    print("Ophalen van alle gesloten issues...", end='', flush=True)
    try:
        # De enige wijziging is hier: --state "closed"
        command = ["gh", "issue", "list", "--state", "closed", "--json", "number"]
        result = subprocess.run(command, check=True, capture_output=True, text=True, encoding='utf-8')
        issues = json.loads(result.stdout)
        issue_numbers = [issue['number'] for issue in issues]
        print(f" ✅ {len(issue_numbers)} gevonden.")
        return issue_numbers
    except (subprocess.CalledProcessError, json.JSONDecodeError) as e:
        print(f"\n❌ FOUT: Kon gesloten issues niet ophalen: {e}")
        return []

def delete_issue(issue_number: int):
    """Deletes a single GitHub issue by its number."""
    print(f"   Issue #{issue_number} verwijderen...", end='', flush=True)
    # Gebruik 'issue delete' en de '--yes' vlag om de interactieve prompt over te slaan
    command = ["gh", "issue", "delete", str(issue_number), "--yes"]
    try:
        subprocess.run(command, check=True, capture_output=True, text=True, encoding='utf-8')
        print(" ✅")
    except subprocess.CalledProcessError as e:
        print(" ❌ Fout!")
        print(f"      Error bij verwijderen van issue: {e.stderr.strip()}")

def main():
    """Main function to fetch and delete all closed issues."""
    if not check_gh_cli():
        return

    print("🚀 Starten met het permanent verwijderen van GESLOTEN issues...")
    print("-" * 60)

    issue_numbers = get_closed_issue_numbers()

    if not issue_numbers:
        print("Geen gesloten issues gevonden om te verwijderen.")
    else:
        # User confirmation with a clear warning
        print("⚠️ WAARSCHUWING: Deze actie is permanent en kan niet ongedaan worden gemaakt.")
        confirm = input(f"Je staat op het punt om {len(issue_numbers)} GESLOTEN issues permanent te VERWIJDEREN. Weet je het zeker? (ja/nee): ")
        if confirm.lower() not in ['ja', 'y']:
            print("Actie geannuleerd.")
            return

        for number in issue_numbers:
            delete_issue(number)

    print("-" * 60)
    print("✅ Opschonen van de 'Done' lijst is voltooid.")

if __name__ == "__main__":
    main()

