"""
Command Line Interface for the Expense Tracker application.
"""

import os
import sys
import click
from datetime import datetime
from typing import Optional, Dict, List, Any

from expense_tracker.services.expense_service import ExpenseService
from expense_tracker.services.budget_service import BudgetService
from expense_tracker.services.report_service import ReportService
from expense_tracker.services.alert_service import AlertService
from expense_tracker.services.sharing_service import SharingService
from expense_tracker.utils.formatters import format_date, format_month_year


@click.group()
def cli():
    """Expense Tracker CLI."""
    pass


# Expense Commands
@cli.group()
def expense():
    """Manage expenses."""
    pass


@expense.command(name="add")
@click.option("--amount", required=True, help="Expense amount")
@click.option("--category", required=True, help="Expense category")
@click.option("--description", help="Expense description")
@click.option("--date", help="Expense date (YYYY-MM-DD)")
@click.option("--user-id", type=int, default=1, help="User ID")
def add_expense(amount, category, description, date, user_id):
    """Add a new expense."""
    try:
        expense = ExpenseService.add_expense(
            amount=amount,
            category_name=category,
            description=description,
            date_str=date,
            user_id=user_id
        )
        
        click.echo(f"Expense added successfully: ${expense['amount']:.2f} for {expense['category']} on {format_date(expense['date'])}")
        
        # Check for budget alerts
        alerts = AlertService.check_and_create_alerts(user_id)
        if alerts:
            click.echo("\nBudget Alerts:")
            for alert in alerts:
                click.echo(f"  - {alert['message']}")
    
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)


@expense.command(name="list")
@click.option("--from", "from_date", help="Start date (YYYY-MM-DD)")
@click.option("--to", "to_date", help="End date (YYYY-MM-DD)")
@click.option("--category", help="Filter by category")
@click.option("--user-id", type=int, default=1, help="User ID")
def list_expenses(from_date, to_date, category, user_id):
    """List expenses with optional filtering."""
    try:
        expenses = ExpenseService.get_expenses(
            start_date=from_date,
            end_date=to_date,
            category_name=category,
            user_id=user_id
        )
        
        if not expenses:
            click.echo("No expenses found.")
            return
        
        click.echo(f"\nExpenses ({len(expenses)}):")
        click.echo("-" * 80)
        click.echo(f"{'Date':<12} {'Category':<15} {'Amount':>10} {'Description':<40}")
        click.echo("-" * 80)
        
        for expense in expenses:
            date_str = format_date(expense['date'])
            description = expense['description'] or ""
            if len(description) > 37:
                description = description[:34] + "..."
            
            click.echo(
                f"{date_str:<12} {expense['category']:<15} "
                f"${expense['amount']:>8.2f} {description:<40}"
            )
        
        # Calculate total
        total = sum(expense['amount'] for expense in expenses)
        click.echo("-" * 80)
        click.echo(f"{'Total:':<28} ${total:>8.2f}")
    
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)


@expense.command(name="delete")
@click.argument("expense_id", type=int)
@click.option("--user-id", type=int, default=1, help="User ID")
def delete_expense(expense_id, user_id):
    """Delete an expense."""
    try:
        success = ExpenseService.delete_expense(expense_id, user_id)
        
        if success:
            click.echo(f"Expense {expense_id} deleted successfully.")
        else:
            click.echo(f"Expense {expense_id} not found or you don't have permission to delete it.")
    
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)


# Budget Commands
@cli.group()
def budget():
    """Manage budgets."""
    pass


@budget.command(name="set")
@click.option("--category", required=True, help="Budget category")
@click.option("--amount", required=True, help="Budget amount")
@click.option("--month", type=int, required=True, help="Month (1-12)")
@click.option("--year", type=int, required=True, help="Year")
@click.option("--alert-threshold", type=float, default=0.8, help="Alert threshold (0.0-1.0)")
@click.option("--user-id", type=int, default=1, help="User ID")
def set_budget(category, amount, month, year, alert_threshold, user_id):
    """Set a budget for a category and month."""
    try:
        budget = BudgetService.set_budget(
            category_name=category,
            amount=amount,
            month=month,
            year=year,
            user_id=user_id,
            alert_threshold=alert_threshold
        )
        
        month_year = format_month_year(budget['month'], budget['year'])
        click.echo(f"Budget set successfully: ${budget['amount']:.2f} for {budget['category']} in {month_year}")
    
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)


