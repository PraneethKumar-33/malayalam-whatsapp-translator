import pytest

from backend.app.transliterator import IndicXlit
from phase7.preprocessing import normalize_roman_malayalam


pytestmark = pytest.mark.indicxlit_runtime


def has_malayalam_script(text: str) -> bool:
    return any("\u0D00" <= char <= "\u0D7F" for char in text)


def test_real_indicxlit_runtime_initializes(real_indicxlit_engine):
    assert real_indicxlit_engine is not None
    assert callable(real_indicxlit_engine.translit_sentence)


def test_real_runtime_transliterates_roman_malayalam(real_indicxlit_engine):
    output = real_indicxlit_engine.translit_sentence(
        "vegam vaa",
        lang_code="ml",
    )

    assert isinstance(output, str)
    assert output.strip()
    assert has_malayalam_script(output)


@pytest.mark.parametrize(
    "text",
    [
        "ninakku innu sukhamano?",
        "njan innu college-il pokunnu",
        "evideya?",
        "shari chetta",
        "vegam vaa",
        "nale class undo?",
    ],
)
def test_real_runtime_handles_whatsapp_style_inputs(
    real_indicxlit_engine,
    text,
):
    output = real_indicxlit_engine.translit_sentence(
        text,
        lang_code="ml",
    )

    assert isinstance(output, str)
    assert output.strip()
    assert has_malayalam_script(output)


def test_roman_normalization_flows_into_real_indicxlit(
    real_indicxlit_engine,
):
    normalized = normalize_roman_malayalam("njan nale varam")

    assert normalized == "njan naale varam"

    output = real_indicxlit_engine.translit_sentence(
        normalized,
        lang_code="ml",
    )

    assert isinstance(output, str)
    assert output.strip()
    assert has_malayalam_script(output)


def test_backend_adapter_uses_real_indicxlit_engine(
    real_indicxlit_engine,
):
    transliterator = IndicXlit(engine=real_indicxlit_engine)

    output = transliterator.transliterate("vegam vaa")

    assert isinstance(output, str)
    assert output.strip()
    assert has_malayalam_script(output)


def test_reused_engine_handles_multiple_inputs(real_indicxlit_engine):
    inputs = [
        "vegam vaa",
        "evideya?",
        "nale class undo?",
    ]

    outputs = [
        real_indicxlit_engine.translit_sentence(text, lang_code="ml")
        for text in inputs
    ]

    assert len(outputs) == 3
    assert all(isinstance(output, str) for output in outputs)
    assert all(output.strip() for output in outputs)
    assert all(has_malayalam_script(output) for output in outputs)


def test_same_input_is_stable_with_reused_engine(real_indicxlit_engine):
    output1 = real_indicxlit_engine.translit_sentence(
        "vegam vaa",
        lang_code="ml",
    )
    output2 = real_indicxlit_engine.translit_sentence(
        "vegam vaa",
        lang_code="ml",
    )

    assert output1 == output2
