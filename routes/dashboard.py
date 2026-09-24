from flask import Blueprint, render_template, jsonify, g, session, redirect, url_for
from models import db, Income, Expense, SavingsGoal, BudgetCategory
from routes import login_required
from services.finance_calculator import format_inr, calculate_savings_rate
from services.financial_health import calculate_financial_health_score
from services.ai_advisor import generate_personalized_tips

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/')
def landing():
    """Fintech-style landing page."""
    if session.get('user_id'):
        return redirect(url_for('dashboard.index'))
    return render_template('index.html')


@dashboard_bp.route('/dashboard')
@login_required
def index():
    """Main authenticated financial overview dashboard."""
    user = g.user

    # Fetch user transactions (Strict user data isolation)
    user_incomes = Income.query.filter_by(user_id=user.id).order_by(Income.date.desc()).all()
    user_expenses = Expense.query.filter_by(user_id=user.id).order_by(Expense.date.desc()).all()
    user_goals = SavingsGoal.query.filter_by(user_id=user.id).order_by(SavingsGoal.created_at.desc()).all()
    user_budgets = BudgetCategory.query.filter_by(user_id=user.id).all()

    # Calculate Monthly Income (Sum of income records or fallback to baseline monthly_income)
    recorded_income = sum(float(i.amount) for i in user_incomes)
    effective_income = recorded_income if recorded_income > 0 else float(user.monthly_income or 0.0)

    total_expenses = sum(float(e.amount) for e in user_expenses)
    current_savings = effective_income - total_expenses
    savings_rate = calculate_savings_rate(effective_income, total_expenses)

    # Budget total
    planned_budget = sum(float(b.planned_amount) for b in user_budgets)

    # Financial Health Score
    health_data = calculate_financial_health_score(
        income=effective_income,
        expenses=total_expenses,
        planned_budget=planned_budget,
        goals=user_goals
    )

    # Category breakdown for charts and tips
    category_totals = {}
    for exp in user_expenses:
        cat = exp.category
        category_totals[cat] = category_totals.get(cat, 0.0) + float(exp.amount)

    sorted_categories = sorted(category_totals.items(), key=lambda x: x[1], reverse=True)
    top_cat = sorted_categories[0][0] if sorted_categories else "None"
    top_cat_amt = sorted_categories[0][1] if sorted_categories else 0.0

    # Financial context for tips
    context = {
        'total_income': effective_income,
        'total_expenses': total_expenses,
        'savings_rate': savings_rate,
        'category_totals': category_totals,
        'top_category': top_cat,
        'top_category_amount': top_cat_amt,
        'goals': [g.to_dict() for g in user_goals]
    }
    personalized_tips = generate_personalized_tips(context)

    # Recent 5 expenses
    recent_expenses = user_expenses[:5]

    return render_template(
        'dashboard.html',
        user=user,
        effective_income=effective_income,
        formatted_income=format_inr(effective_income),
        total_expenses=total_expenses,
        formatted_expenses=format_inr(total_expenses),
        current_savings=current_savings,
        formatted_savings=format_inr(current_savings),
        savings_rate=savings_rate,
        health_data=health_data,
        recent_expenses=recent_expenses,
        goals=user_goals[:3],
        personalized_tips=personalized_tips[:4],
        format_inr=format_inr
    )


@dashboard_bp.route('/api/dashboard/chart-data')
@login_required
def chart_data():
    """JSON API endpoint providing chart datasets for frontend visualization."""
    user = g.user
    user_incomes = Income.query.filter_by(user_id=user.id).all()
    user_expenses = Expense.query.filter_by(user_id=user.id).all()

    recorded_income = sum(float(i.amount) for i in user_incomes)
    effective_income = recorded_income if recorded_income > 0 else float(user.monthly_income or 0.0)
    total_expenses = sum(float(e.amount) for e in user_expenses)

    # Category breakdown
    category_totals = {}
    for exp in user_expenses:
        cat = exp.category
        category_totals[cat] = category_totals.get(cat, 0.0) + float(exp.amount)

    category_labels = list(category_totals.keys())
    category_values = [round(v, 2) for v in category_totals.values()]

    return jsonify({
        'categories': {
            'labels': category_labels,
            'values': category_values
        },
        'comparison': {
            'labels': ['Monthly Income', 'Total Expenses', 'Net Savings'],
            'values': [
                round(effective_income, 2),
                round(total_expenses, 2),
                round(max(0.0, effective_income - total_expenses), 2)
            ]
        }
    })
