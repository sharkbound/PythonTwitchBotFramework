from itertools import chain
from pathlib import Path
from typing import Dict, Iterable, Tuple, Optional

from .config import Config, cfg

__all__ = ('perms', 'Permissions', 'generate_permission_files', 'permission_defaults')

permission_defaults = {
    'admin': {
        'name': 'admin',
        'permissions': ['*'],
        'members': [cfg.owner]
    },
}


class Permissions:
    def __init__(self):
        self.channels: Dict[str, Config] = {}

    def load_permissions(self, channel: str, force_update=False):
        """loads a config file (or creates the config if it doesnt exist) into the cache of the permission object"""
        channel = channel.lower()
        if channel in self and not force_update:
            return

        config = Config(
            file_path=Path(f'configs', f'{channel}_perms.json'),
            **permission_defaults)

        self.channels[channel] = config

        if channel not in config.data['admin']['members']:
            config.data['admin']['members'].append(channel)
            self.channels[channel].save()

    def iter_user_groups(self, channel: str, user: str):
        """yields all permission groups a user is in for a channel"""
        user = user.lower()
        yield from ((name, group) for name, group in self[channel] if user in group['members'])

    def iter_groups(self, channel: str):
        if channel in self:
            yield from self[channel]

    def iter_user_permissions(self, channel: str, user: str):
        """yields all permissions from a specified user for the channel"""
        user = user.lower()
        for group_name, group in self.iter_user_groups(channel, user):
            yield from group['permissions']

    def has_permission(self, channel: str, user: str, perm: str) -> bool:
        """checks if a user has a permission"""
        if not perm:
            return True

        user, perm = user.lower(), perm.lower()
        search = {perm, '*'}
        return user == cfg.owner or any(p in search for p in self.iter_user_permissions(channel, user))

    def get_group(self, channel: str, group: str) -> Optional[dict]:
        """gets a permission group by the name passed in, returns None if not found"""
        group = group.lower()
        if channel not in self or group not in self.channels[channel].data:
            return None

        return self[channel].data[group]

    def iter_group_permissions(self, channel: str, group: str):
        group = group.lower()
        g = self.get_group(channel, group)
        if not g:
            return

        yield from g['permissions']

    def iter_group_members(self, channel: str, group: str):
        group = group.lower()
        g = self.get_group(channel, group)
        if not g:
            return

        yield from g['members']

    def add_permission(self, channel: str, group: str, perm: str) -> bool:
        """adds a permission to a permission group for a channel, returns if it was successful"""
        group, perm = group.lower(), perm.lower()
        g = self.get_group(channel, group)

        if not g:
            return False

        if perm not in g['permissions']:
            g['permissions'].append(perm)
            self[channel].save()

        return True

    def delete_permission(self, channel: str, group: str, perm: str) -> bool:
        """adds a permission to a permission group for a channel, returns if it was successful"""
        group, perm = group.lower(), perm.lower()
        g = self.get_group(channel, group)

        if not g:
            return False

        if perm in g['permissions']:
            g['permissions'].remove(perm)
            self[channel].save()

        return True

    def add_group(self, channel: str, group: str) -> bool:
        """adds a permission group to the channels config, returns if it was successful"""
        group = group.lower()
        if self.get_group(channel, group):
            return False

        self[channel].data[group] = {
            'name': group,
            'permissions': [],
            'members': []
        }
        self[channel].save()

        return True

    def delete_group(self, channel: str, group: str) -> bool:
        """adds a permission group to the channels config, returns if it was successful"""
        group = group.lower()
        if not self.get_group(channel, group):
            return False

        del self[channel].data[group]
        self[channel].save()

        return True

    def reload_permissions(self, channel=None):
        if not channel:
            for channel in tuple(self.channels):
                self.load_permissions(channel, force_update=True)
            return True

        elif channel in self:
            self.load_permissions(channel, force_update=True)
            return True

        return False

    def add_member(self, channel: str, group: str, member: str):
        group = group.lower()
        g = self.get_group(channel, group)

        if not g:
            return False

        member = member.lower()

        if member not in g['members']:
            g['members'].append(member)
            self[channel].save()

        return True

    def delete_member(self, channel: str, group: str, member: str):
        group = group.lower()
        g = self.get_group(channel, group)

        if not g:
            return False

        member = member.lower()

        if member not in g['members']:
            return False

        g['members'].remove(member)
        self[channel].save()

        return True

    def __contains__(self, item):
        return item in self.channels

    def __iter__(self) -> Iterable[Tuple[str, Config]]:
        yield from self.channels.items()

    def __getitem__(self, item) -> Config:
        """gets a channels Config, creates if not exists"""
        if item not in self:
            self.load_permissions(item)
        return self.channels[item]


# permissions are requested/generated in channel.py in __init__ for Channel class
perms = Permissions()


def generate_permission_files(*extra_channels):
    from .config import cfg
    for channel in chain(cfg.channels, extra_channels):
        perms.load_permissions(channel, force_update=False)
