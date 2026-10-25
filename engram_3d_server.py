"""
engram_3d_server.py
===================
Engram-0: Local HTTP & Live Telemetry Server for the 3D UI Command Center.

Serves `engram_0_3d_ui.html` and provides live JSON API endpoints backed
directly by `connectome_ir.py`, `reversible_thermo_engram.py`,
`semantic_tokenizer.py`, `spi_persona_engine.py`, and `verify_dynamics.py`:
  - GET  /                   -> Interactive 3D Command Center UI
  - GET  /api/telemetry      -> Full 3D Connectome, Hopfield, and 50-trial ledger JSON
  - POST /api/decode         -> Live 35% Poisson probe decoding & tokenization
  - POST /api/query_spi      -> Live strictly-gated query to Dr. Alistair Vance SPI
"""

from __future__ import annotations

from http.server import BaseHTTPRequestHandler, HTTPServer
import json
from pathlib import Path
from typing import Dict

from connectome_ir import ConnectomeIR
from reversible_thermo_engram import BIOLOGICAL_TEMP_K, TARGET_THETA_HZ, ReversibleThermoEngram
from semantic_tokenizer import SemanticTokenizer
from spi_persona_engine import SPIPersonaEngine
from verify_dynamics import run_verification_suite


WORKSPACE_DIR = Path(__file__).resolve().parent
TELEMETRY_FILE = WORKSPACE_DIR / "engram_0_telemetry.json"
UI_HTML_FILE = WORKSPACE_DIR / "engram_0_3d_ui.html"


class Engram3DState:
    """Stateful singleton holding the initialized Engram-0 pipeline for the 3D UI."""

    def __init__(self) -> None:
        self.connectome = ConnectomeIR(d=64, M=8, mode="HYBRID", f_theta_hz=TARGET_THETA_HZ, seed=42)
        self.spurious = self.connectome.generate_spurious_attractors(n_spurious=6)
        self.engram = ReversibleThermoEngram(
            X=self.connectome.X,
            gamma=1.2250,
            beta=9.00,
            temperature_k=BIOLOGICAL_TEMP_K,
            f_theta_hz=TARGET_THETA_HZ,
            spurious_basis=self.spurious,
            seed=42,
        )
        self.tokenizer = SemanticTokenizer(X=self.connectome.X, metadata=self.connectome.metadata)
        self.spi = SPIPersonaEngine()
        if not TELEMETRY_FILE.exists():
            run_verification_suite(str(TELEMETRY_FILE))


STATE = Engram3DState()


class Engram3DRequestHandler(BaseHTTPRequestHandler):
    """HTTP handler serving the 3D UI and live Engram-0 dynamical API."""

    def _send_json(self, payload: Dict[str, object], status: int = 200) -> None:
        raw = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def do_GET(self) -> None:  # noqa: N802
        if self.path in ("/", "/index.html", "/engram_0_3d_ui.html"):
            html_bytes = UI_HTML_FILE.read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(html_bytes)))
            self.end_headers()
            self.wfile.write(html_bytes)
        elif self.path == "/api/telemetry":
            data = json.loads(TELEMETRY_FILE.read_text(encoding="utf-8"))
            self._send_json(data)
        else:
            self._send_json({"error": "Not found"}, status=404)

    def do_POST(self) -> None:  # noqa: N802
        length = int(self.headers.get("Content-Length", "0"))
        body = json.loads(self.rfile.read(length).decode("utf-8")) if length > 0 else {}

        if self.path == "/api/decode":
            target_idx = int(body.get("target_index", 0))
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
        elif self.path == "/api/query_spi":
            target_idx = int(body.get("target_index", 0))
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
            self._send_json({"error": "Unknown endpoint"}, status=404)


def run_server(host: str = "127.0.0.1", port: int = 8765) -> None:
    server = HTTPServer((host, port), Engram3DRequestHandler)
    print(f"Engram-0 3D Command Center active at http://{host}:{port}")
    server.serve_forever()


if __name__ == "__main__":
    run_server()
