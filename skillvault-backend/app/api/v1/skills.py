import math
from fastapi import APIRouter, Depends, Query, status, HTTPException
from pydantic import BaseModel, Field

from app.api.deps import (
    get_execution_repository,
    get_execution_service,
    get_generation_service,
    get_retrieval_service,
    get_skill_service,
    get_analytics_service,
)
from app.db.repositories.execution_repository import ExecutionRepository
from app.schemas.common import PaginatedResponse
from app.schemas.execution import ExecutionResponse
from app.schemas.skill import (
    SkillCreate,
    SkillResponse,
    SkillSearchRequest,
    SkillSearchResult,
    SkillUpdate,
    SkillVersionResponse,
)
from app.services.analytics_service import AnalyticsService
from app.services.execution_service import ExecutionService
from app.services.generation_service import GenerationService
from app.services.retrieval_service import RetrievalService
from app.services.skill_service import SkillService

router = APIRouter(prefix="/skills", tags=["Skills"])


class SkillGenerateRequest(BaseModel):
    task: str


class SkillGenerateResponse(BaseModel):
    status: str
    skill: dict
    validation: dict


class DirectExecuteRequest(BaseModel):
    inputs: dict = Field(default_factory=dict)


class RollbackRequest(BaseModel):
    target_version_id: str


def _to_skill_response(skill) -> SkillResponse:
    rate = skill.success_count / skill.usage_count if skill.usage_count > 0 else 0.0
    return SkillResponse(
        id=skill.id,
        name=skill.name,
        slug=skill.slug,
        description=skill.description,
        capability=skill.capability,
        category=skill.category,
        status=skill.status,
        risk_level=skill.risk_level,
        input_schema=skill.input_schema,
        output_schema=skill.output_schema,
        dependencies=skill.dependencies,
        active_version_id=skill.active_version_id,
        usage_count=skill.usage_count,
        success_count=skill.success_count,
        failure_count=skill.failure_count,
        success_rate=round(rate, 4),
        created_at=skill.created_at,
        updated_at=skill.updated_at,
    )


@router.get("", response_model=PaginatedResponse[SkillResponse], summary="List skills with filtering")
async def list_skills(
    status: str | None = Query(None, description="Filter by status (DRAFT, ACTIVE, DEPRECATED, ARCHIVED)"),
    category: str | None = Query(None, description="Filter by category"),
    name: str | None = Query(None, description="Filter by name substring"),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    skill_service: SkillService = Depends(get_skill_service),
):
    skills, total = await skill_service.list_skills(
        status=status, category=category, name=name, page=page, limit=limit
    )
    items = [_to_skill_response(s) for s in skills]
    pages = math.ceil(total / limit) if total > 0 else 0
    return PaginatedResponse(items=items, total=total, page=page, limit=limit, pages=pages)


@router.post("/search", response_model=dict[str, list[SkillSearchResult]], summary="Semantic skill retrieval search")
async def search_skills(
    payload: SkillSearchRequest,
    retrieval_service: RetrievalService = Depends(get_retrieval_service),
):
    results = await retrieval_service.search_similar_skills(
        query=payload.query, top_k=payload.top_k
    )
    return {"results": results}


@router.post("/generate", response_model=SkillGenerateResponse, status_code=status.HTTP_201_CREATED, summary="Dynamically generate, AST-validate, and persist a DRAFT skill")
async def generate_skill_endpoint(
    payload: SkillGenerateRequest,
    generation_service: GenerationService = Depends(get_generation_service),
    skill_service: SkillService = Depends(get_skill_service),
):
    task_analysis = await generation_service.analyze_task(payload.task)
    generated_skill = await generation_service.generate_skill(payload.task, task_analysis)
    val_res = await generation_service.validate_skill(generated_skill)

    if not val_res.valid:
        return SkillGenerateResponse(
            status="VALIDATION_FAILED",
            skill={"name": generated_skill.name, "slug": generated_skill.slug},
            validation=val_res.model_dump(),
        )

    skill_create = SkillCreate(
        name=generated_skill.name,
        description=generated_skill.description,
        capability=generated_skill.capability,
        category=generated_skill.category or "general",
        status="DRAFT",
        source_type="GENERATED",
        created_by="AGENT",
        risk_level="UNTRUSTED",
        input_schema=generated_skill.input_schema,
        output_schema=generated_skill.output_schema,
        dependencies=generated_skill.dependencies,
        code=generated_skill.code,
        language=generated_skill.language or "python",
        entrypoint=generated_skill.entrypoint or "run",
    )

    skill = await skill_service.create_skill(skill_create)

    return SkillGenerateResponse(
        status="DRAFT_CREATED",
        skill={
            "id": skill.id,
            "name": skill.name,
            "slug": skill.slug,
            "source_type": skill.source_type,
            "status": skill.status,
            "version": "1.0.0",
        },
        validation=val_res.model_dump(),
    )


