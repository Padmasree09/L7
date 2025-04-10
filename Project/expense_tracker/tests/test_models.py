"""
Tests for the database models.
"""

import unittest
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from expense_tracker.db.models import Base, User, Category, Expense, Budget, Alert


class TestModels(unittest.TestCase):
    """Test cases for the database models."""

    def setUp(self):
        """Set up test fixtures."""
        # Create an in-memory SQLite database for testing
        self.engine = create_engine('sqlite:///:memory:')
        
        # Create tables
        Base.metadata.create_all(self.engine)
        
        # Create a session
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
        
        # Add test data
        self.create_test_data()

    def tearDown(self):
        """Clean up after tests."""
        self.session.close()
        Base.metadata.drop_all(self.engine)

    def create_test_data(self):
        """Create test data for database tests."""
        # Create users
        self.user1 = User(username='user1', email='user1@example.com')
        self.user2 = User(username='user2', email='user2@example.com')
        self.session.add_all([self.user1, self.user2])
        
        # Create categories
        self.food_category = Category(name='Food', description='Food expenses', is_default=True)
        self.transport_category = Category(name='Transport', description='Transport expenses', is_default=True)
        self.session.add_all([self.food_category, self.transport_category])
        
        # Create expenses
        self.expense1 = Expense(
            amount=50.0,
            description='Groceries',
            date=datetime(2023, 5, 15),
            user=self.user1,
            category=self.food_category
        )
        self.expense2 = Expense(
            amount=30.0,
            description='Bus ticket',
            date=datetime(2023, 5, 16),
            user=self.user1,
            category=self.transport_category
        )
        self.expense3 = Expense(
            amount=20.0,
            description='Lunch',
            date=datetime(2023, 5, 17),
            user=self.user2,
            category=self.food_category
        )
        self.session.add_all([self.expense1, self.expense2, self.expense3])
        
        # Create budgets
        self.budget1 = Budget(
            amount=200.0,
            month=5,
            year=2023,
            user=self.user1,
            category=self.food_category,
            alert_threshold=0.8
        )
        self.budget2 = Budget(
            amount=100.0,
            month=5,
            year=2023,
            user=self.user1,
            category=self.transport_category,
            alert_threshold=0.7
        )
        self.session.add_all([self.budget1, self.budget2])
        
        # Create alerts
        self.alert1 = Alert(
            message='Budget alert for Food category',
            user_id=self.user1.id,
            budget_id=self.budget1.id
        )
        self.session.add(self.alert1)
        
        # Create a group expense with participants
        self.group_expense = Expense(
            amount=30.0,  # Split amount
            description='Dinner',
            date=datetime(2023, 5, 18),
            user=self.user1,
            category=self.food_category,
            is_group_expense=True,
            total_amount=60.0  # Total before splitting
        )
        self.group_expense.participants.append(self.user1)
        self.group_expense.participants.append(self.user2)
        self.session.add(self.group_expense)
        
        # Commit the changes
        self.session.commit()

    def test_user_relationships(self):
        """Test User model relationships."""
        # Test expenses relationship
        user1 = self.session.query(User).filter_by(username='user1').first()
        self.assertEqual(len(user1.expenses), 3)  # 2 regular expenses + 1 group expense
        
        # Test budgets relationship
        self.assertEqual(len(user1.budgets), 2)
        
        # Test shared_expenses relationship
        self.assertEqual(len(user1.shared_expenses), 1)
        
        # Test user2's shared expenses
        user2 = self.session.query(User).filter_by(username='user2').first()
        self.assertEqual(len(user2.shared_expenses), 1)

    def test_category_relationships(self):
        """Test Category model relationships."""
        # Test expenses relationship
        food_category = self.session.query(Category).filter_by(name='Food').first()
        self.assertEqual(len(food_category.expenses), 3)  # 2 regular + 1 group expense
        
        # Test budgets relationship
        self.assertEqual(len(food_category.budgets), 1)

    def test_expense_relationships(self):
        """Test Expense model relationships."""
        # Test user relationship
        expense = self.session.query(Expense).filter_by(description='Groceries').first()
        self.assertEqual(expense.user.username, 'user1')
        
        # Test category relationship
        self.assertEqual(expense.category.name, 'Food')
        
        # Test group expense and participants
        group_expense = self.session.query(Expense).filter_by(description='Dinner').first()
        self.assertTrue(group_expense.is_group_expense)
        self.assertEqual(group_expense.total_amount, 60.0)
        self.assertEqual(len(group_expense.participants), 2)
        participant_ids = [p.id for p in group_expense.participants]
        self.assertIn(self.user1.id, participant_ids)
        self.assertIn(self.user2.id, participant_ids)

    def test_budget_relationships(self):
        """Test Budget model relationships."""
        # Test user relationship
        budget = self.session.query(Budget).filter_by(amount=200.0).first()
        self.assertEqual(budget.user.username, 'user1')
        
        # Test category relationship
        self.assertEqual(budget.category.name, 'Food')

    def test_alert_relationships(self):
        """Test Alert model relationships."""
        # Get the alert
        alert = self.session.query(Alert).first()
        
        # Verify alert properties
        self.assertEqual(alert.message, 'Budget alert for Food category')
        self.assertFalse(alert.is_read)
        self.assertIsNotNone(alert.created_at)
        
        # Verify the budget_id reference
        self.assertEqual(alert.budget_id, self.budget1.id)
        
        # Verify the user_id reference
        self.assertEqual(alert.user_id, self.user1.id)

    def test_expense_constraints(self):
        """Test Expense model constraints."""
        # Create an expense with invalid category_id
        invalid_expense = Expense(
            amount=25.0,
            description='Invalid expense',
            user_id=self.user1.id,
            category_id=999  # Non-existent category
        )
        self.session.add(invalid_expense)
        
        # Should raise an integrity error when committed
        with self.assertRaises(Exception):
            self.session.commit()
        
        # Rollback the session for the next test
        self.session.rollback()
        
    def test_budget_constraints(self):
        """Test Budget model constraints."""
        # Create a budget with invalid user_id
        invalid_budget = Budget(
            amount=150.0,
            month=5,
            year=2023,
            user_id=999,  # Non-existent user
            category_id=self.food_category.id
        )
        self.session.add(invalid_budget)
        
        # Should raise an integrity error when committed
        with self.assertRaises(Exception):
            self.session.commit()
        
        # Rollback the session
        self.session.rollback()


if __name__ == '__main__':
    unittest.main() 