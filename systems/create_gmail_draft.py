"""
System: create_gmail_draft.py
Verantwoordelijkheid: Aanmaken van een Gmail-concept met het draaiboek
en een link naar het Google Doc, klaar voor controle en verzending.
"""

import base64
import re
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from googleapiclient.discovery import build
from systems.google_auth import get_credentials


def create_gmail_draft(
    aan: str,
    onderwerp: str,
    bedrijfsnaam: str,
    project_naam: str,
    productie_datum: str,
    medium: str,
    productie_type: str,
    doc_url: str,
    draaiboek_markdown: str,
) -> str:
    """
    Maakt een Gmail-concept aan met het draaiboek.

    Args:
        aan: E-mailadres van de klant (mag leeg zijn).
        onderwerp: Onderwerpregel.
        bedrijfsnaam: Naam van het bedrijf.
        project_naam: Naam van het project.
        productie_datum: Datum van de opname.
        medium: "Video" of "Foto".
        productie_type: Bijv. "Brandmovie", "Portretfotografie".
        doc_url: URL naar het Google Doc (mag leeg zijn).
        draaiboek_markdown: De volledige draaiboektekst in Markdown.

    Returns:
        URL naar het Gmail-concept.
    """
    creds = get_credentials()
    service = build("gmail", "v1", credentials=creds)

    tekst_body = _maak_email_tekst(
        bedrijfsnaam, project_naam, productie_datum,
        medium, productie_type, doc_url, draaiboek_markdown
    )
    html_body = _maak_email_html(
        bedrijfsnaam, project_naam, productie_datum,
        medium, productie_type, doc_url, draaiboek_markdown
    )

    bericht = MIMEMultipart("alternative")
    bericht["Subject"] = onderwerp
    if aan:
        bericht["To"] = aan

    bericht.attach(MIMEText(tekst_body, "plain", "utf-8"))
    bericht.attach(MIMEText(html_body, "html", "utf-8"))

    raw = base64.urlsafe_b64encode(bericht.as_bytes()).decode("utf-8")

    concept = service.users().drafts().create(
        userId="me",
        body={"message": {"raw": raw}},
    ).execute()

    draft_id = concept.get("id")
    return f"https://mail.google.com/mail/#drafts/{draft_id}"


def _maak_email_tekst(bedrijfsnaam, project_naam, productie_datum,
                       medium, productie_type, doc_url, draaiboek) -> str:
    """Platte tekstversie van de e-mail."""
    doc_regel = f"\nBekijk het draaiboek ook online:\n{doc_url}\n" if doc_url else ""

    draaiboek_schoon = re.sub(r"\*\*(.+?)\*\*", r"\1", draaiboek)
    draaiboek_schoon = re.sub(r"^#{1,3} ", "", draaiboek_schoon, flags=re.MULTILINE)

    return f"""Beste {bedrijfsnaam},

Bedankt voor jullie aanvraag. Hierbij het draaiboek voor "{project_naam}" — {productie_type} ({medium}).
Opnamedatum: {productie_datum}
{doc_regel}
Lees het draaiboek door en laat ons weten als je vragen of aanpassingen hebt.

─────────────────────────────────────────

{draaiboek_schoon}

─────────────────────────────────────────

Met vriendelijke groet,

[NAAM]
Novum Visuals
info@novumvisuals.nl
www.novumvisuals.nl
"""


