from typing import List

from fastapi import APIRouter, HTTPException
from sqlalchemy.orm import selectinload


from app.models import Task, Project, ProjectMemmber
from app.dependencies import db_dep, project_manager_dep
from app.schemas.tasks import (
    TaskCreateIn, 
    TaskCreateOut, 
    TaskListOut,
    TaskEditIn,
    TaskEditOut,
    TaskDetailOut
)

router = APIRouter(
    prefix="/tasks",
    tags=["tasks"]
)


@router.post("/create/", response_model=TaskCreateOut)
async def task_create(db: db_dep, user: project_manager_dep, task_in: TaskCreateIn):
    project = db.query(Project).filter(Project.id==task_in.project_id).first()

    # Project borligini tekshirish
    if not project:
        raise HTTPException(
            detail="Project Not Found.",
            status_code=404
        )
    
    project_member = db.query(ProjectMemmber).filter(ProjectMemmber.project_id==task_in.project_id, ProjectMemmber.user_id==task_in.assignee_id).first()

    # taskga biriktirilayotgan user project ga qo'shilganini tekshirish
    if not project_member:
        raise HTTPException(
            detail="Bu user project ga biriktirilmagan.",
            status_code=403
        )
    
    manager = db.query(ProjectMemmber).filter(ProjectMemmber.project_id==task_in.project_id, ProjectMemmber.user_id==user.id).first()
    
    # taskni yaratayotgan manager project ga qo'shilganini tekshirish
    if not manager:
        raise HTTPException(
            detail="Task yaratayptgan manager project ga biriktirlmagan.",
            status_code=403
        )

    # create new task
    new_task = Task(
        key=task_in.key,
        summary=task_in.summary,
        description=task_in.description,
        priority=task_in.priority,
        due_date=task_in.due_date,
        project_id=task_in.project_id,
        status_id=task_in.status_id,
        assignee_id=task_in.assignee_id,
        reporter_id=user.id
    )

    db.add(new_task)
    db.commit()
    db.refresh(new_task)

    return new_task
    
    
@router.get("/list/", response_model=List[TaskListOut])
async def task_list(db: db_dep):
    
    tasks = (
        db.query(Task).
        options(
            # load_only(Task.id, Task.key, Task.summary, Task.description, Task.priority, Task.due_date),
            selectinload(Task.project),
            selectinload(Task.status),
            selectinload(Task.assignee),
            selectinload(Task.reporter)
        )
        .all()
    )

    # tasks = db.query(Task).all()

    return tasks


@router.delete("/{task_id:int}/delete/")
async def delete_task(db: db_dep, task_id: int):
    task = db.query(Task).filter(Task.id==task_id).first()

    if not task:
        raise HTTPException(
            detail="Task not found.",
            status_code=404
        )
    
    db.delete(task)
    db.commit()

    return {
        "success": True,
        "message": "Task delete successfully"
    }


@router.put("/{task_id:int}/update/", response_model=TaskEditOut)
async def edit_task(db: db_dep, task_id: int, user: project_manager_dep, task_in: TaskEditIn):
    task = db.query(Task).filter(Task.id==task_id).first()

    if not task:
        raise HTTPException(
            detail=f"Task with {task_id} not found.",
            status_code=404
        )

    project_member = db.query(ProjectMemmber).filter(
        ProjectMemmber.user_id==user.id, 
        ProjectMemmber.project_id==task.project_id
        ).first()

    if not project_member:
        raise HTTPException(
            detail="Siz bu task yaratilgan loyihaga biriktirilmagansiz.",
            status_code=403
        )
    
    if not db.query(Task).filter(Task.reporter_id==user.id).first():
        raise HTTPException(
            detail="Siz bu task ni yaratmagansiz.",
            status_code=403
        )
    
    update_task = task_in.model_dump(exclude_unset=True)

    for key, value in update_task.items():
        setattr(task, key, value)
    
    db.commit()
    db.refresh(task)

    return task
    
    

@router.get("/{task_id:int}/", response_model=TaskDetailOut)
async def task_detail(db: db_dep, task_id: int):
    task = db.query(Task).filter(Task.id==task_id).first()

    if not task:
        raise HTTPException(
            detail="Task topilmadi.",
            status_code=404
        )
    
    return task

