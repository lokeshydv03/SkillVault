import re
from typing import Any


def run(input_data: dict[str, Any]) -> dict[str, Any]:
    """
    SOC2 / GDPR PII & Security Audit Scanner.
    Scans logs/data for sensitive PII (SSNs, Credit Cards, JWT Tokens) and evaluates compliance score.
    """
    text = str(input_data.get("log_text", "User logged in, SSN: 000-12-3456, Token: eyJhbGciOi..."))

    ssn_matches = re.findall(r"\b\d{3}-\d{2}-\d{4}\b", text)
    cc_matches = re.findall(r"\b(?:\d[ -]*?){13,16}\b", text)
    email_matches = re.findall(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", text)
    jwt_matches = re.findall(r"eyJ[A-Za-z0-9-_=]+\.[A-Za-z0-9-_=]+\.?[A-Za-z0-9-_.+/=]*", text)

    total_violations = len(ssn_matches) + len(cc_matches) + len(jwt_matches)
    compliance_score = max(0, 100 - (total_violations * 25))
    risk_level = "CRITICAL" if total_violations >= 3 else "MEDIUM" if total_violations > 0 else "COMPLIANT"

    return {
        "status": "success",
        "compliance_score": compliance_score,
        "risk_level": risk_level,
        "violations_found": {
            "ssn_leaks": len(ssn_matches),
            "credit_card_leaks": len(cc_matches),
            "jwt_token_leaks": len(jwt_matches),
            "emails_detected": len(email_matches),
        },
        "soc2_status": "PASS" if compliance_score >= 90 else "ACTION_REQUIRED",
    }
