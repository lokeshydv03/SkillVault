from datetime import datetime, timezone
from typing import Any
from sqlalchemy import DateTime, ForeignKey, Integer, Float, String, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import TypeDecorator
from pgvector.sqlalchemy import Vector

from app.core.config import settings
from app.db.base import Base
from app.utils.ids import generate_id


class VectorType(TypeDecorator):
    """
    Custom SQLAlchemy TypeDecorator for Vector embeddings.
    Uses native pgvector Vector(dim) when on PostgreSQL, falling back to JSON for SQLite.
    """
    impl = JSON
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            return dialect.type_descriptor(Vector(settings.SKILL_EMBEDDING_DIMENSION))
        return dialect.type_descriptor(JSON())


class Skill(Base):
    __tablename__ = "skills"

    id: Mapped[str] = mapped_column(
        String(64), primary_key=True, default=lambda: generate_id("skill")
    )
    name: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    slug: Mapped[str] = mapped_column(String(128), nullable=False, unique=True, index=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    capability: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[str] = mapped_column(String(64), default="general", index=True)
    
    # Skill Lifecycle: GENERATED, DRAFT, VALIDATING, ACTIVE, DEPRECATED, ARCHIVED
    status: Mapped[str] = mapped_column(String(32), default="DRAFT", index=True)
    
    # Skill Provenance
    source_type: Mapped[str] = mapped_column(String(32), default="BUILTIN", index=True)  # BUILTIN, GENERATED, IMPORTED, AGENT_EVOLVED
    created_by: Mapped[str] = mapped_column(String(32), default="SYSTEM")                # SYSTEM, AGENT, USER

    risk_level: Mapped[str] = mapped_column(String(32), default="UNTRUSTED")
    input_schema: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    output_schema: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    dependencies: Mapped[list[str]] = mapped_column(JSON, default=list)

    embedding: Mapped[list[float] | None] = mapped_column(
        VectorType(), nullable=True
    )

    active_version_id: Mapped[str | None] = mapped_column(
        String(64),
        ForeignKey("skill_versions.id", use_alter=True, name="fk_skills_active_version_id"),
        nullable=True,
    )

    usage_count: Mapped[int] = mapped_column(Integer, default=0)
    success_count: Mapped[int] = mapped_column(Integer, default=0)
    failure_count: Mapped[int] = mapped_column(Integer, default=0)
    quality_score: Mapped[float] = mapped_column(Float, default=0.0)
    quality_components: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    last_used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    versions: Mapped[list["SkillVersion"]] = relationship(
        "SkillVersion",
        back_populates="skill",
        foreign_keys="SkillVersion.skill_id",
        cascade="all, delete-orphan",
    )
    executions: Mapped[list["Execution"]] = relationship(
        "Execution", back_populates="skill"
    )
    active_version: Mapped["SkillVersion | None"] = relationship(
        "SkillVersion",
        foreign_keys=[active_version_id],
        post_update=True,
    )
