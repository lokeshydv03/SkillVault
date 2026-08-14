from typing import Any, TypedDict


class AgentState(TypedDict, total=False):
    task_id: str
    user_input: str
    normalized_task: str
    task_analysis: dict[str, Any]
    retrieved_skills: list[dict[str, Any]]
    selected_skill: dict[str, Any] | None
    strategy: str  # REUSE | GENERATE
    generated_skill: dict[str, Any] | None
    generation_status: str | None  # NOT_REQUIRED | GENERATING | GENERATED | VALIDATION_FAILED | PERSISTED_DRAFT
    generation_errors: list[str]
    validation_result: dict[str, Any] | None
    generated_skill_id: str | None
    generated_skill_version_id: str | None
    execution_result: dict[str, Any] | None
    error: str | None
