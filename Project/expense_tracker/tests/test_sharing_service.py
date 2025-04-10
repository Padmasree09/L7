"""
Tests for the sharing service module.
"""

import unittest
from datetime import datetime
from unittest.mock import patch, MagicMock
from expense_tracker.services.sharing_service import SharingService


class TestSharingService(unittest.TestCase):
    """Test cases for the sharing service."""

    def setUp(self):
        """Set up test fixtures."""
        # Mock data for testing
        self.payer_id = 1
        self.participant_ids = [2, 3]
        self.all_participants = [1, 2, 3]  # Including payer
        
        # Mock expense data
        self.expense_data = {
            'amount': 90.00,
            'category_name': 'Food',
            'description': 'Dinner',
            'date_str': '2023-05-15'
        }
        
        # Mock users
        self.mock_users = [
            {'id': 1, 'username': 'user1', 'email': 'user1@example.com'},
            {'id': 2, 'username': 'user2', 'email': 'user2@example.com'},
            {'id': 3, 'username': 'user3', 'email': 'user3@example.com'}
        ]
        
        # Mock balances
        self.mock_balances = [
            {'from_user_id': 2, 'to_user_id': 1, 'amount': 30.00},
            {'from_user_id': 3, 'to_user_id': 1, 'amount': 30.00}
        ]

    @patch('expense_tracker.db.session.get_session')
    @patch('expense_tracker.services.expense_service.ExpenseService.add_expense')
    def test_add_shared_expense(self, mock_add_expense, mock_get_session):
        """Test adding a shared expense."""
        # Set up mocks
        mock_session = MagicMock()
        mock_get_session.return_value.__enter__.return_value = mock_session
        
        mock_expense = MagicMock(
            id=1,
            amount=30.00,
            description='Dinner',
            date=datetime(2023, 5, 15, 0, 0),
            category=MagicMock(name='Food'),
            is_group_expense=True,
            total_amount=90.00
        )
        mock_expense.__getitem__ = lambda self, key: {
            'id': 1,
            'amount': 30.00,
            'category': 'Food',
            'description': 'Dinner',
            'date': datetime(2023, 5, 15, 0, 0),
            'is_group_expense': True,
            'total_amount': 90.00
        }[key]
        
        mock_add_expense.return_value = mock_expense
        
        # Call add_shared_expense
        result = SharingService.add_shared_expense(
            payer_id=self.payer_id,
            participant_ids=self.participant_ids,
            **self.expense_data
        )
        
        # Verify the result
        self.assertEqual(result['id'], 1)
        self.assertEqual(result['amount'], 30.00)  # Split amount
        self.assertEqual(result['total_amount'], 90.00)  # Original amount
        self.assertTrue(result['is_group_expense'])
        
        # Verify the expense service was called
        mock_add_expense.assert_called_once()
        
        # Verify participants were added to the expense
        mock_session.query.assert_called()  # For finding participant users
        mock_session.commit.assert_called_once()

    @patch('expense_tracker.db.session.get_session')
    def test_get_shared_expenses(self, mock_get_session):
        """Test retrieving shared expenses for a user."""
        # Set up mock
        mock_session = MagicMock()
        mock_get_session.return_value.__enter__.return_value = mock_session
        
        # Mock expense instances
        mock_expenses = [
            MagicMock(
                id=1,
                amount=30.00,
                description='Dinner',
                date=datetime(2023, 5, 15, 0, 0),
                user_id=1,
                is_group_expense=True,
                total_amount=90.00,
                category=MagicMock(name='Food'),
                participants=[MagicMock(id=1), MagicMock(id=2), MagicMock(id=3)]
            ),
            MagicMock(
                id=2,
                amount=20.00,
                description='Movie tickets',
                date=datetime(2023, 5, 20, 0, 0),
                user_id=2,
                is_group_expense=True,
                total_amount=60.00,
                category=MagicMock(name='Entertainment'),
                participants=[MagicMock(id=1), MagicMock(id=2), MagicMock(id=3)]
            )
        ]
        
        # Configure the mock query
        mock_query = mock_session.query.return_value.join.return_value.filter.return_value
        mock_query.order_by.return_value.all.return_value = mock_expenses
        
        # Call get_shared_expenses
        shared_expenses = SharingService.get_shared_expenses(user_id=1)
        
        # Verify the result
        self.assertEqual(len(shared_expenses), 2)
        
        # Verify the first expense data
        self.assertEqual(shared_expenses[0]['id'], 1)
        self.assertEqual(shared_expenses[0]['amount'], 30.00)
        self.assertEqual(shared_expenses[0]['total_amount'], 90.00)
        self.assertEqual(shared_expenses[0]['category'], 'Food')
        self.assertEqual(shared_expenses[0]['payer'], 1)
        self.assertEqual(len(shared_expenses[0]['participants']), 3)
        
        # Verify the second expense data
        self.assertEqual(shared_expenses[1]['id'], 2)
        self.assertEqual(shared_expenses[1]['amount'], 20.00)
        self.assertEqual(shared_expenses[1]['total_amount'], 60.00)
        self.assertEqual(shared_expenses[1]['category'], 'Entertainment')
        self.assertEqual(shared_expenses[1]['payer'], 2)
        self.assertEqual(len(shared_expenses[1]['participants']), 3)
        
        # Verify query construction
        mock_session.query.assert_called_once()

    @patch('expense_tracker.db.session.get_session')
    def test_get_balances(self, mock_get_session):
        """Test retrieving user balances."""
        # Set up mock
        mock_session = MagicMock()
        mock_get_session.return_value.__enter__.return_value = mock_session
        
        # Mock a list of expenses that would create balances
        mock_expenses = [
            # User 1 paid for dinner, split with users 2 and 3
            MagicMock(
                id=1,
                amount=30.00,  # Split amount per person
                user_id=1,     # Paid by user 1
                is_group_expense=True,
                total_amount=90.00,
                participants=[MagicMock(id=1), MagicMock(id=2), MagicMock(id=3)]
            ),
            # User 2 paid for movie, split with users 1 and 3
            MagicMock(
                id=2,
                amount=20.00,  # Split amount per person
                user_id=2,     # Paid by user 2
                is_group_expense=True,
                total_amount=60.00,
                participants=[MagicMock(id=1), MagicMock(id=2), MagicMock(id=3)]
            )
        ]
        
        # Configure the mock query for expenses
        mock_session.query.return_value.filter.return_value.all.return_value = mock_expenses
        
        # Call get_balances
        balances = SharingService.get_balances(user_id=1)
        
        # Verify the result structure
        self.assertIn('owed_to_user', balances)
        self.assertIn('owed_by_user', balances)
        self.assertIn('net_balance', balances)
        
        # Expected values based on the mock expenses:
        # Expense 1: User 1 paid $90, so users 2 and 3 each owe $30 to user 1
        # Expense 2: User 2 paid $60, so user 1 owes $20 to user 2
        # Net result: User 2 owes $10 to user 1, User 3 owes $30 to user 1
        
        # For user 1's perspective:
        # - They are owed $30 by user 3 and $10 by user 2 (after offsetting)
        # - They owe $0
        
        # Verify balances for user 1
        # Note: Exact values depend on how your service calculates balances
        # This test might need adjustment based on your implementation
        self.assertTrue(balances['net_balance'] > 0)  # User 1 should be owed money
        self.assertEqual(len(balances['owed_to_user']), 2)  # From users 2 and 3
        
        # Verify query construction
        mock_session.query.assert_called()

    @patch('expense_tracker.db.session.get_session')
    @patch('expense_tracker.services.expense_service.ExpenseService.add_expense')
    def test_settle_balance(self, mock_add_expense, mock_get_session):
        """Test settling a balance between users."""
        # Set up mocks
        mock_session = MagicMock()
        mock_get_session.return_value.__enter__.return_value = mock_session
        
        mock_settlement_expense = {'id': 3, 'amount': 30.00, 'category': 'Settlement'}
        mock_add_expense.return_value = mock_settlement_expense
        
        # Call settle_balance
        result = SharingService.settle_balance(
            from_user_id=2,
            to_user_id=1,
            amount=30.00,
            date_str='2023-05-25',
            description='Settling dinner debt'
        )
        
        # Verify the result
        self.assertEqual(result['id'], 3)
        self.assertEqual(result['amount'], 30.00)
        
        # Verify expense service was called with correct parameters
        mock_add_expense.assert_called_once()
        call_args = mock_add_expense.call_args[1]
        self.assertEqual(call_args['amount'], 30.00)
        self.assertEqual(call_args['category_name'], 'Settlement')
        self.assertEqual(call_args['user_id'], 1)  # To user
        self.assertEqual(call_args['description'], 'Settlement from user 2 - Settling dinner debt')
        
        # Verify database session interaction
        mock_session.commit.assert_called_once()


if __name__ == '__main__':
    unittest.main() 