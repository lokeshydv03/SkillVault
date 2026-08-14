from datetime import datetime
from typing import Any
from pydantic import BaseModel, Field

from app.schemas.common import BaseSchema


class TaskCreate(BaseModel):
    input: str = Field(..., description="User's task prompt / input instruction")


class TaskAnalysis(BaseModel):
    task_type: str = Field(default="general", description="Categorized task type")
    required_capabilities: list[str] = Field(default_factory=list, description="Capabilities needed")
    input_type: str = Field(default="text", description="Type of input expected")
    output_type: str = Field(default="structured", description="Type of output expected")
    complexity: str = Field(default="medium", description="Estimated complexity (low, medium, high)")


class TaskResponse(BaseSchema):
    id: str
    user_input: str
    normalized_task: str | None = None
    status: str
    strategy: str | None = None
    result: dict[str, Any] | None = None
    error: str | None = None
    created_at: datetime
    updated_at: datetime


class TaskExecutionResponse(BaseModel):
    task_id: str
    status: str
    strategy: str
    skill: dict[str, Any] | None = None
    execution: dict[str, Any] | None = None
    result: dict[str, Any] | None = None
    error: str | None = None
