from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from . import datastore_config


def get_db_config():
    return datastore_config.DB_CONFIG

def get_cache_config():
    return datastore_config.CACHE_CONFIG

def get_session():
    db_config = get_db_config()
    db_uri = db_config['SQLALCHEMY_DATABASE_URI']
    engine = create_engine(db_uri)
    Session = sessionmaker(engine)
    return Session
