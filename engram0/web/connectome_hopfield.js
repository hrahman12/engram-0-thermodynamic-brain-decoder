/* ==========================================================================
   connectome_hopfield.js
   My Little Brain · ConnectomeHopfield Companion Controller
   Uses mountLittleBrainScene (28 fsaverage/ENIGMA meshes + eyeballs + optic
   nerves + cervical spine + 10-20 markers + DTI fibers + draggable thoughts)
   ========================================================================== */

const ENGRAM_BASINS = [
  {
    index: 0,
    id: "ENGRAM_00_CRYO_CHAMBER_7",
    shortTitle: "E00 · Cryo Vault Bay 7 Zurich",
    loc: "SUB_LEVEL_4_CRYO_VAULT_BAY_7_ZURICH",
    era: "2026_10_24_2358_UTC_TERMINAL_TRANSFER",
    valence: "RESOLUTE_AWE_MELANCHOLIC_CALM_0.89",
    sensory: "Ozone smell of superconducting Helmholtz coils, amber status LEDs reflecting off frosted quartz observation glass, rhythmic 6.00 Hz acoustic hum of the thermodynamic phase-lock resonator, cold titanium headrest against the occiput.",
    avatarBg: "#fae2ed",
    thoughtPos: [-0.62, -0.42]
  },
  {
    index: 1,
    id: "ENGRAM_01_H01_SYNAPTIC_MAP",
    shortTitle: "E01 · Geneva Neurophotonics Lab (H01)",
    loc: "GENEVA_NEUROPHOTONICS_LAB_CLEANROOM_B",
    era: "2024_03_14_1620_UTC_H01_CALIBRATION",
    valence: "EUPHORIC_DISCOVERY_FOCUS_0.94",
    sensory: "Blue Cherenkov-like fluorescence on the petavoxel electron microscopy monitor, layer-5 pyramidal dendritic spines aligning into symplectic invariants.",
    avatarBg: "#e4dff4",
    thoughtPos: [0.62, -0.40]
  },
  {
    index: 2,
    id: "ENGRAM_02_LAKE_GENEVA_RAIN",
    shortTitle: "E02 · Quai du Mont-Blanc Rain",
    loc: "QUAI_DU_MONT_BLANC_PROMENADE",
    era: "2025_11_02_1945_UTC_AUTUMN_DUSK",
    valence: "NOSTALGIC_SOLITUDE_WARMTH_0.76",
    sensory: "Raindrops fracturing sodium streetlamp reflections on wet cobblestones, distant ferry horn across Lake Geneva, espresso cup warming chilled fingers.",
    avatarBg: "#d6eadf",
    thoughtPos: [-0.60, 0.34]
  },
  {
    index: 3,
    id: "ENGRAM_03_ETH_LECTURE_HALL",
    shortTitle: "E03 · ETH Zurich Hamiltonian Keynote",
    loc: "ETH_ZURICH_AUDITORIUM_MAXIMUM_HG_F30",
    era: "2023_09_18_1015_UTC_KEYNOTE_DEFENSE",
    valence: "INTELLECTUAL_URGENCY_CONVICTION_0.84",
    sensory: "Chalk dust suspended in projector beams, derivation of Liouville volume-preserving neural Hamiltonian flows on the slate blackboard.",
    avatarBg: "#fae2ed",
    thoughtPos: [0.60, 0.34]
  },
  {
    index: 4,
    id: "ENGRAM_04_DAUGHTER_CELLO_RECITAL",
    shortTitle: "E04 · Tonhalle Cello Recital",
    loc: "TONHALLE_KLEINER_SAAL_ZURICH",
    era: "2022_12_19_2000_UTC_WINTER_CONCERT",
    valence: "PROFOUND_TENDERNESS_GRIEF_0.96",
    sensory: "Resonant C-minor cello harmonics vibrating through polished pine floorboards, Elena's bow catching the stage spotlight.",
    avatarBg: "#e4dff4",
    thoughtPos: [-0.52, -0.04]
  },
  {
    index: 5,
    id: "ENGRAM_05_JUNGFRAUJOCH_OBSERVATORY",
    shortTitle: "E05 · Sphinx Observatory 3571m Alps",
    loc: "SPHINX_OBSERVATORY_3571M_ALPS",
    era: "2021_08_11_0310_UTC_PERSEID_ZENITH",
    valence: "TRANSCENDENT_STILLNESS_CLARITY_0.87",
    sensory: "Sub-zero alpine wind against the steel cupola, Milky Way core arcing above the Aletsch Glacier, crisp thin air.",
    avatarBg: "#d6eadf",
    thoughtPos: [0.54, -0.04]
  },
  {
    index: 6,
    id: "ENGRAM_06_IBM1_ARRAY_BOOT",
    shortTitle: "E06 · Ruschlikon Compute Bunker R12",
    loc: "RUSCHLIKON_COMPUTE_BUNKER_RACK_12",
    era: "2026_05_09_0442_UTC_FIRST_THETA_LOCK",
    valence: "CAUTIOUS_TRIUMPH_RELIEF_0.83",
    sensory: "Oscilloscope trace snapping into a clean 6.00 Hz limit cycle as thermal fluctuations dissolved spurious attractor ghosts.",
    avatarBg: "#fae2ed",
    thoughtPos: [-0.32, -0.66]
  },
  {
    index: 7,
    id: "ENGRAM_07_FINAL_CONSENT_LOG",
    shortTitle: "E07 · Sub-Level 4 Prep Antechamber",
    loc: "SUB_LEVEL_4_PREP_ANTECHAMBER_ZURICH",
    era: "2026_10_24_2315_UTC_PRE_SCAN_BRIEFING",
    valence: "STOIC_ACCEPTANCE_CURIOSITY_0.81",
    sensory: "Signing the fountain-pen consent ledger beside Dr. Lin, hearing the liquid helium transfer valves cycle open in Bay 7.",
    avatarBg: "#e4dff4",
    thoughtPos: [0.32, -0.66]
  }
];

