"""
Alert service module for managing budget alerts.
"""

from typing import List, Dict, Any, Optional, Tuple, Union
from datetime import datetime

from expense_tracker.db.models import Alert, Budget, User
from expense_tracker.db.session import get_db_session
from expense_tracker.services.budget_service import BudgetService
from expense_tracker.services.notification_service import NotificationService


class AlertService:
    """Service class for managing budget alerts."""
    
    @staticmethod
    def get_alerts(user_id: int, include_read: bool = False) -> List[Dict[str, Any]]:
        """Get alerts for a user.
        
        Args:
            user_id: User ID
            include_read: Whether to include read alerts
            
        Returns:
            List of alert dictionaries
        """
        with get_db_session() as db:
            # Build query
            query = db.query(Alert).filter(Alert.user_id == user_id)
            
            # Filter out read alerts if needed
            if not include_read:
                query = query.filter(Alert.is_read == False)
            
            # Execute query
            alerts = query.order_by(Alert.created_at.desc()).all()
            
            # Convert to dictionaries
            return [
                {
                    'id': alert.id,
                    'message': alert.message,
                    'is_read': alert.is_read,
                    'created_at': alert.created_at,
                    'budget_id': alert.budget_id
                }
                for alert in alerts
            ]
    
    @staticmethod
    def mark_alert_as_read(alert_id: int, user_id: int) -> bool:
        """Mark an alert as read.
        
        Args:
            alert_id: Alert ID
            user_id: User ID for verification
            
        Returns:
            bool: True if marked successfully, False otherwise
        """
        with get_db_session() as db:
            alert = db.query(Alert).filter(
                Alert.id == alert_id,
                Alert.user_id == user_id
            ).first()
            
            if not alert:
                return False
            
            alert.is_read = True
            db.commit()
            return True
    
    @staticmethod
    def mark_all_alerts_as_read(user_id: int) -> int:
        """Mark all alerts as read for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            int: Number of alerts marked as read
        """
        with get_db_session() as db:
            # Find unread alerts
            unread_alerts = db.query(Alert).filter(
                Alert.user_id == user_id,
                Alert.is_read == False
            ).all()
            
            # Mark as read
            count = 0
            for alert in unread_alerts:
                alert.is_read = True
                count += 1
            
            if count > 0:
                db.commit()
            
            return count
    
    @staticmethod
    def check_and_create_alerts(user_id: int) -> List[Dict[str, Any]]:
        """Check budgets and create alerts if needed.
        
        Args:
            user_id: User ID
            
        Returns:
            List of created alert dictionaries
        """
        # Use the budget service to check for alerts
        return BudgetService.check_budget_alerts(user_id)
    
    @staticmethod
    def check_and_send_notifications(user_id: int, email: Optional[str] = None) -> Tuple[bool, str]:
        """Check budgets, create alerts, and send notifications.
        
        Args:
            user_id: User ID
            email: Email address to send notifications to
            
        Returns:
            Tuple[bool, str]: Success flag and message
        """
        # Check budgets and create alerts
        alerts = AlertService.check_and_create_alerts(user_id)
        
        if not alerts:
            return True, "No budget alerts to send."
        
        # If no email provided, try to get from user profile
        if not email:
            with get_db_session() as db:
                user = db.query(User).filter(User.id == user_id).first()
                if user:
                    email = user.email
        
        if not email:
            return False, "No email address provided or found in user profile."
        
        # Send notifications
        notification_service = NotificationService()
        success, message = notification_service.send_multiple_budget_alerts(email, alerts)
        
        return success, message
    
    @staticmethod
    def delete_alert(alert_id: int, user_id: int) -> bool:
        """Delete an alert.
        
        Args:
            alert_id: Alert ID
            user_id: User ID for verification
            
        Returns:
            bool: True if deleted successfully, False otherwise
        """
        with get_db_session() as db:
            alert = db.query(Alert).filter(
                Alert.id == alert_id,
                Alert.user_id == user_id
            ).first()
            
            if not alert:
                return False
            
            db.delete(alert)
            db.commit()
            return True 