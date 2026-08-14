from datetime import datetime, timezone
from typing import Any
from sqlalchemy import DateTime, ForeignKey, String, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.utils.ids import generate_id


class TaskEvent(Base):
    __tablename__ = "task_events"

    id: Mapped[str] = mapped_column(
        String(64), primary_key=True, default=lambda: generate_id("event")
    )
    task_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False, index=True
    )
    event_type: Mapped[str] = mapped_column(
        String(64), nullable=False, index=True
    )  # TASK_RECEIVED, SKILL_SEARCH_STARTED, SKILL_FOUND, SKILL_SELECTED, SKILL_GENERATION_STARTED, SKILL_GENERATED, VALIDATION_STARTED, VALIDATION_PASSED, WORKFLOW_COMPOSED, EXECUTION_STARTED, EXECUTION_COMPLETED, EXECUTION_FAILED
    payload: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    task: Mapped["Task"] = relationship("Task")