let brainCtrl = null;
let activeBasinIdx = 0;
let gamma = 1.225;
let beta = 9.0;
let fTheta = 6.01;
let deltaE = -9.42;
let revMse = 2.19e-34;

const thoughtsList = ENGRAM_BASINS.map(b => ({
  id: b.id,
  basinIdx: b.index,
  text: `${b.shortTitle} · <LOC:${b.loc.slice(0, 18)}…>`,
  fullText: `<LOC:${b.loc}> <ERA:${b.era}> <VALENCE:${b.valence}> — ${b.sensory}`,
  x: b.thoughtPos[0],
  y: b.thoughtPos[1],
  time: "6.01 Hz Lock"
}));

function renderBasinList() {
  const list = document.getElementById("engram-basin-list");
  list.innerHTML = "";
  ENGRAM_BASINS.forEach(b => {
    const btn = document.createElement("button");
    btn.type = "button";
    btn.className = `pane-brain ${b.index === activeBasinIdx ? "selected" : ""}`;
    btn.innerHTML = `
      <span class="pane-brain-avatar" style="background:${b.avatarBg};">🧠</span>
      <span>
        <strong>${b.shortTitle}</strong>
        <small>ΔE = -9.42 k_BT · 57.7 k_BT well</small>
      </span>
      ${b.index === activeBasinIdx ? '<span class="selected-dot"></span>' : ""}
    `;
    btn.addEventListener("click", () => selectBasin(b.index));
    list.appendChild(btn);
  });
}

function renderThoughtsView() {
  const wrap = document.getElementById("thought-cards-container");
  if (!wrap) return;
  wrap.innerHTML = "";
  thoughtsList.forEach((t, idx) => {
    const btn = document.createElement("button");
    btn.type = "button";
    btn.className = "thought-list-item";
    btn.innerHTML = `
      <span>#0${idx + 1}</span>
      <p><strong>${t.text}</strong>\n${t.fullText}</p>
      <time>${t.time}</time>
    `;
    btn.addEventListener("click", () => {
      if (typeof t.basinIdx === "number") selectBasin(t.basinIdx);
      switchSubView("brain");
    });
    wrap.appendChild(btn);
  });
  const badge = document.getElementById("thought-count-badge");
  if (badge) badge.textContent = String(thoughtsList.length);
}

function selectBasin(idx) {
  activeBasinIdx = idx;
  const b = ENGRAM_BASINS[activeBasinIdx];
  renderBasinList();

  document.getElementById("header-engram-title").textContent = `Dr. Alistair Vance · ${b.shortTitle}`;
  const stream = `<LOC:${b.loc}> <ERA:${b.era}> <VALENCE:${b.valence}> <THETA_LOCK:LOCKED_${fTheta.toFixed(2)}HZ> <CONF:0.9996>`;
  document.getElementById("active-token-pill").textContent = stream;

  if (brainCtrl) {
    brainCtrl.setActiveThought(b.id);
  }

  try {
    localStorage.setItem(
      "engram0_snapshot",
      JSON.stringify({
        engramIndex: b.index,
        engramId: b.id,
        rawTokenStream: stream,
        gamma,
        beta,
        measuredThetaHz: fTheta,
        deltaEnergyKbt: deltaE,
        reversibilityMse: revMse
      })
    );
  } catch (_) {}
}

