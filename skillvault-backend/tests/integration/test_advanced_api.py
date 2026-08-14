import pytest


@pytest.mark.asyncio
async def test_analytics_overview_endpoint(async_client):
    response = await async_client.get("/api/v1/analytics/overview")
    assert response.status_code == 200
    data = response.json()
    assert "total_skills" in data
    assert "active_skills" in data
    assert "draft_skills" in data
    assert "success_rate" in data


@pytest.mark.asyncio
async def test_capability_gaps_endpoint(async_client):
    response = await async_client.get("/api/v1/analytics/capability-gaps")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_workflows_lifecycle(async_client):
    # First get skills to obtain a valid skill_id
    skills_res = await async_client.get("/api/v1/skills")
    assert skills_res.status_code == 200
    skills = skills_res.json()["items"]
    assert len(skills) > 0
    valid_skill_id = skills[0]["id"]

    # Create workflow
    payload = {
        "name": "Test Data Pipeline Workflow",
        "description": "Multi-step workflow test",
        "steps": [
            {
                "step_number": 1,
                "skill_id": valid_skill_id,
                "input_mapping": {"data": "test_input"},
                "output_mapping": {"result": "step_1_output"},
            }
        ],
    }

    create_res = await async_client.post("/api/v1/workflows", json=payload)
    assert create_res.status_code == 201
    wf = create_res.json()
    assert "id" in wf
    assert wf["steps_count"] == 1

    # List workflows
    list_res = await async_client.get("/api/v1/workflows")
    assert list_res.status_code == 200
    assert len(list_res.json()) >= 1


@pytest.mark.asyncio
async def test_direct_skill_execution_and_stats(async_client):
    skills_res = await async_client.get("/api/v1/skills")
    skills = skills_res.json()["items"]
    valid_skill_id = skills[0]["id"]

    # Stats
    stats_res = await async_client.get(f"/api/v1/skills/{valid_skill_id}/stats")
    assert stats_res.status_code == 200
    stats = stats_res.json()
    assert "quality_score" in stats
    assert "quality_components" in stats

    # Direct Execute with custom python code skill creation
    create_skill_res = await async_client.post(
        "/api/v1/skills",
        json={
            "name": "Custom Math Multiplier",
            "description": "Multiplies input number by 2",
            "capability": "math, multiplication",
            "category": "math",
            "status": "ACTIVE",
            "source_type": "BUILTIN",
            "risk_level": "LOW",
            "code": "def run(input_data: dict) -> dict:\n    val = input_data.get('x', 0)\n    return {'result': val * 2}\n",
            "language": "python",
            "entrypoint": "run",
        },
    )
    assert create_skill_res.status_code == 201
    new_skill_id = create_skill_res.json()["id"]

    exec_res = await async_client.post(
        f"/api/v1/skills/{new_skill_id}/execute",
        json={"inputs": {"x": 21}},
    )
    assert exec_res.status_code == 200
    res_data = exec_res.json()
    assert "execution_id" in res_data
    assert res_data["status"] == "SUCCESS"
    assert res_data["output"] == {"result": 42}
