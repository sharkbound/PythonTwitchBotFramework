from typing import Dict

from dataclasses import dataclass, field

from .util import get_url


@dataclass
class Emote:
    id: int
    code: str
    set: int = field(default=0, repr=False)
    desc: str = field(default='', repr=False)


GLOBAL_EMOTE_API = 'https://twitchemotes.com/api_cache/v3/global.json'
emotes: Dict[str, Emote] = {}


async def fetch_global_emotes():
    data = await get_url(GLOBAL_EMOTE_API)
    emotes.clear()

    for k, v in data.items():
        emotes[k] = Emote(int(v['id']), v['code'], v['emoticon_set'], v['description'])
