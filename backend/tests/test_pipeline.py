import pytest

from backend.app.pipeline import (
    MixedTextUnsupportedError,
    TranslationPipeline,
)


class FakeTransliterator:
    def __init__(self):
        self.received = None

    def transliterate(self, text):
        self.received = text
        return "ഇന്ന് വിളിക്കാം"


class FakeTranslator:
    def __init__(self):
        self.received = None

    def translate(self, text):
        self.received = text
        return f"EN:{text}"


def make_transliterator():
    return FakeTransliterator()


def make_translator():
    return FakeTranslator()


def test_english_is_returned_unchanged():
    pipeline = TranslationPipeline(
        transliterator_factory=make_transliterator,
        translator_factory=make_translator,
    )

    result = pipeline.process(
        "Can you send me the file?",
        indiclid_code="eng_Latn",
    )

    assert result.route == "english"
    assert result.translation == "Can you send me the file?"


def test_native_malayalam_goes_directly_to_translation():
    translator = FakeTranslator()

    pipeline = TranslationPipeline(
        transliterator_factory=make_transliterator,
        translator_factory=lambda: translator,
    )

    result = pipeline.process(
        "നാളെ വരാം",
        indiclid_code="mal_Mlym",
    )

    assert result.route == "malayalam_native"
    assert translator.received == "നാളെ വരാം"
    assert result.translation == "EN:നാളെ വരാം"


def test_roman_malayalam_uses_normalization_transliteration_and_translation():
    transliterator = FakeTransliterator()
    translator = FakeTranslator()

    pipeline = TranslationPipeline(
        transliterator_factory=lambda: transliterator,
        translator_factory=lambda: translator,
    )

    result = pipeline.process(
        "njan nale varam",
        indiclid_code="mal_Latn",
    )

    assert result.route == "roman_malayalam"
    assert transliterator.received == "njan naale varam"
    assert translator.received == "ഇന്ന് വിളിക്കാം"
    assert result.translation == "EN:ഇന്ന് വിളിക്കാം"


def test_mixed_text_is_explicitly_not_implemented_yet():
    pipeline = TranslationPipeline(
        transliterator_factory=make_transliterator,
        translator_factory=make_translator,
    )

    with pytest.raises(MixedTextUnsupportedError):
        pipeline.process("നാളെ class online ആണോ?")


def test_english_does_not_initialize_any_runtime():
    calls = []

    def transliterator_factory():
        calls.append("transliterator")
        return FakeTransliterator()

    def translator_factory():
        calls.append("translator")
        return FakeTranslator()

    pipeline = TranslationPipeline(
        transliterator_factory=transliterator_factory,
        translator_factory=translator_factory,
    )

    result = pipeline.process(
        "Hello",
        indiclid_code="eng_Latn",
    )

    assert result.route == "english"
    assert result.translation == "Hello"
    assert calls == []


def test_native_malayalam_initializes_only_translator():
    calls = []

    def transliterator_factory():
        calls.append("transliterator")
        return FakeTransliterator()

    def translator_factory():
        calls.append("translator")
        return FakeTranslator()

    pipeline = TranslationPipeline(
        transliterator_factory=transliterator_factory,
        translator_factory=translator_factory,
    )

    pipeline.process(
        "നാളെ വരാം",
        indiclid_code="mal_Mlym",
    )

    assert calls == ["translator"]


def test_roman_malayalam_initializes_both_runtimes():
    calls = []

    def transliterator_factory():
        calls.append("transliterator")
        return FakeTransliterator()

    def translator_factory():
        calls.append("translator")
        return FakeTranslator()

    pipeline = TranslationPipeline(
        transliterator_factory=transliterator_factory,
        translator_factory=translator_factory,
    )

    pipeline.process(
        "njan nale varam",
        indiclid_code="mal_Latn",
    )

    assert calls == [
        "transliterator",
        "translator",
    ]