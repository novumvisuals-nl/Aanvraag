"""
setup_google.py
Voer dit script EENMALIG uit om je Google-account te koppelen.
Er opent een browser waar je inlogt en toegang geeft tot Google Docs en Gmail.
Daarna wordt token.json opgeslagen en hoef je dit niet meer te doen.

Gebruik:
    python3 setup_google.py
"""

from pathlib import Path
from systems.google_auth import get_credentials, TOKEN_PATH, CREDENTIALS_PATH

def main():
    print("\n🔐 Novum Visuals — Google Koppeling Setup\n")

    if not CREDENTIALS_PATH.exists():
        print("❌  credentials.json niet gevonden!")
        print()
        print("Stap 1: Ga naar https://console.cloud.google.com/")
        print("Stap 2: Maak een nieuw project aan (of gebruik een bestaand)")
        print("Stap 3: Schakel in: Google Docs API + Gmail API")
        print("        (via 'APIs & Services' → 'Enable APIs and Services')")
        print("Stap 4: Ga naar 'APIs & Services' → 'Credentials'")
        print("Stap 5: Klik 'Create Credentials' → 'OAuth client ID'")
        print("Stap 6: Kies type: 'Desktop app'")
        print("Stap 7: Download het JSON-bestand")
        print("Stap 8: Sla het op als 'credentials.json' in deze map:")
        print(f"        {CREDENTIALS_PATH}")
        print()
        print("Voer daarna dit script opnieuw uit.")
        return

    if TOKEN_PATH.exists():
        antwoord = input("token.json bestaat al. Opnieuw autoriseren? (j/n): ").strip().lower()
        if antwoord != "j":
            print("✅  Bestaande koppeling behouden.")
            return
        TOKEN_PATH.unlink()

    print("Een browser wordt geopend voor autorisatie...")
    print("Log in met je Novum Visuals Google-account.\n")

    try:
        creds = get_credentials()
        print(f"\n✅  Gelukt! Koppeling opgeslagen in: {TOKEN_PATH}")
        print("    De draaiboek generator kan nu Google Docs en Gmail gebruiken.")
    except Exception as e:
        print(f"\n❌  Fout tijdens autorisatie: {e}")

if __name__ == "__main__":
    main()
