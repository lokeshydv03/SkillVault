from typing import Any
from app.agent.graph import create_agent_graph
from app.core.exceptions import TaskNotFoundError
from app.db.models.task import Task
from app.db.repositories.execution_repository import ExecutionRepository
from app.db.repositories.task_repository import TaskRepository
from app.schemas.task import TaskExecutionResponse
from app.services.execution_service import ExecutionService
from app.services.generation_service import GenerationService
from app.services.retrieval_service import RetrievalService
from app.services.skill_service import SkillService


class TaskService:
    def __init__(
        self,
        task_repo: TaskRepository,
        execution_repo: ExecutionRepository,
        generation_service: GenerationService,
        retrieval_service: RetrievalService,
        skill_service: SkillService,
        execution_service: ExecutionService,
    ):
        self.task_repo = task_repo
        self.execution_repo = execution_repo
        self.generation_service = generation_service
        self.retrieval_service = retrieval_service
        self.skill_service = skill_service
        self.execution_service = execution_service

    async def get_task(self, task_id: str) -> Task:
        task = await self.task_repo.get_by_id(task_id)
        if not task:
            raise TaskNotFoundError(task_id)
        return task

    async def create_and_execute_task(self, user_input: str) -> TaskExecutionResponse:
        # 1. Create task record PENDING
        task = await self.task_repo.create(user_input=user_input)

        # 2. Build LangGraph workflow
        app = create_agent_graph(
            generation_service=self.generation_service,
            retrieval_service=self.retrieval_service,
            skill_service=self.skill_service,
            execution_service=self.execution_service,
        )

        initial_state = {
            "task_id": task.id,
            "user_input": user_input,
        }

        # 3. Update task status ANALYZING
        await self.task_repo.update_status(task.id, status="ANALYZING")

        # 4. Invoke LangGraph workflow
        final_state: dict[str, Any] = await app.ainvoke(initial_state)

        # 5. Extract output artifacts & audit trace
        strategy = final_state.get("strategy", "GENERATE")
        retrieved_skills = final_state.get("retrieved_skills", [])
        selected_skill = final_state.get("selected_skill")
        execution_result = final_state.get("execution_result", {})
        err = final_state.get("error") or execution_result.get("error")

        exec_status = execution_result.get("status")
        if exec_status in ("SUCCESS", "DRAFT_SAVED"):
            final_status = "COMPLETED"
        else:
            final_status = "FAILED"

        if err and not exec_status in ("SUCCESS", "DRAFT_SAVED"):
            final_status = "FAILED"

        retrieval_trace = {
            "query": user_input,
            "normalized_task": final_state.get("normalized_task"),
            "candidates": [
                {"skill_id": r.get("skill_id"), "name": r.get("name"), "score": r.get("score")}
                for r in retrieved_skills
            ],
            "selected_skill": selected_skill.get("slug") if selected_skill else None,
            "strategy": strategy,
        }

        # 6. Update task in DB
        await self.task_repo.update_status(
            task_id=task.id,
            status=final_status,
            strategy=strategy,
            normalized_task=final_state.get("normalized_task"),
            retrieval_trace=retrieval_trace,
            result_data=execution_result.get("output_data"),
            error=err,
        )

        return TaskExecutionResponse(
            task_id=task.id,
            status=final_status.lower(),
            strategy=strategy.lower(),
            skill=selected_skill,
            execution=execution_result,
            result=execution_result.get("output_data"),
            error=err,
        )

    async def get_task_executions(self, task_id: str):
        await self.get_task(task_id)
        return await self.execution_repo.get_by_task_id(task_id)
