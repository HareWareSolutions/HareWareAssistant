from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from contextlib import asynccontextmanager

DATABASE_URL_HAREWARE = "postgresql+asyncpg://hareware:HareWare402025@localhost/harewareassistant"
DATABASE_URL_MMANIA = "postgresql+asyncpg://hareware:HareWare402025@localhost/mmaniadeboloassistant"
DATABASE_URL_HWADMIN = "postgresql+asyncpg://hareware:HareWare402025@localhost/hareware"
DATABASE_URL_MALAMAN = "postgresql+asyncpg://hareware:HareWare402025@localhost/malamanassistant"
DATABASE_URL_EMINY = "postgresql+asyncpg://hareware:HareWare402025@localhost/eminyassistant"


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
    engine = create_async_engine(DATABASE_URL, echo=True)
    SessionLocal = sessionmaker(
        engine, class_=AsyncSession, autocommit=False, autoflush=False
    )
    return engine, SessionLocal


Base = declarative_base()


@asynccontextmanager
async def get_db(env: str = "hareware"):
    engine, SessionLocal = get_engine_and_session(env)
    async with SessionLocal() as db:
        try:
            yield db
            await db.commit()
        except Exception as e:
            await db.rollback()
            raise e
        finally:
            await db.close()
