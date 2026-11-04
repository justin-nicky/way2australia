"""Active product language codes from `config/language_registry.json` (Spec 010)."""

from pathlib import Path

from way2australia_rag.evaluation.suite import inside, read_json
from way2australia_rag.retrieval.errors import RetrievalConfigurationError

LANGUAGE_REGISTRY = "config/language_registry.json"


def _active_product_support_codes(raw: object) -> set[str]:
    support = raw.get("product_support") if isinstance(raw, dict) else None
    if not isinstance(support, dict):
        raise RetrievalConfigurationError(
            "'language_registry.json' has no product_support section."
        )
    codes: set[str] = set()
    for entry in support.values():
        if (
            isinstance(entry, dict)
            and entry.get("status") == "active"
            and isinstance(entry.get("internal_code"), str)
        ):
            codes.add(entry["internal_code"])
    return codes


def active_lote_codes(repo_root: Path) -> list[str]:
    """Active `product_support` codes, without `en`."""
    raw = read_json(inside(repo_root, LANGUAGE_REGISTRY))
    return sorted(_active_product_support_codes(raw))
