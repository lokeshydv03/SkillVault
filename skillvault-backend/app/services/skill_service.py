from typing import Any
from app.core.exceptions import SkillNotFoundError
from app.db.models.skill import Skill
from app.db.models.skill_version import SkillVersion
from app.db.repositories.skill_repository import SkillRepository
from app.schemas.skill import SkillCreate, SkillUpdate
from app.services.embedding_service import EmbeddingService
from app.skills.builtin import BUILTIN_SKILL_DEFINITIONS


class SkillService:
    def __init__(self, skill_repo: SkillRepository, embedding_service: EmbeddingService):
        self.skill_repo = skill_repo
        self.embedding_service = embedding_service

    async def create_skill(self, data: SkillCreate) -> Skill:
        embedding = await self.embedding_service.generate_skill_embedding(
            name=data.name,
            description=data.description,
            capability=data.capability,
            input_schema=data.input_schema,
            output_schema=data.output_schema,
        )

        skill = await self.skill_repo.create(
            name=data.name,
            description=data.description,
            capability=data.capability,
            category=data.category,
            risk_level=data.risk_level,
            source_type=data.source_type,
            created_by=data.created_by,
            input_schema=data.input_schema,
            output_schema=data.output_schema,
            dependencies=data.dependencies,
            embedding=embedding,
            status="ACTIVE" if data.risk_level in ("TRUSTED", "LOW") else "DRAFT",
        )

        await self.skill_repo.create_version(
            skill_id=skill.id,
            version="1.0.0",
            code=data.code,
            language=data.language,
            entrypoint=data.entrypoint,
            description=data.description,
            input_schema=data.input_schema,
            output_schema=data.output_schema,
            dependencies=data.dependencies,
        )

        result = await self.skill_repo.get_by_id(skill.id)
        if not result:
            raise SkillNotFoundError(skill.id)
        return result

    async def get_skill(self, skill_id: str) -> Skill:
        skill = await self.skill_repo.get_by_id(skill_id)
        if not skill:
            raise SkillNotFoundError(skill_id)
        return skill

    async def list_skills(
        self,
        status: str | None = None,
        category: str | None = None,
        name: str | None = None,
        page: int = 1,
        limit: int = 10,
    ) -> tuple[list[Skill], int]:
        return await self.skill_repo.list_skills(
            status=status, category=category, name=name, page=page, limit=limit
        )

    async def update_skill(self, skill_id: str, data: SkillUpdate) -> Skill:
        existing = await self.get_skill(skill_id)
        update_dict = data.model_dump(exclude_unset=True)

        if any(k in update_dict for k in ("name", "description", "capability")):
            new_embedding = await self.embedding_service.generate_skill_embedding(
                name=update_dict.get("name", existing.name),
                description=update_dict.get("description", existing.description),
                capability=update_dict.get("capability", existing.capability),
                input_schema=update_dict.get("input_schema", existing.input_schema),
                output_schema=update_dict.get("output_schema", existing.output_schema),
            )
            update_dict["embedding"] = new_embedding

        updated = await self.skill_repo.update_skill(skill_id, **update_dict)
        if not updated:
            raise SkillNotFoundError(skill_id)
        return updated

    async def delete_skill(self, skill_id: str) -> bool:
        await self.get_skill(skill_id)
        return await self.skill_repo.delete_skill(skill_id)

    async def get_versions(self, skill_id: str) -> list[SkillVersion]:
        await self.get_skill(skill_id)
        return await self.skill_repo.get_versions(skill_id)

    async def seed_builtin_skills(self) -> None:
        """Seed all 6 trusted built-in skills idempotently and update embeddings."""
        for defn in BUILTIN_SKILL_DEFINITIONS:
            existing = await self.skill_repo.get_by_slug(defn["slug"])
            embedding = await self.embedding_service.generate_skill_embedding(
                name=defn["name"],
                description=defn["description"],
                capability=defn["capability"],
                input_schema=defn["input_schema"],
                output_schema=defn["output_schema"],
            )
            if not existing:
                skill = await self.skill_repo.create(
                    name=defn["name"],
                    slug=defn["slug"],
                    description=defn["description"],
                    capability=defn["capability"],
                    category=defn["category"],
                    risk_level=defn["risk_level"],
                    source_type="BUILTIN",
                    created_by="SYSTEM",
                    status="ACTIVE",
                    input_schema=defn["input_schema"],
                    output_schema=defn["output_schema"],
                    embedding=embedding,
                )
                await self.skill_repo.create_version(
                    skill_id=skill.id,
                    version=defn.get("version", "1.0.0"),
                    code=defn["code"],
                    description=defn["description"],
                    input_schema=defn["input_schema"],
                    output_schema=defn["output_schema"],
                )
            else:
                await self.skill_repo.update_skill(
                    existing.id,
                    name=defn["name"],
                    description=defn["description"],
                    capability=defn["capability"],
                    status="ACTIVE",
                    embedding=embedding,
                )
        await self.skill_repo.session.commit()
