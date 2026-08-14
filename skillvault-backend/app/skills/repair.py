from typing import Any
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models.failure import SkillFailure
from app.db.models.version import SkillVersion
from app.services.llm_provider import LLMProvider
from app.utils.ids import generate_id
from pydantic import BaseModel, Field


class RepairedSkillProposal(BaseModel):
    code: str = Field(..., description="Repaired Python source code")
    explanation: str = Field(..., description="Explanation of root cause fix")


class SkillRepairEngine:
    def __init__(self, session: AsyncSession, llm_provider: LLMProvider):
        self.session = session
        self.llm_provider = llm_provider

    async def record_failure(
        self,
        skill_id: str,
        skill_version_id: str | None,
        execution_id: str | None,
        failure_type: str,
        error_message: str,
        stack_trace: str | None = None,
        input_payload: dict[str, Any] | None = None,
    ) -> SkillFailure:
        """
        Persists structured failure context into Skill Vault Failure Memory.
        """
        failure = SkillFailure(
            skill_id=skill_id,
            skill_version_id=skill_version_id,
            execution_id=execution_id,
            failure_type=failure_type,
            error_message=error_message,
            stack_trace=stack_trace,
            input_payload=input_payload or {},
        )
        self.session.add(failure)
        await self.session.flush()
        return failure

    async def propose_repair(
        self,
        skill_id: str,
        failing_code: str,
        failure_type: str,
        error_message: str,
    ) -> dict[str, Any]:
        """
        Synthesizes a proposed repair candidate version using LLM,
        leaving status as REPAIR_CANDIDATE (never auto-promoting).
        """
        system_prompt = (
            "You are an expert Python Security & Bug Repair Engine. "
            "Analyze the failing Python skill code and error context, and produce a corrected implementation. "
            "Maintain entrypoint contract 'def run(input_data: dict) -> dict:'."
        )

        user_prompt = (
            f"Failing Skill Code:\n```python\n{failing_code}\n```\n\n"
            f"Failure Type: {failure_type}\n"
            f"Error Message: {error_message}\n\n"
            "Propose a repaired implementation."
        )

        proposal: RepairedSkillProposal = await self.llm_provider.generate_structured(
            prompt=user_prompt,
            response_model=RepairedSkillProposal,
            system_prompt=system_prompt,
        )

        repair_version_id = generate_id("ver")
        repair_version = SkillVersion(
            id=repair_version_id,
            skill_id=skill_id,
            version="1.1.0-REPAIR",
            code=proposal.code,
            language="python",
            entrypoint="run",
            description=f"Repair candidate: {proposal.explanation}",
            metadata_info={"repair_status": "REPAIR_CANDIDATE", "fix": proposal.explanation},
        )
        self.session.add(repair_version)
        await self.session.flush()

        return {
            "version_id": repair_version_id,
            "version": "1.1.0-REPAIR",
            "status": "REPAIR_CANDIDATE",
            "explanation": proposal.explanation,
            "code": proposal.code,
        }
