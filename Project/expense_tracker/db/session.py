"""
Database session management for the expense tracker application.
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base

from expense_tracker.db.models import Base

# Get database path from environment or use default
DB_PATH = os.environ.get('EXPENSE_TRACKER_DB', 'sqlite:///expense_tracker.db')

# Create the SQLAlchemy engine
engine = create_engine(DB_PATH, connect_args={"check_same_thread": False})

# Create a session factory
session_factory = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create a scoped session for thread safety
SessionLocal = scoped_session(session_factory)

def get_db():
    """Get a database session.
    
    Yields:
        SQLAlchemy Session: Database session
        
    Example:
        with get_db() as db:
            result = db.query(User).all()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
# Function to get a new session for use in a with statement
def get_db_session():
    """Get a database session for use in a with statement.
    
    Returns:
        SQLAlchemy Session: Database session
        
    Example:
        with get_db_session() as db:
            result = db.query(User).all()
    """
    db = SessionLocal()
    try:
        return db
    except Exception:
        db.close()
        raise 