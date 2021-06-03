import os
import json
from pathlib import Path
from typing import Optional, Union
from .gui import show_auth_gui

__all__ = ('cfg', 'Config', 'database_cfg', 'CONFIG_FOLDER', 'generate_config', 'get_oauth', 'get_nick', 'get_client_id',
           'DEFAULT_NICK', 'DEFAULT_OAUTH', 'DEFAULT_CLIENT_ID', 'is_config_valid', 'get_command_prefix', 'message_timer_cfg')

CONFIG_FOLDER = Path('configs')


# noinspection PyTypeChecker
class Config:
    def __init__(self, file_path: Union[str, Path], **defaults):
        if isinstance(file_path, str):
            file_path = Path(file_path)

        self.file_path: Path = file_path
        self.data = {}
        self.defaults = defaults

        self.load()
        self._add_missing_keys()

    def _add_missing_keys(self):
        """checks that all default keys are present"""
        for k, v in self.defaults.items():
            if k not in self.data:
                self.data[k] = v

        self.save()

    @property
    def exist(self):
        """returns if the config file exist"""
        return self.file_path.exists()

    @property
    def in_folder(self):
        """returns if the config file is in a folder"""
        return len(os.path.split(self.file_path)) > 1

    def regen(self):
        """restores config file to its default state and values"""
        self.create(overwrite=True)
        self.load()

    def save(self):
        """updates the config file with the current config data"""
        with open(self.file_path, 'w') as file:
            json.dump(self.data, file, indent=2)

    def load(self):
        """
        loads the config file's contents into this config object's `data` attribute
        creates the config if it doesnt exist
        """
        if not self.exist:
            self.create()

        with open(self.file_path) as file:
            self.data = json.load(file)

    def create(self, overwrite=False):
        """creates the config json file, does nothing if it already exist, except if `ignore_exist` is True"""
        if self.exist and not overwrite:
            return

        if self.in_folder:
            try:
                os.makedirs(os.path.join(os.curdir, *os.path.split(self.file_path)[:-1]))
            except FileExistsError:
                pass

        with open(self.file_path, 'w') as file:
            json.dump(self.defaults, file, indent=2)

    def __getattr__(self, item):
        """allows for getting config values by accessing a attribute"""
        return self.__dict__[item] if item in self.__dict__ else self.data.get(item)

    def __getitem__(self, item):
        return self.__getattr__(item)

    def __setitem__(self, key, value):
        self.data[key] = value
        self.save()

    def __contains__(self, item):
        return item in self.data

    def __iter__(self):
        yield from self.data.items()


DEFAULT_OAUTH = 'oauth:'
DEFAULT_NICK = 'nick'
DEFAULT_CLIENT_ID = 'CLIENT_ID'

cfg = Config(
    file_path=CONFIG_FOLDER / 'config.json',
    nick=DEFAULT_NICK,
    oauth=DEFAULT_OAUTH,
    client_id=DEFAULT_CLIENT_ID,
    prefix='!',
    default_balance=200,
    loyalty_interval=60,
    loyalty_amount=2,
    owner='BOT_OWNER_NAME',
    channels=['channel'],
    mods_folder='mods',
    commands_folder='commands',
    command_server_enabled=True,
    command_server_port=1337,
    command_server_host='0.0.0.0',
    command_server_password='',
    disable_whispers=True,
    use_command_whitelist=False,
    send_message_on_command_whitelist_deny=True,
    send_message_on_disabled_command_use=True,
    command_whitelist=[
        'help', 'commands', 'reloadcmdwhitelist', 'reloadmod', 'reloadperms', 'disablemod', 'enablemod', 'disablecmdglobal', 'disablecmd',
        'enablecmdglobal', 'enablecmd', 'addcmd', 'delcmd', 'updatecmd', 'cmd'
    ],
    enable_cooldown_bypass_permissions=True,
)

message_timer_cfg = Config(
    file_path=CONFIG_FOLDER / 'message_timer_options.json',
    no_chat_message_auto_disable_seconds=300,
)

