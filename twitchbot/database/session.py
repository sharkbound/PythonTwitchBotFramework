from sqlalchemy import create_engine, orm
from sqlalchemy.ext.declarative import declarative_base
from ..config import mysql_cfg

__all__ = ('Base', 'engine', 'session', 'DB_FILENAME', 'init_tables')

if mysql_cfg.enabled:
    try:
        import mysql.connector
    except (ImportError, ModuleNotFoundError):
        print(
            'Could not find mysql connection library, please install it via pip:\n\tpip install --upgrade --user mysql-connector-python')
        input('\npress enter to exit...')
        exit(1)

Base = declarative_base()
DB_FILENAME = 'database.sqlite'
engine = create_engine(f'sqlite:///{DB_FILENAME}'
                       if not mysql_cfg.enabled else
                       f'mysql+mysqlconnector://{mysql_cfg.username}:{mysql_cfg.password}@{mysql_cfg.address}:{mysql_cfg.port}/{mysql_cfg.database}')
Session = orm.sessionmaker(bind=engine)
session: orm.Session = Session()


def init_tables():
    Base.metadata.create_all(engine)
