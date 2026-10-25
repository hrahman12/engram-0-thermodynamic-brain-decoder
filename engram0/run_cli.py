"""
engram0/run_cli.py
==================
Interactive CLI runner for Engram-0 (ConnectomeHopfield x ThermoSPI).
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from verify_dynamics import print_formatted_ledger, run_verification_suite


def main() -> None:
    ledger = run_verification_suite(str(ROOT_DIR / "engram_0_telemetry.json"))
    print_formatted_ledger(ledger)


if __name__ == "__main__":
    main()
