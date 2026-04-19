from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Use standard sync sqlite for simplicity
SQLALCHEMY_DATABASE_URL = "sqlite:///./medscan.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    """Dependency to get the DB session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
