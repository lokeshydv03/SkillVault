import pytest
from app.db.models.skill import Skill
from app.schemas.execution import ExecutionResult
from app.services.skill_evaluator import BasicSkillEvaluator


@pytest.mark.asyncio
async def test_basic_evaluator_success():
    evaluator = BasicSkillEvaluator()
    skill = Skill(name="CSV Analyzer", status="ACTIVE")
    res = ExecutionResult(
        status="SUCCESS", output_data={"status": "success", "rows": 10}, latency_ms=12.5
    )

    eval_res = await evaluator.evaluate(skill, "Analyze CSV", res)
    assert eval_res.is_passed is True
    assert eval_res.score == 1.0


@pytest.mark.asyncio
async def test_basic_evaluator_failed_execution():
    evaluator = BasicSkillEvaluator()
    skill = Skill(name="CSV Analyzer", status="ACTIVE")
    res = ExecutionResult(
        status="FAILED", output_data={}, error="Division by zero", latency_ms=5.0
    )

    eval_res = await evaluator.evaluate(skill, "Analyze CSV", res)
    assert eval_res.is_passed is False
    assert eval_res.score == 0.0
