import re


class Tags:
    def __init__(self, tags: str):
        self.all_tags = {name: value for name, value in _split_tags(tags)}
        self.badges: dict = _parse_badges(self.all_tags.get('@badges'))
        self.color: str = self.all_tags.get('color')
        self.display_name: str = self.all_tags.get('display-name')
        self.emotes: str = self.all_tags.get('emotes')
        self.id: str = self.all_tags.get('id')
        self.mod: int = _try_parse_int(self.all_tags.get('mod'))
        self.room_id: int = _try_parse_int(self.all_tags.get('room-id'))
        self.subscriber: int = _try_parse_int(self.all_tags.get('subscriber'))
        self.tmi_sent_ts: int = _try_parse_int(self.all_tags.get('tmi-sent-ts'))
        self.turbo: int = _try_parse_int(self.all_tags.get('turbo'))
        self.user_id: int = _try_parse_int(self.all_tags.get('user-id'))
        self.user_type: int = self.all_tags.get('user-type')
        self.bits: int = _try_parse_int(self.all_tags.get('bits'))
        self.bits_leader: int = self.all_tags.get('bits-leader')
        self.broadcaster: int = self.badges.get('broadcaster', 0)
        self.msg_id: str = self.all_tags.get('msg-id')

        # bit_leader is initially a string, it is then parsed into a int here
        if self.bits_leader:
            self.bits_leader = _try_parse_int(self.bits_leader.partition('/')[-1])


def _split_tags(tags: str):
    for tag in tags.split(';'):
        name, _, value = tag.partition('=')
        yield name, value


def _parse_badges(badges: str):
    if not badges:
        return {}

    all_badges = badges.split(',')
    ret = {}

    for badge in all_badges:
        if '/' in badge:
            name, value = badge.split('/')

            if value.isdigit():
                value = int(value)

            ret[name] = value

        else:
            ret[badge] = badge

    return ret


def _try_parse_int(value, default=0):
    try:
        return int(value)
    except (ValueError, TypeError):
        return default

# example tags (split by =)
# (('@badges', 'broadcaster/1'),
# ('color', '#FF69B4'),
# ('display-name', 'bob'),
# ('emotes', ''),
# ('id', '4585b203-ad2e-40ab-9a54-e4d6e91cb85e'),
# ('mod', '0'),
# ('room-id', '1234'),
# ('subscriber', '0'),
# ('tmi-sent-ts', '1527291908857'),
# ('turbo', '0'),
# ('user-id', '1234'),
# ('user-type', ' '))
