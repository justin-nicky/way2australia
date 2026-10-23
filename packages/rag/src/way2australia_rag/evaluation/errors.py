"""Evaluation error hierarchy. Messages never carry case text, paths or secrets."""


class EvaluationError(Exception):
    """Base class for all evaluation failures."""


class EvaluationConfigurationError(EvaluationError):
    """An evaluation suite, dataset, schema or setting is missing or invalid."""
