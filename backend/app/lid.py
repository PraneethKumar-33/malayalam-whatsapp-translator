"""
Phase 8 — IndicLID adapter boundary.

The original Phase 5 IndicLID runtime/model artifacts were not committed
to this repository. This module intentionally defines the backend contract
without pretending that a local IndicLID model is currently installed.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class LIDResult:
    code: str
    confidence: float | None = None


class IndicLIDUnavailableError(RuntimeError):
    """Raised when IndicLID inference is requested but not configured."""


class IndicLID:
    """
    Backend-facing IndicLID adapter.

    The production implementation will wrap the validated Phase 5 inference
    API (`batch_predict([text], 1)`) once the model/runtime is provisioned.
    """

    def __init__(self) -> None:
        self._loaded = False

    def predict(self, text: str) -> LIDResult:
        if not text or not text.strip():
            raise ValueError("Text cannot be empty.")

        raise IndicLIDUnavailableError(
            "IndicLID model/runtime is not configured in this environment."
        )
