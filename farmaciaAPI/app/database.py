# app/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Ajuste com seus dados reais
DATABASE_URL = "postgresql+psycopg2://farmacia_user:senha_forte@localhost:5432/farmacia_prescricao"

engine = create_engine(DATABASE_URL, echo=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


# Dependência para injetar sessão de banco nas rotas
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