@budget.command(name="list")
@click.option("--month", type=int, help="Filter by month (1-12)")
@click.option("--year", type=int, help="Filter by year")
@click.option("--category", help="Filter by category")
@click.option("--user-id", type=int, default=1, help="User ID")
def list_budgets(month, year, category, user_id):
    """List budgets with optional filtering."""
    try:
        budgets = BudgetService.get_budgets(
            month=month,
            year=year,
            category_name=category,
            user_id=user_id
        )
        
        if not budgets:
            click.echo("No budgets found.")
            return
        
        click.echo(f"\nBudgets ({len(budgets)}):")
        click.echo("-" * 60)
        click.echo(f"{'Month':<15} {'Category':<15} {'Amount':>10} {'Alert at':>10}")
        click.echo("-" * 60)
        
        for budget in budgets:
            month_year = format_month_year(budget['month'], budget['year'])
            alert_percentage = budget['alert_threshold'] * 100
            
            click.echo(
                f"{month_year:<15} {budget['category']:<15} "
                f"${budget['amount']:>8.2f} {alert_percentage:>8.1f}%"
            )
    
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)


@budget.command(name="status")
@click.option("--month", type=int, required=True, help="Month (1-12)")
@click.option("--year", type=int, required=True, help="Year")
@click.option("--user-id", type=int, default=1, help="User ID")
def budget_status(month, year, user_id):
    """Show budget status for the current month."""
    try:
        status = BudgetService.get_budget_status(month, year, user_id)
        
        if not status:
            click.echo(f"No budgets found for {format_month_year(month, year)}.")
            return
        
        month_year = format_month_year(month, year)
        
        click.echo(f"\nBudget Status for {month_year}:")
        click.echo("-" * 80)
        click.echo(f"{'Category':<15} {'Budget':>10} {'Spent':>10} {'Remaining':>10} {'Used':>10} {'Status':<15}")
        click.echo("-" * 80)
        
        for item in status:
            percentage = item['percentage_used'] * 100
            alert_status = "OK"
            
            if percentage >= 100:
                alert_status = "EXCEEDED!"
            elif percentage >= item['alert_threshold'] * 100:
                alert_status = "WARNING"
            
            click.echo(
                f"{item['category']:<15} ${item['budget']:>8.2f} ${item['spent']:>8.2f} "
                f"${item['remaining']:>8.2f} {percentage:>8.1f}% {alert_status:<15}"
            )
        
        # Calculate totals
        total_budget = sum(item['budget'] for item in status)
        total_spent = sum(item['spent'] for item in status)
        total_remaining = total_budget - total_spent
        total_percentage = (total_spent / total_budget) * 100 if total_budget > 0 else 0
        
        click.echo("-" * 80)
        click.echo(
            f"{'TOTAL:':<15} ${total_budget:>8.2f} ${total_spent:>8.2f} "
            f"${total_remaining:>8.2f} {total_percentage:>8.1f}%"
        )
    
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)


@budget.command(name="delete")
@click.argument("budget_id", type=int)
@click.option("--user-id", type=int, default=1, help="User ID")
def delete_budget(budget_id, user_id):
    """Delete a budget."""
    try:
        success = BudgetService.delete_budget(budget_id, user_id)
        
        if success:
            click.echo(f"Budget {budget_id} deleted successfully.")
        else:
            click.echo(f"Budget {budget_id} not found or you don't have permission to delete it.")
    
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)


# Report Commands
@cli.group()
def report():
    """Generate reports."""
    pass


@report.command(name="monthly")
@click.option("--month", type=int, required=True, help="Month (1-12)")
@click.option("--year", type=int, required=True, help="Year")
@click.option("--export", help="Export to file (CSV)")
@click.option("--format", "format_type", type=click.Choice(["text", "csv"]), default="text", help="Output format")
@click.option("--user-id", type=int, default=1, help="User ID")
def monthly_report(month, year, export, format_type, user_id):
    """Generate a monthly expense summary report."""
    try:
        # Generate report
        report_content = ReportService.generate_monthly_summary(
            month=month,
            year=year,
            user_id=user_id,
            format_type=format_type
        )
        
        # Export or display
        if export:
            success, message = ReportService.export_report_to_file(report_content, export)
            if success:
                click.echo(message)
            else:
                click.echo(f"Error: {message}", err=True)
                sys.exit(1)
        else:
            click.echo(report_content)
    
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)


