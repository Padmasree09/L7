# Expense Tracker & Savings Goal Manager

A comprehensive Python application for tracking daily expenses and managing savings goals with advanced budgeting features.

## Features

### Core Features

- **Expense Logging**: Track expenses with date, amount, category, and description
- **Budget Management**: Set and monitor category-specific monthly budgets
- **Expense Categorization**: Organize expenses by predefined or custom categories
- **Reporting**: Generate monthly spending summaries and budget comparisons

### Advanced Features

- **Multi-Month Budgeting**: Set different budgets for different months
- **Custom Alerts**: Receive notifications when spending approaches budget limits
- **Email Notifications**: Get alerts via email for important budget events
- **Group Expense Sharing**: Split and track expenses among multiple people

## Installation

### Prerequisites

- Python 3.8+
- SQLite3 (included in Python)

### Standard Installation

1. Clone the repository

   ```
   git clone https://github.com/yourusername/expense-tracker.git
   cd expense-tracker
   ```

2. Create a virtual environment (optional but recommended)

   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies

   ```
   pip install -r requirements.txt
   ```

4. Initialize the database

   ```
   python -m expense_tracker.db.init_db
   ```

5. Run the application
   ```
   python -m expense_tracker
   ```

### Docker Installation

1. Build the Docker image

   ```
   docker build -t expense-tracker .
   ```

2. Run the container
   ```
   docker run -p 5000:5000 expense-tracker
   ```

## Usage

### Managing Expenses

```python
# Add a new expense
python -m expense_tracker expense add --amount 25.50 --category "Food" --description "Lunch at cafe" --date "2023-05-15"

# View all expenses
python -m expense_tracker expense list

# View expenses by category
python -m expense_tracker expense list --category "Food"

# View expenses by date range
python -m expense_tracker expense list --from "2023-05-01" --to "2023-05-31"
```

### Managing Budgets

```python
# Set a monthly budget for a category
python -m expense_tracker budget set --category "Food" --amount 300 --month "2023-05"

# View all budgets
python -m expense_tracker budget list

# View budget status (with spending)
python -m expense_tracker budget status
```

### Generating Reports

```python
# Monthly summary report (specify both year and month)
python -m expense_tracker report monthly --year 2023 --month 5  # For May 2023

# Sample output:
# Monthly Expense Summary - May 2023
# ==================================
# +------------+----------+--------------+
# | Category   | Amount   | % of Total   |
# +============+==========+==============+
# | Food       | $25.50   | 100.0%      |
# +------------+----------+--------------+
# | TOTAL      | $25.50   | 100.0%      |
# +------------+----------+--------------+

# Category comparison report (specify both year and month)
python -m expense_tracker report category --year 2023 --month 5  # For May 2023

# Sample output:
# Budget vs. Actual - May 2023
# ============================
# +------------+----------+----------+-------------+----------+----------+
# | Category   | Budget   | Actual   | Remaining   | % Used   | Status   |
# +============+==========+==========+=============+==========+==========+
# +------------+----------+----------+-------------+----------+----------+

# Export report to CSV (specify filename)
python -m expense_tracker report monthly --year 2023 --month 5 --export monthly_report.csv
```

Note:

- The month parameter uses numbers 1-12 representing the months (e.g., 1 for January, 12 for December)
- The year parameter is required and should be specified in YYYY format
- When using --export, you must provide a filename for the CSV export

## Testing

Run the test suite with:

```bash
pytest
```

## Project Structure

```
expense_tracker/
├── __init__.py
├── __main__.py
├── cli.py
├── config.py
├── db/
│   ├── __init__.py
│   ├── init_db.py
│   ├── models.py
│   └── session.py
├── services/
│   ├── __init__.py
│   ├── expense_service.py
│   ├── budget_service.py
│   ├── alert_service.py
│   ├── report_service.py
│   ├── notification_service.py
│   └── sharing_service.py
├── utils/
│   ├── __init__.py
│   ├── validators.py
│   └── formatters.py
└── tests/
    ├── __init__.py
    ├── test_expense_service.py
    ├── test_budget_service.py
    ├── test_alert_service.py
    ├── test_report_service.py
    └── test_notification_service.py
```

## License

MIT
