"""
connectome_ir.py
================
Engram-0: Plug-and-Play Connectome Intermediate Representation (IR) Adapter.

Supports macroscopic IBM-1 neural mass matrices and microscopic Google H01
human cortical slice matrices. Maps directed graph coupling weights (W) and
axonal/dendritic conduction latencies (tau) into normalized continuous
associative engram bases: X in R^{d x M}.

Pure-software dynamical neural decoder (No hardware silicon, SPICE, or EDA).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Literal, Optional, Tuple
import numpy as np


ConnectomeMode = Literal["IBM-1", "H01", "HYBRID"]


@dataclass
class EngramMetadata:
    """Episodic metadata associated with each column basis vector in X."""
    engram_id: str
    index: int
    location_token: str
    era_token: str
    valence_token: str
    sensory_summary: str
    basin_weight: float = 1.0
    is_spurious: bool = False


@dataclass
class ConnectomeGraph3D:
    """3D anatomical and topological graph representation for 3D UI visualization."""
    node_coords: np.ndarray          # Shape: (N, 3) in mm (MNI-like / cortical slab space)
    node_labels: List[str]           # Length N
    node_Subsystems: List[str]       # Length N (e.g. 'Hippocampus-CA3', 'H01-L5-Pyramidal')
    coupling_matrix: np.ndarray      # Shape: (N, N) directed coupling weights
    latency_matrix_ms: np.ndarray    # Shape: (N, N) conduction latencies in ms
    engram_basis: np.ndarray         # Shape: (d, M) normalized continuous associative basis X
    engram_metadata: List[EngramMetadata] = field(default_factory=list)


# Exact 158 Google H01 C3 Segment IDs from query: "#interneuron #L2 NSe>=800 <NSi"
# Position: [379548.5, 137610.125, 2660.5], Voxel size: [8nm, 8nm, 33nm], colorSeed: 4270253886
H01_C3_SEGMENT_IDS: List[str] = [
    "1100054524", "1115430292", "12237931142", "1333290325", "1538274151", "1539076840",
    "1594648509", "1638188509", "1828951844", "1915887451", "1988993337", "20070214646",
    "2090806103", "2134549398", "2178704414", "2294780853", "2339328448", "2499107339",
    "2499384877", "2557789796", "2673254402", "27622860459", "27651872764", "27870683066",
    "2791142865", "28000894735", "28045909614", "28378958224", "28409678489", "28452985548",
    "28525770719", "28643309290", "28672203772", "28802547903", "28803598117", "28918216929",
    "29021270843", "29182786959", "29238417446", "29298236361", "2935896346", "29459096371",
    "29618159554", "29765396306", "29925423252", "29938695074", "29969547791", "30101233972",
    "3023633866", "30376944711", "30406000355", "3052908678", "30668773752", "30767987832",
    "30871567933", "30974109956", "31031989065", "31032951251", "31061717348", "31133932587",
    "31149133165", "3125564306", "31658722916", "32444986357", "3430740099", "3504577656",
    "3518943222", "3573728110", "36123853342", "36153829678", "36241229806", "36284756264",
    "36445761568", "36590837294", "36619747807", "36620463168", "36633005581", "3664545249",
    "36662790455", "36678107375", "36763714196", "36809473223", "36822073774", "36822262086",
    "36852896228", "37173591638", "37218168369", "37318668413", "37319791473", "37420743412",
    "37421824682", "37463700916", "37536734693", "37581252436", "37594612366", "37668755920",
    "37770758892", "37801070911", "37930756265", "37958718097", "38018479939", "38092682277",
    "38106873604", "38208029710", "38222309348", "38339219897", "38368158152", "38383402139",
    "3839697992", "38413115427", "38543488421", "38573083867", "38586823171", "38602358951",
    "38717924646", "38863556782", "38863862489", "3897678996", "38994907574", "39023934118",
    "39038491013", "39052800624", "39081564265", "39271712983", "39271916939", "39359991385",
    "3941569746", "39505037109", "39694250521", "40043667040", "40102203154", "40247497000",
    "40378483178", "40407875435", "40464862282", "41354296446", "41630488832", "4217863883",
    "4318903980", "45701832369", "4580553370", "4698412002", "4784821941", "48079386659",
    "4917456198", "4961186471", "5062824784", "5499847526", "58866575372", "59536235974",
    "5965326176", "6024781859", "664433854", "707068981", "794630620", "823395680",
    "853035674", "910562342",
]
H01_VOXEL_DIMENSIONS_M = {"x": 8e-9, "y": 8e-9, "z": 3.3e-8}
H01_CANONICAL_POSITION = (379548.5, 137610.125, 2660.5)
H01_SEGMENT_QUERY = "#interneuron #L2 NSe>=800 <NSi"
H01_COLOR_SEED = 4270253886


# Consolidated episodic memories of Dr. Alistair Vance
CANONICAL_VANCE_ENGRAMS: List[EngramMetadata] = [
    EngramMetadata(
        engram_id="ENGRAM_00_CRYO_CHAMBER_7",
        index=0,
        location_token="SUB_LEVEL_4_CRYO_VAULT_BAY_7_ZURICH",
        era_token="2026_10_24_2358_UTC_TERMINAL_TRANSFER",
        valence_token="RESOLUTE_AWE_MELANCHOLIC_CALM_0.89",
        sensory_summary=(
            "Ozone smell of superconducting Helmholtz coils, amber status LEDs reflecting "
            "off frosted quartz observation glass, rhythmic 6.00 Hz acoustic hum of the "
            "thermodynamic phase-lock resonator, cold titanium headrest against the occiput."
        ),
        basin_weight=1.00,
        is_spurious=False,
    ),
    EngramMetadata(
        engram_id="ENGRAM_01_H01_SYNAPTIC_MAP",
        index=1,
        location_token="GENEVA_NEUROPHOTONICS_LAB_CLEANROOM_B",
        era_token="2024_03_14_1620_UTC_H01_CALIBRATION",
        valence_token="EUPHORIC_DISCOVERY_FOCUS_0.94",
        sensory_summary=(
            "Blue Cherenkov-like fluorescence on the petavoxel electron microscopy monitor, "
            "layer-5 pyramidal dendritic spines aligning into symplectic invariants."
        ),
        basin_weight=0.92,
        is_spurious=False,
    ),
    EngramMetadata(
        engram_id="ENGRAM_02_LAKE_GENEVA_RAIN",
        index=2,
        location_token="QUAI_DU_MONT_BLANC_PROMENADE",
        era_token="2025_11_02_1945_UTC_AUTUMN_DUSK",
        valence_token="NOSTALGIC_SOLITUDE_WARMTH_0.76",
        sensory_summary=(
            "Raindrops fracturing sodium streetlamp reflections on wet cobblestones, "
            "distant ferry horn across Lake Geneva, espresso cup warming chilled fingers."
        ),
        basin_weight=0.88,
        is_spurious=False,
    ),
    EngramMetadata(
        engram_id="ENGRAM_03_ETH_LECTURE_HALL",
        index=3,
        location_token="ETH_ZURICH_AUDITORIUM_MAXIMUM_HG_F30",
        era_token="2023_09_18_1015_UTC_KEYNOTE_DEFENSE",
        valence_token="INTELLECTUAL_URGENCY_CONVICTION_0.84",
        sensory_summary=(
            "Chalk dust suspended in projector beams, derivation of Liouville volume-preserving "
            "neural Hamiltonian flows on the slate blackboard."
        ),
        basin_weight=0.86,
        is_spurious=False,
    ),
    EngramMetadata(
        engram_id="ENGRAM_04_DAUGHTER_CELLO_RECITAL",
        index=4,
        location_token="TONHALLE_KLEINER_SAAL_ZURICH",
        era_token="2022_12_19_2000_UTC_WINTER_CONCERT",
        valence_token="PROFOUND_TENDERNESS_GRIEF_0.96",
        sensory_summary=(
            "Resonant C-minor cello harmonics vibrating through polished pine floorboards, "
            "Elena's bow catching the stage spotlight."
        ),
        basin_weight=0.91,
        is_spurious=False,
    ),
    EngramMetadata(
        engram_id="ENGRAM_05_JUNGFRAUJOCH_OBSERVATORY",
        index=5,
        location_token="SPHINX_OBSERVATORY_3571M_ALPS",
        era_token="2021_08_11_0310_UTC_PERSEID_ZENITH",
        valence_token="TRANSCENDENT_STILLNESS_CLARITY_0.87",
        sensory_summary=(
            "Sub-zero alpine wind against the steel cupola, Milky Way core arcing above "
            "the Aletsch Glacier, crisp thin air."
        ),
        basin_weight=0.85,
        is_spurious=False,
    ),
    EngramMetadata(
        engram_id="ENGRAM_06_IBM1_ARRAY_BOOT",
        index=6,
        location_token="RUSCHLIKON_COMPUTE_BUNKER_RACK_12",
        era_token="2026_05_09_0442_UTC_FIRST_THETA_LOCK",
        valence_token="CAUTIOUS_TRIUMPH_RELIEF_0.83",
        sensory_summary=(
            "Oscilloscope trace snapping into a clean 6.00 Hz limit cycle as thermal "
            "fluctuations dissolved spurious attractor ghosts."
        ),
        basin_weight=0.87,
        is_spurious=False,
    ),
    EngramMetadata(
        engram_id="ENGRAM_07_FINAL_CONSENT_LOG",
        index=7,
        location_token="SUB_LEVEL_4_PREP_ANTECHAMBER_ZURICH",
        era_token="2026_10_24_2315_UTC_PRE_SCAN_BRIEFING",
        valence_token="STOIC_ACCEPTANCE_CURIOSITY_0.81",
        sensory_summary=(
            "Signing the fountain-pen consent ledger beside Dr. Lin, hearing the liquid "
            "helium transfer valves cycle open in Bay 7."
        ),
        basin_weight=0.89,
        is_spurious=False,
    ),
]


class ConnectomeIR:
    """
    Plug-and-play Connectome Adapter mapping macroscopic IBM-1 neural mass matrices
    and microscopic Google H01 cortical slice matrices into normalized continuous
    associative engram bases X in R^{d x M}.
    """

    def __init__(
        self,
        d: int = 64,
        M: int = 8,
        mode: ConnectomeMode = "HYBRID",
        f_theta_hz: float = 6.00,
        seed: int = 42,
    ) -> None:
        self.d = d
        self.M = min(M, len(CANONICAL_VANCE_ENGRAMS))
        self.mode: ConnectomeMode = mode
        self.f_theta_hz = f_theta_hz
        self.seed = seed
        self.rng = np.random.default_rng(seed)

        self.W_ibm1, self.tau_ibm1, self.coords_ibm1, self.labels_ibm1 = (
            self._build_ibm1_neural_mass_matrices(n_nodes=d)
        )
        self.W_h01, self.tau_h01, self.coords_h01, self.labels_h01 = (
            self._build_google_h01_cortical_matrices(n_nodes=d)
        )

        self.W, self.tau, self.node_coords, self.node_labels, self.subsystems = (
            self._fuse_connectome(mode=self.mode)
        )
        self.X = self.compute_engram_basis(self.W, self.tau)
        self.metadata: List[EngramMetadata] = CANONICAL_VANCE_ENGRAMS[: self.M]

    def _build_ibm1_neural_mass_matrices(
        self, n_nodes: int
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray, List[str]]:
        """
        Generates a realistic macroscopic IBM-1 directed connectome matrix (W)
        with small-world modular structure and axonal tract latencies (tau in ms).
        """
        rng = np.random.default_rng(self.seed + 101)
        phi = np.linspace(0, 2 * np.pi, n_nodes, endpoint=False)
        z_norm = np.linspace(-0.85, 0.85, n_nodes)
        radius_xy = np.sqrt(np.clip(1.0 - z_norm**2, 0.1, 1.0))
        x = 65.0 * radius_xy * np.cos(phi * 2.5)
        y = 85.0 * radius_xy * np.sin(phi * 2.5)
        z = 50.0 * z_norm
        coords = np.stack([x, y, z], axis=1)

        diff = coords[:, None, :] - coords[None, :, :]
        dist_mm = np.linalg.norm(diff, axis=-1)

        tau_ms = 1.2 + dist_mm / 6.5
        np.fill_diagonal(tau_ms, 0.0)

        n_modules = 8
        module_ids = np.arange(n_nodes) % n_modules
        same_module = (module_ids[:, None] == module_ids[None, :]).astype(np.float64)

        W = (0.65 * same_module + 0.25) * np.exp(-dist_mm / 45.0)
        asymmetry = rng.normal(0.0, 0.12, size=(n_nodes, n_nodes))
        W = np.clip(W + asymmetry, 0.0, None)
        np.fill_diagonal(W, 0.0)

        eigvals = np.linalg.eigvals(W)
        max_eig = np.max(np.abs(eigvals))
        if max_eig > 1e-8:
            W = W / max_eig

        regions = [
            "CA3-Pyramidal", "CA1-Stratum", "Entorhinal-L2", "Dentate-Gyrus",
            "PFC-DLPFC", "PFC-vmPFC", "Cingulate-ACC", "Retrosplenial",
            "Temporal-MTG", "Visual-V1", "Visual-V4", "Auditory-A1",
            "Insula-Ant", "Amygdala-BLA", "Thalamus-MD", "Parietal-IPL",
        ]
        labels = [f"IBM1_{regions[i % len(regions)]}_{i:02d}" for i in range(n_nodes)]
        return W, tau_ms, coords, labels

    def _build_google_h01_cortical_matrices(
        self, n_nodes: int
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray, List[str]]:
        """
        Generates a microscopic Google H01 human temporal cortex laminar matrix (L1-L6)
        capturing canonical microcircuit connectivity (L4 -> L2/3 -> L5 -> L6) and
        local dendritic conduction delays.
        """
        rng = np.random.default_rng(self.seed + 202)
        layers = ["L2_3_Pyr", "L4_Stellate", "L5_ThickTufted", "L6_Corticothalamic", "PV_Basket", "SST_Martinotti"]
        layer_idx = np.arange(n_nodes) % len(layers)

        theta = np.linspace(0, 4 * np.pi, n_nodes, endpoint=False)
        r = 18.0 + 6.0 * (layer_idx / len(layers))
        x = r * np.cos(theta)
        y = r * np.sin(theta)
        z = 35.0 - 12.0 * layer_idx + rng.normal(0.0, 1.5, size=n_nodes)
        coords = np.stack([x, y, z], axis=1)

        diff = coords[:, None, :] - coords[None, :, :]
        dist_um_scaled = np.linalg.norm(diff, axis=-1)

        tau_ms = 0.8 + 0.11 * dist_um_scaled
        np.fill_diagonal(tau_ms, 0.0)

        canonical_laminar = np.array([
            [0.55, 0.10, 0.75, 0.15, 0.60, 0.45],
            [0.85, 0.45, 0.30, 0.10, 0.55, 0.20],
            [0.25, 0.05, 0.65, 0.70, 0.50, 0.65],
            [0.10, 0.60, 0.20, 0.40, 0.45, 0.30],
            [0.70, 0.70, 0.70, 0.50, 0.35, 0.15],
            [0.65, 0.25, 0.80, 0.40, 0.20, 0.10],
        ])

        W = np.zeros((n_nodes, n_nodes), dtype=np.float64)
        for i in range(n_nodes):
            for j in range(n_nodes):
                if i != j:
                    base_w = canonical_laminar[layer_idx[j], layer_idx[i]]
                    spatial_decay = np.exp(-dist_um_scaled[i, j] / 32.0)
                    synapse_multiplicity = 1.0 + 0.25 * np.sin(0.7 * i + 1.3 * j)
                    W[i, j] = base_w * spatial_decay * synapse_multiplicity

        eigvals = np.linalg.eigvals(W)
        max_eig = np.max(np.abs(eigvals))
        if max_eig > 1e-8:
            W = W / max_eig

        labels = [
            f"H01_seg{H01_C3_SEGMENT_IDS[i % len(H01_C3_SEGMENT_IDS)]}_{layers[layer_idx[i]]}"
            for i in range(n_nodes)
        ]
        return W, tau_ms, coords, labels

    def _fuse_connectome(
        self, mode: ConnectomeMode
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray, List[str], List[str]]:
        """Selects or fuses IBM-1 and Google H01 connectome tensors."""
        if mode == "IBM-1":
            subsystems = ["IBM-1_Macro" for _ in range(self.d)]
            return self.W_ibm1, self.tau_ibm1, self.coords_ibm1, self.labels_ibm1, subsystems
        elif mode == "H01":
            subsystems = ["H01_Cortical" for _ in range(self.d)]
            return self.W_h01, self.tau_h01, self.coords_h01, self.labels_h01, subsystems
        else:
            W = 0.55 * self.W_ibm1 + 0.45 * self.W_h01
            tau = 0.50 * self.tau_ibm1 + 0.50 * self.tau_h01
            coords = 0.65 * self.coords_ibm1 + 0.35 * self.coords_h01
            labels = [
                f"{self.labels_ibm1[i]}::{self.labels_h01[i].split('_')[1]}"
                for i in range(self.d)
            ]
            subsystems = [
                "IBM-1_Macro" if i % 2 == 0 else "H01_MicroSlice"
                for i in range(self.d)
            ]
            return W, tau, coords, labels, subsystems

    def compute_engram_basis(
        self,
        W: np.ndarray,
        tau_ms: np.ndarray,
        M: Optional[int] = None,
    ) -> np.ndarray:
        """
        Maps directed coupling weights W in R^{d x d} and conduction latencies
        tau_ms in R^{d x d} into a normalized continuous associative engram basis
        matrix X in R^{d x M}.
        """
        num_patterns = M if M is not None else self.M
        omega_theta_rad_ms = 2.0 * np.pi * (self.f_theta_hz / 1000.0)
        tau_char_ms = 18.0

        delay_kernel = W * np.exp(-tau_ms / tau_char_ms) * np.cos(omega_theta_rad_ms * tau_ms)

        sym_part = 0.5 * (delay_kernel + delay_kernel.T)
        skew_part = 0.5 * (delay_kernel - delay_kernel.T)
        associative_operator = sym_part + 0.35 * (skew_part @ skew_part.T)

        u_vecs, s_vals, _ = np.linalg.svd(associative_operator)

        raw_basis = np.zeros((self.d, num_patterns), dtype=np.float64)
        node_idx = np.arange(self.d, dtype=np.float64)
        for mu in range(num_patterns):
            spectral_mode = u_vecs[:, mu]
            harmonic_carrier = np.cos(2.0 * np.pi * (mu + 1) * node_idx / self.d + 0.4 * mu)
            raw_basis[:, mu] = 0.75 * spectral_mode + 0.25 * harmonic_carrier / np.sqrt(self.d)

        q_ortho, r_mat = np.linalg.qr(raw_basis)
        signs = np.sign(np.diag(r_mat))
        signs[signs == 0] = 1.0
        X = q_ortho * signs[None, :]

        norms = np.linalg.norm(X, axis=0, keepdims=True)
        X = X / np.clip(norms, 1e-12, None)
        return X

    def generate_spurious_attractors(self, n_spurious: int = 6) -> np.ndarray:
        """
        Generates shallow spurious cross-talk states (frustrated mixtures of subsets of
        canonical engrams plus orthogonal jitter) to test the 5% Sleep Pruning Rule.
        """
        rng = np.random.default_rng(self.seed + 999)
        spurious_basis = np.zeros((self.d, n_spurious), dtype=np.float64)
        for k in range(n_spurious):
            i1 = k % self.M
            i2 = (k + 1) % self.M
            i3 = (k + 2) % self.M
            mix = 0.45 * self.X[:, i1] - 0.38 * self.X[:, i2] + 0.25 * self.X[:, i3]
            ortho_noise = rng.normal(0.0, 0.30, size=self.d)
            ortho_noise -= np.dot(ortho_noise, self.X[:, 0]) * self.X[:, 0]
            vec = mix + ortho_noise
            spurious_basis[:, k] = vec / np.linalg.norm(vec)
        return spurious_basis

    def sample_noisy_probe(
        self,
        target_index: int = 0,
        poisson_noise_fraction: float = 0.35,
        rng: Optional[np.random.Generator] = None,
    ) -> np.ndarray:
        """
        Generates an input probe vector corrupted by 35% Poisson shot noise,
        modeling stochastic spike-count fluctuations in cortical readout.
        """
        gen = rng if rng is not None else self.rng
        target_vec = self.X[:, target_index].copy()

        rate_scale = 40.0
        baseline_rate = np.clip((target_vec + 0.35) * rate_scale, 1.0, None)
        poisson_counts = gen.poisson(lam=baseline_rate).astype(np.float64)
        poisson_fluctuation = (poisson_counts - baseline_rate) / rate_scale
        poisson_fluctuation /= max(np.linalg.norm(poisson_fluctuation), 1e-12)

        noisy_probe = (1.0 - poisson_noise_fraction) * target_vec + (
            poisson_noise_fraction * poisson_fluctuation
        )
        return noisy_probe / np.linalg.norm(noisy_probe)

    def export_graph_3d(self) -> ConnectomeGraph3D:
        """Exports the complete 3D anatomical and associative graph for UI rendering."""
        return ConnectomeGraph3D(
            node_coords=self.node_coords.copy(),
            node_labels=list(self.node_labels),
            node_Subsystems=list(self.subsystems),
            coupling_matrix=self.W.copy(),
            latency_matrix_ms=self.tau.copy(),
            engram_basis=self.X.copy(),
            engram_metadata=list(self.metadata),
        )
