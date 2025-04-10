"""
Report service module for generating expense and budget reports.
"""

import os
from datetime import datetime
from typing import List, Dict, Any, Optional, Union, Tuple

from expense_tracker.services.expense_service import ExpenseService
from expense_tracker.services.budget_service import BudgetService
from expense_tracker.utils.formatters import (
    format_currency, format_date, format_month_year,
    format_percentage, format_table, export_to_csv, format_budget_status
)
from expense_tracker.utils.validators import validate_month_year


class ReportService:
    """Service class for generating reports."""
    
    @staticmethod
    def generate_monthly_summary(
        month: int,
        year: int,
        user_id: int = 1,
        format_type: str = "text"
    ) -> str:
        """Generate a monthly summary report.
        
        Args:
            month: Month number (1-12)
            year: Year
            user_id: User ID
            format_type: Output format (text or csv)
            
        Returns:
            str: Formatted report
        """
        # Validate month and year
        date_params = validate_month_year(month, year)
        month = date_params["month"]
        year = date_params["year"]
        
        # Get expense totals by category
        category_totals = ExpenseService.get_expense_totals_by_category(month, year, user_id)
        
        # Calculate the total expenses
        total_amount = sum(item["total"] for item in category_totals)
        
        # Prepare data for report
        report_data = [
            {
                "category": item["category"],
                "amount": format_currency(item["total"]),
                "percentage": format_percentage(item["total"] / total_amount if total_amount > 0 else 0)
            }
            for item in category_totals
        ]
        
        # Add total row
        report_data.append({
            "category": "TOTAL",
            "amount": format_currency(total_amount),
            "percentage": "100.0%"
        })
        
        # Define headers
        headers = {
            "category": "Category",
            "amount": "Amount",
            "percentage": "% of Total"
        }
        
        # Generate report
        if format_type.lower() == "csv":
            return export_to_csv(report_data, headers)
        else:
            title = f"Monthly Expense Summary - {format_month_year(month, year)}"
            return format_table(report_data, headers, title)
    
    @staticmethod
    def generate_category_comparison(
        month: int,
        year: int,
        user_id: int = 1,
        format_type: str = "text"
    ) -> str:
        """Generate a category comparison report (budget vs. actual).
        
        Args:
            month: Month number (1-12)
            year: Year
            user_id: User ID
            format_type: Output format (text or csv)
            
        Returns:
            str: Formatted report
        """
        # Validate month and year
        date_params = validate_month_year(month, year)
        month = date_params["month"]
        year = date_params["year"]
        
        # Get budget status
        budget_status = BudgetService.get_budget_status(month, year, user_id)
        
        # Prepare data for report
        report_data = [
            {
                "category": status["category"],
                "budget": format_currency(status["budget"]),
                "actual": format_currency(status["spent"]),
                "difference": format_currency(status["remaining"]),
                "percentage": format_percentage(status["percentage_used"]),
                "status": format_budget_status(status["spent"], status["budget"])
            }
            for status in budget_status
        ]
        
        # Define headers
        headers = {
            "category": "Category",
            "budget": "Budget",
            "actual": "Actual",
            "difference": "Remaining",
            "percentage": "% Used",
            "status": "Status"
        }
        
        # Generate report
        if format_type.lower() == "csv":
            return export_to_csv(report_data, headers)
        else:
            title = f"Budget vs. Actual - {format_month_year(month, year)}"
            return format_table(report_data, headers, title)
    
    @staticmethod
    def generate_annual_summary(
        year: int,
        user_id: int = 1,
        format_type: str = "text"
    ) -> str:
        """Generate an annual summary report.
        
        Args:
            year: Year
            user_id: User ID
            format_type: Output format (text or csv)
            
        Returns:
            str: Formatted report
        """
        # Get monthly totals
        monthly_totals = ExpenseService.get_expense_totals_by_month(year, user_id)
        
        # Calculate the total expenses
        total_amount = sum(item["total"] for item in monthly_totals)
        
        # Prepare data for report
        report_data = [
            {
                "month": format_month_year(item["month"], year),
                "amount": format_currency(item["total"]),
                "percentage": format_percentage(item["total"] / total_amount if total_amount > 0 else 0)
            }
            for item in monthly_totals
        ]
        
        # Add total row
        report_data.append({
            "month": "TOTAL",
            "amount": format_currency(total_amount),
            "percentage": "100.0%"
        })
        
        # Define headers
        headers = {
            "month": "Month",
            "amount": "Amount",
            "percentage": "% of Total"
        }
        
        # Generate report
        if format_type.lower() == "csv":
            return export_to_csv(report_data, headers)
        else:
            title = f"Annual Expense Summary - {year}"
            return format_table(report_data, headers, title)
    
    @staticmethod
    def export_report_to_file(report_content: str, filename: str) -> Tuple[bool, str]:
        """Export a report to a file.
        
        Args:
            report_content: The report content
            filename: The filename to save
            
        Returns:
            Tuple[bool, str]: Success flag and message
        """
        try:
            with open(filename, "w") as f:
                f.write(report_content)
            return True, f"Report saved to {os.path.abspath(filename)}"
        except Exception as e:
            return False, f"Error saving report: {str(e)}" 