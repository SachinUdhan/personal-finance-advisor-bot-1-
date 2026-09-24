import pytest
from datetime import date
from models import db, User, Expense, Income, SavingsGoal, BudgetCategory
from services.finance_calculator import calculate_emi, calculate_savings_rate, format_inr
from services.financial_health import calculate_financial_health_score
from services.ai_advisor import query_ai_advisor, build_fallback_response


# 1. Flask application starts
def test_app_starts(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b"Personal Finance Advisor Bot" in response.data or b"FinanceBot" in response.data


# 2. Registration works
def test_registration(client, app):
    response = client.post('/register', data={
        'full_name': 'Aarav Patel',
        'email': 'aarav@example.com',
        'password': 'Password123',
        'confirm_password': 'Password123',
        'age': '24',
        'monthly_income': '45000'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b"Account created successfully" in response.data

    with app.app_context():
        user = User.query.filter_by(email='aarav@example.com').first()
        assert user is not None
        assert user.full_name == 'Aarav Patel'
        assert user.age == 24
        assert user.monthly_income == 45000.0


# 3. Password is hashed
def test_password_is_hashed(app):
    with app.app_context():
        user = User(
            full_name="Hash Check",
            email="hash@example.com",
            age=25,
            monthly_income=30000.0
        )
        user.set_password("PlainSecret123")
        assert user.password_hash != "PlainSecret123"
        assert len(user.password_hash) > 20
        assert user.check_password("PlainSecret123") is True
        assert user.check_password("WrongPassword") is False


# 4. Login works
def test_login_success(client, app):
    with app.app_context():
        user = User(full_name="Login User", email="login@example.com", age=30, monthly_income=60000)
        user.set_password("ValidPassword123")
        db.session.add(user)
        db.session.commit()

    response = client.post('/login', data={
        'email': 'login@example.com',
        'password': 'ValidPassword123'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b"Welcome back, Login User!" in response.data
    assert b"Dashboard" in response.data


# 5. Invalid login is rejected
def test_invalid_login_rejected(client, app):
    response = client.post('/login', data={
        'email': 'nonexistent@example.com',
        'password': 'wrongpassword'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b"Invalid email or password" in response.data


# 6. Protected routes require authentication
def test_protected_routes_require_auth(client):
    protected_urls = ['/dashboard', '/expenses', '/budget', '/goals', '/chatbot', '/report', '/profile']
    for url in protected_urls:
        response = client.get(url, follow_redirects=False)
        # Should redirect to login
        assert response.status_code == 302
        assert '/login' in response.headers['Location']


# 7. Expense creation works
def test_expense_creation(auth_client, app):
    response = auth_client.post('/expenses/add', data={
        'title': 'Grocery Shopping',
        'amount': '3200',
        'category': 'Food',
        'date': '2025-09-20',
        'description': 'Supermarket fruits and vegetables'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b"Grocery Shopping" in response.data

    with app.app_context():
        exp = Expense.query.filter_by(title='Grocery Shopping').first()
        assert exp is not None
        assert exp.amount == 3200.0
        assert exp.category == 'Food'


# 8. Expense calculations work
def test_expense_calculations(app):
    with app.app_context():
        user = User(full_name="Calc User", email="calcexp@example.com", age=26, monthly_income=50000)
        user.set_password("Pass12345!")
        db.session.add(user)
        db.session.commit()

        exp1 = Expense(user_id=user.id, title='Rent', amount=15000, category='Housing', date=date.today())
        exp2 = Expense(user_id=user.id, title='Electricity', amount=2500, category='Bills', date=date.today())
        exp3 = Expense(user_id=user.id, title='Dinner', amount=1500, category='Food', date=date.today())
        db.session.add_all([exp1, exp2, exp3])
        db.session.commit()

        user_expenses = Expense.query.filter_by(user_id=user.id).all()
        total_exp = sum(e.amount for e in user_expenses)
        assert total_exp == 19000.0


# 9. Income calculations work
def test_income_calculations(app):
    with app.app_context():
        user = User(full_name="Income Calc User", email="incomecalc@example.com", age=28, monthly_income=40000)
        user.set_password("Pass12345!")
        db.session.add(user)
        db.session.commit()

        inc1 = Income(user_id=user.id, source='Salary', income_type='Salary', amount=45000, date=date.today())
        inc2 = Income(user_id=user.id, source='Design Consulting', income_type='Freelance', amount=12000, date=date.today())
        db.session.add_all([inc1, inc2])
        db.session.commit()

        user_incomes = Income.query.filter_by(user_id=user.id).all()
        total_inc = sum(i.amount for i in user_incomes)
        assert total_inc == 57000.0


# 10. Savings calculation works
def test_savings_calculation():
    # Regular savings
    rate = calculate_savings_rate(income=50000.0, expenses=35000.0)
    assert rate == 30.0

    # Deficit savings
    def_rate = calculate_savings_rate(income=40000.0, expenses=50000.0)
    assert def_rate == -25.0

    # Zero income handling
    zero_rate = calculate_savings_rate(income=0.0, expenses=1000.0)
    assert zero_rate == 0.0


# 11. EMI calculation works
def test_emi_calculation():
    # Principal: 500,000, Rate: 12% p.a., Tenure: 12 months
    result = calculate_emi(principal=500000.0, annual_rate=12.0, tenure_months=12)
    # Standard formula check: r = 0.01, (1.01)^12 = 1.126825
    # EMI = 500000 * 0.01 * 1.126825 / (0.126825) approx 44,424.39
    assert result['monthly_emi'] == pytest.approx(44424.39, abs=0.5)
    assert result['total_payment'] == pytest.approx(533092.68, abs=5.0)
    assert result['total_interest'] == pytest.approx(33092.68, abs=5.0)


# 12. Zero-interest EMI works
def test_zero_interest_emi():
    result = calculate_emi(principal=60000.0, annual_rate=0.0, tenure_months=6)
    assert result['monthly_emi'] == 10000.0
    assert result['total_payment'] == 60000.0
    assert result['total_interest'] == 0.0
    assert result['interest_percentage'] == 0.0


# 13. Financial health calculation works
def test_financial_health_calculation():
    # Healthy scenario
    healthy = calculate_financial_health_score(income=100000, expenses=40000, planned_budget=45000)
    assert healthy['score'] >= 75
    assert healthy['rating'] in ['Excellent', 'Good']
    assert healthy['savings_rate'] == 60.0
    assert 'disclaimer' in healthy

    # Deficit scenario
    deficit = calculate_financial_health_score(income=30000, expenses=45000, planned_budget=30000)
    assert deficit['score'] < 50
    assert deficit['rating'] in ['Needs Improvement', 'Critical']


# 14. Goal progress calculation works
def test_goal_progress_calculation(app):
    with app.app_context():
        goal = SavingsGoal(
            user_id=1,
            name="Emergency Reserve",
            target_amount=100000.0,
            current_amount=40000.0,
            target_date=date(date.today().year + 1, date.today().month, 1)
        )
        assert goal.progress_percentage == 40.0
        assert goal.remaining_amount == 60000.0
        assert goal.is_completed is False
        assert goal.suggested_monthly_savings > 0

        # When goal is completed
        goal.current_amount = 100000.0
        assert goal.progress_percentage == 100.0
        assert goal.remaining_amount == 0.0
        assert goal.is_completed is True
        assert goal.suggested_monthly_savings == 0.0


# 15. User data isolation works
def test_user_data_isolation(client, app):
    with app.app_context():
        # Create User A
        user_a = User(full_name="User Alpha", email="alpha@example.com", age=25, monthly_income=50000)
        user_a.set_password("AlphaPass123!")
        db.session.add(user_a)
        db.session.commit()

        # Create User B
        user_b = User(full_name="User Beta", email="beta@example.com", age=29, monthly_income=70000)
        user_b.set_password("BetaPass123!")
        db.session.add(user_b)
        db.session.commit()

        # Add private expense for User A
        exp_a = Expense(user_id=user_a.id, title="Secret Alpha Purchase", amount=9999, category="Other", date=date.today())
        db.session.add(exp_a)
        db.session.commit()
        exp_a_id = exp_a.id

    # Log in as User B
    client.post('/login', data={'email': 'beta@example.com', 'password': 'BetaPass123!'}, follow_redirects=True)

    # User B views expense list: MUST NOT see User A's expense
    resp = client.get('/expenses')
    assert b"Secret Alpha Purchase" not in resp.data

    # User B attempts to delete User A's expense
    del_resp = client.post(f'/expenses/delete/{exp_a_id}', follow_redirects=True)
    assert b"access denied" in del_resp.data or b"Expense not found" in del_resp.data

    # Verify User A's expense still safely exists in DB
    with app.app_context():
        still_exists = db.session.get(Expense, exp_a_id)
        assert still_exists is not None
        assert still_exists.title == "Secret Alpha Purchase"


# 16. Chatbot fallback advisor works with user financial context
def test_chatbot_context_advisor(auth_client, app):
    with app.app_context():
        user = User.query.filter_by(email="test@example.com").first()
        exp = Expense(user_id=user.id, title="Weekend Dineout", amount=4000, category="Food", date=date.today())
        db.session.add(exp)
        db.session.commit()

    response = auth_client.post('/api/chatbot/message', json={
        'message': 'Where am I spending too much?'
    })
    assert response.status_code == 200
    data = response.get_json()
    assert 'reply' in data
    assert 'Food' in data['reply']
    assert 'disclaimer' in data
