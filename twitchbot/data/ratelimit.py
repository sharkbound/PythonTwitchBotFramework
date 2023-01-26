from typing import NamedTuple, Optional

__all__ = [
    'RateLimit'
]


class RateLimit(NamedTuple):
    remaining: int
    limit: int
    reset: int

    @staticmethod
    def from_headers_or_none(headers: dict) -> Optional['RateLimit']:
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
            limit=headers['Ratelimit-Limit'],
            remaining=headers['Ratelimit-Remaining'],
            reset=headers['Ratelimit-Reset']
        )
