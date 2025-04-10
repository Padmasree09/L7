"""
Tests for the validators utility.
"""

import pytest
from datetime import datetime

from expense_tracker.utils.validators import (
    validate_amount, validate_date, validate_month_year,
    validate_string, validate_email, validate_threshold,
    ValidationError
)


class TestValidators:
    """Test class for validator functions."""
    
    def test_validate_amount_valid(self):
        """Test validation of valid amounts."""
        # Test with positive float
        result = validate_amount(25.50)
        assert result == 25.50
        
        # Test with positive integer
        result = validate_amount(100)
        assert result == 100.0
        
        # Test with string representation
        result = validate_amount("75.25")
        assert result == 75.25
    
    def test_validate_amount_invalid(self):
        """Test validation of invalid amounts."""
        # Test with negative amount
        with pytest.raises(ValidationError) as excinfo:
            validate_amount(-25.50)
        assert "must be greater than zero" in str(excinfo.value)
        
        # Test with zero
        with pytest.raises(ValidationError) as excinfo:
            validate_amount(0)
        assert "must be greater than zero" in str(excinfo.value)
        
        # Test with non-numeric string
        with pytest.raises(ValidationError) as excinfo:
            validate_amount("not a number")
        assert "must be a valid number" in str(excinfo.value)
    
    def test_validate_date_valid(self):
        """Test validation of valid dates."""
        # Test with valid date string
        result = validate_date("2023-05-15")
        assert isinstance(result, datetime)
        assert result.year == 2023
        assert result.month == 5
        assert result.day == 15
        
        # Test with datetime object
        date_obj = datetime(2023, 6, 20)
        result = validate_date(date_obj)
        assert result == date_obj
        
        # Test with None (should return current date)
        result = validate_date()
        assert isinstance(result, datetime)
    
    def test_validate_date_invalid(self):
        """Test validation of invalid dates."""
        # Test with invalid format
        with pytest.raises(ValidationError) as excinfo:
            validate_date("15/05/2023")
        assert "must be in YYYY-MM-DD format" in str(excinfo.value)
        
        # Test with invalid date
        with pytest.raises(ValidationError) as excinfo:
            validate_date("2023-13-45")  # Invalid month and day
        assert "must be in YYYY-MM-DD format" in str(excinfo.value)
    
    def test_validate_month_year_valid(self):
        """Test validation of valid month and year."""
        # Test valid values
        result = validate_month_year(5, 2023)
        assert result == {"month": 5, "year": 2023}
        
        # Test string values that can be converted
        result = validate_month_year("12", "2025")
        assert result == {"month": 12, "year": 2025}
    
    def test_validate_month_year_invalid(self):
        """Test validation of invalid month and year."""
        # Test invalid month
        with pytest.raises(ValidationError) as excinfo:
            validate_month_year(13, 2023)
        assert "Month must be between 1 and 12" in str(excinfo.value)
        
        # Test negative month
        with pytest.raises(ValidationError) as excinfo:
            validate_month_year(-5, 2023)
        assert "Month must be between 1 and 12" in str(excinfo.value)
        
        # Test invalid year
        with pytest.raises(ValidationError) as excinfo:
            validate_month_year(5, 1999)
        assert "Year must be between 2000 and 2100" in str(excinfo.value)
    
    def test_validate_string_valid(self):
        """Test validation of valid strings."""
        # Test normal string
        result = validate_string("Test string", "description")
        assert result == "Test string"
        
        # Test with min_length
        result = validate_string("abc", "name", min_length=3)
        assert result == "abc"
    
    def test_validate_string_invalid(self):
        """Test validation of invalid strings."""
        # Test empty string
        with pytest.raises(ValidationError) as excinfo:
            validate_string("", "name")
        assert "name cannot be empty" in str(excinfo.value)
        
        # Test None
        with pytest.raises(ValidationError) as excinfo:
            validate_string(None, "name")
        assert "name cannot be empty" in str(excinfo.value)
        
        # Test too short
        with pytest.raises(ValidationError) as excinfo:
            validate_string("ab", "name", min_length=3)
        assert "name must be at least 3 characters" in str(excinfo.value)
        
        # Test too long
        with pytest.raises(ValidationError) as excinfo:
            validate_string("abcdef", "name", max_length=5)
        assert "name cannot exceed 5 characters" in str(excinfo.value)
    
    def test_validate_email_valid(self):
        """Test validation of valid emails."""
        # Test standard email
        result = validate_email("user@example.com")
        assert result == "user@example.com"
        
        # Test with subdomain
        result = validate_email("user@sub.example.com")
        assert result == "user@sub.example.com"
        
        # Test with plus addressing
        result = validate_email("user+tag@example.com")
        assert result == "user+tag@example.com"
    
    def test_validate_email_invalid(self):
        """Test validation of invalid emails."""
        # Test empty email
        with pytest.raises(ValidationError) as excinfo:
            validate_email("")
        assert "Email cannot be empty" in str(excinfo.value)
        
        # Test None
        with pytest.raises(ValidationError) as excinfo:
            validate_email(None)
        assert "Email cannot be empty" in str(excinfo.value)
        
        # Test invalid format (missing domain)
        with pytest.raises(ValidationError) as excinfo:
            validate_email("user@")
        assert "Invalid email format" in str(excinfo.value)
        
        # Test invalid format (missing @)
        with pytest.raises(ValidationError) as excinfo:
            validate_email("user.example.com")
        assert "Invalid email format" in str(excinfo.value)
    
    def test_validate_threshold_valid(self):
        """Test validation of valid thresholds."""
        # Test with float
        result = validate_threshold(0.75)
        assert result == 0.75
        
        # Test with integer (will be converted to float)
        result = validate_threshold(1)
        assert result == 1.0
        
        # Test with string representation
        result = validate_threshold("0.5")
        assert result == 0.5
    
    def test_validate_threshold_invalid(self):
        """Test validation of invalid thresholds."""
        # Test with negative value
        with pytest.raises(ValidationError) as excinfo:
            validate_threshold(-0.5)
        assert "Threshold must be between 0 and 1" in str(excinfo.value)
        
        # Test with value > 1
        with pytest.raises(ValidationError) as excinfo:
            validate_threshold(1.5)
        assert "Threshold must be between 0 and 1" in str(excinfo.value)
        
        # Test with non-numeric string
        with pytest.raises(ValidationError) as excinfo:
            validate_threshold("not a number")
        assert "Threshold must be a valid number" in str(excinfo.value) 