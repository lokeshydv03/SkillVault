from typing import AsyncGenerator
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.database import get_db
from app.db.repositories.execution_repository import ExecutionRepository
from app.db.repositories.skill_repository import SkillRepository
from app.db.repositories.task_repository import TaskRepository
from app.services.analytics_service import AnalyticsService
from app.services.embedding_service import EmbeddingService
from app.services.event_service import EventService
from app.services.execution_service import ExecutionService
from app.services.generation_service import GenerationService
from app.services.llm_provider import LLMProvider, MockLLMProvider, OpenAIProvider
from app.services.retrieval_service import RetrievalService
from app.services.skill_evaluator import BasicSkillEvaluator, SkillEvaluator
from app.services.skill_metrics_service import SkillMetricsService
from app.services.skill_service import SkillService
from app.services.skill_validator import PythonASTValidator, SkillValidator
from app.services.task_service import TaskService
from app.skills.executor import LocalSkillExecutor, SkillExecutor


def get_llm_provider() -> LLMProvider:
    api_key = settings.OPENAI_API_KEY
    if api_key and not api_key.startswith("mock") and api_key != "your-openai-api-key-here":
        try:
            return OpenAIProvider()
        except Exception:
            return MockLLMProvider()
    return MockLLMProvider()


def get_skill_executor() -> SkillExecutor:
    return LocalSkillExecutor()


def get_skill_validator() -> SkillValidator:
    return PythonASTValidator()


def get_skill_evaluator() -> SkillEvaluator:
    return BasicSkillEvaluator()


def get_task_repository(session: AsyncSession = Depends(get_db)) -> TaskRepository:
    return TaskRepository(session)


def get_skill_repository(session: AsyncSession = Depends(get_db)) -> SkillRepository:
    return SkillRepository(session)


def get_execution_repository(session: AsyncSession = Depends(get_db)) -> ExecutionRepository:
    return ExecutionRepository(session)


def get_analytics_service(session: AsyncSession = Depends(get_db)) -> AnalyticsService:
    return AnalyticsService(session)


def get_event_service(session: AsyncSession = Depends(get_db)) -> EventService:
    return EventService(session)


def get_embedding_service(
    llm_provider: LLMProvider = Depends(get_llm_provider),
) -> EmbeddingService:
    return EmbeddingService(llm_provider)


def get_metrics_service(
    skill_repo: SkillRepository = Depends(get_skill_repository),
) -> SkillMetricsService:
    return SkillMetricsService(skill_repo)


def get_retrieval_service(
    skill_repo: SkillRepository = Depends(get_skill_repository),
    embedding_service: EmbeddingService = Depends(get_embedding_service),
) -> RetrievalService:
    return RetrievalService(skill_repo, embedding_service)


def get_generation_service(
    llm_provider: LLMProvider = Depends(get_llm_provider),
) -> GenerationService:
    return GenerationService(llm_provider)


def get_execution_service(
    execution_repo: ExecutionRepository = Depends(get_execution_repository),
    metrics_service: SkillMetricsService = Depends(get_metrics_service),
    executor: SkillExecutor = Depends(get_skill_executor),
) -> ExecutionService:
    return ExecutionService(execution_repo, metrics_service, executor)


def get_skill_service(
    skill_repo: SkillRepository = Depends(get_skill_repository),
    embedding_service: EmbeddingService = Depends(get_embedding_service),
) -> SkillService:
    return SkillService(skill_repo, embedding_service)


def get_task_service(
    task_repo: TaskRepository = Depends(get_task_repository),
    execution_repo: ExecutionRepository = Depends(get_execution_repository),
    generation_service: GenerationService = Depends(get_generation_service),
    retrieval_service: RetrievalService = Depends(get_retrieval_service),
    skill_service: SkillService = Depends(get_skill_service),
    execution_service: ExecutionService = Depends(get_execution_service),
) -> TaskService:
    return TaskService(
        task_repo=task_repo,
        execution_repo=execution_repo,
        generation_service=generation_service,
        retrieval_service=retrieval_service,
        skill_service=skill_service,
        execution_service=execution_service,
    )
