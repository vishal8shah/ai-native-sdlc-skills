"""Validate the justification supplied with a synthetic demo request."""


def request_is_valid(value=None):
    """Return whether value is a string containing non-whitespace text."""
    return isinstance(value, str) and bool(value.strip())
