from typing import List

from sqlalchemy.orm import selectinload
from fastapi import APIRouter, HTTPException, Response


from app.services import generated_task_key
from app.models import Task, Project, ProjectMember
from app.dependencies import db_dep, project_manager_dep, current_user_dep
from app.schemas.tasks import (
    TaskCreateRequest,
    TaskDetailResponse,
    TaskListResponse,
    TaskUpdateRequest,
    TaskMoveRequest
)

router = APIRouter(
    prefix="/tasks",
    tags=["tasks"]
)


@router.get("/all/", response_model=List[TaskListResponse])
async def get_tasks(db: db_dep):
    tasks = db.query(Task).all()
    return tasks


@router.post("/create/", response_model=TaskDetailResponse)
async def task_create(
    db: db_dep, 
    user: project_manager_dep, 
    task_data: TaskCreateRequest):

    project = db.query(Project).filter(Project.key==task_data.project_key).first()

    if not project:
        raise HTTPException(404, "Project Not Found.")

    
    manager = db.query(ProjectMember).filter(
        ProjectMember.project_id==project.id, 
        ProjectMember.user_id==user.id).first()
    
    # taskni yaratayotgan manager project ga qo'shilganini tekshirish
    if not manager:
        raise HTTPException(403,"Task yaratayptgan manager project ga biriktirlmagan.")

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
        assignee_id=task_data.assignee_id
    )

    db.add(new_task)
    db.commit()
    db.refresh(new_task)

    return new_task
    

@router.get("/{task_key:str}/")
async def get_task_by_key(
    db: db_dep, 
    current_user: current_user_dep,
    task_key: str):

    task = db.query(Task).filter(Task.key==task_key).first()

    if not task:
        raise HTTPException(404, "Task Not Found.")
    
    return task
    

@router.put("/{task_key:str}/edit/")
async def update_task(
    db: db_dep,
    user: project_manager_dep,
    task_key: str,
    data: TaskUpdateRequest):
    
    task = db.query(Task).filter(Task.key==task_key).first()

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
async def delete_task(
    db: db_dep,
    user: project_manager_dep,
    task_key: str):

    task = db.query(Task).filter(Task.key==task_key).first()

    if not task:
        raise HTTPException(404, "Task Not Found.")
    
    if task.reporter_id != user.id:
        raise HTTPException(400, "Bu taskni siz yaratmagansiz. Uni o'chiraolmaysiz.")
    
    db.delete(task)
    db.commit()

    return Response(status_code=204)


@router.patch("/{task_key:str}/move/", response_model=TaskDetailResponse)
async def move_task(
    db: db_dep,
    user: project_manager_dep,
    task_key: str,
    data: TaskMoveRequest):
    ... # ToDo


@router.get("/{task_key:str}/comments/")
async def get_task_comments(
    db: db_dep,
    user: current_user_dep,
    task_key: str):

    task = db.query(Task).filter(Task.key==task_key).first()

    if not task:
        raise HTTPException(404, "Task Not Found.")
    
    comments = task.comments

    return comments

    


# @router.get("/list/", response_model=List[TaskListResponse])
# async def task_list(db: db_dep):
    
#     tasks = (
#         db.query(Task).
#         options(
#             # load_only(Task.id, Task.key, Task.summary, Task.description, Task.priority, Task.due_date),
#             selectinload(Task.project),
#             selectinload(Task.status),
#             selectinload(Task.assignee),
#             selectinload(Task.reporter)
#         )
#         .all()
#     )

#     # tasks = db.query(Task).all()

#     return tasks


# @router.delete("/{task_id:int}/delete/")
# async def delete_task(db: db_dep, task_id: int):
#     task = db.query(Task).filter(Task.id==task_id).first()

#     if not task:
#         raise HTTPException(
#             detail="Task not found.",
#             status_code=404
#         )
    
#     db.delete(task)
#     db.commit()

#     return {
#         "success": True,
#         "message": "Task delete successfully"
#     }


# @router.put("/{task_id:int}/update/", response_model=TaskEditOut)
# async def edit_task(db: db_dep, task_id: int, user: project_manager_dep, task_in: TaskEditIn):
#     task = db.query(Task).filter(Task.id==task_id).first()

#     if not task:
#         raise HTTPException(
#             detail=f"Task with {task_id} not found.",
#             status_code=404
#         )

#     project_member = db.query(ProjectMemmber).filter(
#         ProjectMemmber.user_id==user.id, 
#         ProjectMemmber.project_id==task.project_id
#         ).first()

#     if not project_member:
#         raise HTTPException(
#             detail="Siz bu task yaratilgan loyihaga biriktirilmagansiz.",
#             status_code=403
#         )
    
#     if not db.query(Task).filter(Task.reporter_id==user.id).first():
#         raise HTTPException(
#             detail="Siz bu task ni yaratmagansiz.",
#             status_code=403
#         )
    
#     update_task = task_in.model_dump(exclude_unset=True)

#     for key, value in update_task.items():
#         setattr(task, key, value)
    
#     db.commit()
#     db.refresh(task)

#     return task
    
    

# @router.get("/{task_id:int}/", response_model=TaskDetailOut)
# async def task_detail(db: db_dep, task_id: int):
#     task = db.query(Task).filter(Task.id==task_id).first()

#     if not task:
#         raise HTTPException(
#             detail="Task topilmadi.",
#             status_code=404
#         )
    
#     return task


# @router.put("/{task_id:int}/add-assignee/", response_model=TaskDetailOut)
# async def task_add_assignee(db: db_dep, user: project_manager_dep, task_id: int, task_in: TaskAddAssigneeIn):
#     task = db.query(Task).filter(Task.id==task_id).first()


#     if task.reporter_id != user.id:
#         raise HTTPException(
#             detail="Siz bu taskni yaratmagansiz.",
#             status_code=403
#         )

#     if not task:
#         raise HTTPException(
#             detail="Task not found.",
#             status_code=404
#         )
    
#     status = db.query(Status).filter(Status.id==task_in.status_id).first()

#     if not status:
#         raise HTTPException(
#             detail="Status not found.",
#             status_code=404
#         )
    
#     task.assignee_id = task_in.assignee_id
#     task.status_id = task_in.status_id

#     db.commit()
#     db.refresh(task)

#     return task

    

# @router.patch("/{task_id:int}/")
# async def update_status_for_task(db: db_dep):
#     ...
    









