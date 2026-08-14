from typing import Any, Callable

from app.skills.builtin.churn_sentiment_predictor import run as run_churn_sentiment
from app.skills.builtin.executive_contract_summarizer import run as run_contract_summarizer
from app.skills.builtin.financial_forecaster import run as run_financial_forecaster
from app.skills.builtin.llm_cost_optimizer import run as run_cost_optimizer
from app.skills.builtin.security_audit_scanner import run as run_security_scanner
from app.skills.builtin.csv_analyzer import run as run_csv_analyzer

BUILTIN_SKILLS_MAP: dict[str, Callable[[dict[str, Any]], dict[str, Any]]] = {
    "financial-forecaster": run_financial_forecaster,
    "security-audit-scanner": run_security_scanner,
    "churn-sentiment-predictor": run_churn_sentiment,
    "executive-contract-summarizer": run_contract_summarizer,
    "llm-cost-optimizer": run_cost_optimizer,
    "csv-analyzer": run_csv_analyzer,
}

BUILTIN_SKILL_DEFINITIONS: list[dict[str, Any]] = [
    {
        "name": "Financial Variance & Revenue Forecaster",
        "slug": "financial-forecaster",
        "description": "Parse enterprise quarterly revenue & expense records, compute YoY variance, project Q3/Q4 financial growth trajectory, and evaluate budget overrun risks.",
        "capability": "Financial forecasting, revenue projection, YoY variance calculation, budget overrun risk analysis, profit margin calculation",
        "category": "finance",
        "risk_level": "LOW",
        "input_schema": {
            "type": "object",
            "properties": {
                "revenue_q1": {"type": "number", "default": 1000000},
                "revenue_q2": {"type": "number", "default": 1250000},
                "expenses": {"type": "number", "default": 850000},
            },
        },
        "output_schema": {
            "type": "object",
            "properties": {
                "status": {"type": "string"},
                "q3_projected_revenue": {"type": "number"},
                "total_annual_projected_revenue": {"type": "number"},
                "profit_margin_pct": {"type": "number"},
                "budget_overrun_risk": {"type": "string"},
            },
        },
        "code": "BUILTIN:financial_forecaster",
        "version": "1.0.0",
    },
    {
        "name": "SOC2 & GDPR Security Compliance Audit Scanner",
        "slug": "security-audit-scanner",
        "description": "Scan customer support logs, database exports, and API traces for leaked PII (SSNs, Credit Cards, JWT tokens) and generate SOC2 compliance risk scores.",
        "capability": "SOC2 compliance scanning, PII detection, SSN leak detection, credit card audit, JWT token inspection, GDPR compliance rating",
        "category": "security",
        "risk_level": "LOW",
        "input_schema": {
            "type": "object",
            "properties": {
                "log_text": {
                    "type": "string",
                    "default": "User logged in with email john@company.com, SSN: 000-12-3456, token: eyJhbGci...",
                }
            },
        },
        "output_schema": {
            "type": "object",
            "properties": {
                "status": {"type": "string"},
                "compliance_score": {"type": "integer"},
                "risk_level": {"type": "string"},
                "violations_found": {"type": "object"},
                "soc2_status": {"type": "string"},
            },
        },
        "code": "BUILTIN:security_audit_scanner",
        "version": "1.0.0",
    },
    {
        "name": "Customer Churn Risk & Sentiment Analyzer",
        "slug": "churn-sentiment-predictor",
        "description": "Analyze customer CRM feedback, support ticket urgency, and renewal windows to calculate churn probability and flag high-risk enterprise accounts for VP intervention.",
        "capability": "Customer churn risk prediction, Zendesk ticket analysis, renewal risk scoring, sentiment classification, VP escalation alerts",
        "category": "customer_operations",
        "risk_level": "LOW",
        "input_schema": {
            "type": "object",
            "properties": {
                "account_name": {"type": "string", "default": "Acme Enterprise Corp"},
                "support_tickets_30d": {"type": "integer", "default": 12},
                "sentiment_score": {"type": "number", "default": -0.65},
                "days_to_renewal": {"type": "integer", "default": 45},
            },
        },
        "output_schema": {
            "type": "object",
            "properties": {
                "status": {"type": "string"},
                "churn_probability_pct": {"type": "number"},
                "risk_category": {"type": "string"},
                "executive_action": {"type": "string"},
            },
        },
        "code": "BUILTIN:churn_sentiment_predictor",
        "version": "1.0.0",
    },
    {
        "name": "Executive Legal Contract & RFP Synthesizer",
        "slug": "executive-contract-summarizer",
        "description": "Process enterprise vendor contracts or RFPs, extract financial commitments, auto-renewal clauses, and jurisdiction laws to build 1-page executive decision briefings.",
        "capability": "Legal contract parsing, RFP synthesis, financial commitment extraction, auto-renewal clause detection, executive briefing generation",
        "category": "executive_reporting",
        "risk_level": "LOW",
        "input_schema": {
            "type": "object",
            "properties": {
                "contract_title": {"type": "string", "default": "Master Cloud Services Agreement"},
                "contract_value": {"type": "number", "default": 750000},
                "auto_renew": {"type": "boolean", "default": True},
                "governing_law": {"type": "string", "default": "Delaware"},
            },
        },
        "output_schema": {
            "type": "object",
            "properties": {
                "status": {"type": "string"},
                "contract_title": {"type": "string"},
                "total_financial_commitment": {"type": "string"},
                "executive_recommendation": {"type": "string"},
                "approval_tier": {"type": "string"},
            },
        },
        "code": "BUILTIN:executive_contract_summarizer",
        "version": "1.0.0",
    },
    {
        "name": "LLM Token ROI & Cost Savings Calculator",
        "slug": "llm-cost-optimizer",
        "description": "Quantify financial ROI achieved by SkillVault by reusing cached Python capabilities vs. executing LLM code generation calls for enterprise tasks.",
        "capability": "LLM cost optimization, token savings calculation, ROI metric tracking, latency reduction estimation, financial efficiency audit",
        "category": "cost_optimization",
        "risk_level": "LOW",
        "input_schema": {
            "type": "object",
            "properties": {
                "total_tasks_processed": {"type": "integer", "default": 5000},
                "skill_reuse_count": {"type": "integer", "default": 4200},
                "avg_tokens_per_llm_call": {"type": "integer", "default": 3500},
            },
        },
        "output_schema": {
            "type": "object",
            "properties": {
                "status": {"type": "string"},
                "reuse_rate_pct": {"type": "number"},
                "total_tokens_saved": {"type": "integer"},
                "estimated_cost_saved_usd": {"type": "string"},
                "roi_multiplier": {"type": "string"},
            },
        },
        "code": "BUILTIN:llm_cost_optimizer",
        "version": "1.0.0",
    },
    {
        "name": "CSV Analyzer",
        "slug": "csv-analyzer",
        "description": "Analyze structured CSV datasets, employee tables, tabular data, column statistics, row counts, missing value inspection, and profiling.",
        "capability": "CSV parsing, employee salary analysis, column statistics, row aggregation, data profiling, missing value detection",
        "category": "data_analysis",
        "risk_level": "LOW",
        "input_schema": {
            "type": "object",
            "properties": {
                "file_path": {"type": "string", "default": "sample_data/employees.csv"}
            },
        },
        "output_schema": {
            "type": "object",
            "properties": {
                "status": {"type": "string"},
                "total_rows": {"type": "integer"},
                "columns": {"type": "array"},
                "column_analysis": {"type": "object"},
            },
        },
        "code": "BUILTIN:csv_analyzer",
        "version": "1.0.0",
    },
]