database_cfg = Config(
    CONFIG_FOLDER / 'database_config.json',
    connection='{database_format}+{driver}://{username}:{password}@{address}:{port}/{database}',
    database_format='mysql',
    driver='mysqlconnector',
    enabled=False,
    address='localhost',
    port='3306',
    username='root',
    password='password',
    database='twitchbot',
)


def generate_config():
    if not is_config_valid(check_client_id=False):
        if input('show the bot config GUI? [Y/N]: ').lower() == 'y':
            print('please enter your twitch auth info the the GUI that will pop-up shortly')
            auth = show_auth_gui()
            cfg['nick'] = auth.username
            cfg['oauth'] = auth.oauth
        else:
            print(
                'open the config folder at <BOT_FOLDER>/configs/config.json\nthen enter the bot oauth/name, the owner, and the channels to join')
            input('\npress enter to close bot...')
            return False

    if 'oauth:' not in get_oauth().lower():
        print('oauth must start with `oauth:` and be followed by the token itself, ex: oauth:exampletoken12')
        input('press enter to exit...')
        return False

    # removed for now, leaving it if its needed later
    # if len(cfg['oauth']) <= 10:
    #     print('oauth is too short, must be `oauth:` followed by the token itself, ex: oauth:exampletoken12')
    #     input('press enter to exit...')
    #     return False

    # this is to fix the edge case where the user entered enters cased names / channel names
    # without this, the twitch API returns weird responses that are not easy to figure out why it is doing it
    cfg['nick'] = cfg['nick'].lower()
    cfg['owner'] = cfg['owner'].lower()
    cfg['channels'] = [chan.lower() for chan in cfg['channels']]
    cfg.save()

    return True


def is_config_valid(check_client_id=False):
    if (get_nick() == DEFAULT_NICK or get_oauth() == DEFAULT_OAUTH
            or (check_client_id and get_client_id() == DEFAULT_CLIENT_ID)):
        return False
    return True


def get_nick() -> str:
    """
    gets the bot accounts NICK, this is the login username for the bot account

    if the the NICK matches the pattern `ENV_KEY_HERE` it will get `KEY_HERE` from os.environ, else it just grabs it from the cfg
    """
    from .util import get_env_value, is_env_key
    nick = cfg.nick
    if is_env_key(nick):
        value = get_env_value(nick)
        if value is None:
            print(f'could not get NICK from environment with key: {nick[4:]}')
            input('\npress enter to exit...')
            exit(1)
        return value
    return nick


def get_oauth(remove_prefix: bool = False) -> str:
    """
    gets the bot accounts OAUTH
    this is needed because of supporting getting it from os.environ

    if the the OAUTH matches the pattern `ENV_KEY_HERE` it will get `KEY_HERE` from os.environ, else it just grabs it from the cfg
    """
    from .util import get_env_value, is_env_key
    oauth: str = cfg.oauth
    if is_env_key(oauth):
        value = get_env_value(oauth)
        if value is None:
            print(f'could not get OAUTH from environment with key: {oauth[4:]}')
            input('\npress enter to exit...')
            exit(1)

        oauth = value

    if remove_prefix:
        oauth = oauth.replace('oauth:', '')

    return oauth


def get_client_id() -> str:
    """
    gets the bot accounts CLIENT_ID
    this is needed because of supporting getting it from os.environ

    if the the CLIENT_ID matches the pattern `ENV_KEY_HERE` it will get `KEY_HERE` from os.environ, else it just grabs it from the cfg
    """
    from .util import get_env_value, is_env_key
    client_id = cfg.client_id
    if is_env_key(client_id):
        value = get_env_value(client_id)
        if value is None:
            print(f'could not get CLIENT_ID from environment with key: {client_id[4:]}')
            input('\npress enter to exit...')
            exit(1)
        return value
    return client_id


def get_command_prefix() -> str:
    return cfg.prefix
