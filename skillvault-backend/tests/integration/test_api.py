import pytest


@pytest.mark.asyncio
async def test_health_check(async_client):
    response = await async_client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.asyncio
async def test_list_skills(async_client):
    response = await async_client.get("/api/v1/skills")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert data["total"] >= 0


@pytest.mark.asyncio
async def test_search_skills(async_client):
    payload = {"query": "CSV statistical analysis", "top_k": 3}
    response = await async_client.post("/api/v1/skills/search", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "results" in data


@pytest.mark.asyncio
async def test_create_task(async_client):
    payload = {"input": "Analyze text and calculate word count"}
    response = await async_client.post("/api/v1/tasks", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "task_id" in data
    assert data["status"] == "completed"

    task_id = data["task_id"]
    get_res = await async_client.get(f"/api/v1/tasks/{task_id}")
    assert get_res.status_code == 200
    assert get_res.json()["id"] == task_id


@pytest.mark.asyncio
async def test_list_executions(async_client):
    response = await async_client.get("/api/v1/executions")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
