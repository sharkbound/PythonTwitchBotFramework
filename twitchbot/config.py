import os
import json
from pathlib import Path

__all__ = ('cfg', 'Config')


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


cfg = Config(
    file_path=Path('configs', 'config.json'),
    oauth='oauth:',
    client_id='CLIENT_ID',
    nick='nick',
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
)
