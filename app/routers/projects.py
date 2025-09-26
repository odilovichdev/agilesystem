from typing import List

from fastapi import APIRouter, HTTPException

from app.schemas.auth import Role
from app.utils import get_object_or_404
from app.models import Project, ProjectMember, User
from app.services.projects import generate_project_key
from app.dependencies import current_user_dep, db_dep, project_owner_dep
from app.schemas import (
    ProjectCreateRequest,
    ProjectInviteRequest,
    ProjectKickRequest,
    ProjectMemmberResponse,
    ProjectResponse,
    ProjectUpdateRequest,
    TaskListResponse,
)

router = APIRouter(
    prefix="/project", 
    tags=["project"]
)


@router.post("/create/")
async def project_create(
    db: db_dep, data: ProjectCreateRequest, user: project_owner_dep
):
    generated_key = generate_project_key(db=db, name=data.name)

    # project owner yangi project yaratishi
    new_project = Project(
        name=data.name,
        description=data.description,
        key=generated_key,
        owner_id=user.id,
        is_private=data.is_private,
    )

    db.add(new_project)
    db.commit()
    db.refresh(new_project)

    # project yaralganda ownerni ProjectMemmberga qo'shish
    new_project_memmber = ProjectMember(project_id=new_project.id, user_id=user.id)

    db.add(new_project_memmber)
    db.commit()
    db.refresh(new_project_memmber)

    return {"detail": "Create project successfully!"}


@router.get("/all/", response_model=List[ProjectResponse])
async def get_all_project(db: db_dep):
    projects = db.query(Project).all()

    if not projects:
        raise HTTPException(404, "Projects Not Found.")

    return projects


@router.get("/{project_key:str}/", response_model=ProjectResponse)
async def get_project_by_key(db: db_dep, project_key: str):

    project = get_object_or_404(db, Project, key=project_key)
    return project


@router.put("/{project_key:str}/update", response_model=ProjectUpdateRequest)
async def project_update(
    db: db_dep,
    project_key: str,
    user: project_owner_dep,
    new_project: ProjectUpdateRequest,
):
    
    project = get_object_or_404(db, Project, key=project_key)

    if project.owner_id != user.id:
        raise HTTPException(400, "Faqat o'zingiz yaratgan loyihani edit qila olasiz.")

    update_project = new_project.model_dump(exclude_unset=True)

    for key, value in update_project.items():
        setattr(project, key, value)

    if "name" in new_project:
        project.key = generate_project_key(db=db, name=project.name)

    db.commit()
    db.refresh(project)

    return project


@router.get("/{project_key}/members/", response_model=List[ProjectMemmberResponse])
async def get_project_member(db: db_dep, user: current_user_dep, project_key: str):

    project = get_object_or_404(db, Project, key=project_key)

    members = project.members

    return members


@router.post("/{project_key:str}/members/invite/")
async def project_add_member(
    db: db_dep,
    project_key: str,
    user: project_owner_dep,
    invite_data: ProjectInviteRequest,
):
    
    project = get_object_or_404(db, Project, key=project_key)

    # User qo'shayotgan odam shu loyihani yaratganini tekshirish
    if project.owner_id != user.id:
        raise HTTPException(
            403, "Siz faqat o'zingiz yaratgan projectga a'zo qo'sha olasiz."
        )

    user = get_object_or_404(db, User, id=invite_data.user_id)

    if user.role == Role.owner.value:
        raise HTTPException(403, "Loyihada bitta Project Owner bo'ladi.")

    # user project ga biriktirilmaganini tekshirish
    if user in project.members:
        raise HTTPException(400, "User is already in the project.")

    new_member = ProjectMember(user_id=user.id, project_id=project.id)

    db.add(new_member)
    db.commit()
    db.refresh(new_member)

    return {"detail": "User loyihaga muvaffaqiyatli biriktirildi."}


@router.delete("/{project_key}/members/kick/")
async def kick_project_member(
    db: db_dep, user: project_owner_dep, project_key: str, kick_data: ProjectKickRequest
):
    
    project = get_object_or_404(db, Project, key=project_key)

    if project.owner.id != user.id:
        raise HTTPException(403, "Siz bu loyihani yaratmagansiz. Uni o'chira olmaysiz.")

    member = (
        db.query(ProjectMember)
        .filter(
            ProjectMember.user_id == kick_data.user_id,
            ProjectMember.project_id == project.id,
        )
        .first()
    )

    if not member:
        raise HTTPException(404, "Project da bunday azo yo'q.")

    db.delete(member)
    db.commit()

    return {"detail": "Xodim loyihadan muvaffaqiyatli chiqarildi."}


@router.get("/{project_key:str}/tasks/", response_model=List[TaskListResponse])
async def get_project_task(db: db_dep, user: current_user_dep, project_key: str):

    project = get_object_or_404(db, Project, key=project_key)
    tasks = project.tasks
    return tasks
