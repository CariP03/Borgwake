"""Provides generic error classes."""


class ConfigurationError(RuntimeError):
    """A configuration error related to env or YAML variables has occurred."""


class HostResolutionError(RuntimeError):
    """Host resolution failed."""
