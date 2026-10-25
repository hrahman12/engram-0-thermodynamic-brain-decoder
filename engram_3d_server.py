"""
engram_3d_server.py
===================
Engram-0: Local HTTP & Live Telemetry Server for the 3D UI Command Center.

Serves `engram0/web/index.html` (and `connectome_hopfield.html`, `thermo_spi.html`,
`engram_0_3d_ui.html`, and 28 FreeSurfer/ENIGMA binary brain meshes) and provides
live JSON API endpoints backed directly by `connectome_ir.py`,
`reversible_thermo_engram.py`, `semantic_tokenizer.py`, `spi_persona_engine.py`,
and `verify_dynamics.py`.
"""

from __future__ import annotations

from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import mimetypes
from pathlib import Path
from typing import Dict
from urllib.parse import urlparse

from connectome_ir import ConnectomeIR
from reversible_thermo_engram import BIOLOGICAL_TEMP_K, TARGET_THETA_HZ, ReversibleThermoEngram
from semantic_tokenizer import SemanticTokenizer
from spi_persona_engine import SPIPersonaEngine
from verify_dynamics import run_verification_suite


WORKSPACE_DIR = Path(__file__).resolve().parent
WEB_DIR = WORKSPACE_DIR / "engram0" / "web"
TELEMETRY_FILE = WORKSPACE_DIR / "engram_0_telemetry.json"
UI_HTML_FILE = WORKSPACE_DIR / "engram_0_3d_ui.html"


class Engram3DState:
    """Stateful singleton holding the initialized Engram-0 pipeline for the 3D UI."""

    def __init__(self) -> None:
        self.connectome = ConnectomeIR(d=64, M=8, mode="HYBRID", f_theta_hz=TARGET_THETA_HZ, seed=42)
        self.spurious = self.connectome.generate_spurious_attractors(n_spurious=6)
        self.engram = ReversibleThermoEngram(
            X=self.connectome.X,
            gamma=1.4375,
            beta=8.00,
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
    """HTTP handler serving the 3D UI, FreeSurfer/ENIGMA binary meshes, and live Engram-0 dynamical API."""

    def _send_json(self, payload: Dict[str, object], status: int = 200) -> None:
        raw = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def do_GET(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        req_path = parsed.path

        if req_path in ("/", "/index.html"):
            html_bytes = (WEB_DIR / "index.html").read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(html_bytes)))
            self.end_headers()
            self.wfile.write(html_bytes)
            return

        if req_path == "/engram_0_3d_ui.html":
            html_bytes = UI_HTML_FILE.read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(html_bytes)))
            self.end_headers()
            self.wfile.write(html_bytes)
            return

        if req_path in ("/api/telemetry", "/api/state"):
            data = json.loads(TELEMETRY_FILE.read_text(encoding="utf-8"))
            self._send_json(data)
            return

        rel = req_path.lstrip("/")
        if rel.startswith("engram0/web/"):
            rel = rel[len("engram0/web/"):]
        candidate = (WEB_DIR / rel).resolve()
        if not candidate.is_file() and rel.startswith("assets/"):
            candidate = (WORKSPACE_DIR / rel).resolve()
        if (
            (str(candidate).startswith(str(WEB_DIR.resolve())) or str(candidate).startswith(str((WORKSPACE_DIR / "assets").resolve())))
            and candidate.is_file()
        ):
            data = candidate.read_bytes()
            ctype, _ = mimetypes.guess_type(str(candidate))
            if candidate.suffix == ".bin":
                ctype = "application/octet-stream"
            elif candidate.suffix == ".js":
                ctype = "application/javascript; charset=utf-8"
            elif candidate.suffix == ".css":
                ctype = "text/css; charset=utf-8"
            elif candidate.suffix == ".svg":
                ctype = "image/svg+xml"
            self.send_response(200)
            self.send_header("Content-Type", ctype or "application/octet-stream")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
            return

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
        elif self.path == "/api/sleep_prune":
            report = STATE.engram.sleep_prune_spurious_states(n_samples_per_spurious=8, n_steps=36)
            self._send_json({"sleep_pruning_report": report.to_dict()})
        elif self.path == "/api/self_heal":
            data = json.loads(TELEMETRY_FILE.read_text(encoding="utf-8"))
            self._send_json(data)
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
