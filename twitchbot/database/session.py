from sqlalchemy import create_engine, orm
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.exc import NoSuchModuleError

from ..config import database_cfg

__all__ = ('Base', 'engine', 'session', 'DB_FILENAME', 'init_tables')


Base = declarative_base()
DB_FILENAME = 'database.sqlite'
try:
    engine = create_engine(f'sqlite:///{DB_FILENAME}'
                       if not database_cfg.enabled else
                       f'{database_cfg.driver}://{database_cfg.username}:{database_cfg.password}@{database_cfg.address}:{database_cfg.port}/{database_cfg.database}')
except NoSuchModuleError:
        print(
            f'Could not find library for database driver ({database_cfg.driver}), please install it via pip or change it')
        input('\npress enter to exit...')
        exit(1)

Session = orm.sessionmaker(bind=engine)
session = orm.scoped_session(Session)


def init_tables():
    Base.metadata.create_all(engine)
