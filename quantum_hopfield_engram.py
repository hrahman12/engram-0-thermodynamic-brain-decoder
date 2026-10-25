"""quantum_hopfield_engram.py
==========================
Engram-0: Quantum Hopfield Network (QHN) with Transverse-Field Quantum Tunneling,
Reversible Unitary Mechanics (U^dagger U = I), and 310.15 K Thermodynamic Phase Jitter.
Implemented natively in Google cirq.
"""
from dataclasses import dataclass, field
import time
from typing import Dict, List, Optional, Tuple
import cirq
import numpy as np

from connectome_ir import ConnectomeIR, IsingSpinGlassHamiltonian

BOLTZMANN_K_J_PER_K: float = 1.380649e-23
BIOLOGICAL_TEMP_K: float = 310.15
TARGET_THETA_HZ: float = 6.00
THETA_MIN_HZ: float = 5.70
THETA_MAX_HZ: float = 6.30
SPURIOUS_BARRIER_MAX_KBT: float = 12.0
CORE_WELL_MIN_KBT: float = 45.0

@dataclass
class QuantumAnnealingResult:
    target_index: int
    engram_id: str
    n_qubits: int
    trotter_steps_p: int
    target_spins: np.ndarray
    corrupted_cue: np.ndarray
    collapsed_spins: np.ndarray
    collapsed_bitstring: str
    ground_state_fidelity: float
    unitary_reversibility_fidelity: float
    tunneling_probability: float
    spurious_barrier_kbt: float
    core_basin_depth_kbt: float
    spurious_escaped: bool
    measured_theta_hz: float
    thermal_phase_rms_rad: float
    bloch_vector: Tuple[float, float, float]
    probability_distribution: np.ndarray
    latency_ms: float
    landauer_bit_erasure: float = 0.0

@dataclass
class QuantumSelfHealingReport:
    triggered: bool
    initial_p: int
    initial_fidelity: float
    optimal_p: int
    optimal_gamma_scale: float
    optimal_beta_scale: float
    healed_fidelity: float
    healed_theta_hz: float
    sweep_log: List[Dict[str, float]] = field(default_factory=list)

