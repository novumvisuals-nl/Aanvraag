/* ===================================================
   Draaiboek Generator — Frontend logica
   =================================================== */

let huidigeStap = 1;
const totaalStappen = 4;

// ===================================================
// INITIALISATIE
// ===================================================

document.addEventListener("DOMContentLoaded", () => {
  vulTijdDropdowns();
  initialiseerMediumToggle();
});

// ===================================================
// TIJD DROPDOWNS (06:00 – 23:30 in stappen van 30 min)
// ===================================================

function vulTijdDropdowns() {
  const tijdVelden = ["crew_aanvang", "shoot_aanvang", "verwachte_eindtijd"];

  tijdVelden.forEach((id) => {
    const select = document.getElementById(id);
    if (!select) return;

    for (let uur = 6; uur <= 23; uur++) {
      ["00", "30"].forEach((minuten) => {
        const label = `${String(uur).padStart(2, "0")}:${minuten}`;
        const option = document.createElement("option");
        option.value = label;
        option.textContent = label;
        select.appendChild(option);
      });
    }
  });
}

// ===================================================
// FOTO / VIDEO TOGGLE
// ===================================================

const videoTypes = [
  "Brandmovie",
  "Testimonial",
  "Product video",
  "Employer branding",
  "Aftermovie",
  "Campagne video",
  "Social media video",
];

const fotoTypes = [
  "Bedrijfsreportage",
  "Portretfotografie",
  "Productfotografie",
  "Eventfotografie",
  "Campagnefotografie",
  "Actiefotografie",
  "Autofotografie",
];

function initialiseerMediumToggle() {
  const radioButtons = document.querySelectorAll(".medium-radio");
  radioButtons.forEach((radio) => {
    radio.addEventListener("change", () => {
      wisselMedium(radio.value);
    });
  });
}

function wisselMedium(medium) {
  const soortWrapper = document.getElementById("soort-wrapper");
  const soortSelect = document.getElementById("productie_type");
  const muziekWrapper = document.getElementById("muziek-wrapper");

  // Toon de soort dropdown
  soortWrapper.style.display = "flex";
  soortSelect.required = true;

  // Vul de juiste opties
  const types = medium === "Video" ? videoTypes : fotoTypes;
  soortSelect.innerHTML = `<option value="" disabled selected>Selecteer soort ${medium.toLowerCase()}productie</option>`;
  types.forEach((type) => {
    const option = document.createElement("option");
    option.value = type;
    option.textContent = type;
    soortSelect.appendChild(option);
  });

  // Toon/verberg muziek veld (alleen relevant bij video)
  if (muziekWrapper) {
    muziekWrapper.style.display = medium === "Video" ? "flex" : "none";
  }
}

// ===================================================
// STAP NAVIGATIE
// ===================================================

function toonStap(stap) {
  document.querySelectorAll(".form-step").forEach((el) => {
    el.classList.remove("active");
  });

  const stapEl = document.getElementById(`step-${stap}`);
  if (stapEl) stapEl.classList.add("active");

  document.querySelectorAll(".step-item").forEach((item, index) => {
    const stapNr = index + 1;
    item.classList.remove("active", "done");
    if (stapNr === stap) item.classList.add("active");
    else if (stapNr < stap) item.classList.add("done");
  });

  document.querySelectorAll(".step-line").forEach((lijn, index) => {
    lijn.classList.toggle("done", index + 1 < stap);
  });

  huidigeStap = stap;

  const container = document.querySelector(".container");
  if (container) container.scrollIntoView({ behavior: "smooth", block: "start" });
}

function volgendeStap(huidige) {
  const stapEl = document.getElementById(`step-${huidige}`);

  // Stap 2: valideer medium selectie
  if (huidige === 2) {
    const mediumGekozen = document.querySelector(".medium-radio:checked");
    if (!mediumGekozen) {
      toonFormFout(stapEl, "Kies eerst foto of video productie.");
      return;
    }
  }

  // Verplichte velden
  const verplicht = stapEl.querySelectorAll("[required]");
  let geldig = true;
  verplicht.forEach((veld) => {
    if (!veld.value.trim()) {
      veld.classList.add("input-error");
      geldig = false;
      veld.addEventListener("input", () => veld.classList.remove("input-error"), { once: true });
      veld.addEventListener("change", () => veld.classList.remove("input-error"), { once: true });
    }
  });

  if (!geldig) {
    const eersteLeeg = stapEl.querySelector(".input-error");
    if (eersteLeeg) {
      eersteLeeg.scrollIntoView({ behavior: "smooth", block: "center" });
      if (eersteLeeg.focus) eersteLeeg.focus();
    }
    return;
  }

  if (huidige < totaalStappen) toonStap(huidige + 1);
}

