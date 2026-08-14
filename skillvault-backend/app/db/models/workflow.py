from datetime import datetime, timezone
from typing import Any
from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.utils.ids import generate_id


class SkillWorkflow(Base):
    __tablename__ = "skill_workflows"

    id: Mapped[str] = mapped_column(
        String(64), primary_key=True, default=lambda: generate_id("workflow")
    )
    name: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    slug: Mapped[str] = mapped_column(String(128), nullable=False, unique=True, index=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="ACTIVE", index=True)
    input_schema: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    output_schema: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    steps_definition: Mapped[list[dict[str, Any]]] = mapped_column(JSON, default=list)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    steps: Mapped[list["SkillWorkflowStep"]] = relationship(
        "SkillWorkflowStep",
        back_populates="workflow",
        cascade="all, delete-orphan",
        order_by="SkillWorkflowStep.step_number",
    )


class SkillWorkflowStep(Base):
    __tablename__ = "skill_workflow_steps"

    id: Mapped[str] = mapped_column(
        String(64), primary_key=True, default=lambda: generate_id("step")
    )
    workflow_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("skill_workflows.id", ondelete="CASCADE"), nullable=False
    )
    step_number: Mapped[int] = mapped_column(Integer, nullable=False)
    skill_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("skills.id"), nullable=False
    )
    input_mapping: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    output_mapping: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    condition: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)

    workflow: Mapped["SkillWorkflow"] = relationship(
        "SkillWorkflow", back_populates="steps"
    )
    skill: Mapped["Skill"] = relationship("Skill")
