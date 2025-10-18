from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from processor.config.settings import DB_URL

engine = create_engine(DB_URL, echo=False, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
