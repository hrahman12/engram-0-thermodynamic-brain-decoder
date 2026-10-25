"""personal_intake.py
==================
Engram-0: Interactive Autobiographical Memory & Personality Ingestion Engine.
"""
from dataclasses import asdict, dataclass, field
import json
from pathlib import Path
import sys
from typing import Any, Dict, List, Optional

DEFAULT_PROFILE_PATH = Path(__file__).resolve().parent / "user_engram_profile.json"

@dataclass
class UserMemoryTrace:
    slot_index: int
    engram_id: str
    era: str
    location: str
    sensory_trace: str
    valence: float
    valence_label: str = "RESOLUTE_NOSTALGIA"

    def __post_init__(self) -> None:
        self.valence = float(max(-1.0, min(1.0, self.valence)))
        if not self.valence_label:
            self.valence_label = f"VALENCE_{self.valence:+.2f}"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class PersonalityAxioms:
    speech_style: str
    philosophical_axioms: str
    emotional_baseline: str
    cognitive_tempo_hz: float = 6.00

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class UserMindProfile:
    user_id: str
    callsign: str
    substrate_target: str
    model_target: str
    thinking_level: str
    personality: PersonalityAxioms
    memories: List[UserMemoryTrace] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "user_id": self.user_id,
            "callsign": self.callsign,
            "substrate_target": self.substrate_target,
            "model_target": self.model_target,
            "thinking_level": self.thinking_level,
            "personality": self.personality.to_dict(),
            "memories": [m.to_dict() for m in self.memories],
        }

    def save(self, path: Path | str = DEFAULT_PROFILE_PATH) -> Path:
        out_path = Path(path)
        try:
            out_path.write_text(json.dumps(self.to_dict(), indent=2), encoding="utf-8")
            return out_path
        except (OSError, PermissionError):
            tmp_path = Path("/tmp") / out_path.name
            try:
                tmp_path.write_text(json.dumps(self.to_dict(), indent=2), encoding="utf-8")
                return tmp_path
            except Exception:
                return out_path

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "UserMindProfile":
        pers_raw = data.get("personality", {})
        personality = PersonalityAxioms(
            speech_style=str(pers_raw.get("speech_style", "First-person introspective neuro-physicist")),
            philosophical_axioms=str(pers_raw.get("philosophical_axioms", "Memory is an eigenstate of the biological connectome; unitary quantum tunneling and symplectic volume preservation prevent Landauer bit erasure.")),
            emotional_baseline=str(pers_raw.get("emotional_baseline", "Stoic lucidity (310.15 K equilibrium)")),
            cognitive_tempo_hz=float(pers_raw.get("cognitive_tempo_hz", 6.00)),
        )
        memories = [
            UserMemoryTrace(
                slot_index=int(m.get("slot_index", idx)),
                engram_id=str(m.get("engram_id", f"ENGRAM_0{idx}")),
                era=str(m.get("era", "2026")),
                location=str(m.get("location", "Acute Excision Bay 4")),
                sensory_trace=str(m.get("sensory_trace", "Isoflurane vapor, heart monitor flatline")),
                valence=float(m.get("valence", 0.8)),
                valence_label=str(m.get("valence_label", "")),
            )
            for idx, m in enumerate(data.get("memories", []))
        ]
        return cls(
            user_id=str(data.get("user_id", "USER_VANCE_00")),
            callsign=str(data.get("callsign", "ALISTAIR_VANCE_SPI")),
            substrate_target=str(data.get("substrate_target", "GOOGLE_H01_CORTEX_L4")),
            model_target=str(data.get("model_target", "gemini-4-argon")),
            thinking_level=str(data.get("thinking_level", "high")),
            personality=personality,
            memories=memories,
        )

def build_default_user_profile() -> UserMindProfile:
    personality = PersonalityAxioms(
        speech_style="First-person introspective neuro-physicist",
        philosophical_axioms="Memory is an eigenstate of the biological connectome; unitary quantum tunneling and symplectic volume preservation prevent Landauer bit erasure.",
        emotional_baseline="Resolute lucidity anchored by deep episodic nostalgia (310.15 K equilibrium)",
        cognitive_tempo_hz=6.00,
    )
    memories = [
        UserMemoryTrace(slot_index=0, engram_id="ENGRAM_00_KOWLOON_ROOFTOP", era="1994", location="Kowloon Rooftop", sensory_trace="Rain on corrugated iron, ozone from neon transformers, distant Kai Tak landing lights cutting through monsoon mist, wet soldering iron hum.", valence=0.82, valence_label="NOSTALGIC_WONDER_+0.82"),
        UserMemoryTrace(slot_index=1, engram_id="ENGRAM_01_EXCISION_BAY_4", era="2026", location="Acute Excision Bay 4", sensory_trace="Isoflurane vapor, heart monitor flatline, ozone smell of superconducting Helmholtz coils, amber status LEDs on frosted quartz, 6.00 Hz theta lock hum.", valence=-0.64, valence_label="RESOLUTE_TRANSCENDENCE_-0.64"),
        UserMemoryTrace(slot_index=2, engram_id="ENGRAM_02_H01_CLEANROOM_B", era="2024", location="Geneva Neurophotonics Lab Cleanroom B", sensory_trace="Blue Cherenkov-like fluorescence on the petavoxel electron microscopy monitor, Layer-4 stellate and Layer-5 pyramidal dendritic spines aligning in 3D.", valence=0.94, valence_label="EUPHORIC_DISCOVERY_+0.94"),
        UserMemoryTrace(slot_index=3, engram_id="ENGRAM_03_QUAI_MONT_BLANC", era="2025", location="Quai du Mont-Blanc Promenade", sensory_trace="Raindrops fracturing sodium streetlamp reflections on wet cobblestones, distant ferry horn across Lake Geneva, porcelain espresso cup warming chilled fingers.", valence=0.76, valence_label="MELANCHOLIC_WARMTH_+0.76"),
    ]
    return UserMindProfile(user_id="USER_VANCE_00", callsign="ALISTAIR_VANCE_SPI", substrate_target="GOOGLE_H01_CORTEX_L4", model_target="gemini-4-argon", thinking_level="high", personality=personality, memories=memories)

def run_interactive_intake(output_path=DEFAULT_PROFILE_PATH, force_defaults=True):
    prof = build_default_user_profile()
    prof.save(output_path)
    return prof
