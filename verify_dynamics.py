"""
verify_dynamics.py
==================
Engram-0: Automated Pytest & Verification Test Harness.

Executes 50 Monte Carlo trials with 35% Poisson shot noise on input probes
and verifies all 6 mandatory Sandbox Assertions plus the Autonomous Self-Healing
calibration loop (sweeping gamma in [0.8, 2.5] and beta in [4.0, 12.0]).
Also exports 3D phase-space, connectome, and thermodynamic telemetry for the 3D UI.
"""

from __future__ import annotations

import json
from pathlib import Path
import time
from typing import Dict, List
import numpy as np

from connectome_ir import ConnectomeIR
from reversible_thermo_engram import (
    BIOLOGICAL_TEMP_K,
    TARGET_THETA_HZ,
    THETA_MAX_HZ,
    THETA_MIN_HZ,
    ReversibleThermoEngram,
)
from semantic_tokenizer import SemanticTokenizer
from spi_persona_engine import SPIPersonaEngine


NUM_MONTE_CARLO_TRIALS: int = 50
POISSON_NOISE_LEVEL: float = 0.35
MAX_LATENCY_MS: float = 50.0
REVERSIBILITY_MSE_THRESHOLD: float = 1e-5
CORE_RETENTION_THRESHOLD_PCT: float = 98.0


def run_autonomous_self_healing_demo(
    connectome: ConnectomeIR,
    spurious_basis: np.ndarray,
) -> Dict[str, object]:
    engine = ReversibleThermoEngram(
        X=connectome.X,
        gamma=0.80,
        beta=4.00,
        temperature_k=BIOLOGICAL_TEMP_K,
        f_theta_hz=TARGET_THETA_HZ,
        spurious_basis=spurious_basis,
        seed=42,
    )
    probe = connectome.sample_noisy_probe(target_index=0, poisson_noise_fraction=POISSON_NOISE_LEVEL)
    pre_res = engine.decode(probe, n_steps=32, enable_thermal_noise=True)
    pre_audit = engine.audit_sleep_pruning(spurious_basis)

    freq_ok = THETA_MIN_HZ <= pre_res.measured_theta_hz <= THETA_MAX_HZ
    pruning_ok = (
        pre_audit.spurious_dissolved_fraction >= 1.0
        and pre_audit.min_core_retention_pct >= CORE_RETENTION_THRESHOLD_PCT
    )

    heal_report = {
        "initial_gamma": 0.80,
        "initial_beta": 4.00,
        "initial_theta_hz": pre_res.measured_theta_hz,
        "initial_freq_ok": freq_ok,
        "initial_pruning_ok": pruning_ok,
        "triggered_self_healing": not (freq_ok and pruning_ok),
    }

    if not (freq_ok and pruning_ok):
        sweep_result = engine.autonomous_self_heal(
            spurious_basis=spurious_basis,
            sample_probe=probe,
            gamma_range=(0.8, 2.5),
            beta_range=(4.0, 12.0),
            n_grid=9,
        )
        heal_report.update(sweep_result)
    else:
        heal_report.update({
            "healed": True,
            "optimal_gamma": engine.gamma,
            "optimal_beta": engine.beta,
            "sweep_trials": 0,
            "sweep_log": [],
        })

    return heal_report


