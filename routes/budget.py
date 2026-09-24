from flask import Blueprint, render_template, request, redirect, url_for, flash, g
from models import db, BudgetCategory, Income, Expense
from models.expense import VALID_CATEGORIES
from routes import login_required
from services.finance_calculator import format_inr, calculate_savings_rate

budget_bp = Blueprint('budget', __name__)


@budget_bp.route('/budget', methods=['GET', 'POST'])
@login_required
def view_budget():
    user = g.user

    # Fetch effective income
    incomes = Income.query.filter_by(user_id=user.id).all()
    recorded_income = sum(float(i.amount) for i in incomes)
    monthly_income = recorded_income if recorded_income > 0 else float(user.monthly_income or 0.0)

    # If POST: update planned budget categories
    if request.method == 'POST':
        for cat in VALID_CATEGORIES:
            amt_str = request.form.get(f'cat_{cat}', '').strip()
            if amt_str:
                try:
                    amt = max(0.0, float(amt_str))
                    budget_entry = BudgetCategory.query.filter_by(user_id=user.id, category=cat).first()
                    if budget_entry:
                        budget_entry.planned_amount = amt
                    else:
                        budget_entry = BudgetCategory(user_id=user.id, category=cat, planned_amount=amt)
                        db.session.add(budget_entry)
                except ValueError:
                    pass
        db.session.commit()
        flash("Budget allocations updated successfully!", "success")
        return redirect(url_for('budget.view_budget'))

    # Load existing budget allocations
    budgets = {b.category: float(b.planned_amount) for b in BudgetCategory.query.filter_by(user_id=user.id).all()}
    
    # Calculate actual expenses per category to compare
    expenses = Expense.query.filter_by(user_id=user.id).all()
    actual_spent = {}
    for exp in expenses:
        actual_spent[exp.category] = actual_spent.get(exp.category, 0.0) + float(exp.amount)

    total_planned = sum(budgets.get(c, 0.0) for c in VALID_CATEGORIES)
    total_actual = sum(actual_spent.values())
    expected_savings = monthly_income - total_planned
    expected_savings_rate = calculate_savings_rate(monthly_income, total_planned)
    is_over_budget = total_planned > monthly_income

    # Prepare category comparison rows
    category_rows = []
    for cat in VALID_CATEGORIES:
        planned = budgets.get(cat, 0.0)
        actual = actual_spent.get(cat, 0.0)
        remaining = planned - actual
        pct_used = (actual / planned * 100.0) if planned > 0 else (100.0 if actual > 0 else 0.0)
        category_rows.append({
            'name': cat,
            'planned': planned,
            'formatted_planned': format_inr(planned),
            'actual': actual,
            'formatted_actual': format_inr(actual),
            'remaining': remaining,
            'formatted_remaining': format_inr(remaining),
            'pct_used': min(100.0, round(pct_used, 1)),
            'is_over': actual > planned and planned > 0
        })

    return render_template(
        'budget.html',
        user=user,
        monthly_income=monthly_income,
        formatted_income=format_inr(monthly_income),
        total_planned=total_planned,
        formatted_planned=format_inr(total_planned),
        expected_savings=expected_savings,
        formatted_savings=format_inr(expected_savings),
        expected_savings_rate=expected_savings_rate,
        total_actual=total_actual,
        formatted_actual=format_inr(total_actual),
        is_over_budget=is_over_budget,
        category_rows=category_rows,
        format_inr=format_inr
    )
