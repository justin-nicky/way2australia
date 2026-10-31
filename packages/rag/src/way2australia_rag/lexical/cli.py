"""Build the lexical index (Spec 007 R4). Run via ``make index-lexical``.

No Qdrant client and no embedder are created. Exit codes: 0 success; 2 refusal
or configuration error. Output carries labels and counts only: no absolute
paths, chunk text or secrets.
"""

import argparse
import asyncio
import subprocess
import sys
from collections.abc import Sequence
from pathlib import Path

from way2australia_rag.ingestion.cli import build_chunker
from way2australia_rag.ingestion.config import (
    DEFAULT_CONFIG_PATH,
    load_ingestion_config,
    load_runtime_settings,
)
from way2australia_rag.ingestion.errors import IngestionError
from way2australia_rag.ingestion.identity import embedder_identity
from way2australia_rag.ingestion.settings import collection_name
from way2australia_rag.lexical.build import (
    build_lexical_index,
    default_lexical_dir,
    lexical_index_path,
    production_entries,
)
from way2australia_rag.lexical.store import DenseIdentity, LexicalIdentityInput
from way2australia_rag.repositories import (
    DocumentRepositoryError,
    LocalDocumentRepository,
    LocalRepositoryConfig,
)
from way2australia_rag.repositories.hashing import HASH_CONTRACT
from way2australia_rag.retrieval.errors import RetrievalError
from way2australia_rag.retrieval.text import safe_text

EXIT_OK = 0
EXIT_REFUSED = 2


PROTECTED_DIRS = ("knowledge", "evaluation", "config")


class LexicalTargetRefusedError(Exception):
    """The lexical index target is in a protected or not git-ignored location."""


def _inside_git_work_tree(directory: Path) -> bool:
    """True when ``directory`` is inside a git work tree (False outside a repo)."""
    try:
        result = subprocess.run(  # noqa: S603 - fixed argv, no shell
            ["git", "-C", str(directory), "rev-parse", "--is-inside-work-tree"],
            capture_output=True,
            text=True,
            check=False,
            timeout=30,
        )
    except (OSError, subprocess.SubprocessError):
        return False
    return result.returncode == 0 and result.stdout.strip() == "true"


def _is_git_ignored(path: Path, cwd: Path) -> bool:
    try:
        result = subprocess.run(  # noqa: S603 - fixed argv, no shell
            ["git", "-C", str(cwd), "check-ignore", "-q", "--", str(path)],
            capture_output=True,
            check=False,
            timeout=30,
        )
    except (OSError, subprocess.SubprocessError):
        return False
    return result.returncode == 0


def check_target_allowed(target: Path, repo_root: Path) -> None:
    """Refuse a target in or under ``knowledge/``, ``evaluation/`` or ``config/``,
    or, inside a git work tree, any target that git does not report as ignored
    (Spec 007 R4).

    Decided on the real filesystem, not on spelling: the nearest existing
    ancestor of the target is compared (``samefile``) with the protected
    directories and each of their ancestors-in-common, so a differently cased
    name on a case-insensitive filesystem and a not-yet-existing subfolder are
    both caught. A git-ignored target (the default ``.local/lexical``) and a
    target outside any git repository are allowed.
    """
    resolved = target.resolve()
    existing = resolved.parent
    while not existing.exists() and existing != existing.parent:
        existing = existing.parent
    root = repo_root.resolve()
    protected = [root / name for name in PROTECTED_DIRS if (root / name).exists()]
    for ancestor in (existing, *existing.parents):
        for directory in protected:
            if ancestor.samefile(directory):
                raise LexicalTargetRefusedError(
                    "the lexical index must not be written under knowledge/, "
                    "evaluation/ or config/"
                )
    if not _inside_git_work_tree(existing):
        return
    if not _is_git_ignored(resolved, existing):
        raise LexicalTargetRefusedError(
            "the lexical index must be written to a git-ignored location "
            "such as .local/lexical"
        )


def shown_path(path: Path, repo_root: Path) -> str:
    try:
        return path.resolve().relative_to(repo_root).as_posix()
    except ValueError:
        return path.name


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m way2australia_rag.lexical.cli",
        description="Build the lexical (BM25) index for one dense index identity.",
    )
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--config", type=Path, default=None)
    parser.add_argument(
        "--embedder",
        choices=("bge_m3", "fake"),
        default=None,
        help="dense embedder the index belongs to (default: from the config)",
    )
    parser.add_argument(
        "--output", type=Path, default=None, help="lexical index file to write"
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    repo_root = args.repo_root.resolve()
    config_path: Path = args.config or repo_root / DEFAULT_CONFIG_PATH
    try:
        config = load_ingestion_config(config_path)
        settings = load_runtime_settings()
        provider = args.embedder or config.embedder.provider
        model_id, revision = embedder_identity(config, provider)
        chunker = build_chunker(config)
        collection = collection_name(settings.collection_base, config.index_version)
        target: Path = args.output or lexical_index_path(
            settings.lexical_index_dir or default_lexical_dir(repo_root), collection
        )
        if not target.is_absolute():
            target = repo_root / target
        check_target_allowed(target, repo_root)
        repository = LocalDocumentRepository(LocalRepositoryConfig(repo_root=repo_root))
        entries = asyncio.run(production_entries(repository, chunker))
        identity = LexicalIdentityInput(
            collection=collection,
            index_version=config.index_version,
            dense_identity=DenseIdentity(
                collection=collection,
                index_version=config.index_version,
                embedder_model_id=model_id,
                embedder_revision=revision,
            ),
            chunker_name=chunker.name,
            chunker_version=chunker.version,
            chunker_max_chunk_chars=chunker.max_chunk_chars,
            hash_contract=HASH_CONTRACT,
        )
        built = build_lexical_index(entries, target, identity)
    except (
        IngestionError,
        DocumentRepositoryError,
        RetrievalError,
        LexicalTargetRefusedError,
    ) as error:
        print(f"ERROR {type(error).__name__}: {safe_text(error)}", file=sys.stderr)
        return EXIT_REFUSED
    except Exception as error:  # noqa: BLE001 - class name only: no paths or secrets
        print(f"ERROR {type(error).__name__}", file=sys.stderr)
        return EXIT_REFUSED
    print(
        f"lexical index: {shown_path(target, repo_root)} (collection {collection}, "
        f"index_version {config.index_version}; {built.tokenizer_name}; "
        f"chunks {built.chunk_count}; digest {built.source_chunk_digest[:12]})"
    )
    return EXIT_OK


if __name__ == "__main__":
    raise SystemExit(main())
