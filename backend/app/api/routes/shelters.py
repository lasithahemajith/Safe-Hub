from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from geoalchemy2.elements import WKTElement
from app.infrastructure.database.base import get_db
from app.infrastructure.repositories.repositories import ShelterRepository
from app.api.dependencies import require_role
from app.models.db_models import Shelter, User
from app.schemas.schemas import ShelterCreate, ShelterResponse, ShelterUpdate
from app.core.entities.models import UserRole

router = APIRouter(prefix="/shelters", tags=["Shelters"])


@router.post("", response_model=ShelterResponse, status_code=status.HTTP_201_CREATED)
async def create_shelter(
    data: ShelterCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN)),
):
    repo = ShelterRepository(db)
    location = WKTElement(f"POINT({data.longitude} {data.latitude})", srid=4326)
    shelter = Shelter(
        name=data.name,
        capacity=data.capacity,
        available_space=data.available_space,
        latitude=data.latitude,
        longitude=data.longitude,
        location=location,
        contact_number=data.contact_number,
        address=data.address,
    )
    return repo.create(shelter)


@router.get("", response_model=List[ShelterResponse])
async def list_shelters(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    repo = ShelterRepository(db)
    return repo.list_all(skip=skip, limit=limit)


@router.get("/nearby", response_model=List[ShelterResponse])
async def get_nearby_shelters(
    lat: float = Query(..., ge=-90, le=90),
    lon: float = Query(..., ge=-180, le=180),
    radius_km: float = Query(20, ge=0.1, le=500),
    db: Session = Depends(get_db),
):
    repo = ShelterRepository(db)
    return repo.find_nearby(lat, lon, radius_km)


@router.get("/{shelter_id}", response_model=ShelterResponse)
async def get_shelter(shelter_id: str, db: Session = Depends(get_db)):
    repo = ShelterRepository(db)
    shelter = repo.get_by_id(shelter_id)
    if not shelter:
        raise HTTPException(status_code=404, detail="Shelter not found")
    return shelter


@router.patch("/{shelter_id}", response_model=ShelterResponse)
async def update_shelter(
    shelter_id: str,
    data: ShelterUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN, UserRole.RESPONDER)),
):
    repo = ShelterRepository(db)
    shelter = repo.get_by_id(shelter_id)
    if not shelter:
        raise HTTPException(status_code=404, detail="Shelter not found")

    if data.available_space is not None:
        shelter.available_space = data.available_space
    if data.is_active is not None:
        shelter.is_active = data.is_active

    return repo.update(shelter)