def run_verification_suite(export_telemetry_path: str | None = "engram_0_telemetry.json") -> Dict[str, object]:
    t0_init = time.perf_counter()
    connectome = ConnectomeIR(d=64, M=8, mode="HYBRID", f_theta_hz=TARGET_THETA_HZ, seed=42)
    spurious_basis = connectome.generate_spurious_attractors(n_spurious=6)
    init_ms = (time.perf_counter() - t0_init) * 1000.0

    heal_report = run_autonomous_self_healing_demo(connectome, spurious_basis)
    optimal_gamma = float(heal_report["optimal_gamma"])
    optimal_beta = float(heal_report["optimal_beta"])

    engram_layer = ReversibleThermoEngram(
        X=connectome.X,
        gamma=optimal_gamma,
        beta=optimal_beta,
        temperature_k=BIOLOGICAL_TEMP_K,
        f_theta_hz=TARGET_THETA_HZ,
        spurious_basis=spurious_basis,
        seed=42,
    )
    tokenizer = SemanticTokenizer(X=connectome.X, metadata=connectome.metadata)

    _warm_probe = connectome.sample_noisy_probe(target_index=0, poisson_noise_fraction=POISSON_NOISE_LEVEL)
    _warm_traj = engram_layer.decode(_warm_probe, n_steps=36)
    _ = tokenizer.tokenize(_warm_traj)

    rng = np.random.default_rng(20261025)
    trial_records: List[Dict[str, object]] = []
    delta_energies: List[float] = []
    reversibility_mses: List[float] = []
    measured_frequencies: List[float] = []
    stage1_to_3_latencies_ms: List[float] = []
    decoded_packets = []
    sample_trajectories_3d = []

    proj_3d_basis = connectome.X[:, :3]

    for trial_idx in range(NUM_MONTE_CARLO_TRIALS):
        target_engram_idx = 0 if trial_idx == 0 else (trial_idx % connectome.M)

        t_start = time.perf_counter()
        noisy_probe = connectome.sample_noisy_probe(
            target_index=target_engram_idx,
            poisson_noise_fraction=POISSON_NOISE_LEVEL,
            rng=rng,
        )
        traj = engram_layer.decode(
            probe_q=noisy_probe,
            n_steps=36,
            sim_duration_s=1.0,
            enable_thermal_noise=True,
            record_stride=2,
            rng=rng,
        )
        packet = tokenizer.tokenize(traj)
        t_end = time.perf_counter()

        latency_ms = (t_end - t_start) * 1000.0

        delta_energies.append(traj.delta_energy_kbt)
        reversibility_mses.append(traj.reversibility_mse)
        measured_frequencies.append(traj.measured_theta_hz)
        stage1_to_3_latencies_ms.append(latency_ms)
        decoded_packets.append(packet)

        if trial_idx < 12:
            coords_3d = (traj.trajectory_q @ proj_3d_basis).tolist()
            sample_trajectories_3d.append({
                "trial_id": trial_idx,
                "target_engram": target_engram_idx,
                "matched_engram": traj.matched_engram_idx,
                "initial_energy_kbt": round(traj.initial_energy_kbt, 4),
                "settled_energy_kbt": round(traj.settled_energy_kbt, 4),
                "delta_energy_kbt": round(traj.delta_energy_kbt, 4),
                "measured_theta_hz": round(traj.measured_theta_hz, 4),
                "reversibility_mse": float(traj.reversibility_mse),
                "latency_ms": round(latency_ms, 4),
                "tokens": packet.raw_token_stream,
                "path_3d": coords_3d,
                "energy_trace": [round(float(e), 4) for e in traj.trajectory_energy],
            })

        trial_records.append({
            "trial": trial_idx + 1,
            "target_idx": target_engram_idx,
            "matched_idx": traj.matched_engram_idx,
            "initial_energy_kbt": traj.initial_energy_kbt,
            "settled_energy_kbt": traj.settled_energy_kbt,
            "delta_energy_kbt": traj.delta_energy_kbt,
            "reversibility_mse": traj.reversibility_mse,
            "measured_theta_hz": traj.measured_theta_hz,
            "latency_ms": latency_ms,
            "confidence": packet.confidence_score,
            "tokens": packet.raw_token_stream,
        })

    jac_det = engram_layer.compute_symplectic_jacobian_det(_warm_probe, dt=0.004)
    pruning_audit = engram_layer.audit_sleep_pruning(spurious_basis=spurious_basis, rng=rng)

    spi_engine = SPIPersonaEngine()
    terminal_packet = decoded_packets[0]
    mandatory_query = "Where were you right before consciousness was preserved?"
    turn_1 = spi_engine.query(mandatory_query, terminal_packet, allow_live_api=True)

    turn_2 = spi_engine.query(
        "How did the 6.00 Hz REM theta clock and 310.15 K thermal noise affect spurious attractor states?",
        terminal_packet,
        allow_live_api=True,
    )
    h01_packet = next((p for p in decoded_packets if p.engram_index == 1), decoded_packets[1])
    turn_3 = spi_engine.query(
        "Recall the Google H01 cortical calibration in your Geneva neurophotonics lab.",
        h01_packet,
        allow_live_api=True,
    )
    cello_packet = next((p for p in decoded_packets if p.engram_index == 4), decoded_packets[4])
    turn_4 = spi_engine.query(
        "What episodic memory is locked inside your acoustic-limbic attractor basin from the Tonhalle?",
        cello_packet,
        allow_live_api=True,
    )

    a1_pass = all(de < 0.0 for de in delta_energies)
    a2_pass = all(mse < REVERSIBILITY_MSE_THRESHOLD for mse in reversibility_mses) and (
        abs(jac_det - 1.0) < 1e-9
    )
    a3_pass = all(THETA_MIN_HZ <= f <= THETA_MAX_HZ for f in measured_frequencies)
    a4_pass = (
        pruning_audit.spurious_dissolved_fraction == 1.0
        and pruning_audit.min_core_retention_pct >= CORE_RETENTION_THRESHOLD_PCT
        and float(np.max(pruning_audit.spurious_well_depths_kbt)) <= 12.0
        and float(np.min(pruning_audit.core_well_depths_initial_kbt)) >= 45.0
    )
    a5_pass = all(lat < MAX_LATENCY_MS for lat in stage1_to_3_latencies_ms)
    a6_pass = bool(turn_1.grounding_verified)

    ledger = {
        "project": "Engram-0 — Reversible Thermodynamic Brain Decoding & Digital Persona Engine",
        "target_model": "gemini-4-argon (thinking_level='high')",
        "temperature_k": BIOLOGICAL_TEMP_K,
        "num_monte_carlo_trials": NUM_MONTE_CARLO_TRIALS,
        "poisson_noise_fraction": POISSON_NOISE_LEVEL,
        "connectome_init_ms": round(init_ms, 3),
        "calibrated_gamma": optimal_gamma,
        "calibrated_beta": optimal_beta,
        "self_healing_report": heal_report,
        "assertions": {
            "ASSERTION_1_STRICT_ENERGY_MINIMIZATION": {
                "passed": a1_pass,
                "trials_passed": f"{sum(1 for de in delta_energies if de < 0.0)}/{NUM_MONTE_CARLO_TRIALS}",
                "mean_delta_energy_kbt": float(np.mean(delta_energies)),
                "max_delta_energy_kbt": float(np.max(delta_energies)),
                "min_delta_energy_kbt": float(np.min(delta_energies)),
            },
            "ASSERTION_2_SYMPLECTIC_REVERSIBILITY": {
                "passed": a2_pass,
                "jacobian_determinant": jac_det,
                "max_reversibility_mse": float(np.max(reversibility_mses)),
                "mean_reversibility_mse": float(np.mean(reversibility_mses)),
                "threshold_mse": REVERSIBILITY_MSE_THRESHOLD,
            },
            "ASSERTION_3_REM_THETA_RESONANCE_WINDOW": {
                "passed": a3_pass,
                "target_hz": TARGET_THETA_HZ,
                "allowed_window_hz": [THETA_MIN_HZ, THETA_MAX_HZ],
                "mean_measured_hz": float(np.mean(measured_frequencies)),
                "min_measured_hz": float(np.min(measured_frequencies)),
                "max_measured_hz": float(np.max(measured_frequencies)),
            },
            "ASSERTION_4_THERMODYNAMIC_PRUNING_AND_RETENTION": {
                "passed": a4_pass,
                "spurious_dissolved_pct": pruning_audit.spurious_dissolved_fraction * 100.0,
                "max_spurious_well_depth_kbt": float(np.max(pruning_audit.spurious_well_depths_kbt)),
                "min_core_well_depth_kbt": float(np.min(pruning_audit.core_well_depths_initial_kbt)),
                "mean_core_well_depth_kbt": float(np.mean(pruning_audit.core_well_depths_initial_kbt)),
                "min_core_retention_pct": pruning_audit.min_core_retention_pct,
                "mean_core_retention_pct": pruning_audit.mean_core_retention_pct,
            },
            "ASSERTION_5_END_TO_END_LATENCY": {
                "passed": a5_pass,
                "threshold_ms": MAX_LATENCY_MS,
                "mean_latency_ms": float(np.mean(stage1_to_3_latencies_ms)),
                "p95_latency_ms": float(np.percentile(stage1_to_3_latencies_ms, 95)),
                "max_latency_ms": float(np.max(stage1_to_3_latencies_ms)),
            },
            "ASSERTION_6_SPI_PERSONA_GROUNDING": {
                "passed": a6_pass,
                "query": mandatory_query,
                "gating_tokens": turn_1.gating_token_stream,
                "referenced_loc": turn_1.referenced_loc,
                "referenced_era": turn_1.referenced_era,
                "referenced_sensory": turn_1.referenced_sensory,
                "referenced_theta": turn_1.referenced_theta,
                "response": turn_1.persona_response,
            },
        },
        "all_assertions_passed": bool(
            a1_pass and a2_pass and a3_pass and a4_pass and a5_pass and a6_pass
        ),
        "dialogue_transcript": [
            {
                "turn": t.turn_index,
                "query": t.user_query,
                "engram_id": t.engram_id,
                "tokens": t.gating_token_stream,
                "response": t.persona_response,
                "grounding_verified": t.grounding_verified,
            }
            for t in spi_engine.dialogue_history
        ],
        "trial_summary": trial_records,
    }

    if export_telemetry_path:
        graph_3d = connectome.export_graph_3d()
        w_flat = graph_3d.coupling_matrix.copy()
        edges = []
        n_nodes = w_flat.shape[0]
        for i in range(n_nodes):
            for j in range(n_nodes):
                if i != j and w_flat[i, j] > 0.095:
                    edges.append({
                        "source": i,
                        "target": j,
                        "weight": round(float(w_flat[i, j]), 4),
                        "latency_ms": round(float(graph_3d.latency_matrix_ms[i, j]), 3),
                    })
        edges = sorted(edges, key=lambda e: e["weight"], reverse=True)[:180]

        telemetry_payload = {
            "ledger": ledger,
            "connectome_3d": {
                "nodes": [
                    {
                        "id": i,
                        "label": graph_3d.node_labels[i],
                        "subsystem": graph_3d.node_Subsystems[i],
                        "x": round(float(graph_3d.node_coords[i, 0]), 3),
                        "y": round(float(graph_3d.node_coords[i, 1]), 3),
                        "z": round(float(graph_3d.node_coords[i, 2]), 3),
                        "engram_0_loading": round(float(connectome.X[i, 0]), 4),
                    }
                    for i in range(n_nodes)
                ],
                "edges": edges,
                "engrams": [
                    {
                        "index": m.index,
                        "engram_id": m.engram_id,
                        "loc_token": f"<LOC:{m.location_token}>",
                        "era_token": f"<ERA:{m.era_token}>",
                        "valence_token": f"<VALENCE:{m.valence_token}>",
                        "sensory_summary": m.sensory_summary,
                        "well_depth_kbt": round(float(pruning_audit.core_well_depths_initial_kbt[m.index]), 2),
                        "retention_pct": round(float(pruning_audit.core_retention_percentages[m.index]), 2),
                        "anchor_3d": [
                            round(float(connectome.X[:, m.index] @ proj_3d_basis[:, 0]), 4),
                            round(float(connectome.X[:, m.index] @ proj_3d_basis[:, 1]), 4),
                            round(float(connectome.X[:, m.index] @ proj_3d_basis[:, 2]), 4),
                        ],
                    }
                    for m in connectome.metadata
                ],
                "spurious_basins": [
                    {
                        "id": f"SPURIOUS_TRAP_{k:02d}",
                        "well_depth_kbt": round(float(pruning_audit.spurious_well_depths_kbt[k]), 2),
                        "dissolved": bool(pruning_audit.spurious_dissolved_mask[k]),
                    }
                    for k in range(spurious_basis.shape[1])
                ],
            },
            "sample_trajectories_3d": sample_trajectories_3d,
        }
        Path(export_telemetry_path).write_text(json.dumps(telemetry_payload, indent=2), encoding="utf-8")

    return ledger


