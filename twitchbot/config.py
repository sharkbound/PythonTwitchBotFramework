import os
import json
from pathlib import Path
from .gui import show_auth_gui

__all__ = ('cfg', 'Config', 'mysql_cfg', 'CONFIG_FOLDER')

CONFIG_FOLDER = Path('configs')


# noinspection PyTypeChecker
class Config:
    def __init__(self, file_path: Path, **defaults):
        self.file_path = file_path
        self.data = {}
        self.defaults = defaults

        self.load()
        self._validate()

    def _validate(self):
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
        create the config if it doesnt exist
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

    def prompt_edit_oauth(self):
        pass

    def __getattr__(self, item):
        """allows for getting config values by accessing a attribute"""
        return self.__dict__[item] if item in self.__dict__ else self.data.get(item)

    def __getitem__(self, item):
        return self.__getattr__(item)

    def __setitem__(self, key, value):
        self.data[key] = value
        self.save()

    def __iter__(self):
        yield from self.data.items()


DEFAULT_OAUTH = 'oauth:'
DEFAULT_NICK = 'nick'

cfg = Config(
    file_path=CONFIG_FOLDER / 'config.json',
    nick=DEFAULT_NICK,
    oauth=DEFAULT_OAUTH,
    client_id='CLIENT_ID',
    prefix='!',
    default_balance=200,
    loyalty_interval=60,
    loyalty_amount=2,
    owner='BOT_OWNER_NAME',
    channels=['channel'],
    mods_folder='mods',
    command_server_enabled=True,
    command_server_port=1337,
    command_server_host='localhost',
    disable_whispers=False,
)

mysql_cfg = Config(
    CONFIG_FOLDER / 'mysql.json',
    enabled=False,
    address='localhost',
    port='3306',
    username='root',
    password='password',
    database='twitchbot',
)


def init_config():
    if cfg.nick == DEFAULT_NICK or cfg.oauth == DEFAULT_OAUTH:
        print('please enter your twitch auth info the the GUI that will pop-up shortly')
        auth = show_auth_gui()
        cfg['nick'] = auth.username
        cfg['oauth'] = auth.oauth
    if 'oauth:' not in cfg['oauth']:
        print('oauth must start with `oauth:` and be followed by the token itself, ex: oauth:exampletoken12')
        input('press enter to exit...')
        exit()
    if len(cfg['oauth']) <= 10:
        print('oauth is too short, must be `oauth:` followed by the token itself, ex: oauth:exampletoken12')
        input('press enter to exit...')
        exit()
    # this is to fix the edge case where the user entered enters cased names / channel names
    # without this, the twitch API returns weird responses that are not easy to figure out why it is doing it
    cfg['nick'] = cfg['nick'].lower()
    cfg['owner'] = cfg['owner'].lower()
    cfg['channels'] = [chan.lower() for chan in cfg['channels']]
    cfg.save()


init_config()
