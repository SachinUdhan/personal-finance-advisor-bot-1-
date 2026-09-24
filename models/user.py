from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from models import db


class User(db.Model):
    """User account model with secure password hashing and personal financial profile."""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, index=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    monthly_income = db.Column(db.Float, nullable=False, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.now)

    # Relationships
    incomes = db.relationship('Income', backref='user', cascade='all, delete-orphan', lazy=True)
    expenses = db.relationship('Expense', backref='user', cascade='all, delete-orphan', lazy=True)
    goals = db.relationship('SavingsGoal', backref='user', cascade='all, delete-orphan', lazy=True)
    budgets = db.relationship('BudgetCategory', backref='user', cascade='all, delete-orphan', lazy=True)

    def set_password(self, password: str):
        """Hashes password securely with Werkzeug pbkdf2."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        """Verifies candidate password against stored hash."""
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        """Serialize user public attributes (excluding sensitive credentials)."""
        return {
            'id': self.id,
            'full_name': self.full_name,
            'email': self.email,
            'age': self.age,
            'monthly_income': self.monthly_income,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None
        }

    def __repr__(self):
        return f'<User {self.email}>'