@router.post("", response_model=SkillResponse, status_code=status.HTTP_201_CREATED, summary="Create a new skill")
async def create_skill(
    payload: SkillCreate,
    skill_service: SkillService = Depends(get_skill_service),
):
    skill = await skill_service.create_skill(payload)
    return _to_skill_response(skill)


@router.get("/{skill_id}", response_model=SkillResponse, summary="Get skill details")
async def get_skill(
    skill_id: str,
    skill_service: SkillService = Depends(get_skill_service),
):
    skill = await skill_service.get_skill(skill_id)
    return _to_skill_response(skill)


@router.post("/{skill_id}/execute", summary="Execute skill directly as a service")
async def execute_skill_direct(
    skill_id: str,
    payload: DirectExecuteRequest,
    skill_service: SkillService = Depends(get_skill_service),
    execution_service: ExecutionService = Depends(get_execution_service),
):
    skill = await skill_service.get_skill(skill_id)
    exec_res = await execution_service.execute_skill(
        task_id=f"direct_{skill_id}",
        skill_version=skill.active_version,
        input_data=payload.inputs,
        strategy="REUSE",
    )
    return {
        "execution_id": f"exec_direct_{skill_id}",
        "skill_id": skill_id,
        "status": exec_res.status,
        "output": exec_res.output_data,
        "error": exec_res.error,
        "latency_ms": exec_res.latency_ms,
    }


@router.get("/{skill_id}/stats", summary="Get multi-signal quality score and statistics")
async def get_skill_stats(
    skill_id: str,
    skill_service: SkillService = Depends(get_skill_service),
    analytics_service: AnalyticsService = Depends(get_analytics_service),
):
    skill = await skill_service.get_skill(skill_id)
    quality_score, components = analytics_service.calculate_quality_score(skill)
    return {
        "skill_id": skill.id,
        "name": skill.name,
        "usage_count": skill.usage_count,
        "success_count": skill.success_count,
        "failure_count": skill.failure_count,
        "success_rate": skill.success_count / skill.usage_count if skill.usage_count > 0 else 1.0,
        "quality_score": quality_score,
        "quality_components": components,
    }


@router.post("/{skill_id}/rollback", response_model=SkillResponse, summary="Rollback skill active version")
async def rollback_skill_version(
    skill_id: str,
    payload: RollbackRequest,
    skill_service: SkillService = Depends(get_skill_service),
):
    updated = await skill_service.update_skill(skill_id, SkillUpdate(status="ACTIVE"))
    updated.active_version_id = payload.target_version_id
    await skill_service.skill_repo.session.flush()
    return _to_skill_response(updated)


@router.patch("/{skill_id}", response_model=SkillResponse, summary="Update skill attributes")
async def update_skill(
    skill_id: str,
    payload: SkillUpdate,
    skill_service: SkillService = Depends(get_skill_service),
):
    updated = await skill_service.update_skill(skill_id, payload)
    return _to_skill_response(updated)


@router.delete("/{skill_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete skill")
async def delete_skill(
    skill_id: str,
    skill_service: SkillService = Depends(get_skill_service),
):
    await skill_service.delete_skill(skill_id)
    return None


@router.get("/{skill_id}/versions", response_model=list[SkillVersionResponse], summary="Get skill versions")
async def get_skill_versions(
    skill_id: str,
    skill_service: SkillService = Depends(get_skill_service),
):
    return await skill_service.get_versions(skill_id)


@router.get("/{skill_id}/executions", response_model=list[ExecutionResponse], summary="Get skill executions")
async def get_skill_executions(
    skill_id: str,
    execution_repo: ExecutionRepository = Depends(get_execution_repository),
):
    return await execution_repo.get_by_skill_id(skill_id)
