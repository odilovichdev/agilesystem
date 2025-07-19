from fastapi import APIRouter, HTTPException


from app.models import Task, Project, ProjectMemmber
from app.dependencies import db_dep, project_manager_dep
from app.schemas.tasks import TaskCreateIn, TaskCreateOut

router = APIRouter(
    prefix="/tasks",
    tags=["tasks"]
)


@router.post("/create/", response_model=TaskCreateOut)
async def task_create(db: db_dep, user: project_manager_dep, task_in: TaskCreateIn):
    project = db.query(Task).filter(Project.id==task_in.project_id).first()

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
        repoter_id=user.id
    )

    db.add(new_task)
    db.commit()
    db.refresh(new_task)

    return new_task
    

    
    
    
