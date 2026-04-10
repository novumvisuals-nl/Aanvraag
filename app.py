"""
Orchestrator: app.py
Flask-dashboard voor de Draaiboek Generator.
Coördineert: Claude API → Google Docs → Gmail concept.
"""

import logging
from flask import Flask, render_template, request, jsonify
from systems.generate_draaiboek import generate_draaiboek

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/genereer", methods=["POST"])
def genereer():
    """
    Ontvangt formulierdata en:
    1. Genereert een draaiboek via Claude API
    2. Maakt een Google Doc aan (als credentials beschikbaar zijn)
    3. Maakt een Gmail concept aan (als credentials beschikbaar zijn)
    """
    form_data = request.get_json()

    if not form_data:
        return jsonify({"fout": "Geen formulierdata ontvangen."}), 400

    verplichte_velden = ["bedrijfsnaam", "project_naam", "productie_datum", "medium", "productie_type"]
    ontbrekend = [v for v in verplichte_velden if not form_data.get(v, "").strip()]
    if ontbrekend:
        return jsonify({"fout": f"Vul de verplichte velden in: {', '.join(ontbrekend)}"}), 400

    # --- Stap 1: Genereer draaiboek via Claude ---
    try:
        draaiboek = generate_draaiboek(form_data)
    except ValueError as e:
        return jsonify({"fout": str(e)}), 500
    except RuntimeError as e:
        return jsonify({"fout": str(e)}), 503

    # --- Stap 2: Maak Google Doc aan ---
    doc_url = None
    try:
        from systems.create_google_doc import create_google_doc
        titel = (
            f"Draaiboek – {form_data.get('productie_type', '')} – "
            f"{form_data.get('bedrijfsnaam', '')} – {form_data.get('productie_datum', '')}"
        )
        doc_url = create_google_doc(titel, draaiboek)
        app.logger.info(f"Google Doc aangemaakt: {doc_url}")
    except FileNotFoundError:
        app.logger.warning("Google credentials.json niet gevonden — Google Doc overgeslagen.")
    except Exception as e:
        app.logger.warning(f"Google Doc aanmaken mislukt: {e}")

    # --- Stap 3: Maak Gmail concept aan ---
    draft_url = None
    try:
        from systems.create_gmail_draft import create_gmail_draft
        draft_url = create_gmail_draft(
            aan=form_data.get("email_klant", ""),
            onderwerp=(
                f"Draaiboek {form_data.get('productie_type', '')} – "
                f"{form_data.get('bedrijfsnaam', '')} – {form_data.get('productie_datum', '')}"
            ),
            bedrijfsnaam=form_data.get("bedrijfsnaam", ""),
            project_naam=form_data.get("project_naam", ""),
            productie_datum=form_data.get("productie_datum", ""),
            medium=form_data.get("medium", ""),
            productie_type=form_data.get("productie_type", ""),
            doc_url=doc_url or "",
            draaiboek_markdown=draaiboek,
        )
        app.logger.info(f"Gmail concept aangemaakt: {draft_url}")
    except FileNotFoundError:
        app.logger.warning("Google credentials.json niet gevonden — Gmail concept overgeslagen.")
    except Exception as e:
        app.logger.warning(f"Gmail concept aanmaken mislukt: {e}")

    return jsonify({
        "draaiboek": draaiboek,
        "doc_url": doc_url,
        "draft_url": draft_url,
    })


if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5001))
    app.run(debug=False, host="0.0.0.0", port=port)