@report.command(name="category")
@click.option("--month", type=int, required=True, help="Month (1-12)")
@click.option("--year", type=int, required=True, help="Year")
@click.option("--export", help="Export to file (CSV)")
@click.option("--format", "format_type", type=click.Choice(["text", "csv"]), default="text", help="Output format")
@click.option("--user-id", type=int, default=1, help="User ID")
def category_report(month, year, export, format_type, user_id):
    """Generate a category comparison report (budget vs. actual)."""
    try:
        # Generate report
        report_content = ReportService.generate_category_comparison(
            month=month,
            year=year,
            user_id=user_id,
            format_type=format_type
        )
        
        # Export or display
        if export:
            success, message = ReportService.export_report_to_file(report_content, export)
            if success:
                click.echo(message)
            else:
                click.echo(f"Error: {message}", err=True)
                sys.exit(1)
        else:
            click.echo(report_content)
    
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)


@report.command(name="annual")
@click.option("--year", type=int, required=True, help="Year")
@click.option("--export", help="Export to file (CSV)")
@click.option("--format", "format_type", type=click.Choice(["text", "csv"]), default="text", help="Output format")
@click.option("--user-id", type=int, default=1, help="User ID")
def annual_report(year, export, format_type, user_id):
    """Generate an annual expense summary report."""
    try:
        # Generate report
        report_content = ReportService.generate_annual_summary(
            year=year,
            user_id=user_id,
            format_type=format_type
        )
        
        # Export or display
        if export:
            success, message = ReportService.export_report_to_file(report_content, export)
            if success:
                click.echo(message)
            else:
                click.echo(f"Error: {message}", err=True)
                sys.exit(1)
        else:
            click.echo(report_content)
    
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)


# Alert Commands
@cli.group()
def alert():
    """Manage alerts."""
    pass


@alert.command(name="list")
@click.option("--include-read", is_flag=True, help="Include read alerts")
@click.option("--user-id", type=int, default=1, help="User ID")
def list_alerts(include_read, user_id):
    """List budget alerts."""
    try:
        alerts = AlertService.get_alerts(user_id, include_read)
        
        if not alerts:
            click.echo("No alerts found.")
            return
        
        status_text = "All" if include_read else "Unread"
        click.echo(f"\n{status_text} Alerts ({len(alerts)}):")
        click.echo("-" * 80)
        
        for alert in alerts:
            date_str = format_date(alert['created_at'])
            status = "READ" if alert['is_read'] else "NEW"
            
            click.echo(f"[{status}] {date_str} - {alert['message']}")
    
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)


@alert.command(name="check")
@click.option("--send-email", is_flag=True, help="Send email notifications")
@click.option("--email", help="Email address to send notifications to")
@click.option("--user-id", type=int, default=1, help="User ID")
def check_alerts(send_email, email, user_id):
    """Check budgets and create alerts if needed."""
    try:
        if send_email:
            success, message = AlertService.check_and_send_notifications(user_id, email)
            click.echo(message)
        else:
            alerts = AlertService.check_and_create_alerts(user_id)
            
            if not alerts:
                click.echo("No budget alerts detected.")
                return
            
            click.echo(f"\nBudget Alerts ({len(alerts)}):")
            click.echo("-" * 80)
            
            for alert in alerts:
                click.echo(f"- {alert['message']}")
    
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)


@alert.command(name="mark-read")
@click.argument("alert_id", type=int)
@click.option("--user-id", type=int, default=1, help="User ID")
def mark_alert_read(alert_id, user_id):
    """Mark an alert as read."""
    try:
        success = AlertService.mark_alert_as_read(alert_id, user_id)
        
        if success:
            click.echo(f"Alert {alert_id} marked as read.")
        else:
            click.echo(f"Alert {alert_id} not found or you don't have permission to modify it.")
    
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)


@alert.command(name="mark-all-read")
@click.option("--user-id", type=int, default=1, help="User ID")
def mark_all_read(user_id):
    """Mark all alerts as read."""
    try:
        count = AlertService.mark_all_alerts_as_read(user_id)
        
        if count > 0:
            click.echo(f"{count} alerts marked as read.")
        else:
            click.echo("No unread alerts found.")
    
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)


