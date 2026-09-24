from flask import Blueprint, render_template, g
from models import Income, Expense, SavingsGoal, BudgetCategory
from routes import login_required
from services.report_generator import generate_monthly_report_data
from services.finance_calculator import format_inr

report_bp = Blueprint('report', __name__)


@report_bp.route('/report', methods=['GET'])
@login_required
def view_report():
    user = g.user

    incomes = Income.query.filter_by(user_id=user.id).order_by(Income.date.asc()).all()
    expenses = Expense.query.filter_by(user_id=user.id).order_by(Expense.date.asc()).all()
    goals = SavingsGoal.query.filter_by(user_id=user.id).all()
    budgets = BudgetCategory.query.filter_by(user_id=user.id).all()

    report_data = generate_monthly_report_data(
        user=user,
        incomes=incomes,
        expenses=expenses,
        goals=goals,
        budgets=budgets
    )

    return render_template(
        'report.html',
        user=user,
        report=report_data,
        format_inr=format_inr
    )
