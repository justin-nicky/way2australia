"""Opening the retrieval stack (Spec 008). T2 holds the standalone lexical open;
`open_retrieval` joins it in T3."""

from pathlib import Path

from way2australia_rag.ingestion.chunking import Chunker
from way2australia_rag.ingestion.config import RuntimeSettings
from way2australia_rag.lexical.build import default_lexical_dir, lexical_index_path
from way2australia_rag.lexical.freshness import verify_fresh
from way2australia_rag.lexical.store import LexicalIndex
from way2australia_rag.repositories import DocumentRepository
from way2australia_rag.repositories.hashing import HASH_CONTRACT
from way2australia_rag.retrieval.identity import IndexIdentity


def open_standalone_lexical(
    settings: RuntimeSettings,
    repo_root: Path,
    expected: IndexIdentity,
    chunker: Chunker,
    repository: DocumentRepository,
) -> LexicalIndex:
    """Open the lexical file with no Qdrant client and no embedder: file identity,
    configured dense identity and chunker, then freshness against the repository.
    Any refusal closes the file and raises `LexicalIndexBindingError`."""
    directory = settings.lexical_index_dir or default_lexical_dir(repo_root)
    if not directory.is_absolute():
        directory = repo_root / directory
    lexical = LexicalIndex.open(
        lexical_index_path(directory, expected.collection),
        expected.collection,
        expected.index_version,
    )
    try:
        lexical.check_identity(expected, chunker, HASH_CONTRACT)
        verify_fresh(lexical, repository, chunker)
    except BaseException:
        lexical.close()
        raise
    return lexical
