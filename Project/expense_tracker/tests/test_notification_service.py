"""
Tests for the notification service module.
"""

import unittest
from unittest.mock import patch, MagicMock, call
from expense_tracker.services.notification_service import NotificationService


class TestNotificationService(unittest.TestCase):
    """Test cases for the notification service."""

    def setUp(self):
        """Set up test fixtures."""
        # Mock data for testing
        self.user_id = 1
        self.email = "test@example.com"
        
        # Mock alerts
        self.mock_alerts = [
            {
                'id': 1,
                'message': 'Budget alert: You have spent 90% of your Transport budget for May 2023',
                'is_read': False,
                'user_id': 1,
                'budget_id': 2
            },
            {
                'id': 2,
                'message': 'Budget alert: You have spent 100% of your Food budget for May 2023',
                'is_read': False,
                'user_id': 1,
                'budget_id': 1
            }
        ]
        
        # Mock user
        self.mock_user = {
            'id': 1,
            'username': 'testuser',
            'email': 'test@example.com'
        }

    @patch('expense_tracker.services.notification_service.smtplib.SMTP')
    @patch('expense_tracker.config.EMAIL_CONFIG', {
        'smtp_server': 'smtp.example.com',
        'smtp_port': 587,
        'username': 'test@example.com',
        'password': 'password123',
        'use_tls': True
    })
    def test_send_email(self, mock_smtp):
        """Test sending an email."""
        # Set up mock
        mock_smtp_instance = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_smtp_instance
        
        # Call send_email
        success = NotificationService.send_email(
            to_email=self.email,
            subject="Test Subject",
            body="Test Body"
        )
        
        # Verify the result
        self.assertTrue(success)
        
        # Verify SMTP interactions
        mock_smtp.assert_called_once_with('smtp.example.com', 587)
        mock_smtp_instance.starttls.assert_called_once()
        mock_smtp_instance.login.assert_called_once_with('test@example.com', 'password123')
        mock_smtp_instance.sendmail.assert_called_once()
        
        # Verify email content
        args, kwargs = mock_smtp_instance.sendmail.call_args
        self.assertEqual(args[0], 'test@example.com')  # From email
        self.assertEqual(args[1], self.email)  # To email
        email_content = args[2]
        self.assertIn('Subject: Test Subject', email_content)
        self.assertIn('Test Body', email_content)
        
    @patch('expense_tracker.services.notification_service.NotificationService.send_email')
    @patch('expense_tracker.services.alert_service.AlertService.get_alerts')
    @patch('expense_tracker.services.alert_service.AlertService.mark_alert_read')
    def test_send_alert_notifications(self, mock_mark_alert_read, mock_get_alerts, mock_send_email):
        """Test sending alert notifications via email."""
        # Set up mocks
        mock_get_alerts.return_value = self.mock_alerts
        mock_send_email.return_value = True
        mock_mark_alert_read.return_value = True
        
        # Call send_alert_notifications
        sent_count = NotificationService.send_alert_notifications(
            user_id=self.user_id,
            to_email=self.email,
            mark_as_read=True
        )
        
        # Verify the result
        self.assertEqual(sent_count, 2)
        
        # Verify get_alerts was called
        mock_get_alerts.assert_called_once_with(user_id=self.user_id, include_read=False)
        
        # Verify send_email was called with the correct parameters
        self.assertEqual(mock_send_email.call_count, 1)
        send_email_call = mock_send_email.call_args
        self.assertEqual(send_email_call[1]['to_email'], self.email)
        self.assertIn('Budget Alerts', send_email_call[1]['subject'])
        for alert in self.mock_alerts:
            self.assertIn(alert['message'], send_email_call[1]['body'])
        
        # Verify mark_alert_read was called for both alerts
        self.assertEqual(mock_mark_alert_read.call_count, 2)
        expected_calls = [
            call(alert_id=1, user_id=self.user_id),
            call(alert_id=2, user_id=self.user_id)
        ]
        mock_mark_alert_read.assert_has_calls(expected_calls, any_order=True)

    @patch('expense_tracker.services.notification_service.NotificationService.send_email')
    def test_send_monthly_report(self, mock_send_email):
        """Test sending a monthly report via email."""
        # Mock report data
        mock_report = {
            'month': 5,
            'year': 2023,
            'total': 350.00,
            'categories': [
                {'name': 'Food', 'amount': 200.00},
                {'name': 'Transport', 'amount': 100.00},
                {'name': 'Entertainment', 'amount': 50.00}
            ]
        }
        
        # Set up mock
        mock_send_email.return_value = True
        
        # Call send_monthly_report
        success = NotificationService.send_monthly_report(
            to_email=self.email,
            report=mock_report
        )
        
        # Verify the result
        self.assertTrue(success)
        
        # Verify send_email was called with the correct parameters
        mock_send_email.assert_called_once()
        send_email_call = mock_send_email.call_args
        self.assertEqual(send_email_call[1]['to_email'], self.email)
        self.assertIn('Monthly Expense Report', send_email_call[1]['subject'])
        
        # Verify email content contains important report information
        body = send_email_call[1]['body']
        self.assertIn('May 2023', body)
        self.assertIn('$350.00', body)
        self.assertIn('Food', body)
        self.assertIn('$200.00', body)
        self.assertIn('Transport', body)
        self.assertIn('$100.00', body)
        self.assertIn('Entertainment', body)
        self.assertIn('$50.00', body)

    @patch('expense_tracker.services.notification_service.NotificationService.send_email')
    def test_send_budget_status(self, mock_send_email):
        """Test sending a budget status report via email."""
        # Mock budget status data
        mock_budget_status = {
            'month': 5,
            'year': 2023,
            'total_budget': 400.00,
            'total_spent': 350.00,
            'remaining': 50.00,
            'percentage': 87.5,
            'categories': [
                {
                    'name': 'Food',
                    'budget': 200.00,
                    'spent': 180.00,
                    'remaining': 20.00,
                    'percentage': 90.0
                },
                {
                    'name': 'Transport',
                    'budget': 150.00,
                    'spent': 120.00,
                    'remaining': 30.00,
                    'percentage': 80.0
                },
                {
                    'name': 'Entertainment',
                    'budget': 50.00,
                    'spent': 50.00,
                    'remaining': 0.00,
                    'percentage': 100.0
                }
            ]
        }
        
        # Set up mock
        mock_send_email.return_value = True
        
        # Call send_budget_status
        success = NotificationService.send_budget_status(
            to_email=self.email,
            budget_status=mock_budget_status
        )
        
        # Verify the result
        self.assertTrue(success)
        
        # Verify send_email was called with the correct parameters
        mock_send_email.assert_called_once()
        send_email_call = mock_send_email.call_args
        self.assertEqual(send_email_call[1]['to_email'], self.email)
        self.assertIn('Budget Status', send_email_call[1]['subject'])
        
        # Verify email content contains important budget information
        body = send_email_call[1]['body']
        self.assertIn('May 2023', body)
        self.assertIn('87.5%', body)
        self.assertIn('Entertainment: 100.0%', body)
        self.assertIn('$400.00', body)
        self.assertIn('$350.00', body)
        self.assertIn('$50.00', body)


if __name__ == '__main__':
    unittest.main() 