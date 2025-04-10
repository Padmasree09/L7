"""
Expense sharing service module for group expense management.
"""

from datetime import datetime
from typing import List, Dict, Any, Optional, Union, Tuple
from sqlalchemy.orm import Session

from expense_tracker.db.models import Expense, User
from expense_tracker.db.session import get_db_session
from expense_tracker.services.expense_service import ExpenseService
from expense_tracker.utils.validators import validate_amount, validate_date, validate_string


class SharingService:
    """Service class for expense sharing between users."""
    
    @staticmethod
    def add_shared_expense(
        amount: Union[float, str],
        category_name: str,
        description: Optional[str] = None,
        date_str: Optional[str] = None,
        payer_id: int = 1,
        participant_ids: List[int] = None,
        split_type: str = "equal"
    ) -> Dict[str, Any]:
        """Add a shared expense.
        
        Args:
            amount: Total expense amount
            category_name: Category name
            description: Optional description
            date_str: Date string (YYYY-MM-DD)
            payer_id: ID of the user who paid
            participant_ids: List of participant user IDs (including payer)
            split_type: How to split the expense (equal, percentage, amount)
            
        Returns:
            Dict containing the created expense details
            
        Raises:
            ValueError: If validation fails or data is invalid
        """
        # Validate inputs
        amount_float = validate_amount(amount)
        date_obj = validate_date(date_str)
        if description:
            description = validate_string(description, "description")
        
        # Ensure the payer is included in participants
        if participant_ids is None:
            participant_ids = [payer_id]
        elif payer_id not in participant_ids:
            participant_ids.append(payer_id)
        
        # Create the group expense
        expense = ExpenseService.add_expense(
            amount=amount_float,
            category_name=category_name,
            description=description,
            date_str=date_str,
            user_id=payer_id,
            is_group_expense=True,
            participant_ids=participant_ids
        )
        
        # Calculate individual shares based on split type
        num_participants = len(participant_ids)
        individual_amount = amount_float / num_participants
        
        # Store expense details including split information
        expense_detail = {
            **expense,
            'payer_id': payer_id,
            'participant_ids': participant_ids,
            'split_type': split_type,
            'individual_amount': individual_amount,
            'total_amount': amount_float
        }
        
        return expense_detail
    
    @staticmethod
    def get_shared_expenses_for_user(user_id: int) -> List[Dict[str, Any]]:
        """Get all shared expenses involving a user.
        
        Args:
            user_id: User ID
            
        Returns:
            List of shared expense dictionaries
        """
        with get_db_session() as db:
            # Find all expenses where the user is a participant
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                return []
            
            shared_expenses = []
            for expense in user.shared_expenses:
                if expense.is_group_expense:
                    # Extract participant information
                    participants = [
                        {
                            'id': participant.id,
                            'username': participant.username,
                            'is_payer': participant.id == expense.user_id
                        }
                        for participant in expense.participants
                    ]
                    
                    # Calculate individual amount
                    individual_amount = expense.amount / len(participants)
                    
                    # Add to result
                    shared_expenses.append({
                        'id': expense.id,
                        'amount': expense.amount,
                        'description': expense.description,
                        'date': expense.date,
                        'category': expense.category.name,
                        'payer': {
                            'id': expense.user.id,
                            'username': expense.user.username
                        },
                        'participants': participants,
                        'individual_amount': individual_amount,
                        'user_is_payer': expense.user_id == user_id
                    })
            
            return shared_expenses
    
    @staticmethod
    def calculate_balances(user_id: int) -> List[Dict[str, Any]]:
        """Calculate balances with other users.
        
        Args:
            user_id: User ID
            
        Returns:
            List of balance dictionaries
        """
        # Get all shared expenses for the user
        shared_expenses = SharingService.get_shared_expenses_for_user(user_id)
        
        # Calculate balances
        balances = {}
        for expense in shared_expenses:
            payer_id = expense['payer']['id']
            payer_name = expense['payer']['username']
            individual_amount = expense['individual_amount']
            
            for participant in expense['participants']:
                participant_id = participant['id']
                participant_name = participant['username']
                
                # Skip self interactions
                if participant_id == user_id:
                    continue
                
                # Initialize balance entry if needed
                if participant_id not in balances:
                    balances[participant_id] = {
                        'user_id': participant_id,
                        'username': participant_name,
                        'owes_me': 0.0,
                        'i_owe': 0.0,
                        'net_balance': 0.0
                    }
                
                # Update balance based on who paid
                if payer_id == user_id and participant_id != user_id:
                    # I paid, they owe me
                    balances[participant_id]['owes_me'] += individual_amount
                    balances[participant_id]['net_balance'] += individual_amount
                elif payer_id == participant_id:
                    # They paid, I owe them
                    balances[participant_id]['i_owe'] += individual_amount
                    balances[participant_id]['net_balance'] -= individual_amount
        
        # Convert to list and calculate total
        balance_list = list(balances.values())
        
        # Add total balance
        total_owed_to_me = sum(b['owes_me'] for b in balance_list)
        total_i_owe = sum(b['i_owe'] for b in balance_list)
        net_balance = total_owed_to_me - total_i_owe
        
        # Add summary to the beginning
        balance_list.insert(0, {
            'user_id': None,
            'username': 'TOTAL',
            'owes_me': total_owed_to_me,
            'i_owe': total_i_owe,
            'net_balance': net_balance
        })
        
        return balance_list
    
    @staticmethod
    def settle_balance(
        from_user_id: int,
        to_user_id: int,
        amount: Union[float, str],
        date_str: Optional[str] = None,
        description: Optional[str] = None
    ) -> Dict[str, Any]:
        """Record a settlement payment between users.
        
        Args:
            from_user_id: ID of the user making the payment
            to_user_id: ID of the user receiving the payment
            amount: Payment amount
            date_str: Date string (YYYY-MM-DD)
            description: Optional description
            
        Returns:
            Dict containing the settlement details
        """
        # Validate inputs
        amount_float = validate_amount(amount)
        date_obj = validate_date(date_str)
        
        if description is None:
            description = f"Balance settlement payment"
        else:
            description = validate_string(description, "description")
        
        # Create a settlement expense
        settlement = ExpenseService.add_expense(
            amount=amount_float,
            category_name="Settlements",
            description=description,
            date_str=date_str,
            user_id=from_user_id,
            is_group_expense=True,
            participant_ids=[from_user_id, to_user_id]
        )
        
        # Return settlement details
        return {
            **settlement,
            'from_user_id': from_user_id,
            'to_user_id': to_user_id,
            'is_settlement': True
        } 