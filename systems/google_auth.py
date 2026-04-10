"""
System: google_auth.py
Verantwoordelijkheid: OAuth2-authenticatie voor Google APIs (Docs + Gmail).
Lokaal: leest token.json en credentials.json uit de projectmap.
Productie (Railway): leest GOOGLE_TOKEN_JSON en GOOGLE_CREDENTIALS_JSON uit env vars.
"""

import os
import json
from pathlib import Path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

# Benodigde rechten
SCOPES = [
    "https://www.googleapis.com/auth/documents",
    "https://www.googleapis.com/auth/gmail.compose",
]

ROOT = Path(__file__).parent.parent
TOKEN_PATH = ROOT / "token.json"
CREDENTIALS_PATH = ROOT / "credentials.json"


def get_credentials() -> Credentials:
    """
    Haalt geldige Google OAuth2-credentials op.

    Volgorde:
    1. GOOGLE_TOKEN_JSON environment variable (productie/Railway)
    2. token.json bestand (lokale ontwikkeling)

    Raises:
        FileNotFoundError: Als geen token gevonden kan worden.
    """
    creds = None

    # --- Productie: lees token uit environment variable ---
    token_env = os.environ.get("GOOGLE_TOKEN_JSON", "").strip()
    if token_env:
        creds = Credentials.from_authorized_user_info(json.loads(token_env), SCOPES)

    # --- Lokaal: lees token uit bestand ---
    elif TOKEN_PATH.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_PATH), SCOPES)

    # --- Token vernieuwen als verlopen ---
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
        # Alleen lokaal opslaan (in productie werkt schrijven naar env var niet)
        if not token_env and TOKEN_PATH.exists():
            TOKEN_PATH.write_text(creds.to_json())
        return creds

    # --- Geen geldig token gevonden ---
    if not creds or not creds.valid:
        if token_env:
            raise RuntimeError(
                "Google token is ongeldig. Voer setup_google.py lokaal opnieuw uit "
                "en update de GOOGLE_TOKEN_JSON environment variable op Railway."
            )

        # Lokale OAuth-flow starten
        if not CREDENTIALS_PATH.exists():
            raise FileNotFoundError(
                "credentials.json niet gevonden. Voer setup_google.py uit."
            )
        flow = InstalledAppFlow.from_client_secrets_file(str(CREDENTIALS_PATH), SCOPES)
        creds = flow.run_local_server(port=0)
        TOKEN_PATH.write_text(creds.to_json())

    return creds
