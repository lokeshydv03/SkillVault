import pytest
from app.db.models.skill import Skill
from app.db.repositories.skill_repository import SkillRepository
from app.services.embedding_service import EmbeddingService
from app.services.llm_provider import MockLLMProvider
from app.services.retrieval_service import RetrievalService


def test_rerank_scoring_formula():
    mock_llm = MockLLMProvider()
    emb_service = EmbeddingService(mock_llm)
    # We can test score calculation formula directly
    retrieval_service = RetrievalService(None, emb_service)

    trusted_skill = Skill(
        name="CSV Analyzer",
        risk_level="TRUSTED",
        usage_count=10,
        success_count=9,
        failure_count=1,
    )

    final_score, rel_score, success_rate = retrieval_service.calculate_rerank_score(
        trusted_skill, semantic_score=0.90
    )

    # 0.70 * 0.90 + 0.15 * 1.0 + 0.10 * 0.90 + 0.05 * 1.0 = 0.63 + 0.15 + 0.09 + 0.05 = 0.92
    assert final_score == 0.92
    assert rel_score == 1.0
    assert success_rate == 0.9
