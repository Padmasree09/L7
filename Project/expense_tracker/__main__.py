"""
Main module for the Expense Tracker application.

This is the entry point for the application when invoked with
`python -m expense_tracker`.
"""

import sys
from expense_tracker.cli import cli

if __name__ == "__main__":
    cli() 