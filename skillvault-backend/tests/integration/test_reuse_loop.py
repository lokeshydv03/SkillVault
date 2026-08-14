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
async def test_reuse_loop_and_metrics_increment(db_session):
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

    # 1. Seed built-in skills
    await skill_service.seed_builtin_skills()

    # 2. Query matching csv-analyzer built-in skill
    prompt = "Analyze employees.csv and calculate average salary."

    # Run 1
    res1 = await task_service.create_and_execute_task(prompt)
    assert res1.status == "completed"
    assert res1.strategy == "reuse"
    assert res1.skill["slug"] in ["csv-analyzer", "csv_analyzer"]
    assert res1.execution["status"] == "SUCCESS"

    skill_after_run1 = await skill_repo.get_by_slug(res1.skill["slug"])
    assert skill_after_run1.usage_count == 1
    assert skill_after_run1.success_count == 1

    # Run 2
    res2 = await task_service.create_and_execute_task(prompt)
    assert res2.status == "completed"
    assert res2.strategy == "reuse"
    assert res2.execution["status"] == "SUCCESS"

    skill_after_run2 = await skill_repo.get_by_slug(res1.skill["slug"])
    assert skill_after_run2.usage_count == 2
    assert skill_after_run2.success_count == 2


@pytest.mark.asyncio
async def test_missing_capability_triggers_generation(db_session):
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

    await skill_service.seed_builtin_skills()

    missing_prompt = "Render 3D SVG model from complex matrix data."
    res = await task_service.create_and_execute_task(missing_prompt)

    assert res.status == "completed"
    assert res.strategy == "generate"
    assert res.execution["status"] == "DRAFT_SAVED"
