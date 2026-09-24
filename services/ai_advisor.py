import os
import re
import requests
from typing import Dict, Any, List
from services.finance_calculator import format_inr, calculate_savings_rate

FINANCIAL_DISCLAIMER = (
    "This application provides educational financial information and general guidance based on user-provided data. "
    "It is not a substitute for professional financial advice, and calculations or recommendations may not be suitable for every individual."
)


def generate_personalized_tips(context: Dict[str, Any]) -> List[Dict[str, str]]:
    """
    Produces dynamic, tailored tips derived strictly from user's active financial figures.
    """
    tips = []
    income = context.get('total_income', 0.0)
    expenses = context.get('total_expenses', 0.0)
    savings_rate = context.get('savings_rate', 0.0)
    category_totals = context.get('category_totals', {})
    goals = context.get('goals', [])

    # 1. Deficit warning
    if income > 0 and expenses > income:
        deficit = expenses - income
        tips.append({
            'type': 'danger',
            'icon': 'alert-triangle',
            'title': 'Deficit Alert',
            'message': f"Your expenses exceed your income by {format_inr(deficit)} this period. Prioritize cutting non-essential subscriptions and entertainment to prevent debt."
        })

    # 2. Savings rate evaluation
    if income > 0 and savings_rate < 20 and expenses <= income:
        tips.append({
            'type': 'warning',
            'icon': 'trending-down',
            'title': 'Boost Your Savings Rate',
            'message': f"Your current savings rate is {savings_rate}%. Under the 50/30/20 principle, striving for at least 20% ({format_inr(income * 0.20)}) helps build long-term resilience."
        })
    elif income > 0 and savings_rate >= 30:
        tips.append({
            'type': 'success',
            'icon': 'award',
            'title': 'Super Saver Status',
            'message': f"Great job saving {savings_rate}% of your income! Consider directing surplus funds into long-term instruments like index mutual funds or PPF after funding an emergency reserve."
        })

    # 3. High category spending warnings
    if expenses > 0:
        food_exp = category_totals.get('Food', 0.0)
        food_pct = (food_exp / expenses) * 100
        if food_pct > 30 and food_exp > 3000:
            tips.append({
                'type': 'info',
                'icon': 'coffee',
                'title': 'High Food & Dining Outlay',
                'message': f"Food represents {food_pct:.1f}% ({format_inr(food_exp)}) of all spending. Meal planning and reducing food delivery can free up significant monthly cash."
            })

        ent_exp = category_totals.get('Entertainment', 0.0)
        ent_pct = (ent_exp / expenses) * 100
        if ent_pct > 15:
            tips.append({
                'type': 'warning',
                'icon': 'film',
                'title': 'Entertainment Spending',
                'message': f"Entertainment accounts for {ent_pct:.1f}% ({format_inr(ent_exp)}) of expenses. Audit active streaming services and recreational events."
            })

        shopping_exp = category_totals.get('Shopping', 0.0)
        shopping_pct = (shopping_exp / expenses) * 100
        if shopping_pct > 20:
            tips.append({
                'type': 'info',
                'icon': 'shopping-bag',
                'title': 'Shopping & Lifestyle Spending',
                'message': f"Shopping accounts for {shopping_pct:.1f}% ({format_inr(shopping_exp)}). Try applying the 48-hour rule for non-essential purchases before buying."
            })

    # 4. Savings goals guidance
    if not goals:
        tips.append({
            'type': 'info',
            'icon': 'target',
            'title': 'Set Your First Goal',
            'message': "You haven't established any savings goals yet. Setting an 'Emergency Fund' goal covering 3–6 months of basic living costs is a great starting milestone."
        })
    else:
        # Check active goals progress
        incomplete_goals = [g for g in goals if not g.get('is_completed', False)]
        if incomplete_goals:
            top_goal = incomplete_goals[0]
            tips.append({
                'type': 'success',
                'icon': 'flag',
                'title': f"Goal: {top_goal.get('name')}",
                'message': f"You're {top_goal.get('progress_percentage')}% toward your {top_goal.get('name')} target ({format_inr(top_goal.get('current_amount'))} of {format_inr(top_goal.get('target_amount'))}). Suggested monthly save: {format_inr(top_goal.get('suggested_monthly_savings'))}."
            })

    # Fallback default tip if empty
    if not tips:
        tips.append({
            'type': 'info',
            'icon': 'compass',
            'title': 'Financial Awareness',
            'message': "Log all your daily expenses consistently. Consistent tracking is the single most powerful habit for financial freedom."
        })

    return tips


