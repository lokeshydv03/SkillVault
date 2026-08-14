from typing import Any
from app.agent.state import AgentState
from app.core.config import settings


def decide_strategy_node(state: AgentState) -> dict[str, Any]:
    selected = state.get("selected_skill")
    score = selected.get("score", 0.0) if selected else 0.0
    status = selected.get("status", "DRAFT") if selected else "DRAFT"

    # Only ACTIVE skills meeting similarity threshold can be REUSED.
    # DRAFT / UNTRUSTED skills require GENERATE / Sandbox validation.
    if selected and score >= settings.SKILL_MATCH_THRESHOLD and status == "ACTIVE":
        strategy = "REUSE"
    else:
        strategy = "GENERATE"

    return {"strategy": strategy}
