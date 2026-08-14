from typing import Any
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.skill import Skill
from app.db.models.execution import Execution
from app.db.models.capability_gap import CapabilityGap


class AnalyticsService:
    def __init__(self, session: AsyncSession):
        self.session = session

    def calculate_quality_score(self, skill: Skill) -> tuple[float, dict[str, float]]:
        """
        Calculates a multi-signal Skill Quality Score (0.0 to 1.0) based on:
          - 35% Success Rate
          - 20% Test Score (validation status)
          - 15% Reliability (failure count penalty)
          - 10% Performance (latency rating)
          - 10% Usage / Reuse Volume
          - 10% Validation Score
        """
        total = skill.usage_count or 0
        success = skill.success_count or 0
        failures = skill.failure_count or 0

        success_rate = (success / total) if total > 0 else 1.0
        test_score = 1.0 if skill.status == "ACTIVE" else 0.7 if skill.status == "DRAFT" else 0.4
        reliability = max(0.0, 1.0 - (failures * 0.1))
        performance = 0.9  # Baseline latency score
        usage_component = min(1.0, total / 20.0)
        validation_score = 1.0 if skill.risk_level in ("LOW", "TRUSTED") else 0.6

        quality_score = round(
          (0.35 * success_rate)
          + (0.20 * test_score)
          + (0.15 * reliability)
          + (0.10 * performance)
          + (0.10 * usage_component)
          + (0.10 * validation_score),
          3,
        )

        components = {
            "success_rate": round(success_rate, 3),
            "test_score": round(test_score, 3),
            "reliability": round(reliability, 3),
            "performance": round(performance, 3),
            "usage": round(usage_component, 3),
            "validation": round(validation_score, 3),
        }

        return quality_score, components

    async def get_overview_metrics(self) -> dict[str, Any]:
        """
        Dashboard overview metrics.
        """
        total_skills_res = await self.session.execute(select(func.count()).select_from(Skill))
        total_skills = total_skills_res.scalar_one()

        active_skills_res = await self.session.execute(
            select(func.count()).select_from(Skill).where(Skill.status == "ACTIVE")
        )
        active_skills = active_skills_res.scalar_one()

        draft_skills_res = await self.session.execute(
            select(func.count()).select_from(Skill).where(Skill.status == "DRAFT")
        )
        draft_skills = draft_skills_res.scalar_one()

        total_execs_res = await self.session.execute(select(func.count()).select_from(Execution))
        total_executions = total_execs_res.scalar_one()

        successful_execs_res = await self.session.execute(
            select(func.count()).select_from(Execution).where(Execution.status.in_(["SUCCESS", "DRAFT_SAVED"]))
        )
        successful_executions = successful_execs_res.scalar_one()

        overall_success_rate = (
            round((successful_executions / total_executions) * 100, 1) if total_executions > 0 else 100.0
        )

        gaps_res = await self.session.execute(select(func.count()).select_from(CapabilityGap))
        total_gaps = gaps_res.scalar_one()

        return {
            "total_skills": total_skills,
            "active_skills": active_skills,
            "draft_skills": draft_skills,
            "total_executions": total_executions,
            "success_rate": overall_success_rate,
            "total_capability_gaps": total_gaps,
        }

    async def get_capability_gaps(self) -> list[dict[str, Any]]:
        result = await self.session.execute(
            select(CapabilityGap).order_by(CapabilityGap.occurrences_count.desc())
        )
        gaps = result.scalars().all()
        return [
            {
                "id": gap.id,
                "task_description": gap.task_description,
                "required_capability": gap.required_capability,
                "occurrences": gap.occurrences_count,
                "priority": gap.priority,
                "last_seen_at": gap.last_seen_at.isoformat(),
            }
            for gap in gaps
        ]
