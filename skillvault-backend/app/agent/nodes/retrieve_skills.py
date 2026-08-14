from typing import Any
from app.agent.state import AgentState
from app.services.retrieval_service import RetrievalService


async def retrieve_skills_node(
    state: AgentState, retrieval_service: RetrievalService
) -> dict[str, Any]:
    user_input = state.get("user_input", "")
    normalized = state.get("normalized_task", "")
    query = f"{user_input} {normalized}".strip()

    results = await retrieval_service.search_similar_skills(query)

    retrieved = [r.model_dump() for r in results]
    selected = retrieved[0] if retrieved else None

    return {
        "retrieved_skills": retrieved,
        "selected_skill": selected,
    }
