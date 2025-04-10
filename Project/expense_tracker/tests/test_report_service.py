"""
Tests for the report service module.
"""

import unittest
from datetime import datetime
from unittest.mock import patch, MagicMock
from expense_tracker.services.report_service import ReportService


class TestReportService(unittest.TestCase):
    """Test cases for the report service."""

    def setUp(self):
        """Set up test fixtures."""
        # Mock data for testing
        self.user_id = 1
        self.month = 5
        self.year = 2023
        
        # Mock expenses
        self.mock_expenses = [
            {
                'id': 1,
                'amount': 50.00,
                'category': 'Food',
                'description': 'Groceries',
                'date': datetime(2023, 5, 10)
            },
            {
                'id': 2,
                'amount': 30.00,
                'category': 'Transport',
                'description': 'Bus ticket',
                'date': datetime(2023, 5, 15)
            },
            {
                'id': 3,
                'amount': 20.00,
                'category': 'Food',
                'description': 'Lunch',
                'date': datetime(2023, 5, 20)
            }
        ]
        
        # Mock budgets
        self.mock_budgets = [
            {
                'id': 1,
                'category': 'Food',
                'amount': 200.00,
                'month': 5,
                'year': 2023,
                'alert_threshold': 0.8
            },
            {
                'id': 2,
                'category': 'Transport',
                'amount': 100.00,
                'month': 5,
                'year': 2023,
                'alert_threshold': 0.8
            }
        ]

    @patch('expense_tracker.services.expense_service.ExpenseService.get_expenses')
    def test_generate_monthly_report(self, mock_get_expenses):
        """Test generating a monthly report."""
        mock_get_expenses.return_value = self.mock_expenses
        
        report = ReportService.generate_monthly_report(
            month=self.month,
            year=self.year,
            user_id=self.user_id
        )
        
        # Verify the report structure
        self.assertIn('month', report)
        self.assertIn('year', report)
        self.assertIn('categories', report)
        self.assertIn('total', report)
        
        # Verify the totals
        self.assertEqual(report['total'], 100.00)
        
        # Verify category breakdown
        categories = {c['name']: c['amount'] for c in report['categories']}
        self.assertEqual(categories['Food'], 70.00)
        self.assertEqual(categories['Transport'], 30.00)
        
        # Verify the expense service was called with correct parameters
        mock_get_expenses.assert_called_once()

    @patch('expense_tracker.services.expense_service.ExpenseService.get_expenses')
    @patch('expense_tracker.services.budget_service.BudgetService.get_budgets')
    def test_generate_category_report(self, mock_get_budgets, mock_get_expenses):
        """Test generating a category comparison report."""
        mock_get_expenses.return_value = self.mock_expenses
        mock_get_budgets.return_value = self.mock_budgets
        
        report = ReportService.generate_category_report(
            month=self.month,
            year=self.year,
            user_id=self.user_id
        )
        
        # Verify the report structure
        self.assertIn('month', report)
        self.assertIn('year', report)
        self.assertIn('categories', report)
        self.assertIn('total_budget', report)
        self.assertIn('total_spent', report)
        
        # Verify the totals
        self.assertEqual(report['total_budget'], 300.00)
        self.assertEqual(report['total_spent'], 100.00)
        
        # Verify category details
        for category in report['categories']:
            if category['name'] == 'Food':
                self.assertEqual(category['budget'], 200.00)
                self.assertEqual(category['spent'], 70.00)
                self.assertEqual(category['remaining'], 130.00)
                self.assertEqual(category['percentage'], 35.0)
            elif category['name'] == 'Transport':
                self.assertEqual(category['budget'], 100.00)
                self.assertEqual(category['spent'], 30.00)
                self.assertEqual(category['remaining'], 70.00)
                self.assertEqual(category['percentage'], 30.0)
                
        # Verify the service calls
        mock_get_expenses.assert_called_once()
        mock_get_budgets.assert_called_once()

    @patch('expense_tracker.services.expense_service.ExpenseService.get_expenses')
    def test_generate_annual_report(self, mock_get_expenses):
        """Test generating an annual report."""
        # Mock data for annual report
        annual_expenses = self.mock_expenses.copy()
        # Add some expenses from different months
        annual_expenses.append({
            'id': 4,
            'amount': 40.00,
            'category': 'Food',
            'description': 'Dinner',
            'date': datetime(2023, 6, 5)
        })
        annual_expenses.append({
            'id': 5,
            'amount': 25.00,
            'category': 'Transport',
            'description': 'Taxi',
            'date': datetime(2023, 4, 20)
        })
        
        mock_get_expenses.return_value = annual_expenses
        
        report = ReportService.generate_annual_report(
            year=self.year,
            user_id=self.user_id
        )
        
        # Verify the report structure
        self.assertIn('year', report)
        self.assertIn('months', report)
        self.assertIn('categories', report)
        self.assertIn('total', report)
        
        # Verify the total
        self.assertEqual(report['total'], 165.00)
        
        # Verify month breakdown
        april_total = 0
        may_total = 0
        june_total = 0
        
        for month in report['months']:
            if month['month'] == 4:
                april_total = month['amount']
            elif month['month'] == 5:
                may_total = month['amount']
            elif month['month'] == 6:
                june_total = month['amount']
        
        self.assertEqual(april_total, 25.00)
        self.assertEqual(may_total, 100.00)
        self.assertEqual(june_total, 40.00)
        
        # Verify category breakdown
        food_total = 0
        transport_total = 0
        
        for category in report['categories']:
            if category['name'] == 'Food':
                food_total = category['amount']
            elif category['name'] == 'Transport':
                transport_total = category['amount']
        
        self.assertEqual(food_total, 110.00)
        self.assertEqual(transport_total, 55.00)
        
        # Verify the expense service was called
        mock_get_expenses.assert_called_once()


if __name__ == '__main__':
    unittest.main() 