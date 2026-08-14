import math
from fastapi import APIRouter, Depends, Query

from app.api.deps import get_execution_repository
from app.core.exceptions import ExecutionNotFoundError
from app.db.repositories.execution_repository import ExecutionRepository
from app.schemas.common import PaginatedResponse
from app.schemas.execution import ExecutionResponse

router = APIRouter(prefix="/executions", tags=["Executions"])


@router.get("", response_model=PaginatedResponse[ExecutionResponse], summary="List execution logs")
async def list_executions(
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    execution_repo: ExecutionRepository = Depends(get_execution_repository),
):
    items, total = await execution_repo.list_all(page=page, limit=limit)
    pages = math.ceil(total / limit) if total > 0 else 0
    return PaginatedResponse(
        items=[ExecutionResponse.model_validate(e) for e in items],
        total=total,
        page=page,
        limit=limit,
        pages=pages,
    )


@router.get("/{execution_id}", response_model=ExecutionResponse, summary="Get execution record details")
async def get_execution(
    execution_id: str,
    execution_repo: ExecutionRepository = Depends(get_execution_repository),
):
    execution = await execution_repo.get_by_id(execution_id)
    if not execution:
        raise ExecutionNotFoundError(execution_id)
    return execution
