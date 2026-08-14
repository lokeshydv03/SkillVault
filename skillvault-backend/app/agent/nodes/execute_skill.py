from typing import Any
from app.agent.state import AgentState
from app.services.execution_service import ExecutionService
from app.services.skill_service import SkillService


async def execute_skill_node(
    state: AgentState,
    skill_service: SkillService,
    execution_service: ExecutionService,
) -> dict[str, Any]:
    task_id = state["task_id"]
    selected = state.get("selected_skill")
    user_input = state["user_input"]
    strategy = state.get("strategy", "REUSE")

    if not selected or "skill_id" not in selected:
        return {"error": "No valid skill selected for execution."}

    skill = await skill_service.get_skill(selected["skill_id"])
    active_ver = skill.active_version
    retrieval_score = selected.get("score")

    input_payload = {"input": user_input, "task_id": task_id}

    res = await execution_service.execute_skill(
        task_id=task_id,
        skill_version=active_ver,
        input_data=input_payload,
        strategy=strategy,
        retrieval_score=retrieval_score,
    )

    return {"execution_result": res.model_dump()}
