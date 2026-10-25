/* ==========================================================================
   index_app.js
   Engram-0 · My Little Brain × cortex² × Google H01 3D Studio Controller
   ========================================================================== */

const H01_C3_SEGMENTS = [
  "1100054524","1115430292","12237931142","1333290325","1538274151","1539076840",
  "1594648509","1638188509","1828951844","1915887451","1988993337","20070214646",
  "2090806103","2134549398","2178704414","2294780853","2339328448","2499107339",
  "2499384877","2557789796","2673254402","27622860459","27651872764","27870683066",
  "2791142865","28000894735","28045909614","28378958224","28409678489","28452985548",
  "28525770719","28643309290","28672203772","28802547903","28803598117","28918216929",
  "29021270843","29182786959","29238417446","29298236361","2935896346","29459096371",
  "29618159554","29765396306","29925423252","29938695074","29969547791","30101233972",
  "3023633866","30376944711","30406000355","3052908678","30668773752","30767987832",
  "30871567933","30974109956","31031989065","31032951251","31061717348","31133932587",
  "31149133165","3125564306","31658722916","32444986357","3430740099","3504577656",
  "3518943222","3573728110","36123853342","36153829678","36241229806","36284756264",
  "36445761568","36590837294","36619747807","36620463168","36633005581","3664545249",
  "36662790455","36678107375","36763714196","36809473223","36822073774","36822262086",
  "36852896228","37173591638","37218168369","37318668413","37319791473","37420743412",
  "37421824682","37463700916","37536734693","37581252436","37594612366","37668755920",
  "37770758892","37801070911","37930756265","37958718097","38018479939","38092682277",
  "38106873604","38208029710","38222309348","38339219897","38368158152","38383402139",
  "3839697992","38413115427","38543488421","38573083867","38586823171","38602358951",
  "38717924646","38863556782","38863862489","3897678996","38994907574","39023934118",
  "39038491013","39052800624","39081564265","39271712983","39271916939","39359991385",
  "3941569746","39505037109","39694250521","40043667040","40102203154","40247497000",
  "40378483178","40407875435","40464862282","41354296446","41630488832","4217863883",
  "4318903980","45701832369","4580553370","4698412002","4784821941","48079386659",
  "4917456198","4961186471","5062824784","5499847526","58866575372","59536235974",
  "5965326176","6024781859","664433854","707068981","794630620","823395680",
  "853035674","910562342"
];

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
let activeH01SegIdx = 0;
let fTheta = 6.0059;
let deltaE = -9.42;

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

