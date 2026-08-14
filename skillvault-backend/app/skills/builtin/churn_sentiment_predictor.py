from typing import Any


def run(input_data: dict[str, Any]) -> dict[str, Any]:
    """
    Customer Account Churn Risk & Sentiment Analyzer.
    Analyzes ticket volume, sentiment, and renewal window to calculate churn risk.
    """
    account = str(input_data.get("account_name", "Acme Enterprise Corp"))
    tickets = int(input_data.get("support_tickets_30d", 12))
    sentiment = float(input_data.get("sentiment_score", -0.65))
    days_renew = int(input_data.get("days_to_renewal", 45))

    churn_prob = 0.10
    if tickets > 8:
        churn_prob += 0.35
    if sentiment < -0.3:
        churn_prob += 0.35
    if days_renew < 60:
        churn_prob += 0.15

    churn_prob = min(0.99, churn_prob)
    risk_category = "HIGH_CHURN_RISK" if churn_prob > 0.6 else "MODERATE_RISK" if churn_prob > 0.3 else "HEALTHY"

    return {
        "status": "success",
        "account_name": account,
        "churn_probability_pct": round(churn_prob * 100, 1),
        "risk_category": risk_category,
        "executive_action": "Schedule VP Executive Sponsor Call Immediately" if churn_prob > 0.6 else "Standard Customer Success Review",
        "retention_priority": "URGENT" if churn_prob > 0.6 else "NORMAL",
    }
