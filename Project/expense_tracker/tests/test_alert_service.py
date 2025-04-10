"""
Tests for the alert service module.
"""

import unittest
from datetime import datetime
from unittest.mock import patch, MagicMock
from expense_tracker.services.alert_service import AlertService


class TestAlertService(unittest.TestCase):
    """Test cases for the alert service."""

    def setUp(self):
        """Set up test fixtures."""
        # Mock data for testing
        self.user_id = 1
        
        # Mock budgets
        self.mock_budgets = [
            {
                'id': 1,
                'category': 'Food',
                'amount': 200.00,
                'month': 5,
                'year': 2023,
                'alert_threshold': 0.8,
                'spent': 160.00  # 80% of budget
            },
            {
                'id': 2,
                'category': 'Transport',
                'amount': 100.00,
                'month': 5,
                'year': 2023,
                'alert_threshold': 0.8,
                'spent': 90.00  # 90% of budget (exceeds threshold)
            },
            {
                'id': 3,
                'category': 'Entertainment',
                'amount': 50.00,
                'month': 5,
                'year': 2023,
                'alert_threshold': 0.8,
                'spent': 30.00  # 60% of budget (below threshold)
            }
        ]
        
        # Mock alerts
        self.mock_alerts = [
            {
                'id': 1,
                'message': 'Budget alert: You have spent 90% of your Transport budget for May 2023',
                'is_read': False,
                'created_at': datetime(2023, 5, 15, 10, 30, 0),
                'user_id': 1,
                'budget_id': 2
            }
        ]

    @patch('expense_tracker.services.budget_service.BudgetService.get_budgets_with_spending')
    @patch('expense_tracker.services.alert_service.AlertService.create_alert')
    def test_check_and_create_alerts(self, mock_create_alert, mock_get_budgets):
        """Test checking and creating budget alerts."""
        mock_get_budgets.return_value = self.mock_budgets
        mock_create_alert.return_value = {'id': 2, 'message': 'Budget alert: test', 'is_read': False}
        
        alerts = AlertService.check_and_create_alerts(self.user_id)
        
        # Verify that an alert was created for Transport (above threshold)
        self.assertEqual(len(alerts), 1)
        
        # Verify create_alert was called once for Transport
        self.assertEqual(mock_create_alert.call_count, 1)
        
        # Verify the create_alert parameters
        args, kwargs = mock_create_alert.call_args
        self.assertEqual(kwargs['user_id'], self.user_id)
        self.assertEqual(kwargs['budget_id'], 2)  # Transport budget ID
        self.assertIn('Transport', kwargs['message'])

    @patch('expense_tracker.db.session.get_session')
    def test_create_alert(self, mock_get_session):
        """Test creating an alert."""
        mock_session = MagicMock()
        mock_get_session.return_value.__enter__.return_value = mock_session
        
        result = AlertService.create_alert(
            message="Test alert message",
            user_id=self.user_id,
            budget_id=1
        )
        
        # Verify the result structure
        self.assertIn('id', result)
        self.assertIn('message', result)
        self.assertEqual(result['message'], "Test alert message")
        self.assertIn('is_read', result)
        self.assertFalse(result['is_read'])
        
        # Verify session interaction
        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()

    @patch('expense_tracker.db.session.get_session')
    def test_get_alerts(self, mock_get_session):
        """Test retrieving alerts."""
        mock_session = MagicMock()
        mock_query = mock_session.query.return_value.filter.return_value
        mock_query.order_by.return_value.all.return_value = [MagicMock(id=1, message="Test alert", is_read=False)]
        
        mock_get_session.return_value.__enter__.return_value = mock_session
        
        alerts = AlertService.get_alerts(user_id=self.user_id, include_read=False)
        
        # Verify the result
        self.assertEqual(len(alerts), 1)
        self.assertEqual(alerts[0]['id'], 1)
        self.assertEqual(alerts[0]['message'], "Test alert")
        self.assertFalse(alerts[0]['is_read'])
        
        # Verify query construction
        mock_session.query.assert_called_once()
        mock_query.order_by.assert_called_once()

    @patch('expense_tracker.db.session.get_session')
    def test_mark_alert_read(self, mock_get_session):
        """Test marking an alert as read."""
        mock_session = MagicMock()
        mock_alert = MagicMock(id=1, message="Test alert", is_read=False, user_id=self.user_id)
        mock_session.query.return_value.filter.return_value.first.return_value = mock_alert
        
        mock_get_session.return_value.__enter__.return_value = mock_session
        
        result = AlertService.mark_alert_read(alert_id=1, user_id=self.user_id)
        
        # Verify the result
        self.assertTrue(result)
        
        # Verify alert was updated
        self.assertTrue(mock_alert.is_read)
        
        # Verify session interaction
        mock_session.commit.assert_called_once()

    @patch('expense_tracker.db.session.get_session')
    def test_mark_all_alerts_read(self, mock_get_session):
        """Test marking all alerts as read."""
        mock_session = MagicMock()
        mock_alerts = [
            MagicMock(id=1, message="Test alert 1", is_read=False, user_id=self.user_id),
            MagicMock(id=2, message="Test alert 2", is_read=False, user_id=self.user_id)
        ]
        mock_session.query.return_value.filter.return_value.all.return_value = mock_alerts
        
        mock_get_session.return_value.__enter__.return_value = mock_session
        
        count = AlertService.mark_all_alerts_read(user_id=self.user_id)
        
        # Verify the result
        self.assertEqual(count, 2)
        
        # Verify alerts were updated
        self.assertTrue(all(alert.is_read for alert in mock_alerts))
        
        # Verify session interaction
        mock_session.commit.assert_called_once()


if __name__ == '__main__':
    unittest.main() 