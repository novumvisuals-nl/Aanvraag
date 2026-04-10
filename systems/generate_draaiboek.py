"""
System: generate_draaiboek.py
Verantwoordelijkheid: Aanroepen van de Claude API om een professioneel draaiboek
te genereren op basis van de ingevulde projectgegevens.

Shot list & scènes worden automatisch gegenereerd op basis van het productietype.
Specifieke shot list templates per productietype worden later aangeleverd als documenten.
"""

import os
import time
import anthropic
from dotenv import load_dotenv

load_dotenv()


def generate_draaiboek(form_data: dict) -> str:
    """
    Genereert een professioneel draaiboek op basis van de formulierdata.

    Args:
        form_data: Dictionary met alle velden uit het dashboard-formulier.

    Returns:
        Het gegenereerde draaiboek als Markdown-string.

    Raises:
        ValueError: Als de ANTHROPIC_API_KEY niet is ingesteld.
        RuntimeError: Als de API-aanroep mislukt na maximale pogingen.
    """
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY is niet ingesteld in het .env bestand.")

    client = anthropic.Anthropic(api_key=api_key)
    prompt = _build_prompt(form_data)

    max_pogingen = 3
    for poging in range(1, max_pogingen + 1):
        try:
            bericht = client.messages.create(
                model="claude-opus-4-6",
                max_tokens=4096,
                messages=[{"role": "user", "content": prompt}],
            )
            return bericht.content[0].text

        except anthropic.RateLimitError:
            if poging < max_pogingen:
                time.sleep(60)
            else:
                raise RuntimeError("Rate limit bereikt. Probeer het over een minuut opnieuw.")
        except anthropic.APIError as e:
            raise RuntimeError(f"API-fout: {e}") from e


def _build_prompt(data: dict) -> str:
    """Bouwt de gedetailleerde prompt op voor de Claude API."""

    def veld(sleutel: str, standaard: str = "[INVULLEN]") -> str:
        waarde = data.get(sleutel, "").strip()
        return waarde if waarde else standaard

    medium = veld("medium", "Video")
    productie_type = veld("productie_type")
    is_video = medium.lower() == "video"

    # Shot list instructie – wordt later uitgebreid met specifieke templates per type
    shot_list_instructie = f"""
Genereer een professionele shot list voor een **{productie_type}** ({medium.lower()}productie).
Gebruik jouw kennis van professionele {medium.lower()}producties om realistische en praktische shots
samen te stellen die passen bij dit type productie en het opgegeven doel.
De shot list moet direct bruikbaar zijn op de set.
""".strip()

    muziek_sectie = ""
    if is_video and data.get("muziek_sound", "").strip():
        muziek_sectie = f"\n**Muziek / Sound:** {veld('muziek_sound')}"

    prompt = f"""Je bent een professionele productieleider gespecialiseerd in video- en fotoproducties voor bedrijven.
Schrijf een volledig en direct bruikbaar draaiboek in het Nederlands op basis van onderstaande projectinformatie.
Het draaiboek wordt gebruikt door de Novum Visuals crew op locatie. Wees concreet, praktisch en professioneel.

---

## PROJECTINFORMATIE

**Bedrijfsnaam:** {veld('bedrijfsnaam')}
**Projectnaam:** {veld('project_naam')}
**Gewenste opnamedag:** {veld('productie_datum')}
**Gewenste opleveringsdatum:** {veld('deadline_levering', 'Nader te bepalen')}

## PRODUCTIETYPE

**Medium:** {medium}
**Type productie:** {productie_type}
**Doel van de productie:** {veld('productie_doel', 'Niet opgegeven')}
**Doelgroep:** {veld('doelgroep', 'Niet opgegeven')}

## LOCATIE & PLANNING

**Locatie(s):** {veld('locaties')}
**Crew aanwezig om:** {veld('crew_aanvang', 'Nader te bepalen')}
**Start shoot:** {veld('shoot_aanvang', 'Nader te bepalen')}
**Verwachte eindtijd:** {veld('verwachte_eindtijd', 'Nader te bepalen')}
**Logistieke bijzonderheden:** {veld('logistieke_opmerkingen', 'Geen')}

## STIJL & WENSEN

**Stijl en referenties:** {veld('stijl_referenties', 'Geen specifieke wensen opgegeven')}{muziek_sectie}
**Speciale instructies:** {veld('speciale_instructies', 'Geen')}

---

## OPDRACHT

{shot_list_instructie}

Schrijf het draaiboek nu volledig uit met de volgende secties. Gebruik Markdown opmaak.

### 1. PROJECTOVERZICHT
Bondige samenvatting: bedrijf, project, medium, datum en deadline.

### 2. DAGSCHEMA
Gedetailleerde tijdlijn van de volledige productiedag.
Gebruik het formaat: `HH:MM – Activiteit`
Begin bij aankomst crew, eindig bij vertrek. Bouw realistische buffers in voor opbouw, afbouw en eventuele pauzes.

### 3. SHOT LIST
{shot_list_instructie}
Structureer per scène: scènenummer, locatie, omschrijving, stijl/camerahoek, geschatte duur.
Houd rekening met het opgegeven doel, de doelgroep en de stijlwensen.

### 4. LOCATIEOVERZICHT
Per locatie: omschrijving, aandachtspunten, bereikbaarheid.

### 5. CONTACTGEGEVENS
Gebruik [NAAM], [TEL], [EMAIL] als placeholders voor contactpersonen.

### 6. AANDACHTSPUNTEN & BIJZONDERHEDEN
Stijlrichtlijnen, klantwensen, logistieke details en overige opmerkingen.

Schrijf het draaiboek nu volledig uit. Professionele maar toegankelijke toon.
"""
    return prompt
