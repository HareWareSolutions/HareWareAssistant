from app.db.db import engine, Base
from app.models import agendamento, contato, status

Base.metadata.create_all(bind=engine)
