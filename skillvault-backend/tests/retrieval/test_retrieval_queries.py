import pytest
from app.db.repositories.skill_repository import SkillRepository
from app.services.embedding_service import EmbeddingService
from app.services.llm_provider import MockLLMProvider
from app.services.retrieval_service import RetrievalService
from app.services.skill_service import SkillService


@pytest.mark.asyncio
async def test_retrieval_queries_return_matching_skill_in_top_k(db_session):
    mock_llm = MockLLMProvider()
    skill_repo = SkillRepository(db_session)
    emb_service = EmbeddingService(mock_llm)
    ret_service = RetrievalService(skill_repo, emb_service)

    # Seed capabilities
    skill_service = SkillService(skill_repo, emb_service)
    await skill_service.seed_builtin_skills()

    queries = [
        ("Calculate Q3 financial revenue variance", ["financial-forecaster", "Financial Variance & Revenue Forecaster"]),
        ("SOC2 PII security compliance audit", ["security-audit-scanner", "SOC2 & GDPR Security Compliance Audit Scanner"]),
        ("Customer churn probability and Zendesk ticket sentiment", ["churn-sentiment-predictor", "Customer Churn Risk & Sentiment Analyzer"]),
        ("Executive legal contract RFP synthesis", ["executive-contract-summarizer", "Executive Legal Contract & RFP Synthesizer"]),
        ("LLM token cost ROI optimization", ["llm-cost-optimizer", "LLM Token ROI & Cost Savings Calculator"]),
        ("Calculate average salary from employees.csv", ["csv-analyzer", "CSV Analyzer"]),
    ]

    for query, expected_identifiers in queries:
        results = await ret_service.search_similar_skills(query=query, top_k=5)
        assert len(results) > 0, f"No skills retrieved for query '{query}'"

        # Verify expected skill appears within top K results
        top_names_and_slugs = [r.name for r in results] + [r.slug for r in results]
        found = any(exp in top_names_and_slugs for exp in expected_identifiers)
        assert found, f"Expected one of {expected_identifiers} in top K for query '{query}', got {[r.name for r in results]}"
