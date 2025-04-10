"""
Database models for the expense tracker application.
"""

from datetime import datetime
from typing import List, Optional
from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey, Boolean, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

# Many-to-many relationship for group expenses
expense_participant = Table(
    'expense_participant',
    Base.metadata,
    Column('expense_id', Integer, ForeignKey('expenses.id')),
    Column('user_id', Integer, ForeignKey('users.id'))
)

class User(Base):
    """User model for storing user details."""
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    expenses = relationship("Expense", back_populates="user")
    budgets = relationship("Budget", back_populates="user")
    shared_expenses = relationship(
        "Expense", 
        secondary=expense_participant,
        back_populates="participants"
    )
    
    def __repr__(self):
        return f"<User(username={self.username}, email={self.email})>"


class Category(Base):
    """Category model for expense categorization."""
    __tablename__ = 'categories'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(String(200))
    is_default = Column(Boolean, default=False)
    
    # Relationships
    expenses = relationship("Expense", back_populates="category")
    budgets = relationship("Budget", back_populates="category")
    
    def __repr__(self):
        return f"<Category(name={self.name})>"


class Expense(Base):
    """Expense model for storing expense data."""
    __tablename__ = 'expenses'
    
    id = Column(Integer, primary_key=True)
    amount = Column(Float, nullable=False)
    description = Column(String(200))
    date = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Foreign keys
    user_id = Column(Integer, ForeignKey('users.id'))
    category_id = Column(Integer, ForeignKey('categories.id'))
    
    # Relationships
    user = relationship("User", back_populates="expenses")
    category = relationship("Category", back_populates="expenses")
    participants = relationship(
        "User",
        secondary=expense_participant,
        back_populates="shared_expenses"
    )
    
    # For group expenses
    is_group_expense = Column(Boolean, default=False)
    total_amount = Column(Float)  # Total expense amount before splitting
    
    def __repr__(self):
        return f"<Expense(amount={self.amount}, category={self.category.name if self.category else None}, date={self.date})>"


class Budget(Base):
    """Budget model for storing budget targets."""
    __tablename__ = 'budgets'
    
    id = Column(Integer, primary_key=True)
    amount = Column(Float, nullable=False)
    month = Column(Integer, nullable=False)  # 1-12
    year = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    alert_threshold = Column(Float, default=0.8)  # Alert at 80% of budget by default
    
    # Foreign keys
    user_id = Column(Integer, ForeignKey('users.id'))
    category_id = Column(Integer, ForeignKey('categories.id'))
    
    # Relationships
    user = relationship("User", back_populates="budgets")
    category = relationship("Category", back_populates="budgets")
    
    def __repr__(self):
        return f"<Budget(category={self.category.name if self.category else None}, amount={self.amount}, month={self.month}/{self.year})>"


class Alert(Base):
    """Alert model for storing budget alerts."""
    __tablename__ = 'alerts'
    
    id = Column(Integer, primary_key=True)
    message = Column(String(200), nullable=False)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Foreign keys
    user_id = Column(Integer, ForeignKey('users.id'))
    budget_id = Column(Integer, ForeignKey('budgets.id'), nullable=True)
    
    def __repr__(self):
        return f"<Alert(message={self.message}, created_at={self.created_at})>" 