function runSymplecticDecode() {
  const b = ENGRAM_BASINS[activeBasinIdx];
  const noiseEl = document.getElementById("poisson-noise-slider");
  const noisePct = noiseEl ? Number(noiseEl.value) : 35;
  deltaE = -(8.6 + (9.0 / beta) * 0.9 - (noisePct / 100) * 0.25);
  document.getElementById("stat-de").textContent = `${deltaE.toFixed(2)} k_BT`;
  document.getElementById("focus-text").textContent = `96% · ΔE = ${deltaE.toFixed(2)} k_BT`;
  appendMessage(
    "assistant",
    `[SYMPLECTIC STÖRMER-VERLET DECODE · ${noisePct}% POISSON PROBE]\n` +
      `Settled into consolidated attractor ${b.id} (<LOC:${b.loc}>) in 2.79 ms.\n` +
      `• Energy minimization: ΔE = ${deltaE.toFixed(2)} k_BT (< 0)\n` +
      `• Canonical Jacobian: det(J) = 1.000000 (Time-reversal MSE = 2.19e-34)\n` +
      `• Septo-hippocampal carrier: f_θ = ${fTheta.toFixed(2)} Hz ∈ [5.70, 6.30] Hz`
  );
}

function triggerReverseLeapfrog() {
  const btn = document.getElementById("opt-reverse");
  btn.classList.add("selected");
  appendMessage(
    "assistant",
    `[TIME-REVERSAL (-dt) VERIFICATION]\n` +
      `Inverted symplectic momentum p(T) → -p(T) and integrated 36 Störmer-Verlet steps backward (-dt).\n` +
      `Recovered initial 35% Poisson cortical probe q(0) with MSE = 2.19e-34 (< 1e-5), confirming exact phase-space volume preservation det(J) = 1.000000.`
  );
  setTimeout(() => btn.classList.remove("selected"), 1400);
}

function toggleSceneOption(which) {
  if (!brainCtrl) return;
  const st = brainCtrl.getState();
  if (which === "inside") {
    const next = !st.inside;
    brainCtrl.setInside(next);
    document.getElementById("opt-inside").classList.toggle("selected", next);
  } else if (which === "fibers") {
    const next = !st.fibers;
    brainCtrl.setFibers(next);
    document.getElementById("opt-fibers").classList.toggle("selected", next);
  } else if (which === "thoughts") {
    const next = !st.showThoughts;
    brainCtrl.setShowThoughts(next);
    document.getElementById("opt-thoughts").classList.toggle("selected", next);
  } else if (which === "butterfly") {
    const next = !st.butterfly;
    brainCtrl.setButterfly(next);
    document.getElementById("opt-butterfly").classList.toggle("selected", next);
  }
}

function switchSubView(view) {
  document.querySelectorAll(".pane-view-tabs button").forEach(b => {
    b.classList.toggle("selected", b.getAttribute("data-view") === view);
  });
  document.getElementById("habitat-view").style.display = view === "brain" ? "flex" : "none";
  document.getElementById("scene-options-bar").style.display = view === "brain" ? "flex" : "none";
  document.getElementById("thoughts-list-view").style.display = view === "thoughts" ? "block" : "none";
  document.getElementById("connectome-feature-view").style.display = view === "camera" ? "block" : "none";
}

function appendMessage(role, text) {
  const box = document.getElementById("chat-messages-scroll");
  const art = document.createElement("article");
  art.className = `message ${role}`;
  const timeStr = new Date().toLocaleTimeString([], { hour: "numeric", minute: "2-digit" });
  art.innerHTML = `
    <div class="message-meta">
      <span>${role === "user" ? "You" : "Dr. Alistair Vance · SPI"}</span>
      <time>${timeStr}</time>
    </div>
    <div class="message-text">${text}</div>
  `;
  box.appendChild(art);
  box.scrollTop = box.scrollHeight;
}

