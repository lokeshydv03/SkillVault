from typing import Any
from app.agent.state import AgentState
from app.schemas.task import TaskAnalysis
from app.services.generation_service import GenerationService


async def generate_skill_node(
    state: AgentState, generation_service: GenerationService
) -> dict[str, Any]:
    user_input = state["user_input"]
    analysis_dict = state.get("task_analysis", {})
    task_analysis = TaskAnalysis(**analysis_dict)

    generated = await generation_service.generate_skill(user_input, task_analysis)
    return {"generated_skill": generated.model_dump()}
