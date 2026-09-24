from datetime import datetime, date
from flask import Blueprint, render_template, request, redirect, url_for, flash, g, jsonify
from models import db, Expense, Income
from models.expense import VALID_CATEGORIES
from routes import login_required
from services.finance_calculator import format_inr

expenses_bp = Blueprint('expenses', __name__)

VALID_INCOME_TYPES = ['Salary', 'Freelance', 'Business', 'Other']


@expenses_bp.route('/expenses', methods=['GET'])
@login_required
def list_expenses():
    user = g.user
    
    # Filtering parameters
    category_filter = request.args.get('category', '').strip()
    search_query = request.args.get('q', '').strip()
    start_date_str = request.args.get('start_date', '').strip()
    end_date_str = request.args.get('end_date', '').strip()

    # Query user expenses with strict user-data isolation
    query = Expense.query.filter_by(user_id=user.id)

    if category_filter and category_filter in VALID_CATEGORIES:
        query = query.filter(Expense.category == category_filter)

    if search_query:
        query = query.filter(
            (Expense.title.ilike(f'%{search_query}%')) | 
            (Expense.description.ilike(f'%{search_query}%'))
        )

    if start_date_str:
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            query = query.filter(Expense.date >= start_date)
        except ValueError:
            pass

    if end_date_str:
        try:
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            query = query.filter(Expense.date <= end_date)
        except ValueError:
            pass

    expenses = query.order_by(Expense.date.desc(), Expense.id.desc()).all()
    incomes = Income.query.filter_by(user_id=user.id).order_by(Income.date.desc(), Income.id.desc()).all()

    total_expenses = sum(float(e.amount) for e in expenses)
    total_incomes = sum(float(i.amount) for i in incomes)

    # Category totals
    category_breakdown = {}
    for exp in Expense.query.filter_by(user_id=user.id).all():
        category_breakdown[exp.category] = category_breakdown.get(exp.category, 0.0) + float(exp.amount)

    return render_template(
        'expenses.html',
        user=user,
        expenses=expenses,
        incomes=incomes,
        categories=VALID_CATEGORIES,
        income_types=VALID_INCOME_TYPES,
        total_expenses=total_expenses,
        formatted_total_expenses=format_inr(total_expenses),
        total_incomes=total_incomes,
        formatted_total_incomes=format_inr(total_incomes),
        category_breakdown=category_breakdown,
        selected_category=category_filter,
        search_query=search_query,
        start_date=start_date_str,
        end_date=end_date_str,
        today_date=date.today().strftime('%Y-%m-%d'),
        format_inr=format_inr
    )


@expenses_bp.route('/expenses/add', methods=['POST'])
@login_required
def add_expense():
    user = g.user
    title = request.form.get('title', '').strip()
    amount_str = request.form.get('amount', '').strip()
    category = request.form.get('category', '').strip()
    date_str = request.form.get('date', '').strip()
    description = request.form.get('description', '').strip()

    errors = []
    if not title:
        errors.append("Expense name is required.")

    try:
        amount = float(amount_str)
        if amount <= 0:
            errors.append("Expense amount must be greater than zero.")
    except (ValueError, TypeError):
        errors.append("Please enter a valid expense amount.")

    if category not in VALID_CATEGORIES:
        errors.append("Please select a valid expense category.")

    try:
        expense_date = datetime.strptime(date_str, '%Y-%m-%d').date() if date_str else date.today()
    except ValueError:
        errors.append("Please provide a valid transaction date (YYYY-MM-DD).")

    if errors:
        for err in errors:
            flash(err, "danger")
        return redirect(url_for('expenses.list_expenses'))

    new_expense = Expense(
        user_id=user.id,
        title=title,
        amount=amount,
        category=category,
        date=expense_date,
        description=description
    )
    db.session.add(new_expense)
    db.session.commit()

    flash(f"Expense '{title}' for {format_inr(amount)} added successfully!", "success")
    return redirect(url_for('expenses.list_expenses'))


