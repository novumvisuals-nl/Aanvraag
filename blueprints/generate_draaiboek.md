# Blueprint: Draaiboek Generator

## Doel

Genereer een professioneel en volledig draaiboek voor video- en fotoproducties op basis van ingevulde projectgegevens. Het draaiboek wordt gebruikt door crew op locatie en moet direct bruikbaar zijn zonder verdere uitleg.

## Benodigde input

De volgende velden worden verzameld via het dashboard-formulier:

### Stap 1 – Projectgegevens
- `klant_naam`: Naam van de opdrachtgever / klant
- `project_naam`: Naam of werktitel van het project
- `productie_datum`: Datum van de productie
- `deadline_levering`: Deadline voor oplevering eindproduct

### Stap 2 – Productietype & Doel
- `productie_type`: Type productie (bijv. bedrijfsvideo, commercial, social media, fotoshoot, event)
- `productie_doel`: Wat moet de productie bereiken / communiceren?
- `doelgroep`: Voor wie is de uiteindelijke content bedoeld?

### Stap 3 – Locatie & Planning
- `locaties`: Locatie(s) waar gefilmd/gefotografeerd wordt
- `crew_aanvang`: Hoe laat komt de crew aan?
- `shoot_aanvang`: Hoe laat start de daadwerkelijke shoot?
- `verwachte_eindtijd`: Verwachte eindtijd
- `logistieke_opmerkingen`: Bijzonderheden (parkeren, toegang, vergunningen etc.)

### Stap 4 – Crew & Apparatuur
- `crewleden`: Overzicht van crewleden en hun rol
- `apparatuur`: Apparatuur die meegenomen wordt

### Stap 5 – Content & Stijl
- `gewenste_scenes`: Scènes, shots of momenten die zeker vastgelegd moeten worden
- `stijl_referenties`: Stijlwensen, referenties of moodboard beschrijving
- `muziek_sound`: Wensen rondom muziek, voice-over of geluid
- `speciale_instructies`: Overige bijzonderheden of verzoeken van de klant

## Welke systems worden gebruikt

1. `systems/generate_draaiboek.py`
   - Ontvangt de gestructureerde formulierdata als dictionary
   - Stuurt een gedetailleerde prompt naar de Claude API
   - Retourneert het draaiboek als geformatteerde Markdown-tekst

## Verwachte output

Een volledig draaiboek in het Nederlands met de volgende secties:

1. **Projectoverzicht** – Klant, projectnaam, datum, deadline
2. **Dagschema** – Tijdlijn van de productiedag (uur voor uur)
3. **Shot list / Scèneoverzicht** – Genummerde lijst van te filmen/fotograferen momenten
4. **Crew & Rolverdeling** – Wie doet wat?
5. **Locatieoverzicht** – Details per locatie
6. **Apparatuurlijst** – Wat gaat er mee?
7. **Contactgegevens** – Opdrachtgever en relevante contacten
8. **Aandachtspunten & Bijzonderheden** – Logistiek, stijl, klantwensen

## Edge cases

- **Ontbrekende velden**: Als cruciale velden ontbreken, genereert het system een draaiboek met placeholders (`[INVULLEN]`) op die plekken.
- **Meerdere locaties**: Elke locatie krijgt een eigen blok in het schema.
- **API-fout**: Bij een mislukte API-call wordt een foutmelding getoond in het dashboard met instructie om opnieuw te proberen.
- **Rate limiting**: Bij rate limit errors wacht het system 60 seconden en probeert opnieuw (max. 2 pogingen).

## Kwaliteitscriteria

- Het draaiboek is direct bruikbaar op de set zonder aanvullende uitleg
- Nederlandse taal, professionele toon
- Tijden zijn realistisch gebaseerd op de opgegeven informatie
- Shot list is concreet en actiegericht (geen vage omschrijvingen)
