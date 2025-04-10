"""
Expense service module for adding, retrieving, and managing expenses.
"""

from datetime import datetime
from typing import List, Dict, Any, Optional, Union
from sqlalchemy.orm import Session

from expense_tracker.db.models import Expense, Category, User
from expense_tracker.db.session import get_db_session
from expense_tracker.utils.validators import (
    validate_amount, validate_date, validate_string
)


class ExpenseService:
    """Service class for expense management."""
    
    @staticmethod
    def add_expense(
        amount: Union[float, str],
        category_name: str,
        description: Optional[str] = None,
        date_str: Optional[str] = None,
        user_id: int = 1,  # Default to first user
        is_group_expense: bool = False,
        participant_ids: Optional[List[int]] = None
    ) -> Dict[str, Any]:
        """Add a new expense.
        
        Args:
            amount: Expense amount
            category_name: Category name
            description: Optional description
            date_str: Date string (YYYY-MM-DD)
            user_id: User ID (defaults to 1)
            is_group_expense: Whether this is a group expense
            participant_ids: List of participant user IDs
            
        Returns:
            Dict containing the created expense details
            
        Raises:
            ValueError: If validation fails or data is invalid
        """
        # Validate inputs
        amount_float = validate_amount(amount)
        date_obj = validate_date(date_str)
        if description:
            description = validate_string(description, "description")
        
        with get_db_session() as db:
            # Get or create category
            category = db.query(Category).filter(Category.name == category_name).first()
            if not category:
                # Create new category if it doesn't exist
                category = Category(name=category_name)
                db.add(category)
                db.flush()
            
            # Create expense
            expense = Expense(
                amount=amount_float,
                description=description,
                date=date_obj,
                user_id=user_id,
                category_id=category.id,
                is_group_expense=is_group_expense,
                total_amount=amount_float if is_group_expense else None
            )
            db.add(expense)
            
            # Add participants for group expenses
            if is_group_expense and participant_ids:
                participants = db.query(User).filter(User.id.in_(participant_ids)).all()
                expense.participants.extend(participants)
            
            db.commit()
            
            # Return expense as dictionary
            return {
                'id': expense.id,
                'amount': expense.amount,
                'description': expense.description,
                'date': expense.date,
                'category': category.name,
                'is_group_expense': expense.is_group_expense
            }
    
    @staticmethod
    def get_expenses(
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        category_name: Optional[str] = None,
        user_id: int = 1
    ) -> List[Dict[str, Any]]:
        """Get expenses with optional filtering.
        
        Args:
            start_date: Start date string (YYYY-MM-DD)
            end_date: End date string (YYYY-MM-DD)
            category_name: Filter by category name
            user_id: User ID
            
        Returns:
            List of expense dictionaries
        """
        # Validate dates if provided
        start_date_obj = validate_date(start_date, "start_date") if start_date else None
        end_date_obj = validate_date(end_date, "end_date") if end_date else None
        
        with get_db_session() as db:
            # Start with base query
            query = db.query(Expense).join(Category).filter(Expense.user_id == user_id)
            
            # Apply filters
            if start_date_obj:
                query = query.filter(Expense.date >= start_date_obj)
            
            if end_date_obj:
                query = query.filter(Expense.date <= end_date_obj)
            
            if category_name:
                query = query.filter(Category.name == category_name)
            
            # Execute query and return results
            expenses = query.order_by(Expense.date.desc()).all()
            
            return [
                {
                    'id': expense.id,
                    'amount': expense.amount,
                    'description': expense.description,
                    'date': expense.date,
                    'category': expense.category.name,
                    'is_group_expense': expense.is_group_expense
                }
                for expense in expenses
            ]
    
    @staticmethod
    def get_expense_totals_by_category(
        month: int,
        year: int,
        user_id: int = 1
    ) -> List[Dict[str, Any]]:
        """Get total expenses by category for a specific month.
        
        Args:
            month: Month number (1-12)
            year: Year
            user_id: User ID
            
        Returns:
            List of dictionaries with category and total amount
        """
        start_date = datetime(year, month, 1)
        if month == 12:
            end_date = datetime(year + 1, 1, 1)
        else:
            end_date = datetime(year, month + 1, 1)
        
        with get_db_session() as db:
            expenses = db.query(Expense).join(Category).filter(
                Expense.user_id == user_id,
                Expense.date >= start_date,
                Expense.date < end_date
            ).all()
            
            # Group by category
            category_totals = {}
            for expense in expenses:
                category_name = expense.category.name
                if category_name not in category_totals:
                    category_totals[category_name] = 0
                category_totals[category_name] += expense.amount
            
            # Convert to list of dictionaries
            return [
                {'category': category, 'total': amount}
                for category, amount in category_totals.items()
            ]
    
    @staticmethod
    def get_expense_totals_by_month(
        year: int,
        user_id: int = 1
    ) -> List[Dict[str, Any]]:
        """Get total expenses by month for a specific year.
        
        Args:
            year: Year
            user_id: User ID
            
        Returns:
            List of dictionaries with month and total amount
        """
        with get_db_session() as db:
            # Get all expenses for the year
            start_date = datetime(year, 1, 1)
            end_date = datetime(year + 1, 1, 1)
            
            expenses = db.query(Expense).filter(
                Expense.user_id == user_id,
                Expense.date >= start_date,
                Expense.date < end_date
            ).all()
            
            # Group by month
            month_totals = {month: 0 for month in range(1, 13)}
            for expense in expenses:
                month = expense.date.month
                month_totals[month] += expense.amount
            
            # Convert to list of dictionaries
            return [
                {'month': month, 'total': amount}
                for month, amount in month_totals.items()
            ]
            
    @staticmethod
    def delete_expense(expense_id: int, user_id: int = 1) -> bool:
        """Delete an expense.
        
        Args:
            expense_id: ID of the expense to delete
            user_id: User ID for verification
            
        Returns:
            bool: True if deleted successfully, False otherwise
        """
        with get_db_session() as db:
            expense = db.query(Expense).filter(
                Expense.id == expense_id,
                Expense.user_id == user_id
            ).first()
            
            if not expense:
                return False
            
            db.delete(expense)
            db.commit()
            return True 