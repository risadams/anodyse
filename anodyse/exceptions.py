"""Custom exception and warning classes for Anodyse."""


class ParseError(Exception):
    """Raised when a playbook or role YAML file cannot be parsed."""

    pass


class AnnotationWarning(Warning):
    """Emitted when mandatory annotations (@title or @description) are absent."""

    pass


class ManifestError(Exception):
    """Raised when the .anodyse.yml manifest file is invalid or malformed."""

    pass
