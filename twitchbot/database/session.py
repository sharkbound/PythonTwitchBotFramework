from sqlalchemy import create_engine, orm
from sqlalchemy.ext.declarative import declarative_base
from ..config import mysql_cfg

__all__ = ('Base', 'engine', 'session', 'DB_FILENAME', 'init_tables', 'connect_database', 'shutdown_database')

DB_FILENAME = 'database.sqlite'
Base = declarative_base()
engine = None
session: orm.Session = None

if mysql_cfg.enabled:
    try:
        import mysql.connector
    except (ImportError, ModuleNotFoundError):
        print(
            'Could not find mysql connection library, please install it via pip:\n\tpip install --upgrade --user mysql-connector-python')
        input('\npress enter to exit...')
        exit(1)

def connect_database():
    global engine
    global session
     
    engine = create_engine(f'sqlite:///{DB_FILENAME}'
                       if not mysql_cfg.enabled else
                       f'mysql+mysqlconnector://{mysql_cfg.username}:{mysql_cfg.password}@{mysql_cfg.address}:{mysql_cfg.port}/{mysql_cfg.database}')
    Session = orm.sessionmaker(bind=engine)
    session = Session()

def shutdown_database():
    global engine
    global session
    
    session.commit()
    session.close()
    session = None
    engine.dispose()
    engine = None
    
def init_tables():
    if engine is None:
        return
    
    Base.metadata.create_all(engine)

connect_database()
