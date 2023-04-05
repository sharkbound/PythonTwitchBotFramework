from typing import NamedTuple, Optional, Union

__all__ = [
    'RateLimit'
]

from multidict import CIMultiDictProxy


class RateLimit(NamedTuple):
    remaining: int
    limit: int
    reset: int

    @staticmethod
    def from_headers_or_none(headers: Union[dict, CIMultiDictProxy]) -> Optional['RateLimit']:
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
            limit=int(headers['Ratelimit-Limit']),
            remaining=int(headers['Ratelimit-Remaining']),
            reset=int(headers['Ratelimit-Reset'])
        )