def build_fallback_response(query: str, ctx: Dict[str, Any]) -> str:
    """
    Intelligent context-driven rule-based advisor that responds to queries
    using the user's live financial data.
    """
    q = query.lower()
    income = ctx.get('total_income', 0.0)
    expenses = ctx.get('total_expenses', 0.0)
    savings = income - expenses
    savings_rate = ctx.get('savings_rate', 0.0)
    categories = ctx.get('category_totals', {})
    top_cat = ctx.get('top_category', 'None')
    top_cat_amt = ctx.get('top_category_amount', 0.0)
    goals = ctx.get('goals', [])

    # Where am I spending too much?
    if any(k in q for k in ['where', 'spending too much', 'highest expense', 'category', 'spending most']):
        if not categories or expenses == 0:
            return (
                "You haven't recorded any expenses yet! Once you log a few expenses, "
                "I will analyze your top spending categories and pinpoint areas where you can trim down."
            )
        sorted_cats = sorted(categories.items(), key=lambda x: x[1], reverse=True)
        breakdown_str = "\n".join([
            f"- **{cat}**: {format_inr(amt)} ({amt/expenses*100:.1f}% of total spending)"
            for cat, amt in sorted_cats[:4]
        ])
        return (
            f"Based on your recorded transactions, your total expenses are **{format_inr(expenses)}**.\n\n"
            f"Your highest spending area is **{top_cat}** at **{format_inr(top_cat_amt)}**.\n\n"
            f"**Your Top Expense Categories:**\n{breakdown_str}\n\n"
            f"💡 **Recommendation:** If you're looking to trim spending, focus first on discretionary categories "
            f"like Shopping, Entertainment, or Dining Out before trying to reduce fixed obligations like Housing or Bills."
        )

    # How can I save more money / reduce expenses?
    if any(k in q for k in ['save more', 'how to save', 'cut expense', 'reduce expense', 'saving tips']):
        income_50 = format_inr(income * 0.50) if income > 0 else "₹0"
        income_30 = format_inr(income * 0.30) if income > 0 else "₹0"
        income_20 = format_inr(income * 0.20) if income > 0 else "₹0"

        return (
            f"Here is a tailored action plan based on your current numbers:\n\n"
            f"1. **Apply the 50/30/20 Rule for your income of {format_inr(income)}:**\n"
            f"   - **Needs (50% max):** Up to {income_50} for rent, groceries, and essential utilities.\n"
            f"   - **Wants (30% max):** Up to {income_30} for dining out, entertainment, and shopping.\n"
            f"   - **Savings (20% min):** At least {income_20} for emergency fund and investments.\n\n"
            f"2. **Current Standing:** Your current savings rate is **{savings_rate}%** ({format_inr(savings)} saved this period).\n"
            f"3. **Micro-Habit Suggestions:**\n"
            f"   - Implement the **48-Hour Rule** on non-essential purchases over ₹1,000.\n"
            f"   - Audit monthly recurring subscriptions and memberships.\n"
            f"   - Automate a monthly transfer to your savings immediately on payday ('Pay yourself first')."
        )

    # How should I plan my monthly budget?
    if any(k in q for k in ['budget', 'monthly budget', 'plan my budget', 'budgeting']):
        return (
            f"To build an effective monthly budget tailored to your monthly income of **{format_inr(income)}**:\n\n"
            f"1. **Fixed Essentials (Needs - 50% target: {format_inr(income * 0.50)}):**\n"
            f"   Prioritize housing, groceries, transport, utilities, and healthcare.\n\n"
            f"2. **Discretionary Spending (Wants - 30% target: {format_inr(income * 0.30)}):**\n"
            f"   Allocate a specific cap for restaurants, entertainment, gadgets, and personal shopping.\n\n"
            f"3. **Future & Growth (Savings/Debt - 20% target: {format_inr(income * 0.20)}):**\n"
            f"   Feed your active savings goals and emergency reserves before spending on lifestyle.\n\n"
            f"Visit our **Budget Planner** page to input category-by-category allocations and track adherence!"
        )

    # How can I reach my savings goal?
    if any(k in q for k in ['goal', 'reach goal', 'target', 'savings goal']):
        if not goals:
            return (
                "You haven't set up any savings goals yet! Head over to the **Savings Goals** tab "
                "to create a goal (e.g., 'Emergency Fund', 'Laptop', or 'Vacation') with a target date. "
                "The bot will automatically calculate your recommended monthly savings target."
            )
        goal_summaries = []
        for g in goals[:3]:
            name = g.get('name')
            target = g.get('target_amount', 0)
            curr = g.get('current_amount', 0)
            pct = g.get('progress_percentage', 0)
            sugg = g.get('suggested_monthly_savings', 0)
            goal_summaries.append(
                f"- **{name}**: Progress {pct}% ({format_inr(curr)} / {format_inr(target)}). "
                f"Suggested saving: **{format_inr(sugg)}/month**."
            )
        return (
            f"Here is the status of your current savings goals:\n\n"
            + "\n".join(goal_summaries) + "\n\n"
            f"💡 **Strategies to reach goals faster:**\n"
            f"- Set up automatic recurring transfers right after your salary arrives.\n"
            f"- Divert any windfalls, bonuses, or cashback directly to your top priority goal.\n"
            f"- Reduce one discretionary expense per week and transfer the difference to your goal."
        )

    # EMI or loan related questions
    if any(k in q for k in ['emi', 'loan', 'interest', 'debt']):
        return (
            f"When managing loans and EMIs:\n\n"
            f"1. **Rule of Thumb:** Your total monthly loan repayments (EMIs) should not exceed **40%** of your monthly income "
            f"({format_inr(income * 0.40)} for your current income).\n"
            f"2. Use our built-in **EMI Calculator** to simulate monthly installments and total interest across varying tenures.\n"
            f"3. **Prepayment Tip:** Even one extra EMI payment per year or rounding up your monthly payment can cut tenure and interest drastically."
        )

    # General overview or question
    return (
        f"Hello! Here is a summary of your financial snapshot:\n\n"
        f"- **Monthly Income:** {format_inr(income)}\n"
        f"- **Total Recorded Expenses:** {format_inr(expenses)}\n"
        f"- **Net Savings:** {format_inr(savings)} (Savings Rate: **{savings_rate}%**)\n"
        f"- **Highest Expense Category:** {top_cat} ({format_inr(top_cat_amt)})\n\n"
        f"You can ask me questions like:\n"
        f"- *Where am I spending too much?*\n"
        f"- *How can I save more money?*\n"
        f"- *How should I plan my monthly budget?*\n"
        f"- *How can I reach my savings goal faster?*\n"
        f"- *What is a safe EMI amount for my income?*"
    )


