from typing import Any

from app.db.models.skill import Skill
from app.db.models.skill_version import SkillVersion
from app.db.repositories.execution_repository import ExecutionRepository
from app.schemas.execution import ExecutionResult
from app.services.skill_metrics_service import SkillMetricsService
from app.skills.executor import SkillExecutor


class ExecutionService:
    def __init__(
        self,
        execution_repo: ExecutionRepository,
        metrics_service: SkillMetricsService,
        executor: SkillExecutor,
    ):
        self.execution_repo = execution_repo
        self.metrics_service = metrics_service
        self.executor = executor

    async def execute_skill(
        self,
        task_id: str,
        skill_version: SkillVersion | None,
        input_data: dict[str, Any],
        strategy: str = "REUSE",
        retrieval_score: float | None = None,
    ) -> ExecutionResult:
        skill_id = skill_version.skill_id if skill_version else None
        version_id = skill_version.id if skill_version else None
        
        # Async fetch skill object to prevent MissingGreenlet error on lazy-loaded relation
        skill_obj = await self.execution_repo.session.get(Skill, skill_id) if skill_id else None

        # SECURITY BOUNDARY CHECK:
        # Generated / UNTRUSTED skills MUST NOT be executed directly on the host!
        if skill_obj and (skill_obj.source_type == "GENERATED" or skill_obj.status == "DRAFT" or skill_obj.risk_level == "UNTRUSTED"):
            # If not in built-in dispatch list
            slug = skill_obj.slug
            from app.skills.builtin import BUILTIN_SKILLS_MAP
            if slug not in BUILTIN_SKILLS_MAP:
                res = ExecutionResult(
                    status="DRAFT_SAVED",
                    output_data={
                        "notice": "Skill synthesized, AST validated & persisted as DRAFT in Skill Vault. Docker Sandbox environment is required for dynamic execution.",
                        "skill_id": skill_obj.id,
                        "skill_name": skill_obj.name,
                        "status": "DRAFT",
                        "source_type": skill_obj.source_type,
                    },
                    latency_ms=0.0,
                )
                execution = await self.execution_repo.create(
                    task_id=task_id,
                    skill_id=skill_id,
                    skill_version_id=version_id,
                    strategy=strategy,
                    retrieval_score=retrieval_score,
                    input_data=input_data,
                )
                await self.execution_repo.complete_execution(
                    execution_id=execution.id,
                    status=res.status,
                    output_data=res.output_data,
                    latency_ms=0.0,
                )
                return res

        # 1. Create PENDING execution record
        execution = await self.execution_repo.create(
            task_id=task_id,
            skill_id=skill_id,
            skill_version_id=version_id,
            strategy=strategy,
            retrieval_score=retrieval_score,
            input_data=input_data,
        )

        # 2. Execute skill via executor abstraction
        res: ExecutionResult = await self.executor.execute(skill_version, input_data)

        # 3. Complete execution record
        await self.execution_repo.complete_execution(
            execution_id=execution.id,
            status=res.status,
            output_data=res.output_data,
            error=res.error,
            latency_ms=res.latency_ms,
        )

        # 4. Centralized metric tracking
        if skill_id:
            await self.metrics_service.record_execution_metric(
                skill_id=skill_id, success=(res.status == "SUCCESS")
            )

        return res
