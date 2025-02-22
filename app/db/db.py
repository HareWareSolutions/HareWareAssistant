import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL_HAREWARE = "postgresql+pg8000://hareware:HareWare402025@localhost/harewareassistant"
DATABASE_URL_MMANIA = "postgresql+pg8000://hareware:HareWare402025@localhost/mmaniadeboloassistant"
DATABASE_URL_HWADMIN = "postgresql+pg8000://hareware:HareWare402025@localhost/hareware"
DATABASE_URL_MALAMAN = "postgresql+pg8000://hareware:HareWare402025@localhost/malamanassistant"
DATABASE_URL_EMINY = "postgresql+pg8000://hareware:HareWare402025@localhost/eminyassistant"


def get_database_url(env: str = "hareware"):
    if env == "hareware":
        return DATABASE_URL_HAREWARE
    elif env == "mmania":
        return DATABASE_URL_MMANIA
    elif env == "hwadmin":
        return DATABASE_URL_HWADMIN
    elif env == "emyconsultorio":
        return DATABASE_URL_EMINY
    else:
        raise ValueError(f"Ambiente {env} não reconhecido!")


def get_engine_and_session(env: str = "hareware"):
    DATABASE_URL = get_database_url(env)
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return engine, SessionLocal


Base = declarative_base()


def get_db(env: str = "hareware"):
    engine, SessionLocal = get_engine_and_session(env)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
