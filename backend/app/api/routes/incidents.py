from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Query, BackgroundTasks
from sqlalchemy.orm import Session
from geoalchemy2.elements import WKTElement
from app.infrastructure.database.base import get_db
from app.infrastructure.repositories.repositories import IncidentRepository
from app.infrastructure.external_services.s3_service import s3_service
from app.infrastructure.external_services.ai_client import ai_service
from app.infrastructure.notifications.notification_service import email_service
from app.api.dependencies import get_current_user, require_role
from app.api.websocket_manager import ws_manager
from app.models.db_models import User, Incident, IncidentVote, IncidentComment
from app.schemas.schemas import (
    IncidentCreate, IncidentUpdate, IncidentResponse, CommentCreate, CommentResponse, PaginatedResponse
)
from app.core.entities.models import UserRole

router = APIRouter(prefix="/incidents", tags=["Incidents"])


def incident_to_response(incident: Incident, vote_count: int = 0) -> dict:
    return {
        "id": str(incident.id),
        "title": incident.title,
        "description": incident.description,
        "disaster_type": incident.disaster_type,
        "severity": incident.severity,
        "latitude": incident.latitude,
        "longitude": incident.longitude,
        "status": incident.status,
        "reported_by": str(incident.reported_by),
        "image_urls": incident.image_urls or [],
        "ai_damage_level": incident.ai_damage_level,
        "ai_confidence": incident.ai_confidence,
        "vote_count": vote_count,
        "created_at": incident.created_at,
        "updated_at": incident.updated_at,
    }


@router.post("", response_model=IncidentResponse, status_code=status.HTTP_201_CREATED)
async def create_incident(
    data: IncidentCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    repo = IncidentRepository(db)
    location = WKTElement(f"POINT({data.longitude} {data.latitude})", srid=4326)
    incident = Incident(
        title=data.title,
        description=data.description,
        disaster_type=data.disaster_type,
        severity=data.severity,
        latitude=data.latitude,
        longitude=data.longitude,
        location=location,
        reported_by=current_user.id,
        image_urls=[],
    )
    incident = repo.create(incident)

    # Send confirmation email
    background_tasks.add_task(
        email_service.send_incident_confirmation,
        current_user.email,
        incident.title,
        str(incident.id),
    )

    # Broadcast via WebSocket
    resp = incident_to_response(incident)
    background_tasks.add_task(ws_manager.broadcast_new_incident, resp)

    return resp


@router.post("/{incident_id}/images")
async def upload_incident_images(
    incident_id: str,
    files: List[UploadFile] = File(...),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    repo = IncidentRepository(db)
    incident = repo.get_by_id(incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    if str(incident.reported_by) != str(current_user.id) and current_user.role not in [UserRole.ADMIN, UserRole.RESPONDER]:
        raise HTTPException(status_code=403, detail="Permission denied")

    uploaded_urls = []
    for f in files[:5]:  # max 5 images
        url = await s3_service.upload_image(f, folder="incidents")
        if url:
            uploaded_urls.append(url)

    if uploaded_urls:
        incident.image_urls = (incident.image_urls or []) + uploaded_urls
        repo.update(incident)

        # Trigger AI analysis on first image
        if incident.image_urls and not incident.ai_damage_level:
            ai_result = await ai_service.analyze_image(incident.image_urls[0])
            if ai_result:
                incident.ai_damage_level = ai_result.get("damage_level")
                incident.ai_confidence = ai_result.get("confidence")
                repo.update(incident)

    return {"uploaded": uploaded_urls, "total_images": len(incident.image_urls or [])}


@router.get("", response_model=PaginatedResponse)
async def list_incidents(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    disaster_type: Optional[str] = None,
    severity: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
):
    repo = IncidentRepository(db)
    skip = (page - 1) * per_page
    items, total = repo.list_all(
        skip=skip,
        limit=per_page,
        disaster_type=disaster_type,
        severity=severity,
        status=status,
    )
    pages = (total + per_page - 1) // per_page
    results = [incident_to_response(i, repo.get_vote_count(i.id)) for i in items]
    return PaginatedResponse(items=results, total=total, page=page, per_page=per_page, pages=pages)


@router.get("/nearby", response_model=List[IncidentResponse])
async def get_nearby_incidents(
    lat: float = Query(..., ge=-90, le=90),
    lon: float = Query(..., ge=-180, le=180),
    radius_km: float = Query(10, ge=0.1, le=500),
    db: Session = Depends(get_db),
):
    repo = IncidentRepository(db)
    incidents = repo.find_nearby(lat, lon, radius_km)
    return [incident_to_response(i, repo.get_vote_count(i.id)) for i in incidents]


@router.get("/{incident_id}", response_model=IncidentResponse)
async def get_incident(incident_id: str, db: Session = Depends(get_db)):
    repo = IncidentRepository(db)
    incident = repo.get_by_id(incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    return incident_to_response(incident, repo.get_vote_count(incident.id))


@router.put("/{incident_id}", response_model=IncidentResponse)
async def update_incident(
    incident_id: str,
    data: IncidentUpdate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    repo = IncidentRepository(db)
    incident = repo.get_by_id(incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    if str(incident.reported_by) != str(current_user.id) and current_user.role not in [UserRole.ADMIN, UserRole.RESPONDER]:
        raise HTTPException(status_code=403, detail="Permission denied")

    if data.title is not None:
        incident.title = data.title
    if data.description is not None:
        incident.description = data.description
    if data.severity is not None:
        incident.severity = data.severity
    if data.status is not None:
        incident.status = data.status

    incident = repo.update(incident)
    resp = incident_to_response(incident, repo.get_vote_count(incident.id))
    background_tasks.add_task(ws_manager.broadcast_incident_update, resp)
    return resp


@router.post("/{incident_id}/vote")
async def vote_incident(
    incident_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    repo = IncidentRepository(db)
    incident = repo.get_by_id(incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    existing = repo.get_vote(incident_id, str(current_user.id))
    if existing:
        raise HTTPException(status_code=400, detail="Already voted")

    vote = IncidentVote(incident_id=incident_id, user_id=str(current_user.id))
    repo.add_vote(vote)
    return {"vote_count": repo.get_vote_count(incident_id)}


@router.post("/{incident_id}/comments", response_model=CommentResponse, status_code=201)
async def add_comment(
    incident_id: str,
    data: CommentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    repo = IncidentRepository(db)
    incident = repo.get_by_id(incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    comment = IncidentComment(
        incident_id=incident_id,
        user_id=str(current_user.id),
        content=data.content,
    )
    comment = repo.add_comment(comment)
    return comment


@router.get("/{incident_id}/comments", response_model=List[CommentResponse])
async def list_comments(incident_id: str, db: Session = Depends(get_db)):
    repo = IncidentRepository(db)
    return repo.list_comments(incident_id)
