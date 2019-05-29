from typing import NamedTuple

__all__ = [
    'RateLimit'
]


class RateLimit(NamedTuple):
    remaining: int
    limit: int
    reset: int

    @staticmethod
    def from_headers(headers):
        return RateLimit(
            limit=int(headers.get('Ratelimit-Limit')),
            remaining=int(headers.get('Ratelimit-Remaining')),
            reset=int(headers.get('Ratelimit-Reset'))
        )
