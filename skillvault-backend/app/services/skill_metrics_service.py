from datetime import datetime, timezone
from app.db.repositories.skill_repository import SkillRepository


class SkillMetricsService:
    """Centralized service for skill telemetry and execution metrics updating."""

    def __init__(self, skill_repo: SkillRepository):
        self.skill_repo = skill_repo

    async def record_execution_metric(self, skill_id: str, success: bool) -> None:
        skill = await self.skill_repo.get_by_id(skill_id)
        if not skill:
            return

        now = datetime.now(timezone.utc)
        skill.usage_count += 1
        if success:
            skill.success_count += 1
            skill.last_used_at = now
        else:
            skill.failure_count += 1

        self.skill_repo.session.add(skill)
        await self.skill_repo.session.flush()
