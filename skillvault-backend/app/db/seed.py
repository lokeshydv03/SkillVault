import asyncio
from app.core.logging import logger
from app.db.database import AsyncSessionLocal, engine
from app.db.base import Base
from app.db.repositories.skill_repository import SkillRepository
from app.services.embedding_service import EmbeddingService
from app.services.llm_provider import MockLLMProvider, OpenAIProvider
from app.services.skill_service import SkillService
from app.skills.builtin import BUILTIN_SKILL_DEFINITIONS
from app.core.config import settings


async def seed_skills():
    """
    Idempotent Seeding Script for SkillVault Built-in Skill Registry.
    Reads metadata, generates embeddings via EmbeddingService, creates Skill + SkillVersion,
    stores in pgvector, and sets status to ACTIVE. Safe to execute multiple times.
    """
    logger.info("Initializing database tables for seeding...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as session:
        skill_repo = SkillRepository(session)

        # Use OpenAI provider if configured, else Mock provider
        if settings.OPENAI_API_KEY and settings.OPENAI_API_KEY != "mock-openai-key":
            try:
                llm = OpenAIProvider()
            except Exception:
                llm = MockLLMProvider()
        else:
            llm = MockLLMProvider()

        embedding_service = EmbeddingService(llm)

        seeded_count = 0
        skipped_count = 0

        for defn in BUILTIN_SKILL_DEFINITIONS:
            slug = defn["slug"]
            existing = await skill_repo.get_by_slug(slug)

            if existing:
                logger.info(f"Skill '{defn['name']}' (slug: {slug}) already exists in vault. Skipping.")
                skipped_count += 1
                continue

            # Generate real embedding using EmbeddingService
            embedding = await embedding_service.generate_skill_embedding(
                name=defn["name"],
                description=defn["description"],
                capability=defn["capability"],
                input_schema=defn["input_schema"],
                output_schema=defn["output_schema"],
            )

            # Create Skill entity
            skill = await skill_repo.create(
                name=defn["name"],
                description=defn["description"],
                capability=defn["capability"],
                category=defn["category"],
                risk_level=defn["risk_level"],
                status="ACTIVE",
                input_schema=defn["input_schema"],
                output_schema=defn["output_schema"],
                embedding=embedding,
            )

            # Create SkillVersion entity v1.0.0
            await skill_repo.create_version(
                skill_id=skill.id,
                version=defn.get("version", "1.0.0"),
                code=defn["code"],
                description=defn["description"],
                input_schema=defn["input_schema"],
                output_schema=defn["output_schema"],
            )

            logger.info(f"Successfully seeded Skill: {defn['name']} [{skill.id}]")
            seeded_count += 1

        await session.commit()
        logger.info(f"Seeding completed! Seeded: {seeded_count}, Skipped: {skipped_count}.")


if __name__ == "__main__":
    asyncio.run(seed_skills())
