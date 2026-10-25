"""
semantic_tokenizer.py
=====================
Engram-0: Cross-Modal Semantic Tokenizer.

Projects settled continuous analog attractor states q* in R^d into structured
discrete semantic control tokens for strict cognitive gating of the SPI persona:
    <LOC:...>, <ERA:...>, <VALENCE:...>, <THETA_LOCK:...>, <CONF:...>
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List
import numpy as np

from connectome_ir import CANONICAL_VANCE_ENGRAMS, EngramMetadata
from reversible_thermo_engram import THETA_MAX_HZ, THETA_MIN_HZ, TrajectoryResult


@dataclass
class SemanticTokenPacket:
    """Structured cross-modal semantic token representation of a settled attractor."""
    engram_id: str
    engram_index: int
    loc_token: str
    era_token: str
    valence_token: str
    theta_lock_token: str
    conf_token: str
    raw_token_stream: str
    sensory_anchor: str
    confidence_score: float
    cosine_similarity: float
    measured_theta_hz: float
    delta_energy_kbt: float
    settled_energy_kbt: float

    def to_dict(self) -> Dict[str, object]:
        return {
            "engram_id": self.engram_id,
            "engram_index": self.engram_index,
            "loc_token": self.loc_token,
            "era_token": self.era_token,
            "valence_token": self.valence_token,
            "theta_lock_token": self.theta_lock_token,
            "conf_token": self.conf_token,
            "raw_token_stream": self.raw_token_stream,
            "sensory_anchor": self.sensory_anchor,
            "confidence_score": self.confidence_score,
            "cosine_similarity": self.cosine_similarity,
            "measured_theta_hz": self.measured_theta_hz,
            "delta_energy_kbt": self.delta_energy_kbt,
            "settled_energy_kbt": self.settled_energy_kbt,
        }


class SemanticTokenizer:
    """
    Cross-modal projection operator mapping settled continuous Hopfield attractor
    states q* in R^d into discrete semantic tokens:
    <LOC:...>, <ERA:...>, <VALENCE:...>, <THETA_LOCK:...>, <CONF:...>.
    """

    def __init__(
        self,
        X: np.ndarray,
        metadata: List[EngramMetadata] | None = None,
    ) -> None:
        self.X = np.asarray(X, dtype=np.float64)
        self.d, self.M = self.X.shape
        self.metadata = metadata if metadata is not None else CANONICAL_VANCE_ENGRAMS[: self.M]
        self.W_proj = self.X.T.copy()

    def tokenize(self, traj: TrajectoryResult) -> SemanticTokenPacket:
        q_star = traj.settled_state / max(np.linalg.norm(traj.settled_state), 1e-12)
        projections = self.W_proj @ q_star
        best_idx = int(np.argmax(projections))
        cos_sim = float(np.clip(projections[best_idx], -1.0, 1.0))

        attn_peak = float(traj.softmax_attention[best_idx])
        confidence = float(np.clip(0.55 * cos_sim + 0.45 * attn_peak, 0.0, 1.0))

        meta = self.metadata[best_idx]

        in_window = THETA_MIN_HZ <= traj.measured_theta_hz <= THETA_MAX_HZ
        lock_status = "LOCKED" if in_window else "DRIFT"

        loc_tok = f"<LOC:{meta.location_token}>"
        era_tok = f"<ERA:{meta.era_token}>"
        val_tok = f"<VALENCE:{meta.valence_token}>"
        theta_tok = f"<THETA_LOCK:{lock_status}_{traj.measured_theta_hz:.2f}HZ>"
        conf_tok = f"<CONF:{confidence:.4f}>"

        stream = f"{loc_tok} {era_tok} {val_tok} {theta_tok} {conf_tok}"

        return SemanticTokenPacket(
            engram_id=meta.engram_id,
            engram_index=best_idx,
            loc_token=loc_tok,
            era_token=era_tok,
            valence_token=val_tok,
            theta_lock_token=theta_tok,
            conf_token=conf_tok,
            raw_token_stream=stream,
            sensory_anchor=meta.sensory_summary,
            confidence_score=confidence,
            cosine_similarity=cos_sim,
            measured_theta_hz=traj.measured_theta_hz,
            delta_energy_kbt=traj.delta_energy_kbt,
            settled_energy_kbt=traj.settled_energy_kbt,
        )
