from datetime import datetime, timezone
from typing import Any
from sqlalchemy import select, update, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.models.execution import Execution


class ExecutionRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(
        self,
        task_id: str,
        skill_id: str | None = None,
        skill_version_id: str | None = None,
        strategy: str = "REUSE",
        retrieval_score: float | None = None,
        input_data: dict[str, Any] | None = None,
        metadata_info: dict[str, Any] | None = None,
    ) -> Execution:
        execution = Execution(
            task_id=task_id,
            skill_id=skill_id,
            skill_version_id=skill_version_id,
            strategy=strategy,
            retrieval_score=retrieval_score,
            status="PENDING",
            input_data=input_data or {},
            metadata_info=metadata_info or {},
        )
        self.session.add(execution)
        await self.session.flush()
        return execution

    async def complete_execution(
        self,
        execution_id: str,
        status: str,  # SUCCESS, FAILED, DRAFT_SAVED
        output_data: dict[str, Any] | None = None,
        error: str | None = None,
        latency_ms: float = 0.0,
    ) -> Execution | None:
        stmt = (
            update(Execution)
            .where(Execution.id == execution_id)
            .values(
                status=status,
                output_data=output_data,
                error=error,
                latency_ms=latency_ms,
                completed_at=datetime.now(timezone.utc),
            )
            .returning(Execution)
        )
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

    async def get_by_id(self, execution_id: str) -> Execution | None:
        result = await self.session.execute(
            select(Execution)
            .options(selectinload(Execution.skill), selectinload(Execution.skill_version))
            .where(Execution.id == execution_id)
        )
        return result.scalar_one_or_none()

    async def get_by_task_id(self, task_id: str) -> list[Execution]:
        result = await self.session.execute(
            select(Execution)
            .where(Execution.task_id == task_id)
            .order_by(Execution.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_by_skill_id(self, skill_id: str) -> list[Execution]:
        result = await self.session.execute(
            select(Execution)
            .where(Execution.skill_id == skill_id)
            .order_by(Execution.created_at.desc())
        )
        return list(result.scalars().all())

    async def list_all(
        self,
        page: int = 1,
        limit: int = 20,
    ) -> tuple[list[Execution], int]:
        count_stmt = select(func.count()).select_from(Execution)
        total_res = await self.session.execute(count_stmt)
        total = total_res.scalar_one()

        offset = (page - 1) * limit
        stmt = (
            select(Execution)
            .order_by(Execution.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        items = list(result.scalars().all())
        return items, total
