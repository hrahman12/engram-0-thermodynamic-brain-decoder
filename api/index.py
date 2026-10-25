"""
api/index.py
============
Full-Stack Vercel Python Serverless Entrypoint for Project Engram-0.

Serves:
  - GET  /                                 -> 3D Connectome & Neural Connector Graph UI (`engram_0_3d_ui.html`)
  - GET  /studio                           -> My Little Brain / cortex² 3D Studio (`engram0/web/index.html`)
  - GET  /hopfield                         -> 3D Connectome & Hopfield Sanctuary (`engram0/web/connectome_hopfield.html`)
  - GET  /thermo                           -> 3D ThermoSPI Reactor (`engram0/web/thermo_spi.html`)
  - GET  /anatomy/* & /engram0/web/*       -> 28 FreeSurfer/ENIGMA `.bin` 3D meshes, JS, CSS, SVG
  - GET  /api/telemetry | /api/state       -> Live 50-trial verification & 3D telemetry JSON
  - POST /api/decode                       -> Live 35% Poisson probe decoding & semantic tokenization
  - POST /api/sleep_prune                  -> 310.15 K Johnson-Nyquist sleep pruning report
  - POST /api/self_heal                    -> Autonomous (gamma, beta) self-healing calibration
  - POST /api/query_spi                    -> Strictly token-gated Dr. Alistair Vance SPI (`gemini-4-argon`)
"""

from __future__ import annotations

from http.server import BaseHTTPRequestHandler
import json
import mimetypes
from pathlib import Path
import sys
from typing import Dict
from urllib.parse import parse_qs, urlparse

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from connectome_ir import ConnectomeIR
from reversible_thermo_engram import BIOLOGICAL_TEMP_K, TARGET_THETA_HZ, ReversibleThermoEngram
from semantic_tokenizer import SemanticTokenizer
from spi_persona_engine import SPIPersonaEngine
from verify_dynamics import run_verification_suite

WEB_DIR = ROOT_DIR / "engram0" / "web"
TELEMETRY_FILE = ROOT_DIR / "engram_0_telemetry.json"
UI_HTML_FILE = ROOT_DIR / "engram_0_3d_ui.html"


class _VercelEngramSingleton:
    def __init__(self) -> None:
        self.connectome = ConnectomeIR(d=64, M=8, mode="HYBRID", f_theta_hz=TARGET_THETA_HZ, seed=42)
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
        self.tokenizer = SemanticTokenizer(X=self.connectome.X, metadata=self.connectome.metadata)
        self.spi = SPIPersonaEngine()
        self._cached_telemetry: Dict[str, object] | None = None

    def get_telemetry(self) -> Dict[str, object]:
        if self._cached_telemetry is not None:
            return self._cached_telemetry
        if TELEMETRY_FILE.exists():
            self._cached_telemetry = json.loads(TELEMETRY_FILE.read_text(encoding="utf-8"))
            return self._cached_telemetry
        self._cached_telemetry = run_verification_suite(str(ROOT_DIR / "/tmp/engram_0_telemetry.json"))
        return self._cached_telemetry


STATE = _VercelEngramSingleton()


class handler(BaseHTTPRequestHandler):  # noqa: N801
    """Vercel Python Serverless HTTP Handler serving both the 3D UI and dynamical API."""

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

    def _send_json(self, payload: Dict[str, object], status: int = 200) -> None:
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

        # 1. Main 3D Connectome & Connector Graph UI
        if req_path in ("/", "/index.html", "/engram_0_3d_ui.html", "/api/index.py"):
            self._send_bytes(UI_HTML_FILE.read_bytes(), "text/html; charset=utf-8")
            return

        # 2. 3D Studio & Sub-pages
        if req_path in ("/studio", "/engram0/web/index.html"):
            self._send_bytes((WEB_DIR / "index.html").read_bytes(), "text/html; charset=utf-8")
            return
        if req_path in ("/hopfield", "/connectome_hopfield.html", "/engram0/web/connectome_hopfield.html"):
            self._send_bytes((WEB_DIR / "connectome_hopfield.html").read_bytes(), "text/html; charset=utf-8")
            return
        if req_path in ("/thermo", "/thermo_spi.html", "/engram0/web/thermo_spi.html"):
            self._send_bytes((WEB_DIR / "thermo_spi.html").read_bytes(), "text/html; charset=utf-8")
            return

        # 3. Telemetry JSON API
        if req_path in ("/api/telemetry", "/api/state"):
            self._send_json(STATE.get_telemetry())
            return

        # 4. Static Assets (anatomy/*.bin, engram0/web/*, assets/*)
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

        if req_path == "/api/decode":
            target_idx = int(body.get("target_index", 0)) % 8
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
        elif req_path == "/api/sleep_prune":
            report = STATE.engram.sleep_prune_spurious_states(n_samples_per_spurious=8, n_steps=36)
            self._send_json({"sleep_pruning_report": report.to_dict()})
        elif req_path == "/api/self_heal":
            self._send_json(STATE.get_telemetry())
        elif req_path == "/api/query_spi":
            target_idx = int(body.get("target_index", 0)) % 8
            query = str(body.get("query", "Where were you right before consciousness was preserved?"))
            probe = STATE.connectome.sample_noisy_probe(target_index=target_idx, poisson_noise_fraction=0.35)
            traj = STATE.engram.decode(probe, n_steps=36, enable_thermal_noise=True)
            packet = STATE.tokenizer.tokenize(traj)
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
