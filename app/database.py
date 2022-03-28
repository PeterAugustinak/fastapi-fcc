from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .config import settings

username = settings.database_username
password = settings.database_password
host = settings.database_hostname
port = settings.database_port
name = settings.database_name

SQLALCHEMY_DATABASE_URL = \
    f"postgresql://{username}:{password}@{host}:{port}/{name}"

engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