# Sharing Commands
@cli.group()
def share():
    """Manage shared expenses."""
    pass


@share.command(name="add")
@click.option("--amount", required=True, help="Expense amount")
@click.option("--category", required=True, help="Expense category")
@click.option("--description", help="Expense description")
@click.option("--date", help="Expense date (YYYY-MM-DD)")
@click.option("--payer-id", type=int, required=True, help="ID of the user who paid")
@click.option("--participant", "participants", type=int, multiple=True, help="Participant user IDs")
def add_shared(amount, category, description, date, payer_id, participants):
    """Add a shared expense."""
    try:
        participant_ids = list(participants)
        if not participant_ids:
            click.echo("Error: At least one participant is required.", err=True)
            sys.exit(1)
        
        expense = SharingService.add_shared_expense(
            amount=amount,
            category_name=category,
            description=description,
            date_str=date,
            payer_id=payer_id,
            participant_ids=participant_ids
        )
        
        date_str = format_date(expense['date'])
        participants_count = len(participant_ids)
        individual_amount = expense['individual_amount']
        
        click.echo(f"Shared expense added successfully:")
        click.echo(f"  Amount: ${expense['amount']:.2f} for {expense['category']} on {date_str}")
        click.echo(f"  Split among {participants_count} participants, ${individual_amount:.2f} each")
    
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)


@share.command(name="list")
@click.option("--user-id", type=int, required=True, help="User ID")
def list_shared(user_id):
    """List shared expenses for a user."""
    try:
        expenses = SharingService.get_shared_expenses_for_user(user_id)
        
        if not expenses:
            click.echo("No shared expenses found.")
            return
        
        click.echo(f"\nShared Expenses ({len(expenses)}):")
        click.echo("-" * 90)
        click.echo(f"{'Date':<12} {'Category':<15} {'Amount':>10} {'Your Share':>10} {'Paid By':<15} {'Description':<25}")
        click.echo("-" * 90)
        
        for expense in expenses:
            date_str = format_date(expense['date'])
            description = expense['description'] or ""
            if len(description) > 22:
                description = description[:19] + "..."
            
            individual_amount = expense['individual_amount']
            payer_name = expense['payer']['username']
            
            click.echo(
                f"{date_str:<12} {expense['category']:<15} "
                f"${expense['amount']:>8.2f} ${individual_amount:>8.2f} "
                f"{payer_name:<15} {description:<25}"
            )
    
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)


@share.command(name="balances")
@click.option("--user-id", type=int, required=True, help="User ID")
def show_balances(user_id):
    """Show balances with other users."""
    try:
        balances = SharingService.calculate_balances(user_id)
        
        if len(balances) <= 1:
            click.echo("No balance information found.")
            return
        
        click.echo(f"\nBalances:")
        click.echo("-" * 70)
        click.echo(f"{'User':<20} {'They Owe You':>15} {'You Owe Them':>15} {'Net Balance':>15}")
        click.echo("-" * 70)
        
        for balance in balances:
            username = balance['username']
            owes_me = balance['owes_me']
            i_owe = balance['i_owe']
            net = balance['net_balance']
            
            # Format net balance
            if net >= 0:
                net_str = f"+${net:.2f}"
            else:
                net_str = f"-${abs(net):.2f}"
            
            click.echo(
                f"{username:<20} ${owes_me:>13.2f} ${i_owe:>13.2f} {net_str:>15}"
            )
    
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)


@share.command(name="settle")
@click.option("--from-id", type=int, required=True, help="ID of the user making the payment")
@click.option("--to-id", type=int, required=True, help="ID of the user receiving the payment")
@click.option("--amount", required=True, help="Settlement amount")
@click.option("--date", help="Settlement date (YYYY-MM-DD)")
@click.option("--description", help="Optional description")
def settle_balance(from_id, to_id, amount, date, description):
    """Record a settlement payment between users."""
    try:
        settlement = SharingService.settle_balance(
            from_user_id=from_id,
            to_user_id=to_id,
            amount=amount,
            date_str=date,
            description=description
        )
        
        date_str = format_date(settlement['date'])
        
        click.echo(f"Settlement recorded successfully:")
        click.echo(f"  Amount: ${settlement['amount']:.2f} on {date_str}")
        click.echo(f"  From user {from_id} to user {to_id}")
    
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1) 