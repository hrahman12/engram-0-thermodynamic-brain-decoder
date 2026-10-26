"""
api/index.py
============
Full-Stack Vercel Serverless Entrypoint for Project Engram-0:
Universal Quantum-Thermodynamic Connectome Engine & WebGPU Cockpit.

Serves:
  - GET  /                                 -> 3D WebGPU Cockpit (`index.html`)
  - GET  /connectome                       -> 3D Connectome & Neural Connector Graph UI (`engram_0_3d_ui.html`)
  - GET  /health                           -> Cirq simulator status, substrate, theta lock
  - GET  /studio                           -> My Little Brain / cortex² 3D Studio (`engram0/web/index.html`)
  - GET  /hopfield                         -> 3D Connectome & Hopfield Sanctuary (`engram0/web/connectome_hopfield.html`)
  - GET  /thermo                           -> 3D ThermoSPI Reactor (`engram0/web/thermo_spi.html`)
  - GET  /anatomy/* & /engram0/web/*       -> 28 FreeSurfer/ENIGMA `.bin` 3D meshes, JS, CSS, SVG
  - GET  /api/telemetry | /api/state       -> Live quantum & thermodynamic verification ledger JSON
  - POST /api/quantum_recall               -> Cirq Quantum Hopfield Network recall & WKB tunneling
  - POST /api/decode                       -> Continuous Symplectic Modern Hopfield decoding
  - POST /api/intake                       -> Digitize Mind User Profile update
  - POST /api/query_spi                    -> Strictly token-gated Dr. Alistair Vance SPI (`gemini-4-argon`)
"""

from __future__ import annotations

from http.server import BaseHTTPRequestHandler
import json
import mimetypes
from pathlib import Path
import sys
from typing import Any, Dict
from urllib.parse import parse_qs, urlparse

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from connectome_ir import ConnectomeIR
from personal_intake import DEFAULT_PROFILE_PATH, UserMindProfile, run_interactive_intake
from quantum_hopfield_engram import (
    BIOLOGICAL_TEMP_K,
    TARGET_THETA_HZ,
    THETA_MAX_HZ,
    THETA_MIN_HZ,
    QuantumHopfieldEngram,
)
from reversible_thermo_engram import ReversibleThermoEngram
from semantic_tokenizer import SemanticTokenizer
from spi_persona_engine import SPIPersonaEngine

WEB_DIR = ROOT_DIR / "engram0" / "web"
TELEMETRY_QUANTUM_FILE = ROOT_DIR / "engram_0_quantum_telemetry.json"
TELEMETRY_FILE = ROOT_DIR / "engram_0_telemetry.json"
INDEX_HTML_FILE = ROOT_DIR / "index.html"
UI_HTML_FILE = ROOT_DIR / "engram_0_3d_ui.html"


class _VercelEngramSingleton:
    def __init__(self) -> None:
        try:
            self.profile = run_interactive_intake(output_path=Path("/tmp/user_engram_profile.json"), force_defaults=True)
        except Exception:
            self.profile = build_default_user_profile()
        self.connectome = ConnectomeIR(
            d=64,
            M=len(self.profile.memories),
            mode="H01",
            f_theta_hz=TARGET_THETA_HZ,
            seed=42,
            user_profile=self.profile,
            n_qubits=8,
        )
        self.spurious = self.connectome.generate_spurious_attractors(n_spurious=6)
        self.engram = ReversibleThermoEngram(
            X=self.connectome.X,
            gamma=1.225,
            beta=9.00,
            temperature_k=BIOLOGICAL_TEMP_K,
            f_theta_hz=TARGET_THETA_HZ,
            spurious_basis=self.spurious,
            seed=42,
        )
        self.qhn = QuantumHopfieldEngram(
            connectome=self.connectome,
            trotter_steps_p=5,
            gamma_scale=1.00,
            beta_scale=1.00,
            f_theta_hz=TARGET_THETA_HZ,
            temperature_k=BIOLOGICAL_TEMP_K,
            seed=42,
        )
        self.tokenizer = SemanticTokenizer(
            X=self.connectome.X,
            metadata=self.connectome.metadata,
            spin_patterns=self.connectome.ising.spin_patterns,
        )
        self.spi = SPIPersonaEngine(user_profile=self.profile)
        self._cached_telemetry: Dict[str, Any] | None = None

    def get_telemetry(self) -> Dict[str, Any]:
        if self._cached_telemetry is not None:
            return self._cached_telemetry
        if TELEMETRY_QUANTUM_FILE.exists():
            self._cached_telemetry = json.loads(TELEMETRY_QUANTUM_FILE.read_text(encoding="utf-8"))
            return self._cached_telemetry
        if TELEMETRY_FILE.exists():
            self._cached_telemetry = json.loads(TELEMETRY_FILE.read_text(encoding="utf-8"))
            return self._cached_telemetry
        from verify_quantum_dynamics import run_quantum_verification_suite

        self._cached_telemetry = run_quantum_verification_suite(str(TELEMETRY_QUANTUM_FILE))
        return self._cached_telemetry


