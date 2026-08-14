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
async def test_generated_skill_security_boundary_draft_saved(db_session):
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

    # Seed built-in skills
    await skill_service.seed_builtin_skills()

    # Prompt requiring missing capability
    untrusted_prompt = "Render 3D SVG model from complex matrix data."
    response = await task_service.create_and_execute_task(untrusted_prompt)

    assert response.status == "completed"
    assert response.strategy == "generate"

    # Verify execution notice states sandbox requirement and status is DRAFT_SAVED
    assert response.execution["status"] == "DRAFT_SAVED"
    assert "Docker Sandbox environment is required" in response.execution["output_data"]["notice"]

    # Verify generated skill in DB is persisted with DRAFT status
    generated_skill = await skill_repo.get_by_id(response.skill["skill_id"])
    assert generated_skill is not None
    assert generated_skill.status == "DRAFT"
    assert generated_skill.source_type == "GENERATED"
