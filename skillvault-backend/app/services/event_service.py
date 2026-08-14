from typing import Any
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models.task_event import TaskEvent


class EventService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def log_event(
        self,
        task_id: str,
        event_type: str,
        payload: dict[str, Any] | None = None,
    ) -> TaskEvent:
        event = TaskEvent(
            task_id=task_id,
            event_type=event_type,
            payload=payload or {},
        )
        self.session.add(event)
        await self.session.flush()
        return event

    async def get_task_events(self, task_id: str) -> list[TaskEvent]:
        result = await self.session.execute(
            select(TaskEvent)
            .where(TaskEvent.task_id == task_id)
            .order_by(TaskEvent.created_at.asc())
        )
        return list(result.scalars().all())