def _maak_email_html(bedrijfsnaam, project_naam, productie_datum,
                      medium, productie_type, doc_url, draaiboek) -> str:
    """HTML-versie van de e-mail met basic opmaak."""
    doc_knop = ""
    if doc_url:
        doc_knop = f"""
        <p style="margin:20px 0;">
          <a href="{doc_url}" style="
            display:inline-block;
            background:linear-gradient(135deg,#4D2E82,#A7328F);
            color:#ffffff;
            text-decoration:none;
            padding:12px 24px;
            border-radius:8px;
            font-family:Arial,sans-serif;
            font-size:14px;
            font-weight:bold;
            letter-spacing:1px;
          ">📄 Open draaiboek in Google Docs</a>
        </p>"""

    draaiboek_html = _markdown_naar_html(draaiboek)

    return f"""<!DOCTYPE html>
<html lang="nl">
<head><meta charset="UTF-8"></head>
<body style="background:#f4f4f4;margin:0;padding:32px 16px;font-family:Arial,sans-serif;">
  <div style="max-width:680px;margin:0 auto;background:#ffffff;border-radius:12px;overflow:hidden;box-shadow:0 2px 12px rgba(0,0,0,0.08);">

    <!-- Header -->
    <div style="background:linear-gradient(135deg,#4D2E82,#A7328F);padding:32px 40px;">
      <h1 style="margin:0;color:#ffffff;font-size:22px;font-weight:900;letter-spacing:1px;text-transform:uppercase;">
        Novum Visuals
      </h1>
      <p style="margin:6px 0 0;color:rgba(255,255,255,0.75);font-size:13px;text-transform:uppercase;letter-spacing:2px;">
        Draaiboek
      </p>
    </div>

    <!-- Intro -->
    <div style="padding:36px 40px 0;">
      <p style="font-size:16px;color:#333;margin:0 0 8px;">Beste <strong>{bedrijfsnaam}</strong>,</p>
      <p style="font-size:15px;color:#555;line-height:1.6;margin:0 0 16px;">
        Bedankt voor jullie aanvraag. Hierbij het draaiboek voor
        <strong>{project_naam}</strong> — {productie_type} ({medium}).
        Opnamedatum: <strong>{productie_datum}</strong>.
      </p>
      <p style="font-size:15px;color:#555;margin:0;">
        Lees het draaiboek door en laat ons weten als je vragen of aanpassingen hebt.
      </p>
      {doc_knop}
    </div>

    <!-- Divider -->
    <div style="margin:0 40px;border-top:1px solid #e8e8e8;"></div>

    <!-- Draaiboek inhoud -->
    <div style="padding:32px 40px;">
      {draaiboek_html}
    </div>

    <!-- Divider -->
    <div style="margin:0 40px;border-top:1px solid #e8e8e8;"></div>

    <!-- Footer -->
    <div style="padding:28px 40px;background:#fafafa;">
      <p style="margin:0;font-size:14px;color:#888;line-height:1.7;">
        Met vriendelijke groet,<br>
        <strong style="color:#333;">[NAAM]</strong><br>
        Novum Visuals<br>
        <a href="mailto:info@novumvisuals.nl" style="color:#A7328F;">info@novumvisuals.nl</a> ·
        <a href="https://www.novumvisuals.nl" style="color:#A7328F;">www.novumvisuals.nl</a>
      </p>
    </div>

  </div>
</body>
</html>"""


def _markdown_naar_html(markdown: str) -> str:
    """Converteert Markdown naar eenvoudige HTML voor de e-mail."""
    regels = markdown.split("\n")
    html_delen = []
    in_lijst = False

    for regel in regels:
        stripped = regel.rstrip()

        if not stripped:
            if in_lijst:
                html_delen.append("</ul>")
                in_lijst = False
            html_delen.append("")
            continue

        if stripped.startswith("# "):
            tekst = stripped[2:]
            html_delen.append(
                f'<h2 style="color:#1a1a1a;font-size:20px;font-weight:900;'
                f'text-transform:uppercase;letter-spacing:1px;'
                f'margin:28px 0 10px;padding-bottom:8px;'
                f'border-bottom:2px solid #f0e8f8;">{tekst}</h2>'
            )
        elif stripped.startswith("## "):
            tekst = stripped[3:]
            html_delen.append(
                f'<h3 style="color:#4D2E82;font-size:15px;font-weight:700;'
                f'text-transform:uppercase;letter-spacing:1px;'
                f'margin:20px 0 8px;">{tekst}</h3>'
            )
        elif stripped.startswith("### "):
            tekst = stripped[4:]
            html_delen.append(
                f'<h4 style="color:#A7328F;font-size:13px;font-weight:700;'
                f'text-transform:uppercase;letter-spacing:0.5px;'
                f'margin:16px 0 6px;">{tekst}</h4>'
            )
        elif stripped.startswith("---"):
            html_delen.append('<hr style="border:none;border-top:1px solid #eeeeee;margin:20px 0;">')
        elif stripped.startswith(("- ", "* ")):
            if not in_lijst:
                html_delen.append('<ul style="padding-left:20px;margin:8px 0;">')
                in_lijst = True
            tekst = _inline_opmaak(stripped[2:])
            html_delen.append(f'<li style="color:#444;font-size:14px;margin-bottom:5px;">{tekst}</li>')
        else:
            if in_lijst:
                html_delen.append("</ul>")
                in_lijst = False
            tekst = _inline_opmaak(stripped)
            html_delen.append(
                f'<p style="color:#444;font-size:14px;line-height:1.65;margin:0 0 8px;">{tekst}</p>'
            )

    if in_lijst:
        html_delen.append("</ul>")

    return "\n".join(html_delen)


def _inline_opmaak(tekst: str) -> str:
    """Verwerkt inline Markdown (vet, cursief) naar HTML."""
    tekst = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", tekst)
    tekst = re.sub(r"\*(.+?)\*", r"<em>\1</em>", tekst)
    return tekst
