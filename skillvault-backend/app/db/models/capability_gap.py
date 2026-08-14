from datetime import datetime, timezone
from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.utils.ids import generate_id


class CapabilityGap(Base):
    __tablename__ = "capability_gaps"

    id: Mapped[str] = mapped_column(
        String(64), primary_key=True, default=lambda: generate_id("gap")
    )
    task_description: Mapped[str] = mapped_column(Text, nullable=False)
    required_capability: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    occurrences_count: Mapped[int] = mapped_column(Integer, default=1)
    priority: Mapped[str] = mapped_column(String(32), default="MEDIUM", index=True)  # LOW, MEDIUM, HIGH

    last_seen_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
