from typing import Any
from langgraph.graph import END, START, StateGraph

from app.agent.nodes.analyze_task import analyze_task_node
from app.agent.nodes.decide_strategy import decide_strategy_node
from app.agent.nodes.execute_skill import execute_skill_node
from app.agent.nodes.generate_skill import generate_skill_node
from app.agent.nodes.persist_skill import persist_skill_node
from app.agent.nodes.retrieve_skills import retrieve_skills_node
from app.agent.state import AgentState
from app.services.execution_service import ExecutionService
from app.services.generation_service import GenerationService
from app.services.retrieval_service import RetrievalService
from app.services.skill_service import SkillService


def create_agent_graph(
    generation_service: GenerationService,
    retrieval_service: RetrievalService,
    skill_service: SkillService,
    execution_service: ExecutionService,
):
    """
    Build and compile the SkillVault LangGraph StateGraph.
    """
    builder = StateGraph(AgentState)

    # Node wrappers passing services
    async def n_analyze(state: AgentState):
        return await analyze_task_node(state, generation_service)

    async def n_retrieve(state: AgentState):
        return await retrieve_skills_node(state, retrieval_service)

    def n_decide(state: AgentState):
        return decide_strategy_node(state)

    async def n_generate(state: AgentState):
        return await generate_skill_node(state, generation_service)

    async def n_persist(state: AgentState):
        return await persist_skill_node(state, skill_service)

    async def n_execute(state: AgentState):
        return await execute_skill_node(state, skill_service, execution_service)

    # Add Nodes
    builder.add_node("analyze_task", n_analyze)
    builder.add_node("retrieve_skills", n_retrieve)
    builder.add_node("decide_strategy", n_decide)
    builder.add_node("generate_skill", n_generate)
    builder.add_node("persist_skill", n_persist)
    builder.add_node("execute_skill", n_execute)

    # Add Edges
    builder.add_edge(START, "analyze_task")
    builder.add_edge("analyze_task", "retrieve_skills")
    builder.add_edge("retrieve_skills", "decide_strategy")

    # Conditional Branching
    def route_strategy(state: AgentState) -> str:
        return state.get("strategy", "GENERATE")

    builder.add_conditional_edges(
        "decide_strategy",
        route_strategy,
        {
            "REUSE": "execute_skill",
            "GENERATE": "generate_skill",
        },
    )

    builder.add_edge("generate_skill", "persist_skill")
    builder.add_edge("persist_skill", "execute_skill")
    builder.add_edge("execute_skill", END)

    return builder.compile()
