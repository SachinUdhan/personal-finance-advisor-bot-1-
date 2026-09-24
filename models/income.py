from datetime import datetime, date
from models import db


class Income(db.Model):
    """User income transaction record."""
    __tablename__ = 'incomes'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    source = db.Column(db.String(100), nullable=False)
    income_type = db.Column(db.String(50), nullable=False, default='Salary')  # Salary, Freelance, Business, Other
    amount = db.Column(db.Float, nullable=False)
    date = db.Column(db.Date, nullable=False, default=date.today)
    created_at = db.Column(db.DateTime, default=datetime.now)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'source': self.source,
            'income_type': self.income_type,
            'amount': self.amount,
            'date': self.date.strftime('%Y-%m-%d') if self.date else None,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None
        }

    def __repr__(self):
        return f'<Income {self.source}: ₹{self.amount}>'
