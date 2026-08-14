from typing import Any
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.task import Task


class TaskRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, user_input: str) -> Task:
        task = Task(user_input=user_input, status="PENDING")
        self.session.add(task)
        await self.session.flush()
        return task

    async def get_by_id(self, task_id: str) -> Task | None:
        result = await self.session.execute(select(Task).where(Task.id == task_id))
        return result.scalar_one_or_none()

    async def update_status(
        self,
        task_id: str,
        status: str,
        strategy: str | None = None,
        normalized_task: str | None = None,
        retrieval_trace: dict[str, Any] | None = None,
        result_data: dict[str, Any] | None = None,
        error: str | None = None,
    ) -> Task | None:
        update_vals: dict[str, Any] = {"status": status}
        if strategy is not None:
            update_vals["strategy"] = strategy
        if normalized_task is not None:
            update_vals["normalized_task"] = normalized_task
        if retrieval_trace is not None:
            update_vals["retrieval_trace"] = retrieval_trace
        if result_data is not None:
            update_vals["result"] = result_data
        if error is not None:
            update_vals["error"] = error

        stmt = (
            update(Task)
            .where(Task.id == task_id)
            .values(**update_vals)
            .returning(Task)
        )
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()