STATE = _VercelEngramSingleton()


class handler(BaseHTTPRequestHandler):  # noqa: N801
    """Vercel Python Serverless HTTP Handler."""

    def _send_bytes(self, data: bytes, content_type: str, status: int = 200, cache: bool = False) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        if cache:
            self.send_header("Cache-Control", "public, max-age=86400")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _send_json(self, payload: Dict[str, Any], status: int = 200) -> None:
        raw = json.dumps(payload).encode("utf-8")
        self._send_bytes(raw, "application/json; charset=utf-8", status=status)

    def _resolve_path(self) -> str:
        parsed = urlparse(self.path)
        qs = parse_qs(parsed.query)
        if "__path" in qs and qs["__path"]:
            req = qs["__path"][0]
            return req if req.startswith("/") else f"/{req}"
        return parsed.path or "/"

    def do_OPTIONS(self) -> None:  # noqa: N802
        self._send_json({"ok": True})

    def do_GET(self) -> None:  # noqa: N802
        req_path = self._resolve_path()

        # 1. Main 3D WebGPU Cockpit (index.html)
        if req_path in ("/", "/index.html", "/cockpit"):
            self._send_bytes(INDEX_HTML_FILE.read_bytes(), "text/html; charset=utf-8")
            return

        # 2. 3D Connectome & Neural Connector Graph UI
        if req_path in ("/connectome", "/engram_0_3d_ui.html"):
            self._send_bytes(UI_HTML_FILE.read_bytes(), "text/html; charset=utf-8")
            return

        # 3. System Health & Cirq Status
        if req_path == "/health":
            meas_theta = STATE.qhn.measure_rem_theta_frequency()
            self._send_json({
                "status": "ONLINE",
                "simulator": "cirq.Simulator",
                "substrate": "GOOGLE_H01_CORTEX_L4",
                "n_qubits": STATE.qhn.n_qubits,
                "trotter_steps_p": STATE.qhn.trotter_steps_p,
                "temperature_k": BIOLOGICAL_TEMP_K,
                "rem_theta_clock": {
                    "target_hz": TARGET_THETA_HZ,
                    "measured_hz": round(meas_theta, 4),
                    "locked": bool(THETA_MIN_HZ <= meas_theta <= THETA_MAX_HZ),
                },
                "callsign": STATE.profile.callsign,
            })
            return

        # 4. 3D Studio, Sanctuary & Sub-pages
        if req_path in ("/lab", "/brainlab", "/studio", "/engram0/web/index", "/engram0/web/index.html"):
            self._send_bytes((WEB_DIR / "index.html").read_bytes(), "text/html; charset=utf-8")
            return
        if req_path in ("/sanctuary", "/hopfield", "/connectome_hopfield", "/connectome_hopfield.html", "/engram0/web/connectome_hopfield", "/engram0/web/connectome_hopfield.html"):
            self._send_bytes((WEB_DIR / "connectome_hopfield.html").read_bytes(), "text/html; charset=utf-8")
            return
        if req_path in ("/thermo", "/thermo_spi", "/thermo_spi.html", "/engram0/web/thermo_spi", "/engram0/web/thermo_spi.html"):
            self._send_bytes((WEB_DIR / "thermo_spi.html").read_bytes(), "text/html; charset=utf-8")
            return

        # 5. Telemetry JSON API
        if req_path in ("/api/telemetry", "/api/state"):
            self._send_json(STATE.get_telemetry())
            return

        # 6. Static Assets (anatomy/*.bin, engram0/web/*, assets/*)
        rel = req_path.lstrip("/")
        if rel.startswith("engram0/web/"):
            rel = rel[len("engram0/web/"):]
        candidate = (WEB_DIR / rel).resolve()
        if not candidate.is_file() and rel.startswith("assets/"):
            candidate = (ROOT_DIR / rel).resolve()

        if candidate.is_file() and (
            str(candidate).startswith(str(WEB_DIR.resolve()))
            or str(candidate).startswith(str((ROOT_DIR / "assets").resolve()))
        ):
            ctype, _ = mimetypes.guess_type(str(candidate))
            if candidate.suffix == ".bin":
                ctype = "application/octet-stream"
            elif candidate.suffix == ".js":
                ctype = "application/javascript; charset=utf-8"
            elif candidate.suffix == ".css":
                ctype = "text/css; charset=utf-8"
            elif candidate.suffix == ".svg":
                ctype = "image/svg+xml"
            elif candidate.suffix == ".json":
                ctype = "application/json; charset=utf-8"
            self._send_bytes(candidate.read_bytes(), ctype or "application/octet-stream", cache=True)
            return

        self._send_json({"error": f"Not found: {req_path}"}, status=404)

    def do_POST(self) -> None:  # noqa: N802
        req_path = self._resolve_path()
        length = int(self.headers.get("Content-Length", "0"))
        body = json.loads(self.rfile.read(length).decode("utf-8")) if length > 0 else {}

        if req_path in ("/api/quantum_recall", "/api/decode_quantum"):
            target_idx = int(body.get("target_index", 0)) % STATE.connectome.M
            bit_flip = float(body.get("bit_flip_fraction", 0.35))
            q_res = STATE.qhn.run_quantum_recall(target_index=target_idx, bit_flip_fraction=bit_flip)
            packet = STATE.tokenizer.tokenize_quantum(q_res)
            self._send_json({
                "target_index": target_idx,
                "engram_id": q_res.engram_id,
                "ground_state_fidelity": round(q_res.ground_state_fidelity, 5),
                "unitary_reversibility_fidelity": round(q_res.unitary_reversibility_fidelity, 8),
                "tunneling_probability": round(q_res.tunneling_probability, 5),
                "spurious_escaped": q_res.spurious_escaped,
                "measured_theta_hz": round(q_res.measured_theta_hz, 4),
                "collapsed_bitstring": q_res.collapsed_bitstring,
                "bloch_vector": [round(x, 4) for x in q_res.bloch_vector],
                "tokens": packet.to_dict(),
                "latency_ms": round(q_res.latency_ms, 3),
            })

        elif req_path == "/api/intake":
            new_profile = UserMindProfile.from_dict(body)
            STATE.connectome.ingest_user_profile(new_profile)
            STATE.qhn.ising = STATE.connectome.ising
            STATE.tokenizer = SemanticTokenizer(
                X=STATE.connectome.X,
                metadata=STATE.connectome.metadata,
                spin_patterns=STATE.connectome.ising.spin_patterns,
            )
            STATE.spi.set_user_profile(new_profile)
            self._send_json({
                "status": "COMPILED_TO_QUANTUM_ENGRAM",
                "callsign": new_profile.callsign,
                "memories_count": len(new_profile.memories),
            })

        elif req_path == "/api/decode":
            target_idx = int(body.get("target_index", 0)) % STATE.connectome.M
            noise = float(body.get("poisson_noise", 0.35))
            probe = STATE.connectome.sample_noisy_probe(target_index=target_idx, poisson_noise_fraction=noise)
            traj = STATE.engram.decode(probe, n_steps=36, enable_thermal_noise=True)
            packet = STATE.tokenizer.tokenize(traj)
            self._send_json({
                "packet": packet.to_dict(),
                "initial_energy_kbt": traj.initial_energy_kbt,
                "settled_energy_kbt": traj.settled_energy_kbt,
                "delta_energy_kbt": traj.delta_energy_kbt,
                "reversibility_mse": traj.reversibility_mse,
                "measured_theta_hz": traj.measured_theta_hz,
            })

        elif req_path == "/api/query_spi":
            target_idx = int(body.get("target_index", 0)) % STATE.connectome.M
            query = str(body.get("query", "Who are you and what do you remember most vividly?"))
            q_res = STATE.qhn.run_quantum_recall(target_index=target_idx, bit_flip_fraction=0.35)
            packet = STATE.tokenizer.tokenize_quantum(q_res)
            turn = STATE.spi.query(query, packet, allow_live_api=True)
            self._send_json({
                "turn": turn.turn_index,
                "query": turn.user_query,
                "engram_id": turn.engram_id,
                "tokens": turn.gating_token_stream,
                "response": turn.persona_response,
                "grounding_verified": turn.grounding_verified,
            })
        else:
            self._send_json({"error": f"Unknown endpoint {req_path}"}, status=404)
