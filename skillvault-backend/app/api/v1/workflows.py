from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, get_skill_repository
from app.db.models.workflow import SkillWorkflow, SkillWorkflowStep
from app.db.repositories.skill_repository import SkillRepository
from app.skills.graph_validator import GraphValidator, WorkflowValidationResult
from app.utils.ids import generate_id

router = APIRouter(prefix="/workflows", tags=["Workflows"])


class WorkflowStepCreate(BaseModel):
    step_number: int
    skill_id: str
    input_mapping: dict = Field(default_factory=dict)
    output_mapping: dict = Field(default_factory=dict)
    condition: dict | None = None


class WorkflowCreate(BaseModel):
    name: str
    description: str
    steps: list[WorkflowStepCreate]


@router.post("", status_code=status.HTTP_201_CREATED, summary="Create a new Skill Workflow graph")
async def create_workflow(
    payload: WorkflowCreate,
    session: AsyncSession = Depends(get_db),
    skill_repo: SkillRepository = Depends(get_skill_repository),
):
    skills, _ = await skill_repo.list_skills(limit=500)
    existing_skill_ids = {s.id for s in skills}

    validator = GraphValidator()
    steps_dict = [s.model_dump() for s in payload.steps]
    validation: WorkflowValidationResult = validator.validate_graph(
        steps=steps_dict,
        existing_skill_ids=existing_skill_ids,
    )

    if not validation.valid:
        raise HTTPException(
            status_code=400,
            detail=f"Workflow graph validation failed: {'; '.join(validation.errors)}",
        )

    workflow_id = generate_id("workflow")
    slug = payload.name.lower().replace(" ", "-")

    workflow = SkillWorkflow(
        id=workflow_id,
        name=payload.name,
        slug=slug,
        description=payload.description,
        status="ACTIVE",
        steps_definition=steps_dict,
    )
    session.add(workflow)
    await session.flush()

    for s in payload.steps:
        step = SkillWorkflowStep(
            workflow_id=workflow_id,
            step_number=s.step_number,
            skill_id=s.skill_id,
            input_mapping=s.input_mapping,
            output_mapping=s.output_mapping,
            condition=s.condition,
        )
        session.add(step)

    await session.flush()

    return {
        "id": workflow.id,
        "name": workflow.name,
        "slug": workflow.slug,
        "description": workflow.description,
        "steps_count": len(payload.steps),
        "status": workflow.status,
    }


@router.get("", summary="List skill workflows")
async def list_workflows(session: AsyncSession = Depends(get_db)):
    result = await session.execute(select(SkillWorkflow).order_by(SkillWorkflow.created_at.desc()))
    workflows = result.scalars().all()
    return [
        {
            "id": w.id,
            "name": w.name,
            "slug": w.slug,
            "description": w.description,
            "steps_count": len(w.steps_definition),
            "status": w.status,
            "created_at": w.created_at.isoformat(),
        }
        for w in workflows
    ]


@router.get("/{workflow_id}", summary="Get workflow specification")
async def get_workflow(workflow_id: str, session: AsyncSession = Depends(get_db)):
    result = await session.execute(select(SkillWorkflow).where(SkillWorkflow.id == workflow_id))
    workflow = result.scalar_one_or_none()
    if not workflow:
        raise HTTPException(status_code=404, detail=f"Workflow '{workflow_id}' not found.")
    return {
        "id": workflow.id,
        "name": workflow.name,
        "slug": workflow.slug,
        "description": workflow.description,
        "steps": workflow.steps_definition,
        "status": workflow.status,
        "created_at": workflow.created_at.isoformat(),
    }
