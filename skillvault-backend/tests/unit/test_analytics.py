import pytest
from app.db.models.skill import Skill
from app.services.analytics_service import AnalyticsService


def test_quality_score_calculation():
    skill = Skill(
        id="skill_test",
        name="Test Skill",
        status="ACTIVE",
        risk_level="LOW",
        usage_count=10,
        success_count=9,
        failure_count=1,
    )
    service = AnalyticsService(session=None)
    score, components = service.calculate_quality_score(skill)

    assert 0.0 <= score <= 1.0
    assert "success_rate" in components
    assert "reliability" in components
    assert components["success_rate"] == 0.9
