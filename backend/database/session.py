"""
Database session management and configuration.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from backend.config.settings import settings

# Create SQLAlchemy engine
engine = create_engine(
    settings.sqlalchemy_database_uri,
    pool_pre_ping=True, # Verify connection before usage
    echo=(settings.APP_ENV == "development")
)

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for SQLAlchemy declarative models
Base = declarative_base()
