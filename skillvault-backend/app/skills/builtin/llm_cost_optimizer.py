from typing import Any


def run(input_data: dict[str, Any]) -> dict[str, Any]:
    """
    LLM Token ROI & Cost Savings Calculator.
    Calculates cost saved by SkillVault via skill reuse vs. calling GPT-4o for every enterprise task.
    """
    total_tasks = int(input_data.get("total_tasks_processed", 5000))
    reuse_count = int(input_data.get("skill_reuse_count", 4200))
    tokens_per_call = int(input_data.get("avg_tokens_per_llm_call", 3500))

    tokens_saved = reuse_count * tokens_per_call
    cost_saved_usd = (tokens_saved / 1000.0) * 0.015
    reuse_rate_pct = (reuse_count / total_tasks * 100) if total_tasks > 0 else 0.0
    latency_saved_seconds = reuse_count * 3.5

    return {
        "status": "success",
        "total_tasks_processed": total_tasks,
        "skills_reused_count": reuse_count,
        "reuse_rate_pct": round(reuse_rate_pct, 1),
        "total_tokens_saved": tokens_saved,
        "estimated_cost_saved_usd": f"${cost_saved_usd:,.2f}",
        "total_time_saved_hours": round(latency_saved_seconds / 3600.0, 2),
        "roi_multiplier": f"{round(cost_saved_usd / 50.0, 1)}x",
    }