function vorigeStap(huidige) {
  if (huidige > 1) toonStap(huidige - 1);
}

function toonFormFout(stapEl, bericht) {
  let bestaand = stapEl.querySelector(".form-inline-fout");
  if (!bestaand) {
    bestaand = document.createElement("div");
    bestaand.className = "form-inline-fout";
    const toggleBlock = stapEl.querySelector(".medium-toggle");
    if (toggleBlock) toggleBlock.after(bestaand);
  }
  bestaand.textContent = bericht;
  bestaand.style.display = "block";
  setTimeout(() => { if (bestaand) bestaand.style.display = "none"; }, 3000);
}

// ===================================================
// FORMULIER SUBMIT
// ===================================================

document.getElementById("draaiboek-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  await genereerDraaiboek();
});

async function genereerDraaiboek() {
  const form = document.getElementById("draaiboek-form");
  const inputs = form.querySelectorAll("input, select, textarea");
  const data = {};

  inputs.forEach((el) => {
    if (el.name && el.type !== "radio") {
      data[el.name] = el.value;
    }
  });

  // Voeg medium (foto/video) toe
  const mediumGekozen = document.querySelector(".medium-radio:checked");
  if (mediumGekozen) data.medium = mediumGekozen.value;

  setLadenStatus(true);
  verbergResultaat();
  verbergFout();

  try {
    const response = await fetch("/genereer", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    });

    const json = await response.json();

    if (!response.ok || json.fout) {
      toonFout("Er is iets misgegaan bij het versturen van je aanvraag. Probeer het opnieuw of neem contact op via info@novumvisuals.nl");
      return;
    }

    toonBedankScherm();
  } catch (err) {
    toonFout("Er is iets misgegaan bij het versturen van je aanvraag. Probeer het opnieuw of neem contact op via info@novumvisuals.nl");
  } finally {
    setLadenStatus(false);
  }
}

// ===================================================
// UI HELPERS
// ===================================================

function setLadenStatus(laden) {
  const btn = document.getElementById("genereer-btn");
  const tekst = document.getElementById("btn-tekst");
  const loader = document.getElementById("btn-loader");

  btn.disabled = laden;
  tekst.textContent = laden ? "Aanvraag versturen..." : "Verstuur aanvraag";
  loader.classList.toggle("hidden", !laden);
}

function toonFout(bericht) {
  const foutEl = document.getElementById("fout-melding");
  document.getElementById("fout-tekst").textContent = bericht;
  foutEl.classList.remove("hidden");
  foutEl.scrollIntoView({ behavior: "smooth", block: "center" });
}

function verbergFout() {
  document.getElementById("fout-melding").classList.add("hidden");
}

function toonBedankScherm() {
  // Verberg form en stap-indicator
  document.getElementById("draaiboek-form").classList.add("hidden");
  document.getElementById("steps-indicator").classList.add("hidden");

  // Toon bedankscherm
  const bedank = document.getElementById("bedank-sectie");
  bedank.classList.remove("hidden");
  setTimeout(() => bedank.scrollIntoView({ behavior: "smooth", block: "center" }), 100);
}

function verbergResultaat() {
  // No-op: geen resultaatweergave voor de klant
}



// ===================================================
// INLINE VALIDATIE STIJL
// ===================================================

const stijl = document.createElement("style");
stijl.textContent = `
  .input-error {
    border-color: var(--magenta) !important;
    box-shadow: 0 0 0 3px rgba(167, 50, 143, 0.2) !important;
    animation: schud 0.3s ease;
  }
  .form-inline-fout {
    display: none;
    color: #d4a0cc;
    font-family: 'Lato', sans-serif;
    font-size: 13px;
    margin-top: 8px;
    padding: 8px 14px;
    background: rgba(167, 50, 143, 0.08);
    border: 1px solid rgba(167, 50, 143, 0.2);
    border-radius: 8px;
  }
  @keyframes schud {
    0%, 100% { transform: translateX(0); }
    25%       { transform: translateX(-6px); }
    75%       { transform: translateX(6px); }
  }
`;
document.head.appendChild(stijl);
