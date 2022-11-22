from typing import NamedTuple

__all__ = [
    'RateLimit'
]


class RateLimit(NamedTuple):
    remaining: int
    limit: int
    reset: int

    @staticmethod
    def from_headers_or_none(headers: dict):
        """
        :param headers: dict of headers from the twitch response, expects these keys to be present: ('Ratelimit-Limit', 'Ratelimit-Reset', 'Ratelimit-Remaining')
        :return:
            `Ratelimit` instance if all these keys are present ('Ratelimit-Limit', 'Ratelimit-Reset', 'Ratelimit-Remaining')
            else returns None
        """
        for key in ('Ratelimit-Limit', 'Ratelimit-Reset', 'Ratelimit-Remaining'):
            if key not in headers:
                return None

        return RateLimit(
            limit=int(headers.get('Ratelimit-Limit')),
            remaining=int(headers.get('Ratelimit-Remaining')),
            reset=int(headers.get('Ratelimit-Reset'))
        )
