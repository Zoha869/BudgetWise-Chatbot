"""
Math & Financial Calculator tools.

Pure Python calculations — no external API needed. Keeps the model's
math 100% accurate instead of relying on the LLM to compute it.

Includes:
- calculate_budget   -> totals, savings, % breakdown
- calculate_loan_emi -> monthly EMI, total interest, total payment
"""


CALCULATOR_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "calculate_budget",
            "description": (
                "Calculate total expenses, savings, savings rate, and a "
                "percentage breakdown of each expense category from a "
                "user's income and list of expenses. Use this any time "
                "the user gives concrete numbers and asks for budget "
                "math, totals, or how much they can save."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "income": {
                        "type": "number",
                        "description": "Monthly income after taxes"
                    },
                    "expenses": {
                        "type": "array",
                        "description": "List of expense categories and amounts",
                        "items": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string"},
                                "amount": {"type": "number"}
                            },
                            "required": ["name", "amount"]
                        }
                    }
                },
                "required": ["income", "expenses"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "calculate_loan_emi",
            "description": (
                "Calculate monthly loan/EMI payment, total interest paid, "
                "and total repayment amount given a loan principal, "
                "annual interest rate, and term in months. Use this for "
                "any loan, mortgage, or installment payment question."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "principal": {
                        "type": "number",
                        "description": "Loan amount"
                    },
                    "annual_rate_percent": {
                        "type": "number",
                        "description": "Annual interest rate as a percentage, e.g. 12 for 12%"
                    },
                    "term_months": {
                        "type": "integer",
                        "description": "Loan term in months"
                    }
                },
                "required": ["principal", "annual_rate_percent", "term_months"]
            }
        }
    }
]


def calculate_budget(income, expenses):

    expenses = expenses or []

    total_expenses = sum(
        e.get("amount", 0)
        for e in expenses
    )

    savings = income - total_expenses

    savings_rate = (
        round((savings / income) * 100, 1)
        if income else 0
    )

    breakdown = [
        {
            "name": e.get("name"),
            "amount": e.get("amount", 0),
            "percent_of_income": (
                round((e.get("amount", 0) / income) * 100, 1)
                if income else 0
            )
        }
        for e in expenses
    ]

    return {
        "income": income,
        "total_expenses": total_expenses,
        "savings": savings,
        "savings_rate_percent": savings_rate,
        "breakdown": breakdown
    }


def calculate_loan_emi(principal, annual_rate_percent, term_months):

    monthly_rate = (annual_rate_percent / 100) / 12

    if monthly_rate == 0:
        emi = principal / term_months
    else:
        emi = (
            principal
            * monthly_rate
            * (1 + monthly_rate) ** term_months
        ) / (
            (1 + monthly_rate) ** term_months - 1
        )

    total_payment = emi * term_months
    total_interest = total_payment - principal

    return {
        "monthly_emi": round(emi, 2),
        "total_payment": round(total_payment, 2),
        "total_interest": round(total_interest, 2)
    }