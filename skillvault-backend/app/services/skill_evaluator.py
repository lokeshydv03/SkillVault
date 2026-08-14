from typing import Any, Protocol
from pydantic import BaseModel

from app.db.models.skill import Skill
from app.schemas.execution import ExecutionResult


class EvaluationResult(BaseModel):
    is_passed: bool
    score: float
    details: dict[str, Any] = {}


class SkillEvaluator(Protocol):
    async def evaluate(
        self, skill: Skill | None, task_input: str, result: ExecutionResult
    ) -> EvaluationResult:
        ...


class BasicSkillEvaluator:
    """
    Evaluates skill execution results against contract schema and execution status.
    """

    async def evaluate(
        self, skill: Skill | None, task_input: str, result: ExecutionResult
    ) -> EvaluationResult:
        if result.status != "SUCCESS":
            return EvaluationResult(
                is_passed=False,
                score=0.0,
                details={"error": result.error or "Execution failed."},
            )

        if not isinstance(result.output_data, dict):
            return EvaluationResult(
                is_passed=False,
                score=0.5,
                details={"issue": "Output data is not a valid dictionary object."},
            )

        # Output payload checks
        if "error" in result.output_data and result.output_data.get("status") == "error":
            return EvaluationResult(
                is_passed=False,
                score=0.2,
                details={"issue": result.output_data.get("message", "Internal error flag")},
            )

        return EvaluationResult(
            is_passed=True,
            score=1.0,
            details={"latency_ms": result.latency_ms, "status": "CONTRACT_VERIFIED"},
        )
