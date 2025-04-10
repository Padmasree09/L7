FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Initialize the database
RUN python -m expense_tracker.db.init_db

# Set the entrypoint
ENTRYPOINT ["python", "-m", "expense_tracker"]

# Default command
CMD ["--help"] 