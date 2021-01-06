__all__ = [
    'normalize_string'
]


def normalize_string(string: str) -> str:
    """
    removes trailing or leading whitespace, then converts it to lowercase
    """
    return string.strip().casefold()
