from backend.app.router import (
    contains_malayalam_script,
    roman_malayalam_fallback,
    route_language,
)


def test_indic_lid_native_malayalam():
    assert route_language("നിനക്ക് ഇന്ന് സുഖമാണോ?", "mal_Mlym") == "malayalam_native"


def test_indic_lid_roman_malayalam():
    assert route_language("ninakku innu sukhamano?", "mal_Latn") == "roman_malayalam"


def test_english_without_indic_lid():
    assert route_language("Hello, how are you?", None) == "english"


def test_english_not_triggered_by_common_english_words():
    assert route_language("Can you send me the file?", None) == "english"


def test_unrecognized_short_roman_phrase_is_not_forced_to_malayalam():
    assert roman_malayalam_fallback("vegam vaa") is False
    assert route_language("vegam vaa", None) == "english"


def test_roman_fallback_long_message():
    assert roman_malayalam_fallback(
        "njan innu college-il pokunnu"
    ) is True


def test_non_malayalam_english_message_rejected_by_fallback():
    assert roman_malayalam_fallback("hello brother") is False


def test_native_malayalam_script_detection():
    assert contains_malayalam_script("നാളെ വരാം") is True
    assert contains_malayalam_script("Hello tomorrow") is False


def test_mixed_malayalam_english():
    assert route_language(
        "ഇന്ന് meeting ഉണ്ടോ?",
        "mal_Mlym",
    ) == "malayalam_native"


def test_unknown_lid_with_malayalam_script():
    assert route_language(
        "നാളെ class online ആണോ?",
        "eng_Latn",
    ) == "mixed"


def test_unknown_lid_with_roman_malayalam():
    assert route_language(
        "evideya nee ippo?",
        "kan_Latn",
    ) == "roman_malayalam"
