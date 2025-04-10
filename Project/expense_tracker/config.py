"""
Configuration module for the Expense Tracker application.
"""

import os
from typing import Dict, Any

# Database configuration
DB_CONFIG = {
    "url": os.environ.get("EXPENSE_TRACKER_DB", "sqlite:///expense_tracker.db"),
    "echo": False,  # Set to True to enable SQL query logging
    "connect_args": {"check_same_thread": False}  # Only needed for SQLite
}

# Email configuration
EMAIL_CONFIG = {
    "smtp_server": os.environ.get("SMTP_SERVER", "smtp.gmail.com"),
    "smtp_port": int(os.environ.get("SMTP_PORT", "587")),
    "username": os.environ.get("SMTP_USERNAME", ""),
    "password": os.environ.get("SMTP_PASSWORD", ""),
    "use_tls": True
}

# Default categories
DEFAULT_CATEGORIES = [
    {"name": "Food", "description": "Groceries, restaurants, and food delivery", "is_default": True},
    {"name": "Transport", "description": "Public transport, taxis, and fuel", "is_default": True},
    {"name": "Entertainment", "description": "Movies, events, and other leisure activities", "is_default": True},
    {"name": "Housing", "description": "Rent, mortgage, and home maintenance", "is_default": True},
    {"name": "Utilities", "description": "Electricity, water, and internet bills", "is_default": True},
    {"name": "Healthcare", "description": "Medical expenses and health insurance", "is_default": True},
    {"name": "Shopping", "description": "Clothing, electronics, and other retail purchases", "is_default": True},
    {"name": "Personal", "description": "Personal care and miscellaneous expenses", "is_default": True},
]

# Alert configuration
ALERT_CONFIG = {
    "default_threshold": 0.8,  # Alert when 80% of budget is used
    "check_on_expense_add": True,  # Check for alerts whenever an expense is added
}

# General application configuration
APP_CONFIG = {
    "debug": os.environ.get("EXPENSE_TRACKER_DEBUG", "false").lower() == "true",
    "currency_symbol": os.environ.get("EXPENSE_TRACKER_CURRENCY", "$"),
    "default_user_id": 1  # Default user ID for single-user mode
}


def get_config() -> Dict[str, Any]:
    """Get the full application configuration.
    
    Returns:
        Dict[str, Any]: Complete configuration dictionary
    """
    return {
        "db": DB_CONFIG,
        "email": EMAIL_CONFIG,
        "categories": DEFAULT_CATEGORIES,
        "alerts": ALERT_CONFIG,
        "app": APP_CONFIG
    } 