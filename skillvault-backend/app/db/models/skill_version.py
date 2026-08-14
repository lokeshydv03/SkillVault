from datetime import datetime, timezone
from typing import Any
from sqlalchemy import DateTime, ForeignKey, String, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.utils.ids import generate_id


class SkillVersion(Base):
    __tablename__ = "skill_versions"

    id: Mapped[str] = mapped_column(
        String(64), primary_key=True, default=lambda: generate_id("ver")
    )
    skill_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("skills.id", ondelete="CASCADE"), nullable=False, index=True
    )
    version: Mapped[str] = mapped_column(String(32), nullable=False, default="v1")
    code: Mapped[str] = mapped_column(Text, nullable=False)
    language: Mapped[str] = mapped_column(String(32), default="python")
    entrypoint: Mapped[str] = mapped_column(String(64), default="run")
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    input_schema: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    output_schema: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    dependencies: Mapped[list[str]] = mapped_column(JSON, default=list)
    metadata_info: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    skill: Mapped["Skill"] = relationship(
        "Skill", back_populates="versions", foreign_keys=[skill_id]
    )
    executions: Mapped[list["Execution"]] = relationship(
        "Execution", back_populates="skill_version"
    )