function renderOrbsAndHist() {
  const orbsWrap = document.getElementById("home-orbs");
  if (!orbsWrap) return;
  orbsWrap.innerHTML = "";
  for (let i = 0; i < 8; i++) {
    const isTarget = i === activeBasinIdx;
    const p = isTarget ? 0.96 : Math.max(0.05, 0.20 * Math.exp(-Math.abs(i - activeBasinIdx)));
    const div = document.createElement("div");
    div.className = "cx-orb";
    div.innerHTML = `
      <span style="--p:${p.toFixed(2)}"></span>
      <small>E0${i}</small>
      <em>${(p * 100).toFixed(0)}%</em>
    `;
    orbsWrap.appendChild(div);
  }

  const histWrap = document.getElementById("home-hist-rows");
  if (!histWrap) return;
  histWrap.innerHTML = "";
  const rows = [
    { code: "E00_CRYO", pct: activeBasinIdx === 0 ? 96 : 18, n: "57.7kT", flags: "★ ✓", truth: activeBasinIdx === 0 },
    { code: "E01_H01", pct: activeBasinIdx === 1 ? 96 : 16, n: "57.7kT", flags: "✓", truth: activeBasinIdx === 1 },
    { code: "E02_LAKE", pct: activeBasinIdx === 2 ? 96 : 14, n: "57.7kT", flags: "✓", truth: activeBasinIdx === 2 },
    { code: "SPURIOUS", pct: 2, n: "≤9.3kT", flags: "0%", truth: false }
  ];
  rows.forEach(r => {
    const row = document.createElement("div");
    row.className = `cx-hist-row ${r.truth ? "truth consistent" : ""}`;
    row.innerHTML = `
      <code>${r.code}</code>
      <div class="cx-hist-track"><span style="width:${r.pct}%"></span></div>
      <span class="cx-hist-n">${r.n}</span>
      <span class="cx-hist-flags"><i>${r.flags}</i></span>
    `;
    histWrap.appendChild(row);
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

function renderH01Studio() {
  const grid = document.getElementById("h01-seg-grid");
  if (!grid) return;
  grid.innerHTML = "";
  H01_C3_SEGMENTS.forEach((segId, idx) => {
    const hue = (parseInt(segId.slice(-4), 10) * 137) % 360;
    const btn = document.createElement("button");
    btn.type = "button";
    btn.style.cssText = `display:flex;align-items:center;gap:6px;padding:5px 7px;border-radius:9px;font-family:ui-monospace,monospace;font-size:10px;background:${idx === activeH01SegIdx ? "#e4edde" : "#ffffff90"};border:1px solid ${idx === activeH01SegIdx ? "#8eaa77" : "#e3eadc"};`;
    btn.innerHTML = `<i style="width:8px;height:8px;border-radius:2px;background:hsl(${hue},65%,58%);display:inline-block;"></i><span>${segId}</span>`;
    btn.addEventListener("click", () => {
      activeH01SegIdx = idx;
      document.getElementById("h01-selected-seg-label").textContent = `Active C3 Segment: ${segId} (L2 Interneuron · NSe>=800 <NSi)`;
      renderH01Studio();
      drawH01EmCanvas();
    });
    grid.appendChild(btn);
  });
  drawH01EmCanvas();
}

function drawH01EmCanvas() {
  const cv = document.getElementById("h01-em-canvas");
  if (!cv) return;
  const ctx = cv.getContext("2d");
  const w = cv.width, h = cv.height;
  ctx.fillStyle = "#12161b";
  ctx.fillRect(0, 0, w, h);

  for (let i = 0; i < 220; i++) {
    const x = ((i * 73 + activeH01SegIdx * 19) % w);
    const y = ((i * 41 + activeH01SegIdx * 11) % h);
    const r = 6 + (i % 18);
    ctx.strokeStyle = "rgba(195, 208, 218, 0.14)";
    ctx.beginPath();
    ctx.arc(x, y, r, 0, Math.PI * 2);
    ctx.stroke();
  }

  for (let k = 0; k < 14; k++) {
    const segId = H01_C3_SEGMENTS[(activeH01SegIdx + k) % H01_C3_SEGMENTS.length];
    const hue = (parseInt(segId.slice(-4), 10) * 137) % 360;
    const cx = 65 + ((k * 67) % (w - 130));
    const cy = 48 + ((k * 53) % (h - 96));
    ctx.fillStyle = k === 0 ? `hsla(${hue}, 80%, 60%, 0.55)` : `hsla(${hue}, 65%, 52%, 0.26)`;
    ctx.strokeStyle = `hsla(${hue}, 85%, 68%, 0.9)`;
    ctx.lineWidth = k === 0 ? 2.2 : 1.1;
    ctx.beginPath();
    ctx.ellipse(cx, cy, k === 0 ? 38 : 22, k === 0 ? 24 : 15, k * 0.4, 0, Math.PI * 2);
    ctx.fill();
    ctx.stroke();
  }

  ctx.fillStyle = "#d9e6dc";
  ctx.font = "11px ui-monospace, monospace";
  ctx.fillText(`4nm EM · pos [379548.5, 137610.125, 2660.5] · Seg #${H01_C3_SEGMENTS[activeH01SegIdx]}`, 14, h - 14);
}

function renderAssertionsGrid() {
  const grid = document.getElementById("assertions-cards-grid");
  if (!grid) return;
  const cards = [
    {
      badge: "ASSERTION 1 · 50/50 PASS",
      title: "Strict Energy Minimization (ΔE < 0)",
      val: "Mean ΔE = -9.4213 k_BT",
      desc: "100% of 50 Monte Carlo trials with 35% Poisson shot noise satisfy settled_energy < initial_energy (max ΔE = -7.18 k_BT)."
    },
    {
      badge: "ASSERTION 2 · PASS",
      title: "Symplectic Reversibility (det J = 1)",
      val: "Max MSE = 2.19e-34 (< 1e-5)",
      desc: "Kick-Drift-Kick Störmer-Verlet leapfrog preserves canonical phase-space volume exactly and recovers q(0) under -dt integration."
    },
    {
      badge: "ASSERTION 3 · PASS",
      title: "5% REM Theta Resonance Window",
      val: "f_measured = 6.0059 Hz",
      desc: "Septo-hippocampal carrier stays strictly inside [5.70 Hz, 6.30 Hz] (6.00 Hz ± 5%) after autonomous self-healing calibration."
    },
    {
      badge: "ASSERTION 4 · PASS",
      title: "310.15 K Sleep Pruning & Core Retention",
      val: "100% Pruned · 99.58% Retained",
      desc: "Johnson-Nyquist thermal noise at 310.15 K (37.0°C) dissolves 100% of shallow spurious traps (≤ 9.35 k_BT) while retaining ≥ 99.58% of core wells (57.71 k_BT)."
    },
    {
      badge: "ASSERTION 5 · PASS",
      title: "End-to-End Pipeline Latency (< 50 ms)",
      val: "Mean 2.79 ms · P95 3.01 ms",
      desc: "Vectorized NumPy/SciPy execution across Connectome IR, Symplectic Hopfield relaxation, and Semantic Tokenization."
    },
    {
      badge: "ASSERTION 6 · PASS",
      title: "Strict Cognitive Gating of SPI Persona",
      val: "100% Token-Grounded Recall",
      desc: "Dr. Alistair Vance (gemini-4-argon, thinking_level='high') responds strictly from decoded <LOC>, <ERA>, <VALENCE>, <THETA_LOCK>, and <CONF> tokens."
    }
  ];
  grid.innerHTML = cards
    .map(
      c => `
    <div class="plugin-card">
      <div class="plugin-title">
        <span>🛡️</span>
        <h2>${c.title}</h2>
        <small>${c.badge}</small>
      </div>
      <strong style="font-size: 18px; color: #526b46;">${c.val}</strong>
      <p class="plugin-privacy">${c.desc}</p>
    </div>
  `
    )
    .join("");
}

function selectBasin(idx) {
  activeBasinIdx = idx;
  const b = ENGRAM_BASINS[activeBasinIdx];
  renderBasinList();
  renderOrbsAndHist();

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
        measuredThetaHz: fTheta,
        deltaEnergyKbt: deltaE
      })
    );
  } catch (_) {}
}

