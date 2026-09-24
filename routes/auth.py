import re
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models import db, User

auth_bp = Blueprint('auth', __name__)

EMAIL_REGEX = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if session.get('user_id'):
        return redirect(url_for('dashboard.index'))

    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        age_str = request.form.get('age', '').strip()
        income_str = request.form.get('monthly_income', '').strip()

        # Validation
        errors = []
        if not full_name or len(full_name) < 2:
            errors.append("Please provide your full name (minimum 2 characters).")
        
        if not email or not re.match(EMAIL_REGEX, email):
            errors.append("Please provide a valid email address.")
        
        if not password or len(password) < 6:
            errors.append("Password must be at least 6 characters long.")
            
        if password != confirm_password:
            errors.append("Passwords do not match.")

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

        # Check existing email
        if not errors:
            existing = User.query.filter_by(email=email).first()
            if existing:
                errors.append("An account with this email address already exists.")

        if errors:
            for err in errors:
                flash(err, "danger")
            return render_template(
                'register.html',
                full_name=full_name,
                email=email,
                age=age_str,
                monthly_income=income_str
            )

        # Create user with hashed password
        new_user = User(
            full_name=full_name,
            email=email,
            age=age,
            monthly_income=monthly_income
        )
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        flash("Account created successfully! You can now log in.", "success")
        return redirect(url_for('auth.login'))

    return render_template('register.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if session.get('user_id'):
        return redirect(url_for('dashboard.index'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        if not email or not password:
            flash("Please enter both email and password.", "danger")
            return render_template('login.html', email=email)

        user = User.query.filter_by(email=email).first()
        if not user or not user.check_password(password):
            flash("Invalid email or password. Please try again.", "danger")
            return render_template('login.html', email=email)

        # Establish session
        session.clear()
        session['user_id'] = user.id
        session['user_name'] = user.full_name
        flash(f"Welcome back, {user.full_name}!", "success")

        next_page = request.args.get('next')
        if next_page and next_page.startswith('/'):
            return redirect(next_page)
        return redirect(url_for('dashboard.index'))

    return render_template('login.html')


@auth_bp.route('/logout')
def logout():
    session.clear()
    flash("You have been securely logged out.", "info")
    return redirect(url_for('auth.login'))