@expenses_bp.route('/expenses/edit/<int:expense_id>', methods=['POST'])
@login_required
def edit_expense(expense_id):
    user = g.user
    # Ensure user can only edit their own expense
    expense = Expense.query.filter_by(id=expense_id, user_id=user.id).first()
    if not expense:
        flash("Expense not found or access denied.", "danger")
        return redirect(url_for('expenses.list_expenses'))

    title = request.form.get('title', '').strip()
    amount_str = request.form.get('amount', '').strip()
    category = request.form.get('category', '').strip()
    date_str = request.form.get('date', '').strip()
    description = request.form.get('description', '').strip()

    if not title:
        flash("Expense name cannot be blank.", "danger")
        return redirect(url_for('expenses.list_expenses'))

    try:
        amount = float(amount_str)
        if amount <= 0:
            flash("Amount must be greater than zero.", "danger")
            return redirect(url_for('expenses.list_expenses'))
    except (ValueError, TypeError):
        flash("Invalid amount.", "danger")
        return redirect(url_for('expenses.list_expenses'))

    if category not in VALID_CATEGORIES:
        flash("Invalid category selected.", "danger")
        return redirect(url_for('expenses.list_expenses'))

    try:
        if date_str:
            expense.date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        flash("Invalid date format.", "danger")
        return redirect(url_for('expenses.list_expenses'))

    expense.title = title
    expense.amount = amount
    expense.category = category
    expense.description = description
    db.session.commit()

    flash(f"Expense '{title}' updated successfully.", "success")
    return redirect(url_for('expenses.list_expenses'))


@expenses_bp.route('/expenses/delete/<int:expense_id>', methods=['POST'])
@login_required
def delete_expense(expense_id):
    user = g.user
    expense = Expense.query.filter_by(id=expense_id, user_id=user.id).first()
    if not expense:
        flash("Expense not found or access denied.", "danger")
        return redirect(url_for('expenses.list_expenses'))

    title = expense.title
    db.session.delete(expense)
    db.session.commit()

    flash(f"Expense '{title}' deleted.", "info")
    return redirect(url_for('expenses.list_expenses'))


@expenses_bp.route('/incomes/add', methods=['POST'])
@login_required
def add_income():
    user = g.user
    source = request.form.get('source', '').strip()
    income_type = request.form.get('income_type', 'Salary').strip()
    amount_str = request.form.get('amount', '').strip()
    date_str = request.form.get('date', '').strip()

    errors = []
    if not source:
        errors.append("Income source is required (e.g. Salary, Client).")

    try:
        amount = float(amount_str)
        if amount <= 0:
            errors.append("Income amount must be greater than zero.")
    except (ValueError, TypeError):
        errors.append("Please enter a valid income amount.")

    if income_type not in VALID_INCOME_TYPES:
        income_type = 'Other'

    try:
        inc_date = datetime.strptime(date_str, '%Y-%m-%d').date() if date_str else date.today()
    except ValueError:
        errors.append("Please enter a valid date.")

    if errors:
        for err in errors:
            flash(err, "danger")
        return redirect(url_for('expenses.list_expenses'))

    new_income = Income(
        user_id=user.id,
        source=source,
        income_type=income_type,
        amount=amount,
        date=inc_date
    )
    db.session.add(new_income)
    db.session.commit()

    flash(f"Income '{source}' for {format_inr(amount)} added successfully!", "success")
    return redirect(url_for('expenses.list_expenses'))


@expenses_bp.route('/incomes/delete/<int:income_id>', methods=['POST'])
@login_required
def delete_income(income_id):
    user = g.user
    income = Income.query.filter_by(id=income_id, user_id=user.id).first()
    if not income:
        flash("Income record not found or access denied.", "danger")
        return redirect(url_for('expenses.list_expenses'))

    source = income.source
    db.session.delete(income)
    db.session.commit()

    flash(f"Income '{source}' deleted.", "info")
    return redirect(url_for('expenses.list_expenses'))