_CACHED_LEDGER: Dict[str, object] | None = None


def _get_ledger() -> Dict[str, object]:
    global _CACHED_LEDGER
    if _CACHED_LEDGER is None:
        _CACHED_LEDGER = run_verification_suite()
    return _CACHED_LEDGER


def test_assertion_1_strict_energy_minimization() -> None:
    ledger = _get_ledger()
    a1 = ledger["assertions"]["ASSERTION_1_STRICT_ENERGY_MINIMIZATION"]  # type: ignore[index]
    assert a1["passed"] is True
    assert a1["max_delta_energy_kbt"] < 0.0


def test_assertion_2_symplectic_reversibility() -> None:
    ledger = _get_ledger()
    a2 = ledger["assertions"]["ASSERTION_2_SYMPLECTIC_REVERSIBILITY"]  # type: ignore[index]
    assert a2["passed"] is True
    assert abs(a2["jacobian_determinant"] - 1.0) < 1e-9
    assert a2["max_reversibility_mse"] < REVERSIBILITY_MSE_THRESHOLD


def test_assertion_3_rem_resonance_window() -> None:
    ledger = _get_ledger()
    a3 = ledger["assertions"]["ASSERTION_3_REM_THETA_RESONANCE_WINDOW"]  # type: ignore[index]
    assert a3["passed"] is True
    assert THETA_MIN_HZ <= a3["min_measured_hz"] <= a3["max_measured_hz"] <= THETA_MAX_HZ


