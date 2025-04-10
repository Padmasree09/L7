"""
Database initialization script.

This module creates database tables and populates them with default data.
"""

from expense_tracker.db.models import Base, Category, User
from expense_tracker.db.session import engine, get_db_session

DEFAULT_CATEGORIES = [
    {"name": "Food", "description": "Groceries, restaurants, and food delivery", "is_default": True},
    {"name": "Transport", "description": "Public transport, taxis, and fuel", "is_default": True},
    {"name": "Entertainment", "description": "Movies, events, and other leisure activities", "is_default": True},
    {"name": "Housing", "description": "Rent, mortgage, and home maintenance", "is_default": True},
    {"name": "Utilities", "description": "Electricity, water, and internet bills", "is_default": True},
    {"name": "Healthcare", "description": "Medical expenses and health insurance", "is_default": True},
    {"name": "Shopping", "description": "Clothing, electronics, and other retail purchases", "is_default": True},
    {"name": "Personal", "description": "Personal care and miscellaneous expenses", "is_default": True},
]


def create_tables():
    """Create all database tables."""
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully.")


def populate_default_data():
    """Populate the database with default data."""
    with get_db_session() as db:
        # Check if we already have categories
        existing_categories = db.query(Category).count()
        if existing_categories == 0:
            # Add default categories
            for category_data in DEFAULT_CATEGORIES:
                category = Category(**category_data)
                db.add(category)
            
            # Add a default user for testing
            default_user = User(
                username="demo",
                email="demo@example.com"
            )
            db.add(default_user)
            
            db.commit()
            print("Default data added successfully.")
        else:
            print("Database already contains data, skipping default data creation.")


def init_db():
    """Initialize the database."""
    create_tables()
    populate_default_data()


if __name__ == "__main__":
    init_db()
    print("Database initialization complete.") 