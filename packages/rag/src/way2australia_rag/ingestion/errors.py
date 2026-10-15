"""Ingestion error hierarchy. Messages never carry absolute paths or secrets."""


class IngestionError(Exception):
    """Base class for all ingestion failures."""


class IngestionConfigurationError(IngestionError):
    """The ingestion configuration or runtime settings are invalid."""


class IndexSettingsMismatchError(IngestionError):
    """Recorded index settings differ from the settings the run wants."""


class OptionalDependencyError(IngestionError):
    """An optional dependency group is required but not installed."""
