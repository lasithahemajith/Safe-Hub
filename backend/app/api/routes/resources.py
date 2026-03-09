from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from geoalchemy2.elements import WKTElement
from app.infrastructure.database.base import get_db
from app.infrastructure.repositories.repositories import ResourceRepository
from app.api.dependencies import require_role, get_current_user
from app.models.db_models import Resource, User
from app.schemas.schemas import ResourceCreate, ResourceResponse, ResourceUpdate
from app.core.entities.models import UserRole

router = APIRouter(prefix="/resources", tags=["Resources"])


@router.post("", response_model=ResourceResponse, status_code=status.HTTP_201_CREATED)
async def create_resource(
    data: ResourceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN, UserRole.RESPONDER)),
):
    repo = ResourceRepository(db)
    location = WKTElement(f"POINT({data.longitude} {data.latitude})", srid=4326)
    resource = Resource(
        resource_type=data.resource_type,
        latitude=data.latitude,
        longitude=data.longitude,
        location=location,
        description=data.description,
        contact=data.contact,
    )
    return repo.create(resource)


@router.get("", response_model=List[ResourceResponse])
async def list_resources(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    repo = ResourceRepository(db)
    return repo.list_all(skip=skip, limit=limit)


@router.get("/{resource_id}", response_model=ResourceResponse)
async def get_resource(
    resource_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    repo = ResourceRepository(db)
    resource = repo.get_by_id(resource_id)
    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")
    return resource


@router.patch("/{resource_id}", response_model=ResourceResponse)
async def update_resource(
    resource_id: str,
    data: ResourceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN, UserRole.RESPONDER)),
):
    repo = ResourceRepository(db)
    resource = repo.get_by_id(resource_id)
    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")

    if data.status is not None:
        resource.status = data.status
    if data.latitude is not None:
        resource.latitude = data.latitude
    if data.longitude is not None:
        resource.longitude = data.longitude
        resource.location = WKTElement(f"POINT({data.longitude} {data.latitude})", srid=4326)
    if data.assigned_incident is not None:
        resource.assigned_incident = data.assigned_incident

    return repo.update(resource)
