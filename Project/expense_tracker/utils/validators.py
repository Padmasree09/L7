"""
Validation utilities for the expense tracker application.
"""

import re
from datetime import datetime
from typing import Optional, Union, Dict, Any, List

class ValidationError(Exception):
    """Exception raised for validation errors."""
    def __init__(self, message:str, field:Optional[str]=None):
        self.message = message
        self.field = field
        super().__init__(self.message)


def validate_amount(amount: Union[float, str], field_name: str = "amount") -> float:
    """Validate an expense or budget amount.
    
    Args:
        amount: The amount to validate
        field_name: The name of the field being validated
        
    Returns:
        float: The validated amount
        
    Raises:
        ValidationError: If the amount is invalid
    """
    try:
        amount_float = float(amount)
    except (ValueError, TypeError):
        raise ValidationError(f"Invalid {field_name}: must be a valid number", field_name)
    
    if amount_float <= 0:
        raise ValidationError(f"Invalid {field_name}: must be greater than zero", field_name)
    
    return amount_float


def validate_date(date_str: Optional[str] = None, field_name: str = "date") -> datetime:
    """Validate and parse a date string.
    
    Args:
        date_str: The date string in YYYY-MM-DD format (defaults to today)
        field_name: The name of the field being validated
        
    Returns:
        datetime: The validated date
        
    Raises:
        ValidationError: If the date format is invalid
    """
    if not date_str:
        return datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    
    try:
        # Try to parse the date string
        if isinstance(date_str, str):
            # Check format (YYYY-MM-DD)
            if not re.match(r'^\d{4}-\d{2}-\d{2}$', date_str):
                raise ValueError("Invalid date format")
            
            # Parse date
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            return date_obj
        elif isinstance(date_str, datetime):
            return date_str
        else:
            raise ValueError("Invalid date type")
    except ValueError:
        raise ValidationError(
            f"Invalid {field_name}: must be in YYYY-MM-DD format", field_name
        )


def validate_month_year(month: int, year: int) -> Dict[str, int]:
    """Validate month and year values.
    
    Args:
        month: Month number (1-12)
        year: Year (e.g. 2023)
        
    Returns:
        Dict containing validated month and year
        
    Raises:
        ValidationError: If month or year is invalid
    """
    # Validate month
    try:
        month_int = int(month)
        if month_int < 1 or month_int > 12:
            raise ValidationError("Month must be between 1 and 12", "month")
    except (ValueError, TypeError):
        raise ValidationError("Month must be a valid number", "month")
    
    # Validate year
    try:
        year_int = int(year)
        if year_int < 2000 or year_int > 2100:
            raise ValidationError("Year must be between 2000 and 2100", "year")
    except (ValueError, TypeError):
        raise ValidationError("Year must be a valid number", "year")
    
    return {"month": month_int, "year": year_int}


def validate_string(value: str, field_name: str, min_length: int = 1, max_length: int = 200) -> str:
    """Validate a string field.
    
    Args:
        value: The string to validate
        field_name: Name of the field being validated
        min_length: Minimum allowed length
        max_length: Maximum allowed length
        
    Returns:
        str: The validated string
        
    Raises:
        ValidationError: If the string is invalid
    """
    if not value:
        raise ValidationError(f"{field_name} cannot be empty", field_name)
    
    if not isinstance(value, str):
        raise ValidationError(f"{field_name} must be a string", field_name)
    
    if len(value) < min_length:
        raise ValidationError(
            f"{field_name} must be at least {min_length} characters", field_name
        )
    
    if len(value) > max_length:
        raise ValidationError(
            f"{field_name} cannot exceed {max_length} characters", field_name
        )
    
    return value


def validate_email(email: str) -> str:
    """Validate an email address.
    
    Args:
        email: Email address to validate
        
    Returns:
        str: The validated email
        
    Raises:
        ValidationError: If the email is invalid
    """
    # Basic email validation
    if not email or not isinstance(email, str):
        raise ValidationError("Email cannot be empty", "email")
    
    # Simple regex pattern for email validation
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email):
        raise ValidationError("Invalid email format", "email")
    
    return email


def validate_threshold(threshold: Union[float, str]) -> float:
    """Validate an alert threshold.
    
    Args:
        threshold: The threshold value (0.0-1.0)
        
    Returns:
        float: The validated threshold
        
    Raises:
        ValidationError: If the threshold is invalid
    """
    try:
        threshold_float = float(threshold)
    except (ValueError, TypeError):
        raise ValidationError("Threshold must be a valid number", "threshold")
    
    if threshold_float < 0 or threshold_float > 1:
        raise ValidationError("Threshold must be between 0 and 1", "threshold")
    
    return threshold_float 