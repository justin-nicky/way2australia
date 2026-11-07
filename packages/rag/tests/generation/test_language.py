"""Message language from script mix (Spec 012 R3, D-D)."""

from way2australia_rag.generation.language import message_language

_DEFAULT_MAP = {"malayalam": "ml"}


def test_latin_query_uses_en() -> None:
    assert message_language("What is the CCL fee?", _DEFAULT_MAP) == "en"


def test_malayalam_query_uses_ml() -> None:
    assert message_language("ഫീ എത്രയാണ്?", _DEFAULT_MAP) == "ml"


def test_mixed_query_uses_non_english() -> None:
    assert message_language("What is mock-ൽ fee?", _DEFAULT_MAP) == "ml"


def test_digits_only_uses_en() -> None:
    assert message_language("12345", _DEFAULT_MAP) == "en"


def test_extra_mapping_in_config_without_code_change() -> None:
    extended = {**_DEFAULT_MAP, "greek": "el"}
    assert message_language("Γειά", extended) == "el"
