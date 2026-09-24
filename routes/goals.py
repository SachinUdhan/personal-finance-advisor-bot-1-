from datetime import datetime, date
from flask import Blueprint, render_template, request, redirect, url_for, flash, g
from models import db, SavingsGoal
from routes import login_required
from services.finance_calculator import format_inr

goals_bp = Blueprint('goals', __name__)


@goals_bp.route('/goals', methods=['GET'])
@login_required
def list_goals():
    user = g.user
    goals = SavingsGoal.query.filter_by(user_id=user.id).order_by(SavingsGoal.created_at.desc()).all()

    total_target = sum(float(g.target_amount) for g in goals)
    total_saved = sum(float(g.current_amount) for g in goals)
    total_remaining = sum(g.remaining_amount for g in goals)
    overall_progress = (total_saved / total_target * 100.0) if total_target > 0 else 0.0

    return render_template(
        'goals.html',
        user=user,
        goals=goals,
        total_target=total_target,
        formatted_total_target=format_inr(total_target),
        total_saved=total_saved,
        formatted_total_saved=format_inr(total_saved),
        total_remaining=total_remaining,
        formatted_total_remaining=format_inr(total_remaining),
        overall_progress=round(overall_progress, 1),
        format_inr=format_inr,
        today_date=date.today().strftime('%Y-%m-%d')
    )


@goals_bp.route('/goals/add', methods=['POST'])
@login_required
def add_goal():
    user = g.user
    name = request.form.get('name', '').strip()
    target_amount_str = request.form.get('target_amount', '').strip()
    current_amount_str = request.form.get('current_amount', '0').strip()
    target_date_str = request.form.get('target_date', '').strip()

    errors = []
    if not name:
        errors.append("Goal name is required (e.g. Emergency Fund, Laptop, Travel).")

    try:
        target_amount = float(target_amount_str)
        if target_amount <= 0:
            errors.append("Target amount must be greater than zero.")
    except (ValueError, TypeError):
        errors.append("Please enter a valid target amount.")

    try:
        current_amount = float(current_amount_str or 0)
        if current_amount < 0:
            errors.append("Current saved amount cannot be negative.")
    except (ValueError, TypeError):
        current_amount = 0.0

    target_date = None
    if target_date_str:
        try:
            target_date = datetime.strptime(target_date_str, '%Y-%m-%d').date()
        except ValueError:
            errors.append("Please provide a valid target date (YYYY-MM-DD).")

    if errors:
        for err in errors:
            flash(err, "danger")
        return redirect(url_for('goals.list_goals'))

    goal = SavingsGoal(
        user_id=user.id,
        name=name,
        target_amount=target_amount,
        current_amount=current_amount,
        target_date=target_date
    )
    db.session.add(goal)
    db.session.commit()

    flash(f"Savings goal '{name}' for {format_inr(target_amount)} created!", "success")
    return redirect(url_for('goals.list_goals'))


@goals_bp.route('/goals/update-progress/<int:goal_id>', methods=['POST'])
@login_required
def update_goal_progress(goal_id):
    user = g.user
    goal = SavingsGoal.query.filter_by(id=goal_id, user_id=user.id).first()
    if not goal:
        flash("Goal not found or access denied.", "danger")
        return redirect(url_for('goals.list_goals'))

    add_amount_str = request.form.get('add_amount', '').strip()
    set_amount_str = request.form.get('set_amount', '').strip()

    try:
        if add_amount_str:
            add_amt = float(add_amount_str)
            if add_amt <= 0:
                flash("Added amount must be positive.", "danger")
                return redirect(url_for('goals.list_goals'))
            goal.current_amount += add_amt
        elif set_amount_str:
            set_amt = float(set_amount_str)
            if set_amt < 0:
                flash("Saved amount cannot be negative.", "danger")
                return redirect(url_for('goals.list_goals'))
            goal.current_amount = set_amt

        db.session.commit()
        flash(f"Goal '{goal.name}' updated! Current balance: {format_inr(goal.current_amount)}.", "success")
    except (ValueError, TypeError):
        flash("Invalid amount entered.", "danger")

    return redirect(url_for('goals.list_goals'))


@goals_bp.route('/goals/delete/<int:goal_id>', methods=['POST'])
@login_required
def delete_goal(goal_id):
    user = g.user
    goal = SavingsGoal.query.filter_by(id=goal_id, user_id=user.id).first()
    if not goal:
        flash("Goal not found or access denied.", "danger")
        return redirect(url_for('goals.list_goals'))

    name = goal.name
    db.session.delete(goal)
    db.session.commit()

    flash(f"Savings goal '{name}' removed.", "info")
    return redirect(url_for('goals.list_goals'))
