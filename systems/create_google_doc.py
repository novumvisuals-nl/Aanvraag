"""
System: create_google_doc.py
Verantwoordelijkheid: Aanmaken van een opgemaakt Google Doc met het draaiboek.
Converteert Markdown naar Google Docs native opmaak (koppen, lijsten, vet).
"""

import re
from googleapiclient.discovery import build
from systems.google_auth import get_credentials


def create_google_doc(titel: str, markdown_inhoud: str) -> str:
    """
    Maakt een nieuw Google Doc aan met het draaiboek.

    Args:
        titel: Documenttitel (bijv. "Draaiboek – Brandmovie – Acme B.V.")
        markdown_inhoud: De draaiboektekst in Markdown-formaat.

    Returns:
        Directe bewerkings-URL van het aangemaakte document.
    """
    creds = get_credentials()
    service = build("docs", "v1", credentials=creds)

    # Maak leeg document aan
    doc = service.documents().create(body={"title": titel}).execute()
    doc_id = doc.get("documentId")

    # Bouw API-requests op vanuit de markdown
    requests = _markdown_naar_requests(markdown_inhoud)

    if requests:
        service.documents().batchUpdate(
            documentId=doc_id,
            body={"requests": requests},
        ).execute()

    return f"https://docs.google.com/document/d/{doc_id}/edit"


def _markdown_naar_requests(markdown: str, start_index: int = 1) -> list:
    """
    Converteert Markdown naar een lijst van Google Docs API-requests.
    Stap 1: één insertText voor de volledige inhoud (markdown-syntax gestript).
    Stap 2: updateParagraphStyle per kop.
    Stap 3: updateTextStyle voor vetgedrukte tekst.
    """
    regels = markdown.split("\n")

    volledige_tekst = ""
    stijl_acties = []   # (abs_start, abs_end, named_style)
    vet_acties = []     # (abs_start, abs_end)

    huidige_offset = 0

    for regel in regels:
        stripped = regel.rstrip()

        if not stripped:
            volledige_tekst += "\n"
            huidige_offset += 1
            continue

        # Bepaal alineastijl en strip koptekens
        if stripped.startswith("# "):
            schone = stripped[2:] + "\n"
            stijl = "HEADING_1"
        elif stripped.startswith("## "):
            schone = stripped[3:] + "\n"
            stijl = "HEADING_2"
        elif stripped.startswith("### "):
            schone = stripped[4:] + "\n"
            stijl = "HEADING_3"
        elif stripped.startswith("---"):
            schone = "\n"
            stijl = None
        elif stripped.startswith(("- ", "* ")):
            schone = stripped[2:] + "\n"
            stijl = "NORMAL_TEXT"
        else:
            schone = stripped + "\n"
            stijl = "NORMAL_TEXT"

        # Detecteer vette stukken binnen de tekst (voor niet-kopreges)
        if stijl == "NORMAL_TEXT":
            pos_in_schone = 0
            schone_zonder_vet = ""
            for m in re.finditer(r"\*\*(.+?)\*\*", schone):
                # Tekst voor de vet-markering
                schone_zonder_vet += schone[pos_in_schone : m.start()]
                vet_start_off = huidige_offset + len(schone_zonder_vet.encode("utf-16-le")) // 2
                vet_tekst = m.group(1)
                schone_zonder_vet += vet_tekst
                vet_end_off = huidige_offset + len(schone_zonder_vet.encode("utf-16-le")) // 2
                vet_acties.append((start_index + vet_start_off, start_index + vet_end_off))
                pos_in_schone = m.end()
            schone_zonder_vet += schone[pos_in_schone:]
            schone = schone_zonder_vet

        offset_start = huidige_offset
        # Google Docs telt UTF-16 code units
        offset_end = offset_start + len(schone.encode("utf-16-le")) // 2

        if stijl and stijl != "NORMAL_TEXT":
            stijl_acties.append((
                start_index + offset_start,
                start_index + offset_end,
                stijl,
            ))

        volledige_tekst += schone
        huidige_offset = offset_end

    # --- Request 1: Volledige tekst invoegen ---
    requests = [
        {
            "insertText": {
                "location": {"index": start_index},
                "text": volledige_tekst,
            }
        }
    ]

    # --- Requests 2+: Alineastijlen toepassen ---
    for abs_start, abs_end, stijl in stijl_acties:
        requests.append(
            {
                "updateParagraphStyle": {
                    "range": {
                        "startIndex": abs_start,
                        "endIndex": abs_end,
                    },
                    "paragraphStyle": {"namedStyleType": stijl},
                    "fields": "namedStyleType",
                }
            }
        )

    # --- Requests 3+: Vetgedrukte tekst ---
    for abs_start, abs_end in vet_acties:
        requests.append(
            {
                "updateTextStyle": {
                    "range": {
                        "startIndex": abs_start,
                        "endIndex": abs_end,
                    },
                    "textStyle": {"bold": True},
                    "fields": "bold",
                }
            }
        )

    return requests