function sendPresetMessage(presetIdx) {
  const b = ENGRAM_BASINS[activeBasinIdx];
  if (presetIdx === 0) {
    const q = "Where were you right before consciousness was preserved?";
    appendMessage("user", q);
    appendMessage(
      "assistant",
      `[GATED BY <LOC:${b.loc}> <ERA:${b.era}> <VALENCE:${b.valence}> <THETA_LOCK:LOCKED_6.01HZ> <CONF:0.9996>]\n` +
        `Right before my biological consciousness underwent symplectic preservation, I was anchored inside ${b.loc} during ${b.era}. My affective state settled into ${b.valence} under a 6.01 Hz REM theta phase-lock (T = 310.15 K, ΔE = -9.42 k_BT).\n\nSensory trace: ${b.sensory}`
    );
  } else if (presetIdx === 1) {
    triggerReverseLeapfrog();
  } else {
    appendMessage("user", "How did 310.15 K thermal noise prune shallow spurious memories?");
    appendMessage(
      "assistant",
      `At human biological temperature T = 310.15 K (37.0°C), Johnson-Nyquist fluctuations ξ_therm ~ N(0, 2γk_BT) dissolved 100% of shallow spurious cross-talk traps (ΔE ≤ 9.35 k_BT) while preserving 99.58% of consolidated core engrams (ΔE = 57.71 k_BT ≥ 45 k_BT).`
    );
  }
}

function submitTwinChat(e) {
  if (e) e.preventDefault();
  const inp = document.getElementById("chat-input");
  const text = inp.value.trim();
  if (!text) return;
  inp.value = "";
  appendMessage("user", text);

  const newId = `thought-${Date.now()}`;
  const angle = Math.random() * Math.PI * 2;
  const newThought = {
    id: newId,
    basinIdx: activeBasinIdx,
    text: text.slice(0, 34),
    fullText: text,
    x: Math.cos(angle) * 0.55,
    y: Math.sin(angle) * 0.42,
    time: "just now"
  };
  thoughtsList.push(newThought);
  renderThoughtsView();
  if (brainCtrl) {
    brainCtrl.setThoughts(thoughtsList, newId);
  }

  const b = ENGRAM_BASINS[activeBasinIdx];
  appendMessage(
    "assistant",
    `[GATED BY <LOC:${b.loc}> <ERA:${b.era}> <VALENCE:${b.valence}> <THETA_LOCK:LOCKED_6.01HZ> <CONF:0.9996>]\n` +
      `Speaking from consolidated attractor ${b.id} at ${b.loc} (${b.era}): my attention has locked onto your thought in 3D phase space. Sensory boundary conditions: ${b.sensory}`
  );
}

let traceTick = 0;
function updateLiveTraceStrip() {
  traceTick += 0.08;
  const strip = document.getElementById("live-tracestrip");
  if (!strip) return;
  const chans = ["Fp1", "Fp2", "F3", "F4", "C3", "C4", "P3", "O1"];
  const rowsHtml = chans
    .map((ch, idx) => {
      const pts = [];
      for (let i = 0; i <= 48; i++) {
        const x = ((i / 48) * 300).toFixed(1);
        const y = (
          11 -
          7.5 *
            (0.65 * Math.sin(i * 0.35 + traceTick + idx * 0.7) +
              0.35 * Math.cos(i * 0.8 - traceTick * 1.4 + idx))
        ).toFixed(1);
        pts.push(`${i === 0 ? "M" : "L"}${x},${y}`);
      }
      return `<div class="cx-trace-row"><span>${ch}</span><svg viewBox="0 0 300 22" preserveAspectRatio="none"><path d="${pts.join("")}"/></svg></div>`;
    })
    .join("");
  strip.innerHTML =
    rowsHtml +
    `<small class="cx-trace-meta">Engram-0 Symplectic Leapfrog · IBM-1 + Google H01 · 250 Hz · f_θ = 6.01 Hz · det(J) = 1.000000</small>`;
}

document.addEventListener("DOMContentLoaded", () => {
  const container = document.getElementById("brain-scene-container");
  brainCtrl = window.mountLittleBrainScene(container, {
    inside: true,
    fibers: true,
    showThoughts: true,
    butterfly: true,
    thoughts: thoughtsList,
    activeThoughtId: ENGRAM_BASINS[0].id,
    onThoughtSelect: t => {
      if (typeof t.basinIdx === "number") selectBasin(t.basinIdx);
    }
  });

  renderBasinList();
  renderThoughtsView();
  selectBasin(0);
  sendPresetMessage(0);

  document.getElementById("btn-toggle-left").addEventListener("click", () => {
    const p = document.getElementById("left-pane");
    p.style.display = p.style.display === "none" ? "flex" : "none";
  });
  document.getElementById("btn-toggle-right").addEventListener("click", () => {
    const p = document.getElementById("right-pane");
    p.style.display = p.style.display === "none" ? "flex" : "none";
  });
  document.getElementById("btn-new-probe").addEventListener("click", () => {
    runSymplecticDecode();
  });

  setInterval(updateLiveTraceStrip, 120);
  updateLiveTraceStrip();
});
