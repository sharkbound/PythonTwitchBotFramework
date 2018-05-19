import os
import json


class Config:
    def __init__(self, file_path='configs/config.json'):
        self.file_path = file_path.replace('\\', '/')
        self.data = {}

        self.load()

    @property
    def exist(self):
        """returns if the config file exist"""
        return os.path.exists(self.file_path)

    @property
    def in_folder(self):
        """returns if the config file is in a folder"""
        return len(os.path.split(self.file_path)) > 1

    def regen(self):
        """restores config file to its default state and values"""
        self.create(ignore_exist=True)
        self.load()

    def save(self):
        """updates the config file with the current config data"""
        with open(self.file_path, 'w') as file:
            json.dump(self.data, file)

    def load(self):
        """
        loads the config file's contents into this config object's `data` attribute
        create the config if it doesnt exist
        """
        if not self.exist:
            self.create()

        with open(self.file_path) as file:
            self.data = json.load(file)

    def create(self, ignore_exist=False):
        """creates the config json file, does nothing if it already exist, except if `ignore_exist` is True"""
        if self.exist and not ignore_exist:
            return

        if self.in_folder:
            os.makedirs(os.path.join(os.curdir, *os.path.split(self.file_path)[:-1]))

        with open(self.file_path, 'w') as file:
            json.dump(dict(
                oauth='oauth:',
                nick='nick',
                prefix='!',
                default_balance=200,
                channels=['channel']
            ), file, indent=2)

    def __getattr__(self, item):
        """allows for getting config values by accessing a attribute"""
        if item in self.__dict__:
            return self.__dict__[item]

        return self.data.get(item)


cfg = Config()
