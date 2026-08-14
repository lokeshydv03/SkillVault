from datetime import datetime, timezone
from typing import Any
from sqlalchemy import DateTime, Float, ForeignKey, String, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.utils.ids import generate_id


class Execution(Base):
    __tablename__ = "executions"

    id: Mapped[str] = mapped_column(
        String(64), primary_key=True, default=lambda: generate_id("exec")
    )
    task_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False, index=True
    )
    skill_id: Mapped[str | None] = mapped_column(
        String(64), ForeignKey("skills.id", ondelete="SET NULL"), nullable=True, index=True
    )
    skill_version_id: Mapped[str | None] = mapped_column(
        String(64), ForeignKey("skill_versions.id", ondelete="SET NULL"), nullable=True, index=True
    )

    strategy: Mapped[str] = mapped_column(String(32), default="REUSE", index=True)  # REUSE, GENERATE, REPAIR, RETRY
    retrieval_score: Mapped[float | None] = mapped_column(Float, nullable=True)

    status: Mapped[str] = mapped_column(String(32), default="PENDING", index=True)  # PENDING, RUNNING, SUCCESS, FAILED, DRAFT_SAVED
    input_data: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    output_data: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    error: Mapped[str | None] = mapped_column(Text, nullable=True)
    latency_ms: Mapped[float | None] = mapped_column(Float, nullable=True)
    metadata_info: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    task: Mapped["Task"] = relationship("Task", back_populates="executions")
    skill: Mapped["Skill | None"] = relationship("Skill", back_populates="executions")
    skill_version: Mapped["SkillVersion | None"] = relationship(
        "SkillVersion", back_populates="executions"
    )
