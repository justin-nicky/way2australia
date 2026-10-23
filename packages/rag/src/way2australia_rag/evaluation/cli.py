"""Evaluation command line (Spec 006).

Run as ``python -m way2australia_rag.evaluation.cli <subcommand>``. T2 provides
``validate`` (``make validate-evaluation``): exit 0 when valid, 1 on validation
problems, 2 on configuration errors or an unexpected exception (class name only).
"""

import argparse
import sys
from collections.abc import Sequence
from pathlib import Path

from way2australia_rag.evaluation.errors import EvaluationError
from way2australia_rag.evaluation.validate import validate_evaluation
from way2australia_rag.retrieval.text import safe_text

EXIT_OK = 0
EXIT_PROBLEMS = 1
EXIT_ERROR = 2


def _validate(repo_root: Path) -> int:
    try:
        problems = validate_evaluation(repo_root)
    except EvaluationError as error:
        print(f"ERROR {type(error).__name__}: {safe_text(error)}", file=sys.stderr)
        return EXIT_ERROR
    except Exception as error:  # never print messages: they may hold case text
        print(f"ERROR {type(error).__name__}", file=sys.stderr)
        return EXIT_ERROR
    for problem in problems:
        print(f"ERROR {problem}")
    if problems:
        print(f"validate-evaluation: FAILED with {len(problems)} problem(s)")
        return EXIT_PROBLEMS
    print("validate-evaluation: OK, 0 problems")
    return EXIT_OK


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="evaluation", description="Way2Australia evaluation tools."
    )
    commands = parser.add_subparsers(dest="command", required=True)
    validate = commands.add_parser(
        "validate", help="validate evaluation suites, cases and candidates"
    )
    validate.add_argument(
        "--repo-root", type=Path, default=Path.cwd(), help="repository root"
    )
    args = parser.parse_args(argv)
    return _validate(args.repo_root.resolve())


if __name__ == "__main__":
    sys.exit(main())