def query_ai_advisor(query: str, context: Dict[str, Any], api_key: str = None) -> Dict[str, Any]:
    """
    Coordinates between external AI provider (if configured) and intelligent fallback engine.
    Ensures safe, robust, educational responses without exposing secrets.
    """
    if not query or not query.strip():
        return {
            'response': "Please enter a question about your personal finances.",
            'disclaimer': FINANCIAL_DISCLAIMER,
            'source': 'system'
        }

    user_query = query.strip()
    api_key = api_key or os.environ.get('AI_API_KEY', '').strip()

    # Attempt external LLM if key is present
    if api_key:
        try:
            # We can use Gemini REST API endpoint
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
            system_prompt = (
                f"You are a helpful, professional, and educational personal finance advisor bot. "
                f"The user's current self-reported financial context is:\n"
                f"- Monthly Income: INR {context.get('total_income', 0)}\n"
                f"- Total Expenses: INR {context.get('total_expenses', 0)}\n"
                f"- Net Savings: INR {context.get('total_income', 0) - context.get('total_expenses', 0)}\n"
                f"- Savings Rate: {context.get('savings_rate', 0)}%\n"
                f"- Expense Categories: {context.get('category_totals', {})}\n"
                f"- Savings Goals: {context.get('goals', [])}\n\n"
                f"Guidelines:\n"
                f"- Give concise, educational, encouraging advice formatted in markdown.\n"
                f"- Use INR (₹) notation.\n"
                f"- Cite the user's actual numbers when answering.\n"
                f"- Always maintain an educational tone and do not claim to offer certified financial advice."
            )
            payload = {
                "contents": [
                    {
                        "role": "user",
                        "parts": [
                            {"text": f"{system_prompt}\n\nUser Question: {user_query}"}
                        ]
                    }
                ]
            }
            res = requests.post(url, json=payload, timeout=7)
            if res.status_code == 200:
                data = res.json()
                bot_text = data['candidates'][0]['content']['parts'][0]['text']
                return {
                    'response': bot_text,
                    'disclaimer': FINANCIAL_DISCLAIMER,
                    'source': 'gemini_api'
                }
        except Exception:
            # Safely fall back to rule-based engine on any error/timeout
            pass

    # Fallback to local intelligent rule-based engine
    response_text = build_fallback_response(user_query, context)
    return {
        'response': response_text,
        'disclaimer': FINANCIAL_DISCLAIMER,
        'source': 'local_advisor'
    }
