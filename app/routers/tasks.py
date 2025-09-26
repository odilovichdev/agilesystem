from typing import List

from fastapi import APIRouter, HTTPException, Response, Request

from app.enums import Role, Status
from app.utils import get_object_or_404
from app.websocket.manager import WSManager
from app.services import generated_task_key
from app.enums import WSEventTypes, Priority
from app.websocket.manager import dispatch_ws_event
from app.services.tasks import TaskTransitionValidator
from app.dependencies import current_user_dep, db_dep, project_manager_dep
from app.models import (
    Project, 
    ProjectMember, 
    Task, 
    User, 
    Notification, 
    AuditLog
)
from app.schemas.tasks import (
    TaskCreateRequest,
    TaskDetailResponse,
    TaskListResponse,
    TaskMoveRequest,
    TaskUpdateRequest,
    TaskAddDeveloperRequest
)

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
    
    project = get_object_or_404(db, Project, key=task_data.project_key)

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
        status=Status.BACKLOG,
        reporter_id=user.id
    )

    db.add(new_task)
    db.flush()

    # Notification yozish
    notification = Notification(
        message=f"Yangi task yaratildi: {new_task.summary}",
        recipient_id=project.owner_id,
        sender_id=user.id,
        task_id=new_task.id,
        project_id=project.id
    )

    db.add(notification)

    # AuditLog yozish
    audit_log = AuditLog(
        action=f"Task {new_task.summary} created",
        user_id=user.id,
        task_id=new_task.id
    )
    db.add(audit_log)

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
            "project_id": new_task.project_id,
            "summary": new_task.summary,
            "priority": new_task.priority,
            "status": new_task.status,
        }
    )

    return new_task


@router.post("/{task_key:str}/add/developer")
async def task_add_developer(
    db: db_dep, 
    task_key: str, 
    current_user: project_manager_dep,
    user_data: TaskAddDeveloperRequest,
    request: Request
):
    
    task = get_object_or_404(db, Task, key=task_key)
    user = get_object_or_404(db, User, id=user_data.user_id)
    
    # Permission check (faqat owner/manager yoki reporter qo‘shishi mumkin)
    if (current_user.role not in [Role.manager, Role.admin, Role.owner] 
        and current_user.id != task.reporter_id):
        raise HTTPException(403, "Sizda ruxsat yo'q")
    
    project_id = task.project_id

    # Developer shu project ichidami?
    is_member = (
        db.query(ProjectMember).
        filter(ProjectMember.project_id==project_id,
               ProjectMember.user_id==user.id
               )
               .first()
    )

    if not is_member:
        raise HTTPException(400, "Developer ushbu projectga a'zo emas!")
    
    # Allaqachon assign qilinganmi?
    if task.assignee_id:
        raise HTTPException(400, "Task already has a developer assigned.")
    
    # Assign developer
    task.assignee_id = user.id
    task.status = Status.TODO

    # AuditLog yozish
    audit_log = AuditLog(
        action=f"Developer {user.fullname} assigneed to task {task.key}",
        user_id=current_user.id,
        task_id=task.id
    )

    db.add(audit_log)

    notif_developer = Notification(
        message=f"Siz {task.key} taskiga biriktirildingiz!",
        recipient_id=user.id,
        sender_id=current_user.id,
        task_id=task.id,
        project_id=project_id
    )
    db.add(notif_developer)

    ws_manager: WSManager = request.app.state.ws_manager
    event_type = WSEventTypes.task_status_change

    await dispatch_ws_event(
        ws_manager=ws_manager,
        event_type=event_type,
        project_id=project_id,
        payload={
            "event": event_type,
            "task_id": task.id,
            "task_key": task.key,
            "developer_id": user.id,
            "developer_name": user.fullname,
            "message": f"{user.fullname} {task.key} taskiga developer qilib biriktirildi."
        }
    )


    db.commit()
    db.refresh(task)

    return {
        "detail": "Developer successfully assigned.",
        "task_key": task.key,
        "developer_id": user.id,
        "developer_name": user.fullname
    }


@router.get("/{task_key:str}/")
async def get_task_by_key(db: db_dep, current_user: current_user_dep, task_key: str):

    task = get_object_or_404(db, Task, key=task_key)
    return task


@router.put("/{task_key:str}/edit/")
async def update_task(
    db: db_dep, user: project_manager_dep, task_key: str, data: TaskUpdateRequest
):
    task = get_object_or_404(db, Task, key=task_key)

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
    task = get_object_or_404(db, Task, key=task_key)

    if task.reporter_id != user.id:
        raise HTTPException(400, "Bu taskni siz yaratmagansiz. Uni o'chiraolmaysiz.")

    db.delete(task)
    db.commit()

    return Response(status_code=204)


@router.patch("/{task_key:str}/move/")
async def move_task(
    db: db_dep, 
    user: current_user_dep, 
    task_key: str, 
    data: TaskMoveRequest,
    request: Request
):  
    
    task: Task = get_object_or_404(db, Task, key=task_key)
    old_status = task.status

    if user.role == Role.developer and task.assignee_id != user.id:
        raise HTTPException(403, "Siz bu taskga biriktirilgan developer emassiz!")
    
    if user.role == Role.tester:
        is_member = db.query(ProjectMember).filter(
            ProjectMember.user_id==user.id,
            ProjectMember.project_id==task.project_id
        ).first()

        if not is_member:
            raise HTTPException(403, "Siz bu projectga a'zo emassiz!")

    if not TaskTransitionValidator.can_move(task.status, data.status, user.role):
        raise HTTPException(400, "Bu status o'zgarishiga ruxsat yo'q!")
    
    task.status = data.status

    # AuditLog yozish
    audit_log = AuditLog(
        action=f"Status changed: {old_status}->{data.status}#",
        user_id=user.id,
        task_id=task.id
    )

    db.add(audit_log)

    recipients = []

    if data.status == Status.TODO:
        recipients=[task.assignee_id]
    elif data.status == Status.IN_PROGRESS:
        recipients=[task.reporter_id]
    elif data.status == Status.READY_FOR_TESTING and data.status == Status.DONE:
        project: Project = get_object_or_404(db, Project, id=task.project_id)
        members = project.members
        recipients = [m.id for m in members]


    # Notification yozish
    for recipient in recipients:
        notification = Notification(
            message=f"Status changed: {old_status}->{data.status}#",
            recipient_id=recipient,
            sender_id=user.id,
            task_id=task.id,
            project_id=task.project_id
        )
        db.add(notification)
    
    event_type = WSEventTypes.task_all

    ws_manager: WSManager = request.app.state.ws_manager

    await dispatch_ws_event(
        ws_manager=ws_manager,
        event_type=event_type,
        project_id=task.project_id,
        payload={
            "event_type": event_type,
            "message": f"Status changed: {old_status}->{data.status}#",
            "project_id": task.project_id,
            "task_id": task.id
        }
    )


    db.commit()

    return {"detail": "Successfully status changed!","new_status": data.status}


@router.get("/{task_key:str}/comments/")
async def get_task_comments(db: db_dep, user: current_user_dep, task_key: str):
    task = db.query(Task).filter(Task.key == task_key).first()

    if not task:
        raise HTTPException(404, "Task Not Found.")

    comments = task.comments

    return comments

