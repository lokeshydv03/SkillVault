from datetime import datetime
from typing import Any
from pydantic import BaseModel, Field

from app.schemas.common import BaseSchema


class ExecutionResponse(BaseSchema):
    id: str
    task_id: str
    skill_id: str | None = None
    skill_version_id: str | None = None
    status: str
    input_data: dict[str, Any] = Field(default_factory=dict)
    output_data: dict[str, Any] | None = None
    error: str | None = None
    latency_ms: float | None = None
    metadata_info: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime
    completed_at: datetime | None = None


class ExecutionResult(BaseModel):
    status: str  # SUCCESS, FAILED
    output_data: dict[str, Any] = Field(default_factory=dict)
    error: str | None = None
    latency_ms: float = 0.0
