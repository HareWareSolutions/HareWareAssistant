import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base


DATABASE_URL_HAREWARE = "postgresql+pg8000://postgres:HareWare%402025@localhost/HareWareAssistant"
DATABASE_URL_MMANIA = "postgresql+pg8000://postgres:HareWare%402025@localhost/mmaniadeboloAssistant"


def get_database_url(env: str = "hareware"):
    if env == "hareware":
        return DATABASE_URL_HAREWARE
    elif env == "mmania":
        return DATABASE_URL_MMANIA
    else:
        raise ValueError(f"Ambiente {env} não reconhecido! Use 'hareware' ou 'mmania'.")


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
