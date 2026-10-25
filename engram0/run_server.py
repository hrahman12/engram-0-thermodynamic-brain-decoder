"""
engram0/run_server.py
=====================
Serves the 3-page Three.js Control-Room Web Suite (`engram0/web/index.html`,
`connectome_hopfield.html`, `thermo_spi.html`), 28 FreeSurfer/ENIGMA binary
brain meshes (`engram0/web/anatomy/*.bin`), and live JSON API endpoints.
"""

from __future__ import annotations

from engram_3d_server import run_server


def main(host: str = "127.0.0.1", port: int = 8765) -> None:
    print(f"[ENGRAM-0] 3D Control-Room Suite online at http://{host}:{port}/index.html")
    print(f"  - Home               : http://{host}:{port}/index.html")
    print(f"  - ConnectomeHopfield : http://{host}:{port}/connectome_hopfield.html")
    print(f"  - ThermoSPI Reactor  : http://{host}:{port}/thermo_spi.html")
    run_server(host=host, port=port)


if __name__ == "__main__":
    main()
