"""Evaluation error hierarchy. Messages never carry case text, paths or secrets."""


class EvaluationError(Exception):
    """Base class for all evaluation failures."""


class EvaluationConfigurationError(EvaluationError):
    """An evaluation suite, dataset, schema or setting is missing or invalid."""


class EvaluationHarnessError(EvaluationError):
    """The evaluation harness itself is broken (for example the unfiltered sanity
    check did not find a forbidden point nearest). Never a pass."""
