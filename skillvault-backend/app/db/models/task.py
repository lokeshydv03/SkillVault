from datetime import datetime, timezone
from typing import Any
from sqlalchemy import DateTime, String, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.utils.ids import generate_id


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[str] = mapped_column(
        String(64), primary_key=True, default=lambda: generate_id("task")
    )
    user_input: Mapped[str] = mapped_column(Text, nullable=False)
    normalized_task: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(32), default="PENDING", index=True)
    strategy: Mapped[str | None] = mapped_column(String(32), nullable=True)
    
    # Audit Trace of retrieval candidates & scores
    retrieval_trace: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)

    result: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    error: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    executions: Mapped[list["Execution"]] = relationship(
        "Execution", back_populates="task", cascade="all, delete-orphan"
    )
