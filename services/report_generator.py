from typing import Dict, Any, List
from datetime import datetime
from services.finance_calculator import format_inr, calculate_savings_rate
from services.financial_health import calculate_financial_health_score


def generate_monthly_report_data(
    user,
    incomes: List[Any],
    expenses: List[Any],
    goals: List[Any],
    budgets: List[Any]
) -> Dict[str, Any]:
    """
    Synthesizes a structured monthly financial report containing cash flow analysis,
    category distributions, goal tracking, and personalized observations.
    """
    total_income = sum(float(i.amount) for i in incomes)
    # If no separate income transaction exists, fallback to user's registered monthly_income
    if total_income == 0 and user.monthly_income > 0:
        total_income = float(user.monthly_income)

    total_expenses = sum(float(e.amount) for e in expenses)
    net_savings = total_income - total_expenses
    savings_rate = calculate_savings_rate(total_income, total_expenses)

    # Category totals and percentages
    category_totals = {}
    for exp in expenses:
        cat = exp.category
        category_totals[cat] = category_totals.get(cat, 0.0) + float(exp.amount)

    sorted_categories = sorted(
        category_totals.items(),
        key=lambda item: item[1],
        reverse=True
    )

    category_breakdown = []
    for cat, amt in sorted_categories:
        pct = (amt / total_expenses * 100.0) if total_expenses > 0 else 0.0
        category_breakdown.append({
            'category': cat,
            'amount': round(amt, 2),
            'formatted_amount': format_inr(amt),
            'percentage': round(pct, 1)
        })

    top_category = sorted_categories[0][0] if sorted_categories else "None"
    top_category_amount = sorted_categories[0][1] if sorted_categories else 0.0

    # Budget planned total
    total_planned_budget = sum(float(b.planned_amount) for b in budgets)

    # Health score
    health_data = calculate_financial_health_score(
        income=total_income,
        expenses=total_expenses,
        planned_budget=total_planned_budget,
        goals=goals
    )

    # Goals breakdown
    goals_data = [g.to_dict() for g in goals]

    # Observations & Actionable Takeaways
    observations = []
    if total_income > 0 and total_expenses > total_income:
        observations.append(
            f"Deficit Spending: Recorded expenses ({format_inr(total_expenses)}) exceed total income ({format_inr(total_income)}) "
            f"by {format_inr(total_expenses - total_income)}. Recommended action: Review discretionary expenses immediately."
        )
    elif savings_rate >= 20:
        observations.append(
            f"Solid Savings Habit: You saved {savings_rate}% ({format_inr(net_savings)}) this period, satisfying the recommended 20% benchmark."
        )
    else:
        observations.append(
            f"Low Savings Rate: At {savings_rate}%, your savings margin is tight. Setting automated transfers right on payday can help retain more cash."
        )

    if top_category != "None" and total_expenses > 0:
        top_pct = (top_category_amount / total_expenses) * 100.0
        observations.append(
            f"Leading Expense: {top_category} accounts for {top_pct:.1f}% ({format_inr(top_category_amount)}) of all spending this period."
        )

    if total_planned_budget > 0:
        if total_expenses <= total_planned_budget:
            variance = total_planned_budget - total_expenses
            observations.append(
                f"Budget Adherence: Congratulations! You remained under your planned budget by {format_inr(variance)}."
            )
        else:
            variance = total_expenses - total_planned_budget
            observations.append(
                f"Budget Overrun: Actual expenses exceeded planned budget by {format_inr(variance)}. Adjust future category caps accordingly."
            )

    if not goals:
        observations.append("Goal Target: No active savings goals detected. Formulating an Emergency Fund goal is recommended.")
    else:
        completed = sum(1 for g in goals if g.is_completed)
        observations.append(f"Goals Milestones: {completed} of {len(goals)} active savings goals have reached 100% completion.")

    return {
        'report_date': datetime.now().strftime('%B %d, %Y'),
        'user_name': user.full_name,
        'user_email': user.email,
        'total_income': total_income,
        'formatted_total_income': format_inr(total_income),
        'total_expenses': total_expenses,
        'formatted_total_expenses': format_inr(total_expenses),
        'net_savings': net_savings,
        'formatted_net_savings': format_inr(net_savings),
        'savings_rate': savings_rate,
        'category_breakdown': category_breakdown,
        'top_category': top_category,
        'formatted_top_category_amount': format_inr(top_category_amount),
        'health_score': health_data['score'],
        'health_rating': health_data['rating'],
        'health_color': health_data['color'],
        'health_summary': health_data['summary'],
        'goals': goals_data,
        'observations': observations,
        'total_planned_budget': total_planned_budget,
        'formatted_planned_budget': format_inr(total_planned_budget),
        'disclaimer': health_data['disclaimer']
    }
