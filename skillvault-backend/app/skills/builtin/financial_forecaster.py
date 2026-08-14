from typing import Any


def run(input_data: dict[str, Any]) -> dict[str, Any]:
    """
    Financial Variance & Q3/Q4 Revenue Forecaster.
    Parses revenue and expenses, computes growth rates, projects Q3/Q4 revenue, and evaluates budget risk.
    """
    q1 = float(input_data.get("revenue_q1", 1000000))
    q2 = float(input_data.get("revenue_q2", 1250000))
    expenses = float(input_data.get("expenses", 850000))

    growth_rate = ((q2 - q1) / q1) if q1 > 0 else 0.0
    q3_projected = q2 * (1 + growth_rate)
    q4_projected = q3_projected * (1 + growth_rate)
    total_annual_projected = q1 + q2 + q3_projected + q4_projected
    net_profit_projected = total_annual_projected - (expenses * 4)
    margin_pct = (net_profit_projected / total_annual_projected * 100) if total_annual_projected > 0 else 0.0

    return {
        "status": "success",
        "quarterly_growth_rate_pct": round(growth_rate * 100, 2),
        "q3_projected_revenue": round(q3_projected, 2),
        "q4_projected_revenue": round(q4_projected, 2),
        "total_annual_projected_revenue": round(total_annual_projected, 2),
        "net_profit_projected": round(net_profit_projected, 2),
        "profit_margin_pct": round(margin_pct, 2),
        "budget_overrun_risk": "LOW" if margin_pct > 20 else "HIGH",
    }