def test_assertion_4_thermodynamic_pruning_and_retention() -> None:
    ledger = _get_ledger()
    a4 = ledger["assertions"]["ASSERTION_4_THERMODYNAMIC_PRUNING_AND_RETENTION"]  # type: ignore[index]
    assert a4["passed"] is True
    assert a4["spurious_dissolved_pct"] == 100.0
    assert a4["min_core_retention_pct"] >= CORE_RETENTION_THRESHOLD_PCT
    assert a4["max_spurious_well_depth_kbt"] <= 12.0
    assert a4["min_core_well_depth_kbt"] >= 45.0


def test_assertion_5_end_to_end_latency() -> None:
    ledger = _get_ledger()
    a5 = ledger["assertions"]["ASSERTION_5_END_TO_END_LATENCY"]  # type: ignore[index]
    assert a5["passed"] is True
    assert a5["max_latency_ms"] < MAX_LATENCY_MS


def test_assertion_6_spi_persona_grounding() -> None:
    ledger = _get_ledger()
    a6 = ledger["assertions"]["ASSERTION_6_SPI_PERSONA_GROUNDING"]  # type: ignore[index]
    assert a6["passed"] is True
    assert a6["referenced_loc"] is True
    assert a6["referenced_era"] is True
    assert a6["referenced_sensory"] is True


