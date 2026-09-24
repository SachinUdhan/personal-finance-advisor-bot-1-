from typing import Dict, Any


def format_inr(amount: float) -> str:
    """
    Formats a numeric amount into Indian Rupee format (e.g., ₹25,000 or ₹1,50,000).
    """
    if amount is None:
        return "₹0"
    
    is_neg = amount < 0
    abs_amt = round(abs(amount), 2)
    int_part = int(abs_amt)
    dec_part = f"{abs_amt:.2f}".split('.')[1]
    
    s = str(int_part)
    if len(s) <= 3:
        formatted = s
    else:
        last3 = s[-3:]
        remaining = s[:-3]
        groups = []
        while len(remaining) > 2:
            groups.insert(0, remaining[-2:])
            remaining = remaining[:-2]
        if remaining:
            groups.insert(0, remaining)
        formatted = ",".join(groups) + "," + last3
    
    prefix = "-₹" if is_neg else "₹"
    if dec_part == "00":
        return f"{prefix}{formatted}"
    return f"{prefix}{formatted}.{dec_part}"


def calculate_savings_rate(income: float, expenses: float) -> float:
    """
    Calculates the savings percentage: (income - expenses) / income * 100.
    Returns 0.0 if income <= 0.
    """
    if not income or income <= 0:
        return 0.0
    savings = income - expenses
    rate = (savings / income) * 100.0
    return round(rate, 2)


def calculate_emi(principal: float, annual_rate: float, tenure_months: int) -> Dict[str, Any]:
    """
    Calculates standard Equated Monthly Installment (EMI), total payment, and total interest.
    
    Formula:
      EMI = P * r * (1 + r)^n / ((1 + r)^n - 1)
      where:
        P = principal
        r = monthly interest rate (annual_rate / 12 / 100)
        n = tenure in months
        
    Handles zero-interest rate (r == 0) appropriately.
    """
    if principal <= 0 or tenure_months <= 0 or annual_rate < 0:
        raise ValueError("Principal and tenure must be positive, and interest rate must be non-negative.")

    if annual_rate == 0:
        monthly_emi = principal / tenure_months
        total_payment = principal
        total_interest = 0.0
    else:
        r = (annual_rate / 12.0) / 100.0
        n = tenure_months
        factor = (1.0 + r) ** n
        monthly_emi = principal * r * factor / (factor - 1.0)
        total_payment = monthly_emi * n
        total_interest = total_payment - principal

    monthly_emi = round(monthly_emi, 2)
    total_payment = round(total_payment, 2)
    total_interest = round(total_interest, 2)

    return {
        'principal': principal,
        'annual_rate': annual_rate,
        'tenure_months': tenure_months,
        'monthly_emi': monthly_emi,
        'total_payment': total_payment,
        'total_interest': total_interest,
        'formatted_emi': format_inr(monthly_emi),
        'formatted_total_payment': format_inr(total_payment),
        'formatted_total_interest': format_inr(total_interest),
        'interest_percentage': round((total_interest / total_payment) * 100, 1) if total_payment > 0 else 0.0,
        'principal_percentage': round((principal / total_payment) * 100, 1) if total_payment > 0 else 100.0
    }
