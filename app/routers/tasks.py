from typing import List

from fastapi import APIRouter, HTTPException, Response, Request

from app.websocket.manager import WSManager
from app.enums import WSEventTypes, Priority
from app.websocket.manager import dispatch_ws_event
from app.models import Project, ProjectMember, Task
from app.dependencies import current_user_dep, db_dep, project_manager_dep
from app.schemas.tasks import (
    TaskCreateRequest,
    TaskDetailResponse,
    TaskListResponse,
    TaskMoveRequest,
    TaskUpdateRequest,
)
from app.services import generated_task_key

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.get("/all/", response_model=List[TaskListResponse])
async def get_tasks(db: db_dep):
    tasks = db.query(Task).all()
    return tasks


@router.post("/create/", response_model=TaskDetailResponse)
async def task_create(
    db: db_dep, 
    user: project_manager_dep, 
    task_data: TaskCreateRequest,
    request: Request
):
    project = db.query(Project).filter(Project.key == task_data.project_key).first()

    if not project:
        raise HTTPException(404, "Project Not Found.")

    manager = (
        db.query(ProjectMember)
        .filter(
            ProjectMember.project_id == project.id, ProjectMember.user_id == user.id
        )
        .first()
    )

    # taskni yaratayotgan manager project ga qo'shilganini tekshirish
    if not manager:
        raise HTTPException(403, "Task yaratayptgan manager project ga biriktirlmagan.")

    # create new task
    new_task = Task(
        key=generated_task_key(db, project),
        summary=task_data.summary,
        description=task_data.description,
        priority=task_data.priority,
        due_date=task_data.due_date,
        project_id=project.id,
        status=task_data.status,
        reporter_id=user.id,
        assignee_id=task_data.assignee_id,
    )

    db.add(new_task)
    db.commit()
    db.refresh(new_task)

    ws_manager: WSManager = request.app.state.ws_manager
    event_type = (
        WSEventTypes.task_created_high
        if task_data.priority == Priority.HIGH
        else WSEventTypes.task_created
    )

    await dispatch_ws_event(
        ws_manager=ws_manager,
        event_type=event_type,
        project_id=new_task.project_id,
        payload={
            "type": event_type,
            "task_id": new_task.id,
            "project_id": new_task.project_id
        }
    )

    return new_task


@router.get("/{task_key:str}/")
async def get_task_by_key(db: db_dep, current_user: current_user_dep, task_key: str):
    task = db.query(Task).filter(Task.key == task_key).first()

    if not task:
        raise HTTPException(404, "Task Not Found.")

    return task


@router.put("/{task_key:str}/edit/")
async def update_task(
    db: db_dep, user: project_manager_dep, task_key: str, data: TaskUpdateRequest
):
    task = db.query(Task).filter(Task.key == task_key).first()

    if not task:
        raise HTTPException(404, "Task Not Found.")

    if task.reporter_id != user.id:
        raise HTTPException(400, "Siz task ni yaratmagansiz. Uni o'zgartira olmaysiz.")

    edit_task = data.model_dump(exclude_unset=True)

    for key, value in edit_task.items():
        setattr(task, key, value)

    db.commit()
    db.refresh(task)

    return task


@router.delete("/{task_key:str}/delete/")
async def delete_task(db: db_dep, user: project_manager_dep, task_key: str):
    task = db.query(Task).filter(Task.key == task_key).first()

    if not task:
        raise HTTPException(404, "Task Not Found.")

    if task.reporter_id != user.id:
        raise HTTPException(400, "Bu taskni siz yaratmagansiz. Uni o'chiraolmaysiz.")

    db.delete(task)
    db.commit()

    return Response(status_code=204)


@router.patch("/{task_key:str}/move/", response_model=TaskDetailResponse)
async def move_task(
    db: db_dep, user: project_manager_dep, task_key: str, data: TaskMoveRequest
): ...  # ToDo


@router.get("/{task_key:str}/comments/")
async def get_task_comments(db: db_dep, user: current_user_dep, task_key: str):
    task = db.query(Task).filter(Task.key == task_key).first()

    if not task:
        raise HTTPException(404, "Task Not Found.")

    comments = task.comments

    return comments

