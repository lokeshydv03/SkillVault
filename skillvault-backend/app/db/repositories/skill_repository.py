import json
import math
from typing import Any
from sqlalchemy import func, select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.models.skill import Skill
from app.db.models.skill_version import SkillVersion
from app.utils.ids import generate_id, generate_slug


class SkillRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(
        self,
        name: str,
        description: str,
        capability: str,
        category: str = "general",
        risk_level: str = "UNTRUSTED",
        source_type: str = "BUILTIN",
        created_by: str = "SYSTEM",
        slug: str | None = None,
        input_schema: dict[str, Any] | None = None,
        output_schema: dict[str, Any] | None = None,
        dependencies: list[str] | None = None,
        embedding: list[float] | None = None,
        status: str = "DRAFT",
    ) -> Skill:
        if not slug:
            slug = generate_slug(name)
            existing = await self.get_by_slug(slug)
            if existing:
                slug = f"{slug}_{generate_id('')[:4]}"

        skill = Skill(
            name=name,
            slug=slug,
            description=description,
            capability=capability,
            category=category,
            status=status,
            source_type=source_type,
            created_by=created_by,
            risk_level=risk_level,
            input_schema=input_schema or {},
            output_schema=output_schema or {},
            dependencies=dependencies or [],
            embedding=embedding,
        )
        self.session.add(skill)
        await self.session.flush()
        return skill

    async def create_version(
        self,
        skill_id: str,
        code: str,
        version: str = "1.0.0",
        language: str = "python",
        entrypoint: str = "run",
        description: str | None = None,
        input_schema: dict[str, Any] | None = None,
        output_schema: dict[str, Any] | None = None,
        dependencies: list[str] | None = None,
        metadata_info: dict[str, Any] | None = None,
    ) -> SkillVersion:
        ver = SkillVersion(
            skill_id=skill_id,
            version=version,
            code=code,
            language=language,
            entrypoint=entrypoint,
            description=description,
            input_schema=input_schema or {},
            output_schema=output_schema or {},
            dependencies=dependencies or [],
            metadata_info=metadata_info or {},
        )
        self.session.add(ver)
        await self.session.flush()

        await self.session.execute(
            update(Skill).where(Skill.id == skill_id).values(active_version_id=ver.id)
        )
        return ver

    async def get_by_id(self, skill_id: str) -> Skill | None:
        result = await self.session.execute(
            select(Skill)
            .options(selectinload(Skill.active_version), selectinload(Skill.versions))
            .where(Skill.id == skill_id)
        )
        return result.scalar_one_or_none()

    async def get_by_slug(self, slug: str) -> Skill | None:
        result = await self.session.execute(
            select(Skill)
            .options(selectinload(Skill.active_version))
            .where(Skill.slug == slug)
        )
        return result.scalar_one_or_none()

    async def list_skills(
        self,
        status: str | None = None,
        category: str | None = None,
        name: str | None = None,
        page: int = 1,
        limit: int = 10,
    ) -> tuple[list[Skill], int]:
        query = select(Skill).options(selectinload(Skill.active_version))

        if status:
            query = query.where(Skill.status == status)
        if category:
            query = query.where(Skill.category == category)
        if name:
            query = query.where(Skill.name.ilike(f"%{name}%"))

        count_query = select(func.count()).select_from(query.subquery())
        total_res = await self.session.execute(count_query)
        total = total_res.scalar_one()

        offset = (page - 1) * limit
        query = query.offset(offset).limit(limit).order_by(Skill.created_at.desc())

        result = await self.session.execute(query)
        skills = list(result.scalars().all())
        return skills, total

    async def update_skill(self, skill_id: str, **kwargs) -> Skill | None:
        update_data = {k: v for k, v in kwargs.items() if v is not None}
        if not update_data:
            return await self.get_by_id(skill_id)

        await self.session.execute(
            update(Skill).where(Skill.id == skill_id).values(**update_data)
        )
        return await self.get_by_id(skill_id)

    async def delete_skill(self, skill_id: str) -> bool:
        result = await self.session.execute(delete(Skill).where(Skill.id == skill_id))
        return result.rowcount > 0

    async def get_versions(self, skill_id: str) -> list[SkillVersion]:
        result = await self.session.execute(
            select(SkillVersion)
            .options(selectinload(SkillVersion.skill))
            .where(SkillVersion.skill_id == skill_id)
            .order_by(SkillVersion.created_at.desc())
        )
        return list(result.scalars().all())

    async def search_similar(
        self,
        query_embedding: list[float],
        top_k: int = 5,
        status_filter: str = "ACTIVE",
    ) -> list[tuple[Skill, float]]:
        bind = self.session.get_bind()
        dialect_name = bind.dialect.name if bind else "postgresql"

        if dialect_name == "postgresql":
            distance_col = Skill.embedding.cosine_distance(query_embedding).label("distance")
            query = (
                select(Skill, distance_col)
                .options(selectinload(Skill.active_version))
                .where(Skill.status == status_filter, Skill.embedding.is_not(None))
                .order_by(distance_col.asc())
                .limit(top_k)
            )
            res = await self.session.execute(query)
            rows = res.all()
            return [(skill, max(0.0, min(1.0, 1.0 - float(dist)))) for skill, dist in rows]

        query = select(Skill).options(selectinload(Skill.active_version)).where(Skill.status == status_filter)
        res = await self.session.execute(query)
        all_skills = res.scalars().all()

        def _cosine_sim(v1: Any, v2: Any) -> float:
            if isinstance(v1, str):
                try: v1 = json.loads(v1)
                except Exception: pass
            if isinstance(v2, str):
                try: v2 = json.loads(v2)
                except Exception: pass

            if not v1 or not v2:
                return 0.0

            try:
                flt1 = [float(x) for x in v1]
                flt2 = [float(x) for x in v2]
            except Exception:
                return 0.0

            if len(flt1) != len(flt2):
                return 0.0

            dot = sum(a * b for a, b in zip(flt1, flt2))
            norm1 = math.sqrt(sum(a * a for a in flt1))
            norm2 = math.sqrt(sum(b * b for b in flt2))
            if norm1 == 0 or norm2 == 0:
                return 0.0
            return max(0.0, min(1.0, dot / (norm1 * norm2)))

        scored = []
        for skill in all_skills:
            sim = _cosine_sim(query_embedding, skill.embedding)
            scored.append((skill, sim))

        # Prioritize BUILTIN skills on equal similarity scores
        scored.sort(key=lambda x: (x[1], 1 if x[0].source_type == "BUILTIN" else 0), reverse=True)
        return scored[:top_k]
