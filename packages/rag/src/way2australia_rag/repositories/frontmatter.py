"""Markdown frontmatter parsing (local-adapter detail).

Frontmatter is a YAML mapping between two `---` lines at the start of a file.
Timestamps are kept as strings so ISO dates validate against the metadata JSON
Schema exactly as written.
"""

from typing import Any

import yaml

_DELIMITER = "---"


class _StringDateLoader(yaml.SafeLoader):
    """SafeLoader that does not turn `2026-10-09` into a `date`."""


_StringDateLoader.yaml_implicit_resolvers = {
    key: [
        (tag, regexp)
        for tag, regexp in resolvers
        if tag != "tag:yaml.org,2002:timestamp"
    ]
    for key, resolvers in yaml.SafeLoader.yaml_implicit_resolvers.items()
}


def split_frontmatter(text: str) -> tuple[dict[str, Any], str]:
    """Return `(metadata, body)`. Raises `ValueError` with a clear reason."""
    lines = text.lstrip("﻿").splitlines(keepends=True)
    if not lines or lines[0].rstrip() != _DELIMITER:
        raise ValueError("missing opening '---' frontmatter delimiter")
    for index in range(1, len(lines)):
        if lines[index].rstrip() == _DELIMITER:
            raw = "".join(lines[1:index])
            body = "".join(lines[index + 1 :])
            try:
                metadata = yaml.load(raw, Loader=_StringDateLoader)  # noqa: S506
            except yaml.YAMLError as exc:
                raise ValueError(f"frontmatter is not valid YAML: {exc}") from exc
            if not isinstance(metadata, dict):
                raise ValueError("frontmatter must be a YAML mapping")
            return metadata, body
    raise ValueError("missing closing '---' frontmatter delimiter")
