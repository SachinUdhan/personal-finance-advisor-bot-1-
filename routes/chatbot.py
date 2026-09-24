from flask import Blueprint, render_template, request, jsonify, g
from models import Income, Expense, SavingsGoal, BudgetCategory
from routes import login_required
from services.finance_calculator import calculate_savings_rate, format_inr
from services.ai_advisor import query_ai_advisor, FINANCIAL_DISCLAIMER

chatbot_bp = Blueprint('chatbot', __name__)


def build_user_context(user):
    """Gathers the user's live financial snapshot for AI prompt injection."""
    user_incomes = Income.query.filter_by(user_id=user.id).all()
    user_expenses = Expense.query.filter_by(user_id=user.id).all()
    user_goals = SavingsGoal.query.filter_by(user_id=user.id).all()

    recorded_income = sum(float(i.amount) for i in user_incomes)
    effective_income = recorded_income if recorded_income > 0 else float(user.monthly_income or 0.0)
    total_expenses = sum(float(e.amount) for e in user_expenses)

    category_totals = {}
    for exp in user_expenses:
        cat = exp.category
        category_totals[cat] = category_totals.get(cat, 0.0) + float(exp.amount)

    sorted_categories = sorted(category_totals.items(), key=lambda x: x[1], reverse=True)
    top_cat = sorted_categories[0][0] if sorted_categories else "None"
    top_cat_amt = sorted_categories[0][1] if sorted_categories else 0.0
    savings_rate = calculate_savings_rate(effective_income, total_expenses)

    return {
        'total_income': effective_income,
        'total_expenses': total_expenses,
        'savings_rate': savings_rate,
        'category_totals': category_totals,
        'top_category': top_cat,
        'top_category_amount': top_cat_amt,
        'goals': [g.to_dict() for g in user_goals]
    }


@chatbot_bp.route('/chatbot', methods=['GET'])
@login_required
def view_chatbot():
    user = g.user
    context = build_user_context(user)
    return render_template(
        'chatbot.html',
        user=user,
        context=context,
        formatted_income=format_inr(context['total_income']),
        formatted_expenses=format_inr(context['total_expenses']),
        disclaimer=FINANCIAL_DISCLAIMER
    )


@chatbot_bp.route('/api/chatbot/message', methods=['POST'])
@login_required
def send_message():
    user = g.user
    data = request.get_json() or {}
    message = data.get('message', '').strip()

    if not message:
        return jsonify({'error': 'Message cannot be empty'}), 400

    context = build_user_context(user)
    result = query_ai_advisor(message, context)

    return jsonify({
        'reply': result['response'],
        'disclaimer': result['disclaimer'],
        'source': result['source']
    })
