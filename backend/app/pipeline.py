"""
Phase 9 — Translation pipeline orchestration.

Connects the existing language router with Phase 7 preprocessing,
IndicXlit transliteration, and IndicTrans2 translation adapters.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from backend.app.router import route_language
from phase7.preprocessing import (
    normalize_malayalam,
    normalize_roman_malayalam,
)


class MixedTextUnsupportedError(RuntimeError):
    """Raised until mixed Malayalam-English processing is implemented."""


@dataclass(frozen=True)
class PipelineResult:
    route: str
    translation: str


class TranslationPipeline:
    def __init__(
        self,
        transliterator_factory: Callable[[], Any],
        translator_factory: Callable[[], Any],
    ) -> None:
        self._transliterator_factory = transliterator_factory
        self._translator_factory = translator_factory

        self._transliterator: Any | None = None
        self._translator: Any | None = None

    def _get_transliterator(self) -> Any:
        if self._transliterator is None:
            self._transliterator = self._transliterator_factory()

        return self._transliterator

    def _get_translator(self) -> Any:
        if self._translator is None:
            self._translator = self._translator_factory()

        return self._translator

    def process(
        self,
        text: str,
        indiclid_code: str | None = None,
    ) -> PipelineResult:
        if not text or not text.strip():
            raise ValueError("Text cannot be empty.")

        cleaned_text = text.strip()
        route = route_language(cleaned_text, indiclid_code)

        if route == "english":
            return PipelineResult(
                route=route,
                translation=cleaned_text,
            )

        if route == "malayalam_native":
            return PipelineResult(
                route=route,
                translation=self._get_translator().translate(
                    cleaned_text
                ),
            )

        if route == "roman_malayalam":
            normalized_roman = normalize_roman_malayalam(
                cleaned_text
            )

            malayalam_text = self._get_transliterator().transliterate(
                normalized_roman
            )

            normalized_malayalam = normalize_malayalam(
                malayalam_text
            )

            return PipelineResult(
                route=route,
                translation=self._get_translator().translate(
                    normalized_malayalam
                ),
            )

        if route == "mixed":
            raise MixedTextUnsupportedError(
                "Mixed Malayalam-English processing is not implemented yet."
            )

        raise RuntimeError(f"Unsupported route: {route}")
