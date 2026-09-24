from datetime import datetime, date
from models import db


class SavingsGoal(db.Model):
    """User savings target and milestone tracker."""
    __tablename__ = 'savings_goals'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    name = db.Column(db.String(120), nullable=False)
    target_amount = db.Column(db.Float, nullable=False)
    current_amount = db.Column(db.Float, nullable=False, default=0.0)
    target_date = db.Column(db.Date, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.now)

    @property
    def remaining_amount(self) -> float:
        return max(0.0, round(self.target_amount - self.current_amount, 2))

    @property
    def progress_percentage(self) -> float:
        if self.target_amount <= 0:
            return 0.0
        pct = (self.current_amount / self.target_amount) * 100.0
        return min(100.0, round(pct, 1))

    @property
    def is_completed(self) -> bool:
        return self.current_amount >= self.target_amount

    @property
    def suggested_monthly_savings(self) -> float:
        """Calculates needed monthly saving to reach target by target_date."""
        rem = self.remaining_amount
        if rem <= 0:
            return 0.0
        if not self.target_date:
            return rem

        today = date.today()
        if self.target_date <= today:
            return rem

        # Calculate approximate months remaining
        months_diff = (self.target_date.year - today.year) * 12 + (self.target_date.month - today.month)
        # If target is later this month or less than 1 month away, treat as 1 month
        if months_diff <= 0:
            months_diff = 1

        return round(rem / months_diff, 2)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.name,
            'target_amount': self.target_amount,
            'current_amount': self.current_amount,
            'remaining_amount': self.remaining_amount,
            'progress_percentage': self.progress_percentage,
            'is_completed': self.is_completed,
            'suggested_monthly_savings': self.suggested_monthly_savings,
            'target_date': self.target_date.strftime('%Y-%m-%d') if self.target_date else None,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None
        }

    def __repr__(self):
        return f'<SavingsGoal {self.name}: ₹{self.current_amount}/₹{self.target_amount}>'
