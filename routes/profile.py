from flask import Blueprint, render_template, request, redirect, url_for, flash, g, session
from models import db, Expense, Income, SavingsGoal, BudgetCategory
from routes import login_required
from services.financial_health import calculate_financial_health_score
from services.finance_calculator import format_inr

profile_bp = Blueprint('profile', __name__)


@profile_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def view_profile():
    user = g.user

    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        age_str = request.form.get('age', '').strip()
        income_str = request.form.get('monthly_income', '').strip()
        current_password = request.form.get('current_password', '')
        new_password = request.form.get('new_password', '')
        confirm_new_password = request.form.get('confirm_new_password', '')

        errors = []
        if not full_name or len(full_name) < 2:
            errors.append("Full name must have at least 2 characters.")

        try:
            age = int(age_str)
            if age < 16 or age > 120:
                errors.append("Age must be between 16 and 120.")
        except (ValueError, TypeError):
            errors.append("Please enter a valid age.")

        try:
            monthly_income = float(income_str)
            if monthly_income < 0:
                errors.append("Monthly income cannot be negative.")
        except (ValueError, TypeError):
            errors.append("Please enter a valid monthly income.")

        # Optional password update
        if new_password:
            if not current_password:
                errors.append("Current password is required to set a new password.")
            elif not user.check_password(current_password):
                errors.append("Current password entered is incorrect.")
            elif len(new_password) < 6:
                errors.append("New password must be at least 6 characters.")
            elif new_password != confirm_new_password:
                errors.append("New passwords do not match.")

        if errors:
            for err in errors:
                flash(err, "danger")
            return redirect(url_for('profile.view_profile'))

        # Update profile
        user.full_name = full_name
        user.age = age
        user.monthly_income = monthly_income
        if new_password:
            user.set_password(new_password)

        db.session.commit()
        session['user_name'] = user.full_name
        flash("Profile updated successfully!", "success")
        return redirect(url_for('profile.view_profile'))

    # Calculate financial health score for profile
    incomes = Income.query.filter_by(user_id=user.id).all()
    expenses = Expense.query.filter_by(user_id=user.id).all()
    goals = SavingsGoal.query.filter_by(user_id=user.id).all()
    budgets = BudgetCategory.query.filter_by(user_id=user.id).all()

    recorded_income = sum(float(i.amount) for i in incomes)
    effective_income = recorded_income if recorded_income > 0 else float(user.monthly_income or 0.0)
    total_expenses = sum(float(e.amount) for e in expenses)
    total_budget = sum(float(b.planned_amount) for b in budgets)

    health_data = calculate_financial_health_score(
        income=effective_income,
        expenses=total_expenses,
        planned_budget=total_budget,
        goals=goals
    )

    return render_template(
        'profile.html',
        user=user,
        health_data=health_data,
        formatted_income=format_inr(user.monthly_income),
        format_inr=format_inr
    )
