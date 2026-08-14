from datetime import datetime
from typing import Any
from pydantic import BaseModel, Field

from app.schemas.common import BaseSchema


class SkillVersionResponse(BaseSchema):
    id: str
    skill_id: str
    version: str
    code: str
    language: str
    entrypoint: str
    description: str | None = None
    input_schema: dict[str, Any] = Field(default_factory=dict)
    output_schema: dict[str, Any] = Field(default_factory=dict)
    dependencies: list[str] = Field(default_factory=list)
    metadata_info: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime


class SkillCreate(BaseModel):
    name: str
    description: str
    capability: str
    category: str = "general"
    status: str = "DRAFT"                                    # GENERATED, DRAFT, VALIDATING, ACTIVE, DEPRECATED, ARCHIVED
    source_type: str = "BUILTIN"                            # BUILTIN, GENERATED, IMPORTED
    created_by: str = "SYSTEM"                              # SYSTEM, AGENT, USER
    risk_level: str = "UNTRUSTED"
    input_schema: dict[str, Any] = Field(default_factory=dict)
    output_schema: dict[str, Any] = Field(default_factory=dict)
    dependencies: list[str] = Field(default_factory=list)
    code: str
    language: str = "python"
    entrypoint: str = "run"


class SkillUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    capability: str | None = None
    category: str | None = None
    status: str | None = None
    source_type: str | None = None
    risk_level: str | None = None
    input_schema: dict[str, Any] | None = None
    output_schema: dict[str, Any] | None = None
    dependencies: list[str] | None = None


class SkillResponse(BaseSchema):
    id: str
    name: str
    slug: str
    description: str
    capability: str
    category: str
    status: str
    source_type: str = "BUILTIN"
    created_by: str = "SYSTEM"
    risk_level: str
    input_schema: dict[str, Any]
    output_schema: dict[str, Any]
    dependencies: list[str]
    active_version_id: str | None = None
    usage_count: int
    success_count: int
    failure_count: int
    last_used_at: datetime | None = None
    success_rate: float = 0.0
    created_at: datetime
    updated_at: datetime


class SkillSearchRequest(BaseModel):
    query: str
    top_k: int = Field(default=5, ge=1, le=20)


class SkillSearchResult(BaseModel):
    skill_id: str
    name: str
    slug: str
    description: str
    capability: str
    score: float
    semantic_score: float
    reliability_score: float
    success_rate: float
    status: str
    source_type: str = "BUILTIN"


class GeneratedSkill(BaseModel):
    name: str = Field(..., description="Skill name")
    slug: str = Field(default="", description="URL-friendly slug identifier")
    description: str = Field(..., description="Detailed capability description")
    capability: str = Field(..., description="Key capabilities description")
    category: str = Field(default="general", description="Categorization folder")
    language: str = Field(default="python", description="Programming language")
    entrypoint: str = Field(default="run", description="Main entry point function name")
    code: str = Field(..., description="Valid Python source code defining entrypoint function")
    input_schema: dict[str, Any] = Field(default_factory=dict, description="Input parameters JSON schema")
    output_schema: dict[str, Any] = Field(default_factory=dict, description="Return result JSON schema")
    dependencies: list[str] = Field(default_factory=list, description="Third-party package requirements")
    reasoning: str = Field(default="", description="Why this new skill was synthesized")
