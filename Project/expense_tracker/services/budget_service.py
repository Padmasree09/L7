"""
Budget service module for managing budgets and alerts.
"""

from datetime import datetime
from typing import List, Dict, Any, Optional, Union
from sqlalchemy.orm import Session

from expense_tracker.db.models import Budget, Category, Expense, Alert
from expense_tracker.db.session import get_db_session
from expense_tracker.utils.validators import (
    validate_amount, validate_month_year, validate_threshold
)


class BudgetService:
    """Service class for budget management."""
    
    @staticmethod
    def set_budget(
        category_name: str,
        amount: Union[float, str],
        month: int,
        year: int,
        user_id: int = 1,
        alert_threshold: float = 0.8
    ) -> Dict[str, Any]:
        """Set a budget for a category and month.
        
        Args:
            category_name: Category name
            amount: Budget amount
            month: Month number (1-12)
            year: Year
            user_id: User ID
            alert_threshold: Alert threshold (0.0-1.0)
            
        Returns:
            Dict containing the created budget details
            
        Raises:
            ValueError: If validation fails or data is invalid
        """
        # Validate inputs
        amount_float = validate_amount(amount)
        date_params = validate_month_year(month, year)
        month = date_params["month"]
        year = date_params["year"]
        threshold = validate_threshold(alert_threshold)
        
        with get_db_session() as db:
            # Get or create category
            category = db.query(Category).filter(Category.name == category_name).first()
            if not category:
                # Create new category if it doesn't exist
                category = Category(name=category_name)
                db.add(category)
                db.flush()
            
            # Check if budget already exists
            existing_budget = db.query(Budget).filter(
                Budget.user_id == user_id,
                Budget.category_id == category.id,
                Budget.month == month,
                Budget.year == year
            ).first()
            
            if existing_budget:
                # Update existing budget
                existing_budget.amount = amount_float
                existing_budget.alert_threshold = threshold
                budget = existing_budget
            else:
                # Create new budget
                budget = Budget(
                    amount=amount_float,
                    month=month,
                    year=year,
                    user_id=user_id,
                    category_id=category.id,
                    alert_threshold=threshold
                )
                db.add(budget)
            
            db.commit()
            
            # Return budget as dictionary
            return {
                'id': budget.id,
                'amount': budget.amount,
                'month': budget.month,
                'year': budget.year,
                'category': category.name,
                'alert_threshold': budget.alert_threshold
            }
    
    @staticmethod
    def get_budgets(
        month: Optional[int] = None,
        year: Optional[int] = None,
        category_name: Optional[str] = None,
        user_id: int = 1
    ) -> List[Dict[str, Any]]:
        """Get budgets with optional filtering.
        
        Args:
            month: Filter by month
            year: Filter by year
            category_name: Filter by category name
            user_id: User ID
            
        Returns:
            List of budget dictionaries
        """
        with get_db_session() as db:
            # Start with base query
            query = db.query(Budget).join(Category).filter(Budget.user_id == user_id)
            
            # Apply filters
            if month is not None:
                query = query.filter(Budget.month == month)
            
            if year is not None:
                query = query.filter(Budget.year == year)
            
            if category_name:
                query = query.filter(Category.name == category_name)
            
            # Execute query and return results
            budgets = query.order_by(Budget.year.desc(), Budget.month.desc()).all()
            
            return [
                {
                    'id': budget.id,
                    'amount': budget.amount,
                    'month': budget.month,
                    'year': budget.year,
                    'category': budget.category.name,
                    'alert_threshold': budget.alert_threshold
                }
                for budget in budgets
            ]
    
    @staticmethod
    def get_budget_status(
        month: int,
        year: int,
        user_id: int = 1
    ) -> List[Dict[str, Any]]:
        """Get budget status for all categories in a specific month.
        
        Args:
            month: Month number (1-12)
            year: Year
            user_id: User ID
            
        Returns:
            List of dictionaries with budget status info
        """
        # Get date range for the month
        start_date = datetime(year, month, 1)
        if month == 12:
            end_date = datetime(year + 1, 1, 1)
        else:
            end_date = datetime(year, month + 1, 1)
        
        with get_db_session() as db:
            # Get all budgets for the month
            budgets = db.query(Budget).join(Category).filter(
                Budget.user_id == user_id,
                Budget.month == month,
                Budget.year == year
            ).all()
            
            # Get expense totals for each category
            result = []
            for budget in budgets:
                # Get expenses for this category and month
                expenses = db.query(Expense).filter(
                    Expense.user_id == user_id,
                    Expense.category_id == budget.category_id,
                    Expense.date >= start_date,
                    Expense.date < end_date
                ).all()
                
                # Calculate total expenses
                total_expenses = sum(expense.amount for expense in expenses)
                
                # Calculate percentage of budget used
                percentage_used = total_expenses / budget.amount if budget.amount > 0 else 0
                
                # Add to result
                result.append({
                    'category': budget.category.name,
                    'budget': budget.amount,
                    'spent': total_expenses,
                    'remaining': budget.amount - total_expenses,
                    'percentage_used': percentage_used,
                    'alert_threshold': budget.alert_threshold,
                    'alert': percentage_used >= budget.alert_threshold
                })
            
            return result
    
    @staticmethod
    def check_budget_alerts(user_id: int = 1) -> List[Dict[str, Any]]:
        """Check all budgets for alerts.
        
        Args:
            user_id: User ID
            
        Returns:
            List of alert dictionaries
        """
        # Get current month and year
        now = datetime.now()
        month = now.month
        year = now.year
        
        # Get budget status
        budget_status = BudgetService.get_budget_status(month, year, user_id)
        
        alerts = []
        with get_db_session() as db:
            for status in budget_status:
                if status['alert']:
                    # Create alert message
                    percentage = status['percentage_used'] * 100
                    if status['percentage_used'] >= 1.0:
                        message = f"ALERT: Budget for {status['category']} exceeded! " \
                                f"(${status['spent']:.2f} / ${status['budget']:.2f}, {percentage:.1f}%)"
                    else:
                        remaining_percent = 100 - percentage
                        message = f"WARNING: Only {remaining_percent:.1f}% of budget for " \
                                f"{status['category']} remaining " \
                                f"(${status['remaining']:.2f} / ${status['budget']:.2f})"
                    
                    # Get budget ID
                    budget = db.query(Budget).join(Category).filter(
                        Budget.user_id == user_id,
                        Budget.month == month,
                        Budget.year == year,
                        Category.name == status['category']
                    ).first()
                    
                    # Create alert
                    alert = Alert(
                        message=message,
                        user_id=user_id,
                        budget_id=budget.id if budget else None
                    )
                    db.add(alert)
                    
                    alerts.append({
                        'category': status['category'],
                        'message': message,
                        'percentage_used': status['percentage_used'],
                        'spent': status['spent'],
                        'budget': status['budget']
                    })
            
            if alerts:
                db.commit()
            
            return alerts
    
    @staticmethod
    def delete_budget(budget_id: int, user_id: int = 1) -> bool:
        """Delete a budget.
        
        Args:
            budget_id: ID of the budget to delete
            user_id: User ID for verification
            
        Returns:
            bool: True if deleted successfully, False otherwise
        """
        with get_db_session() as db:
            budget = db.query(Budget).filter(
                Budget.id == budget_id,
                Budget.user_id == user_id
            ).first()
            
            if not budget:
                return False
            
            db.delete(budget)
            db.commit()
            return True 