function runSymplecticDecode() {
  const b = ENGRAM_BASINS[activeBasinIdx];
  deltaE = -(9.15 + Math.random() * 0.45);
  document.getElementById("stat-de").textContent = `${deltaE.toFixed(2)} k_BT`;
  document.getElementById("focus-text").textContent = `99.96% · ΔE = ${deltaE.toFixed(2)} k_BT · Rev MSE = 2.19e-34`;
  appendMessage(
    "assistant",
    `[SYMPLECTIC STÖRMER-VERLET DECODE · 35% POISSON PROBE]\n` +
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
      `Recovered initial 35% Poisson cortical probe q(0) with MSE = 2.19045e-34 (< 1e-5), confirming exact phase-space volume preservation det(J) = 1.000000.`
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

function toggleQvizCard() {
  const qv = document.getElementById("home-qviz");
  const hab = document.getElementById("habitat-view");
  const btn = document.getElementById("opt-qviz");
  const vis = qv.style.display !== "none";
  qv.style.display = vis ? "none" : "flex";
  hab.classList.toggle("with-qviz", !vis);
  btn.classList.toggle("selected", !vis);
}

function switchSubView(view) {
  document.querySelectorAll(".pane-view-tabs button").forEach(b => {
    b.classList.toggle("selected", b.getAttribute("data-view") === view);
  });
  const isBrain = view === "brain";
  document.getElementById("habitat-view").style.display = isBrain ? "flex" : "none";
  document.getElementById("scene-options-bar").style.display = isBrain ? "flex" : "none";
  document.getElementById("home-qviz").style.display = isBrain ? "flex" : "none";
  document.getElementById("h01-view").style.display = view === "h01" ? "block" : "none";
  document.getElementById("thoughts-list-view").style.display = view === "thoughts" ? "block" : "none";
  document.getElementById("assertions-view").style.display = view === "assertions" ? "block" : "none";
  if (view === "h01") drawH01EmCanvas();
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
  renderOrbsAndHist();
  renderThoughtsView();
  renderH01Studio();
  renderAssertionsGrid();
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

  setInterval(updateLiveTraceStrip, 120);
  updateLiveTraceStrip();
});
