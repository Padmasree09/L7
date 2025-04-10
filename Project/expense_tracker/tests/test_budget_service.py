"""
Tests for the budget service module.
"""

import pytest
from datetime import datetime
from unittest.mock import patch, MagicMock

from expense_tracker.services.budget_service import BudgetService
from expense_tracker.utils.validators import ValidationError


class TestBudgetService:
    """Test class for BudgetService."""
    
    def test_set_budget_valid(self):
        """Test setting a valid budget."""
        # Mock the database session
        with patch('expense_tracker.services.budget_service.get_db_session') as mock_session:
            # Setup the mock
            mock_db = MagicMock()
            mock_session.return_value.__enter__.return_value = mock_db
            
            # Mock the category
            mock_category = MagicMock()
            mock_category.id = 1
            mock_category.name = "Food"
            mock_db.query().filter().first.return_value = mock_category
            
            # Mock the budget
            mock_budget = MagicMock()
            mock_budget.id = 1
            mock_budget.amount = 300.00
            mock_budget.month = 5
            mock_budget.year = 2023
            mock_budget.category = mock_category
            mock_budget.alert_threshold = 0.8
            
            # Setup the db.add to set the mock_budget attributes
            def mock_add(budget):
                budget.id = 1
                budget.amount = 300.00
                budget.category = mock_category
                return None
            
            mock_db.add.side_effect = mock_add
            
            # Call the method
            result = BudgetService.set_budget(
                category_name="Food",
                amount=300.00,
                month=5,
                year=2023
            )
            
            # Assertions
            assert result['id'] == 1
            assert result['amount'] == 300.00
            assert result['category'] == "Food"
            assert result['month'] == 5
            assert result['year'] == 2023
            assert mock_db.add.called
            assert mock_db.commit.called
    
    def test_set_budget_invalid_amount(self):
        """Test setting a budget with invalid amount."""
        # Attempt to set budget with negative amount
        with pytest.raises(ValidationError) as excinfo:
            BudgetService.set_budget(
                category_name="Food",
                amount=-300.00,
                month=5,
                year=2023
            )
        
        assert "must be greater than zero" in str(excinfo.value)
    
    def test_set_budget_invalid_month(self):
        """Test setting a budget with invalid month."""
        # Attempt to set budget with invalid month
        with pytest.raises(ValidationError) as excinfo:
            BudgetService.set_budget(
                category_name="Food",
                amount=300.00,
                month=13,
                year=2023
            )
        
        assert "Month must be between 1 and 12" in str(excinfo.value)
    
    def test_get_budgets(self):
        """Test getting budgets."""
        # Mock the database session
        with patch('expense_tracker.services.budget_service.get_db_session') as mock_session:
            # Setup the mock
            mock_db = MagicMock()
            mock_session.return_value.__enter__.return_value = mock_db
            
            # Create mock budgets
            mock_budget1 = MagicMock()
            mock_budget1.id = 1
            mock_budget1.amount = 300.00
            mock_budget1.month = 5
            mock_budget1.year = 2023
            mock_budget1.alert_threshold = 0.8
            
            mock_category1 = MagicMock()
            mock_category1.name = "Food"
            mock_budget1.category = mock_category1
            
            mock_budget2 = MagicMock()
            mock_budget2.id = 2
            mock_budget2.amount = 150.00
            mock_budget2.month = 5
            mock_budget2.year = 2023
            mock_budget2.alert_threshold = 0.8
            
            mock_category2 = MagicMock()
            mock_category2.name = "Transport"
            mock_budget2.category = mock_category2
            
            # Setup mock query result
            mock_query = MagicMock()
            mock_query.join().filter.return_value = mock_query
            mock_query.order_by().all.return_value = [mock_budget1, mock_budget2]
            mock_db.query.return_value = mock_query
            
            # Call the method
            result = BudgetService.get_budgets(month=5, year=2023)
            
            # Assertions
            assert len(result) == 2
            assert result[0]['id'] == 1
            assert result[0]['amount'] == 300.00
            assert result[0]['category'] == "Food"
            assert result[1]['id'] == 2
            assert result[1]['amount'] == 150.00
            assert result[1]['category'] == "Transport"
    
    def test_get_budget_status(self):
        """Test getting budget status."""
        # Mock the database session
        with patch('expense_tracker.services.budget_service.get_db_session') as mock_session:
            # Setup the mock
            mock_db = MagicMock()
            mock_session.return_value.__enter__.return_value = mock_db
            
            # Create mock budget and category
            mock_budget = MagicMock()
            mock_budget.id = 1
            mock_budget.amount = 300.00
            mock_budget.month = 5
            mock_budget.year = 2023
            mock_budget.alert_threshold = 0.8
            mock_budget.category_id = 1
            
            mock_category = MagicMock()
            mock_category.id = 1
            mock_category.name = "Food"
            mock_budget.category = mock_category
            
            # Create mock expenses
            mock_expense1 = MagicMock()
            mock_expense1.amount = 75.00
            
            mock_expense2 = MagicMock()
            mock_expense2.amount = 50.00
            
            # Setup mock query results
            mock_db.query().join().filter().all.return_value = [mock_budget]
            mock_db.query().filter().all.return_value = [mock_expense1, mock_expense2]
            
            # Call the method
            result = BudgetService.get_budget_status(month=5, year=2023)
            
            # Assertions
            assert len(result) == 1
            assert result[0]['category'] == "Food"
            assert result[0]['budget'] == 300.00
            assert result[0]['spent'] == 125.00  # 75.00 + 50.00
            assert result[0]['remaining'] == 175.00  # 300.00 - 125.00
            assert result[0]['percentage_used'] == 125.00 / 300.00
            assert result[0]['alert'] is False  # 125/300 < 0.8 threshold
    
    def test_delete_budget(self):
        """Test deleting a budget."""
        # Mock the database session
        with patch('expense_tracker.services.budget_service.get_db_session') as mock_session:
            # Setup the mock
            mock_db = MagicMock()
            mock_session.return_value.__enter__.return_value = mock_db
            
            # Mock the budget
            mock_budget = MagicMock()
            mock_budget.id = 1
            mock_db.query().filter().first.return_value = mock_budget
            
            # Call the method
            result = BudgetService.delete_budget(1)
            
            # Assertions
            assert result is True
            assert mock_db.delete.called
            assert mock_db.commit.called 