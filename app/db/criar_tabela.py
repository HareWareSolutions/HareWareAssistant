from app.db.db import get_engine_and_session, Base
from app.models import clientes, contrato

env = "hareware"

engine, SessionLocal = get_engine_and_session(env)

Base.metadata.create_all(bind=engine)
