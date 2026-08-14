import asyncio
import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.api.deps import get_db, get_llm_provider
from app.db.base import Base
from app.main import app
from app.services.embedding_service import EmbeddingService
from app.services.llm_provider import MockLLMProvider
from app.services.skill_service import SkillService
from app.db.repositories.skill_repository import SkillRepository

# Use SQLite in-memory database for fast pytest runs
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestSessionLocal = async_sessionmaker(
    test_engine, class_=AsyncSession, expire_on_commit=False
)


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def db_session() -> AsyncSession:
    # Handle Vector type for SQLite in memory if needed
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with TestSessionLocal() as session:
        # Seed built-in skills for test
        mock_llm = MockLLMProvider()
        skill_repo = SkillRepository(session)
        emb_service = EmbeddingService(mock_llm)
        skill_service = SkillService(skill_repo, emb_service)
        await skill_service.seed_builtin_skills()

        yield session

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def async_client(db_session: AsyncSession):
    async def _override_get_db():
        yield db_session

    def _override_get_llm():
        return MockLLMProvider()

    app.dependency_overrides[get_db] = _override_get_db
    app.dependency_overrides[get_llm_provider] = _override_get_llm

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client

    app.dependency_overrides.clear()
