"""
Formatting utilities for the expense tracker application.
"""

import csv
import io
from datetime import datetime
from typing import Dict, List, Any, Optional, Union

from tabulate import tabulate


def format_currency(amount: float, currency: str = "$") -> str:
    """Format an amount as currency.
    
    Args:
        amount: The amount to format
        currency: The currency symbol
        
    Returns:
        str: Formatted currency string
    """
    return f"{currency}{amount:.2f}"


def format_date(date_obj: datetime, format_str: str = "%Y-%m-%d") -> str:
    """Format a datetime object as a string.
    
    Args:
        date_obj: The datetime to format
        format_str: The date format string
        
    Returns:
        str: Formatted date string
    """
    if not date_obj:
        return ""
    return date_obj.strftime(format_str)


def format_month_year(month: int, year: int) -> str:
    """Format month and year as a string.
    
    Args:
        month: Month number (1-12)
        year: Year
        
    Returns:
        str: Formatted month and year (e.g. "January 2023")
    """
    months = [
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ]
    
    return f"{months[month-1]} {year}"


def format_percentage(value: float) -> str:
    """Format a value as a percentage.
    
    Args:
        value: The value to format
        
    Returns:
        str: Formatted percentage string
    """
    return f"{value*100:.1f}%"


def format_table(data: List[Dict[str, Any]], headers: Dict[str, str], 
                 title: Optional[str] = None) -> str:
    """Format data as a text table.
    
    Args:
        data: List of dictionaries with data
        headers: Dictionary mapping data keys to header names
        title: Optional title for the table
        
    Returns:
        str: Formatted table string
    """
    # Extract header mappings and field keys
    header_keys = list(headers.keys())
    header_labels = list(headers.values())
    
    # Extract rows with specified fields only
    rows = []
    for item in data:
        row = [item.get(key, "") for key in header_keys]
        rows.append(row)
    
    # Add title if provided
    result = ""
    if title:
        result += f"\n{title}\n" + "=" * len(title) + "\n\n"
    
    # Generate table
    result += tabulate(rows, headers=header_labels, tablefmt="grid")
    return result


def export_to_csv(data: List[Dict[str, Any]], 
                  headers: Dict[str, str]) -> str:
    """Export data to CSV format.
    
    Args:
        data: List of dictionaries with data
        headers: Dictionary mapping data keys to header names
        
    Returns:
        str: CSV formatted string
    """
    # Extract header mappings and field keys
    header_keys = list(headers.keys())
    header_labels = list(headers.values())
    
    # Create CSV in memory
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write headers
    writer.writerow(header_labels)
    
    # Write data
    for item in data:
        row = [item.get(key, "") for key in header_keys]
        writer.writerow(row)
    
    return output.getvalue()


def format_budget_status(current: float, budget: float) -> str:
    """Format budget status with visual indicator.
    
    Args:
        current: Current spending amount
        budget: Budget limit amount
        
    Returns:
        str: Formatted budget status
    """
    percentage = current / budget if budget > 0 else 0
    
    if percentage >= 1.0:
        return f"EXCEEDED! ({format_percentage(percentage)})"
    elif percentage >= 0.9:
        return f"Critical ({format_percentage(percentage)})"
    elif percentage >= 0.75:
        return f"Warning ({format_percentage(percentage)})"
    else:
        return f"Good ({format_percentage(percentage)})" 