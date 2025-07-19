from typing import List

from fastapi import APIRouter, HTTPException

from app.models import Status
from app.dependencies import db_dep
from app.schemas.status import (
    StatusCreateIn, 
    StatusCreateOut, 
    StatusListOut,
    StatusUpdateIn,
    StatusUpdateOut
)

router = APIRouter(
    prefix="/status",
    tags=['status']
)



@router.post("/create/", response_model=StatusCreateOut)
async def create_status(db:db_dep, status_in: StatusCreateIn):
    new_status = Status(
        name=status_in.name,
        description=status_in.description
    )

    db.add(new_status)
    db.commit()
    db.refresh(new_status)

    return new_status


@router.get("/list/", response_model=List[StatusListOut])
async def status_list(db: db_dep):
    statuses = db.query(Status).all()
    return statuses


@router.put("/{status_id:int}/update/", response_model=StatusUpdateOut)
async def update_status(db:db_dep, status_id: int, status_in: StatusUpdateIn):
    status = db.query(Status).filter(Status.id==status_id).first()

    if not status:
        raise HTTPException(
            detail="Status Not Found.",
            status_code=404
        )
    
    update_status = status_in.model_dump(exclude_unset=True)

    for key, value in update_status.items():
        setattr(status, key, value)
    
    db.commit()
    db.refresh(status)

    return status


@router.delete("/{status_id:int}/")
async def delete_status(db: db_dep, status_id:int):
    status = db.query(Status).filter(Status.id==status_id).first()

    if not status:
        raise HTTPException(
            detail="Status not found.",
            status_code=404
        )
    
    db.delete(status)
    db.commit()

    return {
        "status": True,
        "message": "Status successfully deleted."
    }