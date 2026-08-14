from datetime import datetime, timezone
from typing import Any
from sqlalchemy import DateTime, ForeignKey, String, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.utils.ids import generate_id


class SkillFailure(Base):
    __tablename__ = "skill_failures"

    id: Mapped[str] = mapped_column(
        String(64), primary_key=True, default=lambda: generate_id("failure")
    )
    skill_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("skills.id"), nullable=False, index=True
    )
    skill_version_id: Mapped[str | None] = mapped_column(
        String(64), ForeignKey("skill_versions.id"), nullable=True
    )
    execution_id: Mapped[str | None] = mapped_column(
        String(64), ForeignKey("executions.id"), nullable=True
    )
    failure_type: Mapped[str] = mapped_column(
        String(64), default="RUNTIME_ERROR", index=True
    )  # INPUT_ERROR, LOGIC_ERROR, RUNTIME_ERROR, TIMEOUT, DEPENDENCY_ERROR, OUTPUT_VALIDATION_ERROR, SECURITY_VALIDATION_ERROR
    error_message: Mapped[str] = mapped_column(Text, nullable=False)
    stack_trace: Mapped[str | None] = mapped_column(Text, nullable=True)
    input_payload: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    skill: Mapped["Skill"] = relationship("Skill")
