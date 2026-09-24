from typing import Dict, Any, List


def calculate_financial_health_score(
    income: float,
    expenses: float,
    planned_budget: float = 0.0,
    goals: List[Any] = None
) -> Dict[str, Any]:
    """
    Computes an educational financial health score (0-100) based on 5 transparent pillars:
      1. Savings Rate (30 pts)
      2. Expense-to-Income Ratio (25 pts)
      3. Budget Adherence (20 pts)
      4. Savings Goal Progress (15 pts)
      5. Cash Flow Stability & Reserve (10 pts)
      
    Returns score, rating category, detailed factor breakdown, tips, and disclaimer.
    """
    if goals is None:
        goals = []

    income = max(0.0, float(income or 0.0))
    expenses = max(0.0, float(expenses or 0.0))
    planned_budget = max(0.0, float(planned_budget or 0.0))

    # 1. Savings Rate Factor (Max 30)
    savings = income - expenses
    savings_rate = (savings / income * 100.0) if income > 0 else 0.0
    
    if income == 0 and expenses == 0:
        savings_pts = 10
        savings_desc = "No financial activity recorded yet."
    elif savings_rate >= 30:
        savings_pts = 30
        savings_desc = f"Outstanding savings rate of {savings_rate:.1f}% (target: >20%)."
    elif savings_rate >= 20:
        savings_pts = 25
        savings_desc = f"Healthy savings rate of {savings_rate:.1f}% meeting the 50/30/20 benchmark."
    elif savings_rate >= 10:
        savings_pts = 18
        savings_desc = f"Moderate savings rate of {savings_rate:.1f}%. Aim to increase to 20%."
    elif savings_rate >= 0:
        savings_pts = 10
        savings_desc = f"Low savings rate of {savings_rate:.1f}%. High portion of income is consumed."
    else:
        savings_pts = 0
        savings_desc = f"Deficit! Expenses exceed income by {abs(savings_rate):.1f}%."

    # 2. Expense-to-Income Ratio (Max 25)
    expense_ratio = (expenses / income * 100.0) if income > 0 else (100.0 if expenses > 0 else 0.0)
    if income == 0 and expenses == 0:
        expense_pts = 10
        expense_desc = "No expenses recorded yet."
    elif expense_ratio <= 50:
        expense_pts = 25
        expense_desc = f"Frugal spending at {expense_ratio:.1f}% of income."
    elif expense_ratio <= 70:
        expense_pts = 20
        expense_desc = f"Balanced spending at {expense_ratio:.1f}% of income."
    elif expense_ratio <= 85:
        expense_pts = 12
        expense_desc = f"Elevated spending at {expense_ratio:.1f}% of income. Little margin for error."
    elif expense_ratio <= 100:
        expense_pts = 5
        expense_desc = f"Living paycheck to paycheck ({expense_ratio:.1f}% spent)."
    else:
        expense_pts = 0
        expense_desc = f"Overspending! You are spending {expense_ratio:.1f}% of your income."

    # 3. Budget Adherence (Max 20)
    if planned_budget > 0:
        if expenses <= planned_budget:
            budget_pts = 20
            budget_desc = "Spending is strictly within your planned monthly budget."
        elif expenses <= planned_budget * 1.10:
            budget_pts = 12
            budget_desc = "Slightly over planned budget (within 10% tolerance)."
        else:
            budget_pts = 5
            budget_desc = "Expenses have exceeded the planned monthly budget by over 10%."
    else:
        budget_pts = 10
        budget_desc = "No budget targets configured yet. Set a monthly budget to boost your score."

    # 4. Savings Goal Progress (Max 15)
    if goals and len(goals) > 0:
        percentages = []
        for g in goals:
            target = getattr(g, 'target_amount', 0.0)
            current = getattr(g, 'current_amount', 0.0)
            pct = (current / target * 100.0) if target > 0 else 0.0
            percentages.append(pct)
        avg_progress = sum(percentages) / len(percentages) if percentages else 0.0

        if avg_progress >= 75:
            goal_pts = 15
            goal_desc = f"Strong goal progress: averaging {avg_progress:.1f}% toward milestones."
        elif avg_progress >= 40:
            goal_pts = 12
            goal_desc = f"Good progress: averaging {avg_progress:.1f}% toward savings goals."
        elif avg_progress > 0:
            goal_pts = 8
            goal_desc = f"Active goals established with {avg_progress:.1f}% progress."
        else:
            goal_pts = 5
            goal_desc = "Goals created, but no funds allocated to them yet."
    else:
        goal_pts = 5
        goal_desc = "No active savings goals. Establishing clear targets improves financial discipline."

    # 5. Stability Buffer (Max 10)
    if savings > 0 and expenses > 0:
        months_buffer = savings / expenses
        if months_buffer >= 1.0:
            buffer_pts = 10
            buffer_desc = "Positive monthly cash flow provides an immediate security cushion."
        else:
            buffer_pts = 7
            buffer_desc = "Positive net savings, maintaining a modest liquidity margin."
    elif savings > 0 and expenses == 0:
        buffer_pts = 10
        buffer_desc = "Income intact without recorded liabilities."
    elif savings == 0:
        buffer_pts = 4
        buffer_desc = "Breakeven cash flow without buffer reserve."
    else:
        buffer_pts = 0
        buffer_desc = "Negative cash flow drains savings and increases debt exposure."

    total_score = int(round(savings_pts + expense_pts + budget_pts + goal_pts + buffer_pts))
    total_score = max(0, min(100, total_score))

    # Categorize score
    if total_score >= 80:
        rating = "Excellent"
        color = "#10b981"
        badge_class = "status-excellent"
        summary = "Your financial habits are disciplined and on track for long-term wealth building."
    elif total_score >= 60:
        rating = "Good"
        color = "#0ea5e9"
        badge_class = "status-good"
        summary = "Solid financial foundation with room for targeted optimization."
    elif total_score >= 40:
        rating = "Needs Improvement"
        color = "#f59e0b"
        badge_class = "status-warning"
        summary = "Elevated spending or low savings indicate vulnerabilities to unexpected shocks."
    else:
        rating = "Critical"
        color = "#ef4444"
        badge_class = "status-critical"
        summary = "Expenses outpace income or savings are depleted. Immediate budgeting intervention advised."

    breakdown = [
        {
            'factor': 'Savings Rate',
            'score': savings_pts,
            'max_score': 30,
            'description': savings_desc
        },
        {
            'factor': 'Expense-to-Income Ratio',
            'score': expense_pts,
            'max_score': 25,
            'description': expense_desc
        },
        {
            'factor': 'Budget Adherence',
            'score': budget_pts,
            'max_score': 20,
            'description': budget_desc
        },
        {
            'factor': 'Savings Goal Progress',
            'score': goal_pts,
            'max_score': 15,
            'description': goal_desc
        },
        {
            'factor': 'Cash Flow Stability',
            'score': buffer_pts,
            'max_score': 10,
            'description': buffer_desc
        }
    ]

    disclaimer = (
        "This Financial Health Score is an educational indicator based on user-provided data. "
        "It is not a credit score, credit rating, or certified financial advice."
    )

    return {
        'score': total_score,
        'rating': rating,
        'color': color,
        'badge_class': badge_class,
        'summary': summary,
        'breakdown': breakdown,
        'savings_rate': round(savings_rate, 1),
        'expense_ratio': round(expense_ratio, 1),
        'disclaimer': disclaimer
    }
