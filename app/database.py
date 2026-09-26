from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

# Default to a local postgres url if env var not set, for development convenience
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost/tartuca_db")

# Normalize postgres:// to postgresql:// if needed (e.g. from Heroku/Railway/Render)
if SQLALCHEMY_DATABASE_URL and SQLALCHEMY_DATABASE_URL.startswith("postgres://"):
    SQLALCHEMY_DATABASE_URL = SQLALCHEMY_DATABASE_URL.replace("postgres://", "postgresql://", 1)

# Detect installed PostgreSQL drivers
has_psycopg = False
try:
    import psycopg  # psycopg 3
    has_psycopg = True
except ImportError:
    pass

has_psycopg2 = False
try:
    import psycopg2  # psycopg 2
    has_psycopg2 = True
except ImportError:
    pass

# Ensure dialect matches available driver
if SQLALCHEMY_DATABASE_URL:
    if "postgresql+psycopg://" in SQLALCHEMY_DATABASE_URL and not has_psycopg and has_psycopg2:
        SQLALCHEMY_DATABASE_URL = SQLALCHEMY_DATABASE_URL.replace("postgresql+psycopg://", "postgresql+psycopg2://", 1)
    elif "postgresql+psycopg2://" in SQLALCHEMY_DATABASE_URL and not has_psycopg2 and has_psycopg:
        SQLALCHEMY_DATABASE_URL = SQLALCHEMY_DATABASE_URL.replace("postgresql+psycopg2://", "postgresql+psycopg://", 1)
    elif SQLALCHEMY_DATABASE_URL.startswith("postgresql://") and not ("+psycopg" in SQLALCHEMY_DATABASE_URL):
        if has_psycopg:
            SQLALCHEMY_DATABASE_URL = SQLALCHEMY_DATABASE_URL.replace("postgresql://", "postgresql+psycopg://", 1)
        elif has_psycopg2:
            SQLALCHEMY_DATABASE_URL = SQLALCHEMY_DATABASE_URL.replace("postgresql://", "postgresql+psycopg2://", 1)

engine = create_engine(
    SQLALCHEMY_DATABASE_URL
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