def print_formatted_ledger(ledger: Dict[str, object]) -> None:
    print("=" * 88)
    print("ENGRAM-0: REVERSIBLE THERMODYNAMIC BRAIN DECODING & DIGITAL PERSONA ENGINE")
    print("Architecture : Pure-Software Dynamical Neural Decoder (IBM-1 + Google H01)")
    print(f"Target Model : {ledger['target_model']}")
    print(f"Temperature  : {ledger['temperature_k']} K (37.0 C) | Trials: {ledger['num_monte_carlo_trials']} (35% Poisson Noise)")
    print("=" * 88)

    heal = ledger["self_healing_report"]  # type: ignore[index]
    print("\n[AUTONOMOUS SELF-HEALING CALIBRATION DIRECTIVE]")
    print(
        f"  Initial Detuned State : gamma={heal['initial_gamma']:.2f}, beta={heal['initial_beta']:.2f} "
        f"-> f_theta={heal['initial_theta_hz']:.2f} Hz (Freq OK: {heal['initial_freq_ok']})"
    )
    print(
        f"  Calibrated Optimum    : gamma={heal['optimal_gamma']:.4f}, beta={heal['optimal_beta']:.4f} "
        f"(Swept {heal['sweep_trials']} grid points -> Healed: {heal['healed']})"
    )

    print("\n[AUTOMATED SANDBOX VERIFICATION LEDGER (ALL 6 ASSERTIONS)]")
    assertions = ledger["assertions"]  # type: ignore[index]
    for name, data in assertions.items():
        status = "PASS" if data["passed"] else "FAIL"
        print(f"  * {name}: [{status}]")
        for k, v in data.items():
            if k not in ("passed", "response"):
                if isinstance(v, float):
                    print(f"      - {k}: {v:.6g}")
                else:
                    print(f"      - {k}: {v}")

    print("\n" + "=" * 88)
    print("INTERACTIVE TERMINAL DIALOGUE TRANSCRIPT — DR. ALISTAIR VANCE (SPI)")
    print("=" * 88)
    for turn in ledger["dialogue_transcript"]:  # type: ignore[index]
        print(f"\n[TURN {turn['turn']} | ENGRAM: {turn['engram_id']}]")
        print(f"  GATING TOKENS : {turn['tokens']}")
        print(f"  USER QUERY    : {turn['query']}")
        print(f"  SPI RESPONSE  :\n    {turn['response'].replace(chr(10), chr(10) + '    ')}")
        print(f"  GROUNDING VERIFIED: {turn['grounding_verified']}")
    print("\n" + "=" * 88)
    print(f"OVERALL VERIFICATION STATUS: {'ALL 6 ASSERTIONS PASSED (100%)' if ledger['all_assertions_passed'] else 'FAILED'}")
    print("=" * 88)


if __name__ == "__main__":
    results = run_verification_suite()
    print_formatted_ledger(results)
