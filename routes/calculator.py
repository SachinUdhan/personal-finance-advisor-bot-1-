from flask import Blueprint, render_template, request, jsonify
from services.finance_calculator import calculate_emi, format_inr

calculator_bp = Blueprint('calculator', __name__)


@calculator_bp.route('/calculator', methods=['GET', 'POST'])
def emi_calculator():
    result = None
    principal = 500000.0
    annual_rate = 8.5
    tenure_months = 36
    error = None

    if request.method == 'POST':
        try:
            p_val = float(request.form.get('principal', 0))
            r_val = float(request.form.get('annual_rate', 0))
            n_val = int(request.form.get('tenure_months', 0))

            if p_val <= 0 or n_val <= 0 or r_val < 0:
                error = "Loan amount and tenure must be positive numbers. Interest rate cannot be negative."
            else:
                principal = p_val
                annual_rate = r_val
                tenure_months = n_val
                result = calculate_emi(principal, annual_rate, tenure_months)
        except (ValueError, TypeError):
            error = "Please enter valid numeric figures for loan calculation."
    else:
        # Default preview calculation
        result = calculate_emi(principal, annual_rate, tenure_months)

    return render_template(
        'calculator.html',
        result=result,
        principal=principal,
        annual_rate=annual_rate,
        tenure_months=tenure_months,
        error=error,
        format_inr=format_inr
    )


@calculator_bp.route('/api/calculator/calculate', methods=['POST'])
def api_calculate_emi():
    data = request.get_json() or {}
    try:
        principal = float(data.get('principal', 0))
        annual_rate = float(data.get('annual_rate', 0))
        tenure_months = int(data.get('tenure_months', 0))

        if principal <= 0 or tenure_months <= 0 or annual_rate < 0:
            return jsonify({'error': 'Invalid inputs: Principal and tenure must be > 0, rate >= 0'}), 400

        result = calculate_emi(principal, annual_rate, tenure_months)
        return jsonify(result)
    except (ValueError, TypeError) as e:
        return jsonify({'error': str(e)}), 400
