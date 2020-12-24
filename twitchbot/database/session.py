from sqlalchemy import create_engine, orm
from sqlalchemy.ext.declarative import declarative_base

from ..config import database_cfg

__all__ = ('Base', 'engine', 'session', 'DB_FILENAME', 'init_tables')

Base = declarative_base()
DB_FILENAME = 'database.sqlite'
try:
    engine = create_engine(f'sqlite:///{DB_FILENAME}'
                           if not database_cfg.enabled else
                           database_cfg.connection.format(
                               database_format=database_cfg.database_format,
                               driver=database_cfg.driver,
                               username=database_cfg.username,
                               password=database_cfg.password,
                               address=database_cfg.address,
                               port=database_cfg.port,
                               database=database_cfg.database
                           ))
except (ImportError, ModuleNotFoundError):
    print(
        f'Could not find library for database driver "{database_cfg.driver}", please install the necessary driver.\n'
        f'for mysql, install this driver (via pip): pip install --upgrade mysql-connector-python')
    input('\npress enter to exit...')
    exit(1)

# noinspection PyUnboundLocalVariable
Session = orm.sessionmaker(bind=engine)
session = orm.scoped_session(Session)


def init_tables():
    Base.metadata.create_all(engine)
