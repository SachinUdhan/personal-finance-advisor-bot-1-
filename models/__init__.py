from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from models.user import User
from models.income import Income
from models.expense import Expense
from models.goal import SavingsGoal
from models.budget import BudgetCategory

__all__ = ['db', 'User', 'Income', 'Expense', 'SavingsGoal', 'BudgetCategory']
