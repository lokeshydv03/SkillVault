import pytest
from app.db.models.skill import Skill
from app.db.models.skill_version import SkillVersion
from app.skills.executor import LocalSkillExecutor


@pytest.mark.asyncio
async def test_local_executor_builtin_skill():
    executor = LocalSkillExecutor()
    skill = Skill(name="CSV Analyzer", slug="csv-analyzer")
    version = SkillVersion(skill=skill, code="", entrypoint="run")

    input_data = {
        "csv_text": "id,name,salary\n1,Alice,80000\n2,Bob,90000"
    }

    res = await executor.execute(version, input_data)
    assert res.status == "SUCCESS"
    assert res.output_data["total_rows"] == 2
    assert "column_analysis" in res.output_data
    assert "salary" in res.output_data["column_analysis"]
    assert res.output_data["column_analysis"]["salary"]["avg"] == 85000.0


@pytest.mark.asyncio
async def test_local_executor_dynamic_python_code():
    executor = LocalSkillExecutor()
    code = """def run(input_data: dict) -> dict:
    val = input_data.get('x', 0)
    return {'result': val * 2}
"""
    skill = Skill(name="Custom Math", slug="custom_math")
    version = SkillVersion(skill=skill, code=code, entrypoint="run")

    res = await executor.execute(version, {"x": 21})
    assert res.status == "SUCCESS"
    assert res.output_data["result"] == 42
