# =============================================================================
# data_model.py  –  PatientData container + InputHandler
#
# PatientData  : lightweight dataclass-like container; serialises to/from dict
# InputHandler : manages the "working copy" of one patient's data and only
#                commits it on explicit save (Next / Done clicks).
# =============================================================================

from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Any
from datetime import datetime


# ── PatientData ───────────────────────────────────────────────────────────────

@dataclass
class PatientData:
    # demographics
    mrn:            str = ""
    first_name:     str = ""
    last_name:      str = ""
    age:            str = ""
    sex:            str = ""
    triage:         str = ""

    # vital signs
    hr:             str = ""
    bp:             str = ""
    rr:             str = ""
    spo2:           str = ""
    temp:           str = ""
    vitals_time:    str = ""

    # labs/ imaging
    ddimer:         str = ""
    troponin:       str = ""
    bnp:            str = ""
    creatinine:     str = ""
    imaging:        str = ""

    # Symptoms & risk factors (values: "Yes" | "No" | "Unknown")
    dyspnea:        str = "Unknown"
    pleuritic_pain: str = "Unknown"
    hemoptysis:     str = "Unknown"
    leg_swelling:   str = "Unknown"
    recent_surgery: str = "Unknown"
    prior_dvt_pe:   str = "Unknown"
    hormone_therapy:str = "Unknown"
    malignancy:     str = "Unknown"

    # Wells criteria (values: "Yes" | "No" | "Unknown")
    dvt_signs:      str = "Unknown"
    pe_likely:      str = "Unknown"
    hr_over_100:    str = "Unknown"
    immobilization: str = "Unknown"
    prev_dvt_pe:    str = "Unknown"
    hemoptysis_w:   str = "Unknown"
    malignancy_w:   str = "Unknown"

    # Computed results
    wells_score:    float = 0.0
    wells_risk:     str   = ""

    # Decision
    recommendation_title:    str = ""
    recommendation_strength: str = ""
    physician_decision:      str = ""
    override_reason:         str = ""
    physician_comments:      str = ""

    # Metadata
    assessment_timestamp: str = ""
    last_updated:         str = ""

    # Helpers

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}".strip()

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "PatientData":
        valid_fields = cls.__dataclass_fields__.keys()
        filtered = {k: v for k, v in d.items() if k in valid_fields}
        return cls(**filtered)

    def missing_critical_fields(self) -> list[str]:
        """Return human-readable names of important empty / Unknown fields."""
        missing: list[str] = []
        if not self.ddimer:
            missing.append("D-dimer not available")
        if not self.troponin:
            missing.append("Troponin not available")
        if self.recent_surgery == "Unknown":
            missing.append("Recent surgery/immobilization not documented")
        if not self.spo2:
            missing.append("O₂ saturation required")
        return missing


# InputHandler

class InputHandler:
    """
    Manages one patient's working-copy data.

    • ``stage_update(field, value)``  – buffer a change (not yet saved)
    • ``commit()``                    – flush staged changes into the live record
    • ``discard()``                   – throw away staged changes
    • ``load(patient_data)``          – start working on an existing record
    • ``current``                     – the committed PatientData
    """

    def __init__(self) -> None:
        self._committed: PatientData = PatientData()
        self._staged:    dict[str, Any] = {}

    # Public API

    @property
    def current(self) -> PatientData:
        return self._committed

    def load(self, patient_data: PatientData) -> None:
        """Replace the committed record with an existing PatientData."""
        self._committed = PatientData.from_dict(patient_data.to_dict())
        self._staged.clear()

    def stage_update(self, field: str, value: Any) -> None:
        """Buffer a field update without persisting it yet."""
        self._staged[field] = value

    def commit(self) -> PatientData:
        """
        Merge staged changes into the committed record.
        Also stamps last_updated.
        Returns the updated record.
        """
        if self._staged:
            data_dict = self._committed.to_dict()
            data_dict.update(self._staged)
            data_dict["last_updated"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self._committed = PatientData.from_dict(data_dict)
            self._staged.clear()
        return self._committed

    def discard(self) -> None:
        """Throw away all staged (uncommitted) changes."""
        self._staged.clear()

    def get_staged(self, field: str, fallback: Any = None) -> Any:
        """Read a staged (not yet committed) value, or fall back to committed."""
        if field in self._staged:
            return self._staged[field]
        return getattr(self._committed, field, fallback)

    def has_staged_changes(self) -> bool:
        return bool(self._staged)

    def compute_wells_score(self) -> tuple[float, str]:
        """
        Calculate Wells score from committed criteria.
        Returns (score, risk_level_string).
        """
        from config.config import WELLS_CRITERIA, RISK_THRESHOLDS

        score = 0.0
        for key, _label, points in WELLS_CRITERIA:
            val = getattr(self._committed, key, "Unknown")
            if val == "Yes":
                score += points

        if score <= 4.0:
            risk = "LOW RISK"
        elif score <= 6.0:
            risk = "MODERATE RISK"
        else:
            risk = "HIGH RISK"

        return round(score, 1), risk

    def data_completeness(self) -> tuple[int, int]:
        """
        Count how many of the key assessment fields are filled.
        Returns (filled, total).
        """
        from config.config import WELLS_CRITERIA, SYMPTOM_FIELDS, VITAL_FIELDS

        all_keys: list[str] = []
        # vitals
        all_keys += [f for f, *_ in VITAL_FIELDS]
        # symptoms
        all_keys += [f for f, *_ in SYMPTOM_FIELDS]
        # wells criteria
        all_keys += [k for k, *_ in WELLS_CRITERIA]

        filled = 0
        for key in all_keys:
            val = getattr(self._committed, key, "")
            if val and val != "Unknown":
                filled += 1

        return filled, len(all_keys)

    def build_pe_pattern_hints(self) -> list[str]:
        """Return a list of active PE pattern hints based on committed data."""
        hints: list[str] = []
        d = self._committed

        try:
            hr = float(d.hr)
            rr = float(d.rr)
            if hr > 100 and rr > 20:
                hints.append("Tachycardia + Tachypnea")
        except (ValueError, TypeError):
            pass

        try:
            if float(d.spo2) < 95:
                hints.append("Hypoxemia (SpO₂ < 95%)")
        except (ValueError, TypeError):
            pass

        if d.pleuritic_pain == "Yes":
            hints.append("Pleuritic chest pain present")
        if d.hemoptysis == "Yes":
            hints.append("Hemoptysis reported")
        if d.leg_swelling == "Yes":
            hints.append("Unilateral leg swelling")

        return hints
