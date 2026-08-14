from fastapi import APIRouter, Depends, status

from app.api.deps import get_event_service, get_task_service
from app.schemas.execution import ExecutionResponse
from app.schemas.task import TaskCreate, TaskExecutionResponse, TaskResponse
from app.services.event_service import EventService
from app.services.task_service import TaskService

router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.post(
    "",
    response_model=TaskExecutionResponse,
    status_code=status.HTTP_200_OK,
    summary="Create and execute task",
    description="Submit a task input. The agent will analyze, retrieve, reuse or generate a skill, and execute it.",
)
async def create_and_execute_task(
    payload: TaskCreate,
    task_service: TaskService = Depends(get_task_service),
):
    return await task_service.create_and_execute_task(payload.input)


@router.get(
    "/{task_id}",
    response_model=TaskResponse,
    summary="Get task details",
)
async def get_task(
    task_id: str,
    task_service: TaskService = Depends(get_task_service),
):
    return await task_service.get_task(task_id)


@router.get(
    "/{task_id}/executions",
    response_model=list[ExecutionResponse],
    summary="Get executions for a task",
)
async def get_task_executions(
    task_id: str,
    task_service: TaskService = Depends(get_task_service),
):
    return await task_service.get_task_executions(task_id)


@router.get(
    "/{task_id}/events",
    summary="Get real-time agent observability event stream for a task",
)
async def get_task_events(
    task_id: str,
    event_service: EventService = Depends(get_event_service),
):
    events = await event_service.get_task_events(task_id)
    return [
        {
            "id": e.id,
            "task_id": e.task_id,
            "event_type": e.event_type,
            "payload": e.payload,
            "created_at": e.created_at.isoformat(),
        }
        for e in events
    ]
