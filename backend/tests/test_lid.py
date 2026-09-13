import pytest

from backend.app.lid import IndicLID, IndicLIDUnavailableError


def test_empty_text_is_rejected():
    with pytest.raises(ValueError):
        IndicLID().predict("")


def test_unconfigured_runtime_is_explicit():
    with pytest.raises(IndicLIDUnavailableError):
        IndicLID().predict("നമസ്കാരം")
