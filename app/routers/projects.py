from typing import List

from sqlalchemy.orm import joinedload
from fastapi import APIRouter, HTTPException

from app.schemas.auth import Role
from app.models import Project, ProjectMemmber, User
from app.dependencies import db_dep, project_owner_dep
from app.schemas import (
    ProjectCreateIn, 
    ProjectCreateOut, 
    ProjectUpdate, 
    ProjectMemmberAddOut, 
    ProjectMemmberAddIn,
    ProjectUserOut
)

router = APIRouter(
    prefix="/project",
    tags=['project']
)



@router.post("/create/", response_model=ProjectCreateOut)
async def project_create(db: db_dep, project_in: ProjectCreateIn, user_in: project_owner_dep):

    # project owner yangi project yaratishi
    new_project = Project(
        name=project_in.name,
        description=project_in.description,
        key=project_in.key,
        owner_id=user_in.id
    )

    db.add(new_project)
    db.commit()
    db.refresh(new_project)

    # project yaralganda ownerni ProjectMemmberga qo'shish
    new_project_memmber = ProjectMemmber(
        project_id=new_project.id,
        user_id=user_in.id
    )

    db.add(new_project_memmber)
    db.commit()
    db.refresh(new_project_memmber)

    return new_project


@router.get("/{project_id:int}/", response_model=ProjectCreateOut)
async def product_detail(db: db_dep, project_id: int):
    project = db.query(Project).filter(Project.id==project_id).first()
    if not project:
        raise HTTPException(
            detail="Page not found.",
            status_code=404
        ) 
    return project


@router.get("/list/", response_model=List[ProjectCreateOut])
async def project_list(db: db_dep):
    products = db.query(Project).options(joinedload(Project.owner)).all()
    return products


@router.put("/{project_id:int}/update", response_model=ProjectUpdate)
async def project_update(db: db_dep, project_id:int, new_project: ProjectUpdate):
    project = db.query(Project).filter(Project.id==project_id).first()

    if not project:
        raise HTTPException(
            detail="Project not found.",
            status_code=404
        )
    update_project = new_project.model_dump(exclude_unset=True)

    for key, value in update_project.items():
        setattr(project, key, value)

    db.commit()
    db.refresh(project)

    return project


@router.delete("{project_id:int}/delete/")
async def project_delete(db: db_dep, project_id: int):
    project = db.query(Project).filter(Project.id==project_id).first()
    if not project:
        raise HTTPException(
            detail="Project not found.",
            status_code=404
        )
    db.delete(project)
    db.commit()
    return {"success": True, "message": "User is successfully deleted."}


@router.post("/{project_id:int}/add-member/", response_model=ProjectMemmberAddOut)
async def project_add_member(
    db: db_dep, 
    project_id:int,
    user: project_owner_dep, 
    project_memmber_in: ProjectMemmberAddIn
    ):
    
    project = db.query(Project).filter(Project.id==project_id).first()

    if not project:
        raise HTTPException(
            detail="Project topilmadi.",
            status_code=404
        )

    # User qo'shayotgan odam shu loyihani yaratganini tekshirish
    if project.owner_id != user.id:
        raise HTTPException(
            detail="Siz faqat o'zingiz yaratgan projectga memmber qo'sha olasiz.",
            status_code=403
        )
    
    p_user = db.query(User).filter(User.id==project_memmber_in.user_id).first()
    
    if p_user.role == Role.PROJECT_OWNER.value:
        raise HTTPException(
            detail="Loyihada bitta Project Owner bo'ladi.",
            status_code=403
        )
    
    project_memmber = db.query(ProjectMemmber).filter(ProjectMemmber.user_id==project_memmber_in.user_id).first()

    # User oldin bu loyihaga qo'shilganini tekshirish
    if project_memmber:
        raise HTTPException(
            detail="Bu user project azosi.",
            status_code=400
        )

    # Loyihaga yangi user qo'shish
    new_project_memmber = ProjectMemmber(
        project_id=project_id,
        user_id=project_memmber_in.user_id
    )

    db.add(new_project_memmber)
    db.commit()
    db.refresh(new_project_memmber)

    return new_project_memmber
    

@router.get("/{project_id:int}/users", response_model=List[ProjectUserOut])
async def project_users(db: db_dep, project_id:int):
    project = db.query(Project).filter(Project.id==project_id).first()

    if not project:
        raise HTTPException(
            detail="Project Not Found.",
            status_code=404
        )
    
    members = db.query(User).join(
        ProjectMemmber, ProjectMemmber.user_id==User.id
    ).filter(ProjectMemmber.project_id==project_id).all()

    return members
    
    
    
