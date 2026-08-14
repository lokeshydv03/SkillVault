import pytest
from app.db.repositories.execution_repository import ExecutionRepository
from app.db.repositories.skill_repository import SkillRepository
from app.db.repositories.task_repository import TaskRepository
from app.services.embedding_service import EmbeddingService
from app.services.execution_service import ExecutionService
from app.services.generation_service import GenerationService
from app.services.llm_provider import MockLLMProvider
from app.services.retrieval_service import RetrievalService
from app.services.skill_metrics_service import SkillMetricsService
from app.services.skill_service import SkillService
from app.services.task_service import TaskService
from app.skills.executor import LocalSkillExecutor


@pytest.mark.asyncio
async def test_agent_reuse_existing_skill(db_session):
    mock_llm = MockLLMProvider()
    task_repo = TaskRepository(db_session)
    skill_repo = SkillRepository(db_session)
    exec_repo = ExecutionRepository(db_session)

    emb_service = EmbeddingService(mock_llm)
    gen_service = GenerationService(mock_llm)
    ret_service = RetrievalService(skill_repo, emb_service)
    skill_service = SkillService(skill_repo, emb_service)
    metrics_service = SkillMetricsService(skill_repo)
    exec_service = ExecutionService(exec_repo, metrics_service, LocalSkillExecutor())

    task_service = TaskService(
        task_repo=task_repo,
        execution_repo=exec_repo,
        generation_service=gen_service,
        retrieval_service=ret_service,
        skill_service=skill_service,
        execution_service=exec_service,
    )

    # Seed built-in capabilities
    await skill_service.seed_builtin_skills()

    response = await task_service.create_and_execute_task(
        "Analyze employees.csv and calculate average salary."
    )

    assert response.status == "completed"
    assert response.task_id is not None
    assert response.strategy in ("reuse", "generate")
    assert response.result is not None


@pytest.mark.asyncio
async def test_agent_generate_missing_skill(db_session):
    mock_llm = MockLLMProvider()
    task_repo = TaskRepository(db_session)
    skill_repo = SkillRepository(db_session)
    exec_repo = ExecutionRepository(db_session)

    emb_service = EmbeddingService(mock_llm)
    gen_service = GenerationService(mock_llm)
    ret_service = RetrievalService(skill_repo, emb_service)
    skill_service = SkillService(skill_repo, emb_service)
    metrics_service = SkillMetricsService(skill_repo)
    exec_service = ExecutionService(exec_repo, metrics_service, LocalSkillExecutor())

    task_service = TaskService(
        task_repo=task_repo,
        execution_repo=exec_repo,
        generation_service=gen_service,
        retrieval_service=ret_service,
        skill_service=skill_service,
        execution_service=exec_service,
    )

    response = await task_service.create_and_execute_task(
        "Convert employees.csv into a polished HTML report containing charts."
    )

    assert response.status == "completed"
    assert response.task_id is not None
    assert response.result is not None
