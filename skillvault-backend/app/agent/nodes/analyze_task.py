from typing import Any
from app.agent.state import AgentState
from app.services.generation_service import GenerationService


async def analyze_task_node(
    state: AgentState, generation_service: GenerationService
) -> dict[str, Any]:
    user_input = state["user_input"]
    analysis = await generation_service.analyze_task(user_input)

    normalized = f"[{analysis.task_type}] Capabilities: {', '.join(analysis.required_capabilities)}"
    return {
        "task_analysis": analysis.model_dump(),
        "normalized_task": normalized,
    }
