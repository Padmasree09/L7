"""
Notification service module for sending email alerts.
"""

import os
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Dict, Any, Optional, Tuple, Union

from expense_tracker.utils.validators import validate_email


class NotificationService:
    """Service class for sending notifications."""
    
    def __init__(self, 
                 smtp_server: Optional[str] = None, 
                 smtp_port: Optional[int] = None,
                 username: Optional[str] = None, 
                 password: Optional[str] = None,
                 use_tls: bool = True):
        """Initialize the notification service.
        
        Args:
            smtp_server: SMTP server address (default from env)
            smtp_port: SMTP server port (default from env)
            username: SMTP username (default from env)
            password: SMTP password (default from env)
            use_tls: Whether to use TLS
        """
        # Get SMTP configuration from environment or use defaults
        self.smtp_server = smtp_server or os.environ.get('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = smtp_port or int(os.environ.get('SMTP_PORT', 587))
        self.username = username or os.environ.get('SMTP_USERNAME', '')
        self.password = password or os.environ.get('SMTP_PASSWORD', '')
        self.use_tls = use_tls
        
        # Set up logging
        self.logger = logging.getLogger(__name__)
    
    def send_email(self, 
                   to_email: str, 
                   subject: str, 
                   message: str,
                   html_message: Optional[str] = None) -> Tuple[bool, str]:
        """Send an email notification.
        
        Args:
            to_email: Recipient email address
            subject: Email subject
            message: Plain text message
            html_message: Optional HTML message
            
        Returns:
            Tuple[bool, str]: Success flag and message
        """
        # Validate email
        try:
            validate_email(to_email)
        except Exception as e:
            return False, f"Invalid email address: {str(e)}"
        
        # Check if SMTP credentials are configured
        if not self.username or not self.password:
            return False, "SMTP credentials not configured. Please set SMTP_USERNAME and SMTP_PASSWORD environment variables."
        
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.username
            msg['To'] = to_email
            
            # Add text part
            text_part = MIMEText(message, 'plain')
            msg.attach(text_part)
            
            # Add HTML part if provided
            if html_message:
                html_part = MIMEText(html_message, 'html')
                msg.attach(html_part)
            
            # Connect to SMTP server
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.ehlo()
            
            # Use TLS if enabled
            if self.use_tls:
                server.starttls()
                server.ehlo()
            
            # Login and send email
            server.login(self.username, self.password)
            server.sendmail(self.username, to_email, msg.as_string())
            server.quit()
            
            return True, f"Email sent successfully to {to_email}"
        
        except Exception as e:
            self.logger.error(f"Error sending email: {str(e)}")
            return False, f"Error sending email: {str(e)}"
    
    def send_budget_alert(self, 
                          to_email: str, 
                          alert_data: Dict[str, Any]) -> Tuple[bool, str]:
        """Send a budget alert email.
        
        Args:
            to_email: Recipient email address
            alert_data: Alert data dictionary
            
        Returns:
            Tuple[bool, str]: Success flag and message
        """
        subject = f"Budget Alert: {alert_data['category']}"
        
        # Create plain text message
        message = f"""
Budget Alert

{alert_data['message']}

Category: {alert_data['category']}
Budget: ${alert_data['budget']:.2f}
Spent: ${alert_data['spent']:.2f}
Percentage Used: {alert_data['percentage_used']*100:.1f}%

Please review your spending and adjust your budget if necessary.

This is an automated message from your Expense Tracker application.
"""
        
        # Create HTML message
        html_message = f"""
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; }}
        .alert {{ padding: 15px; border-radius: 5px; margin-bottom: 20px; }}
        .warning {{ background-color: #fff3cd; border: 1px solid #ffeeba; }}
        .danger {{ background-color: #f8d7da; border: 1px solid #f5c6cb; }}
        .table {{ border-collapse: collapse; width: 100%; }}
        .table th, .table td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        .table th {{ background-color: #f2f2f2; }}
    </style>
</head>
<body>
    <h2>Budget Alert</h2>
    
    <div class="alert {'danger' if alert_data['percentage_used'] >= 1.0 else 'warning'}">
        <strong>{alert_data['message']}</strong>
    </div>
    
    <table class="table">
        <tr>
            <th>Category</th>
            <td>{alert_data['category']}</td>
        </tr>
        <tr>
            <th>Budget</th>
            <td>${alert_data['budget']:.2f}</td>
        </tr>
        <tr>
            <th>Spent</th>
            <td>${alert_data['spent']:.2f}</td>
        </tr>
        <tr>
            <th>Percentage Used</th>
            <td>{alert_data['percentage_used']*100:.1f}%</td>
        </tr>
    </table>
    
    <p>Please review your spending and adjust your budget if necessary.</p>
    
    <p><small>This is an automated message from your Expense Tracker application.</small></p>
</body>
</html>
"""
        
        return self.send_email(to_email, subject, message, html_message)
    
    def send_multiple_budget_alerts(self, 
                                    to_email: str, 
                                    alerts: List[Dict[str, Any]]) -> Tuple[bool, str]:
        """Send multiple budget alerts in a single email.
        
        Args:
            to_email: Recipient email address
            alerts: List of alert data dictionaries
            
        Returns:
            Tuple[bool, str]: Success flag and message
        """
        if not alerts:
            return False, "No alerts to send"
        
        subject = f"Budget Alerts: {len(alerts)} categories require attention"
        
        # Create plain text message
        message = "Budget Alerts\n\n"
        
        for alert in alerts:
            message += f"""
{alert['message']}

Category: {alert['category']}
Budget: ${alert['budget']:.2f}
Spent: ${alert['spent']:.2f}
Percentage Used: {alert['percentage_used']*100:.1f}%

"""
        
        message += "\nPlease review your spending and adjust your budgets if necessary.\n\n"
        message += "This is an automated message from your Expense Tracker application."
        
        # Create HTML message
        html_message = f"""
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; }}
        .alert {{ padding: 15px; border-radius: 5px; margin-bottom: 20px; }}
        .warning {{ background-color: #fff3cd; border: 1px solid #ffeeba; }}
        .danger {{ background-color: #f8d7da; border: 1px solid #f5c6cb; }}
        .table {{ border-collapse: collapse; width: 100%; margin-bottom: 20px; }}
        .table th, .table td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        .table th {{ background-color: #f2f2f2; }}
    </style>
</head>
<body>
    <h2>Budget Alerts</h2>
    
    <p>The following {len(alerts)} categories require your attention:</p>
"""
        
        for alert in alerts:
            html_message += f"""
    <div class="alert {'danger' if alert['percentage_used'] >= 1.0 else 'warning'}">
        <strong>{alert['message']}</strong>
    </div>
    
    <table class="table">
        <tr>
            <th>Category</th>
            <td>{alert['category']}</td>
        </tr>
        <tr>
            <th>Budget</th>
            <td>${alert['budget']:.2f}</td>
        </tr>
        <tr>
            <th>Spent</th>
            <td>${alert['spent']:.2f}</td>
        </tr>
        <tr>
            <th>Percentage Used</th>
            <td>{alert['percentage_used']*100:.1f}%</td>
        </tr>
    </table>
"""
        
        html_message += """
    <p>Please review your spending and adjust your budgets if necessary.</p>
    
    <p><small>This is an automated message from your Expense Tracker application.</small></p>
</body>
</html>
"""
        
        return self.send_email(to_email, subject, message, html_message) 