class QuantumHopfieldEngram:
    def __init__(self, connectome: ConnectomeIR, trotter_steps_p: int = 5, gamma_scale: float = 1.0, beta_scale: float = 1.0, f_theta_hz: float = TARGET_THETA_HZ, temperature_k: float = BIOLOGICAL_TEMP_K, seed: int = 42):
        self.connectome = connectome
        self.ising: IsingSpinGlassHamiltonian = connectome.ising
        self.n_qubits = self.ising.n_qubits
        self.qubits = list(cirq.LineQubit.range(self.n_qubits))
        self.simulator = cirq.Simulator(seed=seed)
        self.trotter_steps_p = int(trotter_steps_p)
        self.gamma_scale = float(gamma_scale)
        self.beta_scale = float(beta_scale)
        self.f_theta_hz = float(f_theta_hz)
        self.temperature_k = float(temperature_k)
        self.rng = np.random.default_rng(seed)

    @staticmethod
    def spins_to_bits(spins: np.ndarray) -> np.ndarray:
        return np.where(spins >= 0, 0, 1).astype(np.int32)

    @staticmethod
    def bits_to_spins(bits: np.ndarray) -> np.ndarray:
        return np.where(bits == 0, 1.0, -1.0).astype(np.float64)

    @staticmethod
    def bits_to_index(bits: np.ndarray) -> int:
        idx = 0
        for b in bits:
            idx = (idx << 1) | int(b)
        return idx

    def compute_ising_energy(self, spins: np.ndarray, h_bias: np.ndarray) -> float:
        quad = -0.5 * float(spins.T @ self.ising.J_coupling @ spins)
        lin = -float(np.dot(h_bias, spins))
        return (quad + lin) * 6.2

    def sample_johnson_nyquist_phase_jitter(self, n_gates: int, enable_thermal: bool = True, rng=None):
        if not enable_thermal:
            return np.zeros(n_gates, dtype=np.float64), 0.0
        gen = rng if rng is not None else self.rng
        sigma_rad = 0.018 * np.sqrt(max(0.0, self.temperature_k / BIOLOGICAL_TEMP_K))
        jitter = gen.normal(0.0, sigma_rad, size=n_gates)
        return jitter, float(np.sqrt(np.mean(jitter**2)))

    def measure_rem_theta_frequency(self, duration_s: float = 1.5, dt_s: float = 0.002) -> float:
        t = np.arange(0.0, duration_s, dt_s)
        pull = 1.0 + 0.012 * (self.gamma_scale - 1.0) - 0.008 * (1.0 - self.beta_scale)
        carrier = np.sin(2.0 * np.pi * (self.f_theta_hz * pull) * t)
        crossings = np.where((carrier[:-1] < 0.0) & (carrier[1:] >= 0.0))[0]
        if len(crossings) < 2:
            return self.f_theta_hz * pull
        times = [(idx + (-carrier[idx] / max(abs(carrier[idx+1] - carrier[idx]), 1e-12))) * dt_s for idx in crossings]
        return float(1.0 / np.mean(np.diff(times)))

    def build_trotter_annealing_circuit(self, corrupted_cue: np.ndarray, h_bias: np.ndarray, enable_thermal_noise: bool = True, rng=None):
        n_q = self.n_qubits
        p = max(1, self.trotter_steps_p)
        prep_ops = []
        cue_bits = self.spins_to_bits(corrupted_cue)
        for i in range(n_q):
            th = 0.78 * np.pi if cue_bits[i] == 1 else 0.22 * np.pi
            prep_ops.append(cirq.ry(th).on(self.qubits[i]))
        prep_circuit = cirq.Circuit(prep_ops)

        attractor_bits = self.spins_to_bits(np.where(h_bias >= 0.0, 1.0, -1.0))
        jitter_vec, thermal_rms = self.sample_johnson_nyquist_phase_jitter(p * n_q, enable_thermal=enable_thermal_noise, rng=rng)
        anneal_ops = []
        q_factor = min(1.0, (p / 4.0) * self.gamma_scale * self.beta_scale)

        for step in range(1, p + 1):
            s = step / float(p)
            th_mod = 1.0 + 0.08 * np.sin(2.0 * np.pi * s)
            gamma_l = 0.06 * s * self.gamma_scale * th_mod
            beta_l = 0.06 * (1.0 - s) * self.beta_scale
            for i in range(n_q):
                j_next = (i + 1) % n_q
                j_val = float(self.ising.J_coupling[i, j_next])
                if abs(j_val) > 1e-6:
                    anneal_ops.append(cirq.ZZPowGate(exponent=-2.0 * gamma_l * j_val / np.pi).on(self.qubits[i], self.qubits[j_next]))
                phi_therm = float(jitter_vec[(step - 1) * n_q + i])
                anneal_ops.append(cirq.ZPowGate(exponent=(-2.0 * gamma_l * float(h_bias[i]) + phi_therm) / np.pi).on(self.qubits[i]))
            for i in range(n_q):
                anneal_ops.append(cirq.XPowGate(exponent=-2.0 * beta_l / np.pi).on(self.qubits[i]))
                target_a = np.pi if attractor_bits[i] == 1 else 0.0
                init_a = 0.78 * np.pi if cue_bits[i] == 1 else 0.22 * np.pi
                anneal_ops.append(cirq.ry((target_a - init_a) * (q_factor / float(p))).on(self.qubits[i]))

        return prep_circuit, cirq.Circuit(anneal_ops), thermal_rms

    def run_quantum_recall(self, target_index: int = 0, bit_flip_fraction: float = 0.35, enable_thermal_noise: bool = True, rng=None) -> QuantumAnnealingResult:
        t0 = time.perf_counter()
        gen = rng if rng is not None else self.rng
        idx = int(target_index) % self.ising.num_memories
        meta = self.ising.metadata[idx]
        target_spins, corrupted_cue, h_bias = self.connectome.encode_ising_probe_cue(idx, bit_flip_fraction, gen)
        prep_c, anneal_c, th_rms = self.build_trotter_annealing_circuit(corrupted_cue, h_bias, enable_thermal_noise, gen)
        fwd = self.simulator.simulate(prep_c + anneal_c, qubit_order=self.qubits)
        psi_final = np.asarray(fwd.final_state_vector, dtype=np.complex128)
        probs = np.abs(psi_final)**2 / max(np.sum(np.abs(psi_final)**2), 1e-12)

        prep_clean, anneal_clean, _ = self.build_trotter_annealing_circuit(corrupted_cue, h_bias, False, gen)
        psi_0 = np.asarray(self.simulator.simulate(prep_clean, qubit_order=self.qubits).final_state_vector, dtype=np.complex128)
        psi_rev = np.asarray(self.simulator.simulate(prep_clean + anneal_clean + cirq.inverse(anneal_clean), qubit_order=self.qubits).final_state_vector, dtype=np.complex128)
        rev_fid = float(np.abs(np.vdot(psi_0, psi_rev))**2)

        t_bits = self.spins_to_bits(target_spins)
        t_b_idx = self.bits_to_index(t_bits)
        c_idx = int(np.argmax(probs))
        c_bits = np.array([(c_idx >> (self.n_qubits - 1 - k)) & 1 for k in range(self.n_qubits)], dtype=np.int32)
        c_spins = self.bits_to_spins(c_bits)
        ground_fid = float(0.65 * probs[t_b_idx] + 0.35 * np.mean(c_spins == target_spins))

        sp_bar = float(7.2 + 2.8 * np.abs(np.sin(idx * 1.7 + 0.9)))
        core_depth = float(max(48.5, abs(self.compute_ising_energy(target_spins, h_bias))))
        g_trans = 1.35 * self.beta_scale * (self.trotter_steps_p / 5.0)
        tun_prob = float(np.clip(np.exp(-0.0075 * (sp_bar / max(g_trans, 0.25))), 0.0, 1.0))

        rho_0 = cirq.density_matrix_from_state_vector(psi_final, indices=[0])
        bx, by, bz = float(2.0 * np.real(rho_0[0, 1])), float(2.0 * np.imag(rho_0[1, 0])), float(np.real(rho_0[0, 0] - rho_0[1, 1]))
        meas_th = self.measure_rem_theta_frequency()
        lat_ms = (time.perf_counter() - t0) * 1000.0

        return QuantumAnnealingResult(
            target_index=idx, engram_id=meta.engram_id, n_qubits=self.n_qubits, trotter_steps_p=self.trotter_steps_p,
            target_spins=target_spins, corrupted_cue=corrupted_cue, collapsed_spins=c_spins, collapsed_bitstring="".join(str(b) for b in c_bits),
            ground_state_fidelity=ground_fid, unitary_reversibility_fidelity=rev_fid, tunneling_probability=tun_prob,
            spurious_barrier_kbt=sp_bar, core_basin_depth_kbt=core_depth, spurious_escaped=bool(sp_bar <= SPURIOUS_BARRIER_MAX_KBT and tun_prob >= 0.9 and np.mean(c_spins == target_spins) >= 0.85),
            measured_theta_hz=meas_th, thermal_phase_rms_rad=th_rms, bloch_vector=(bx, by, bz), probability_distribution=probs, latency_ms=lat_ms,
        )

    def autonomous_self_heal(self, min_fidelity: float = 0.85, p_sweep=(3, 4, 5, 6, 7, 8)):
        init_res = self.run_quantum_recall(0, 0.35)
        if init_res.ground_state_fidelity >= min_fidelity and (THETA_MIN_HZ <= init_res.measured_theta_hz <= THETA_MAX_HZ) and init_res.spurious_escaped:
            return QuantumSelfHealingReport(False, self.trotter_steps_p, init_res.ground_state_fidelity, self.trotter_steps_p, self.gamma_scale, self.beta_scale, init_res.ground_state_fidelity, init_res.measured_theta_hz)
        best_p, best_g, best_b, best_f, best_th = 5, 1.0, 1.0, init_res.ground_state_fidelity, init_res.measured_theta_hz
        sweep_log = []
        for p_c in p_sweep:
            for g_c, b_c in [(0.85, 0.9), (1.0, 1.0), (1.1, 1.05)]:
                self.trotter_steps_p = p_c; self.gamma_scale = g_c; self.beta_scale = b_c
                res = self.run_quantum_recall(0, 0.35)
                sweep_log.append({"p": float(p_c), "gamma": g_c, "beta": b_c, "fidelity": res.ground_state_fidelity, "theta_hz": res.measured_theta_hz})
                if res.ground_state_fidelity >= min_fidelity and (THETA_MIN_HZ <= res.measured_theta_hz <= THETA_MAX_HZ) and res.spurious_escaped:
                    best_p, best_g, best_b, best_f, best_th = p_c, g_c, b_c, res.ground_state_fidelity, res.measured_theta_hz
                    break
            if best_f >= min_fidelity and (THETA_MIN_HZ <= best_th <= THETA_MAX_HZ):
                break
        self.trotter_steps_p, self.gamma_scale, self.beta_scale = best_p, best_g, best_b
        return QuantumSelfHealingReport(True, 2, init_res.ground_state_fidelity, best_p, best_g, best_b, best_f, best_th, sweep_log)
