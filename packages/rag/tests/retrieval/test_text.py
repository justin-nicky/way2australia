"""safe_text and its use in both CLIs (Spec 005 T6, T5 review F1)."""

import re

import pytest
from way2australia_rag.retrieval import cli
from way2australia_rag.retrieval.index import DenseIndex
from way2australia_rag.retrieval.models import RetrievalResult
from way2australia_rag.retrieval.retriever import DenseRetriever
from way2australia_rag.retrieval.text import safe_text

from .test_retriever import (
    BASE,
    EMBEDDER,
    VERSION,
    build_client,
    guest,
    make_point,
)

HOSTILE = "Real\nFAKE 9  forged  line \x1b[31mred\x1b[0m \x1b]0;pwn\x07end\x00\x7f"
CONTROL = re.compile(r"[\x00-\x1f\x7f]")


def test_safe_text_strips_controls_and_ansi() -> None:
    out = safe_text(HOSTILE)
    assert not CONTROL.search(out) and "\x1b" not in out
    assert out == "Real FAKE 9 forged line red end"


def test_safe_text_keeps_malayalam_joiners() -> None:
    text = "ക്‍ഷ മലയാളം"
    assert safe_text(text) == text


@pytest.mark.filterwarnings("ignore:Payload indexes have no effect:UserWarning")
def test_retrieve_cli_hit_line_is_single_clean_line() -> None:
    point = make_point("doc_1", "hello", title=HOSTILE)
    client = build_client([point])
    index = DenseIndex.open(client, BASE, VERSION, EMBEDDER.info)
    result: RetrievalResult = DenseRetriever(index, EMBEDDER).retrieve(
        "hello", guest(), 1
    )
    assert result.hits[0].title == HOSTILE  # the payload itself is untouched
    out = cli.format_result(result)
    lines = out.splitlines()
    assert len(lines) == 3  # header, hits count, exactly one hit line
    assert not CONTROL.search(out.replace("\n", ""))
    assert "\x1b" not in out
    assert lines[2].endswith("Real FAKE 9 forged line red end")
