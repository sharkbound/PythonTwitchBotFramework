from sqlalchemy import create_engine, orm
from sqlalchemy.ext.declarative import declarative_base

__all__ = ('Base', 'engine', 'session', 'DB_FILENAME')

Base = declarative_base()
DB_FILENAME = 'database.sqlite'
engine = create_engine(f'sqlite:///{DB_FILENAME}')
Session = orm.sessionmaker(bind=engine)
session: orm.Session = Session()


def database_init():
    Base.metadata.create_all(engine)
