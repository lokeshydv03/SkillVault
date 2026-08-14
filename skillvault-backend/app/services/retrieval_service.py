from app.core.config import settings
from app.db.models.skill import Skill
from app.db.repositories.skill_repository import SkillRepository
from app.schemas.skill import SkillSearchResult
from app.services.embedding_service import EmbeddingService


class RetrievalService:
    def __init__(self, skill_repo: SkillRepository, embedding_service: EmbeddingService):
        self.skill_repo = skill_repo
        self.embedding_service = embedding_service

    def calculate_rerank_score(
        self, skill: Skill, semantic_score: float
    ) -> tuple[float, float, float]:
        """
        Reranking formula specified:
        final_score = 0.70 * semantic_score + 0.15 * reliability + 0.10 * success_rate + 0.05 * compatibility
        """
        reliability_score = 1.0 if skill.risk_level in ("TRUSTED", "LOW") else 0.70
        success_rate = (
            skill.success_count / skill.usage_count
            if skill.usage_count > 0
            else 1.0
        )
        compatibility_score = 1.0

        final_score = (
            settings.SEMANTIC_WEIGHT * semantic_score
            + settings.RELIABILITY_WEIGHT * reliability_score
            + settings.SUCCESS_RATE_WEIGHT * success_rate
            + settings.COMPATIBILITY_WEIGHT * compatibility_score
        )

        return round(final_score, 4), reliability_score, round(success_rate, 4)

    async def search_similar_skills(
        self, query: str, top_k: int = settings.TOP_K_SKILLS
    ) -> list[SkillSearchResult]:
        query_vector = await self.embedding_service.generate_embedding(query)
        candidates = await self.skill_repo.search_similar(
            query_embedding=query_vector, top_k=top_k, status_filter="ACTIVE"
        )

        results: list[SkillSearchResult] = []
        for skill, sem_score in candidates:
            final_score, rel_score, success_rate = self.calculate_rerank_score(skill, sem_score)
            results.append(
                SkillSearchResult(
                    skill_id=skill.id,
                    name=skill.name,
                    slug=skill.slug,
                    description=skill.description,
                    capability=skill.capability,
                    score=final_score,
                    semantic_score=round(sem_score, 4),
                    reliability_score=rel_score,
                    success_rate=success_rate,
                    status=skill.status,
                )
            )

        results.sort(key=lambda r: r.score, reverse=True)
        return results
