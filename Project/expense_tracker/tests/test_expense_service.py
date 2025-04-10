"""
Tests for the expense service module.
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

from expense_tracker.services.expense_service import ExpenseService
from expense_tracker.utils.validators import ValidationError


class TestExpenseService:
    """Test class for ExpenseService."""
    
    def test_add_expense_valid(self):
        """Test adding a valid expense."""
        # Mock the database session
        with patch('expense_tracker.services.expense_service.get_db_session') as mock_session:
            # Setup the mock
            mock_db = MagicMock()
            mock_session.return_value.__enter__.return_value = mock_db
            
            # Mock the category
            mock_category = MagicMock()
            mock_category.id = 1
            mock_category.name = "Food"
            mock_db.query().filter().first.return_value = mock_category
            
            # Mock the expense
            mock_expense = MagicMock()
            mock_expense.id = 1
            mock_expense.amount = 25.50
            mock_expense.description = "Lunch"
            mock_expense.date = datetime.now()
            mock_expense.category = mock_category
            mock_expense.is_group_expense = False
            
            # Setup the db.add to set the mock_expense attributes
            def mock_add(expense):
                expense.id = 1
                expense.amount = 25.50
                expense.category = mock_category
                return None
            
            mock_db.add.side_effect = mock_add
            
            # Call the method
            result = ExpenseService.add_expense(
                amount=25.50,
                category_name="Food",
                description="Lunch"
            )
            
            # Assertions
            assert result['id'] == 1
            assert result['amount'] == 25.50
            assert result['category'] == "Food"
            assert mock_db.add.called
            assert mock_db.commit.called
    
    def test_add_expense_invalid_amount(self):
        """Test adding an expense with invalid amount."""
        # Attempt to add expense with negative amount
        with pytest.raises(ValidationError) as excinfo:
            ExpenseService.add_expense(
                amount=-25.50,
                category_name="Food",
                description="Lunch"
            )
        
        assert "must be greater than zero" in str(excinfo.value)
    
    def test_get_expenses(self):
        """Test getting expenses."""
        # Mock the database session
        with patch('expense_tracker.services.expense_service.get_db_session') as mock_session:
            # Setup the mock
            mock_db = MagicMock()
            mock_session.return_value.__enter__.return_value = mock_db
            
            # Create mock expenses
            mock_expense1 = MagicMock()
            mock_expense1.id = 1
            mock_expense1.amount = 25.50
            mock_expense1.description = "Lunch"
            mock_expense1.date = datetime.now()
            mock_expense1.is_group_expense = False
            
            mock_category1 = MagicMock()
            mock_category1.name = "Food"
            mock_expense1.category = mock_category1
            
            mock_expense2 = MagicMock()
            mock_expense2.id = 2
            mock_expense2.amount = 35.00
            mock_expense2.description = "Dinner"
            mock_expense2.date = datetime.now() - timedelta(days=1)
            mock_expense2.is_group_expense = False
            
            mock_category2 = MagicMock()
            mock_category2.name = "Food"
            mock_expense2.category = mock_category2
            
            # Setup mock query result
            mock_query = MagicMock()
            mock_query.join().filter.return_value = mock_query
            mock_query.order_by().all.return_value = [mock_expense1, mock_expense2]
            mock_db.query.return_value = mock_query
            
            # Call the method
            result = ExpenseService.get_expenses()
            
            # Assertions
            assert len(result) == 2
            assert result[0]['id'] == 1
            assert result[0]['amount'] == 25.50
            assert result[0]['category'] == "Food"
            assert result[1]['id'] == 2
            assert result[1]['amount'] == 35.00
    
    def test_delete_expense(self):
        """Test deleting an expense."""
        # Mock the database session
        with patch('expense_tracker.services.expense_service.get_db_session') as mock_session:
            # Setup the mock
            mock_db = MagicMock()
            mock_session.return_value.__enter__.return_value = mock_db
            
            # Mock the expense
            mock_expense = MagicMock()
            mock_expense.id = 1
            mock_db.query().filter().first.return_value = mock_expense
            
            # Call the method
            result = ExpenseService.delete_expense(1)
            
            # Assertions
            assert result is True
            assert mock_db.delete.called
            assert mock_db.commit.called
    
    def test_delete_expense_not_found(self):
        """Test deleting a non-existent expense."""
        # Mock the database session
        with patch('expense_tracker.services.expense_service.get_db_session') as mock_session:
            # Setup the mock
            mock_db = MagicMock()
            mock_session.return_value.__enter__.return_value = mock_db
            
            # Mock the query to return None (expense not found)
            mock_db.query().filter().first.return_value = None
            
            # Call the method
            result = ExpenseService.delete_expense(999)
            
            # Assertions
            assert result is False
            assert not mock_db.delete.called
            assert not mock_db.commit.called 