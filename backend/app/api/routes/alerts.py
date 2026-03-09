from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Query
from sqlalchemy.orm import Session
from app.infrastructure.database.base import get_db
from app.infrastructure.repositories.repositories import AlertRepository, UserRepository
from app.infrastructure.notifications.notification_service import email_service, sms_service
from app.api.dependencies import require_role
from app.api.websocket_manager import ws_manager
from app.models.db_models import Alert, User
from app.schemas.schemas import AlertCreate, AlertResponse, PaginatedResponse
from app.core.entities.models import UserRole

router = APIRouter(prefix="/alerts", tags=["Alerts"])


@router.post("", response_model=AlertResponse, status_code=status.HTTP_201_CREATED)
async def create_alert(
    data: AlertCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN, UserRole.RESPONDER)),
):
    repo = AlertRepository(db)
    alert = Alert(
        title=data.title,
        message=data.message,
        region=data.region,
        severity=data.severity,
        created_by=str(current_user.id),
    )
    alert = repo.create(alert)

    alert_data = {
        "id": str(alert.id),
        "title": alert.title,
        "message": alert.message,
        "region": alert.region,
        "severity": alert.severity,
        "created_by": str(alert.created_by),
        "created_at": str(alert.created_at),
    }

    # Broadcast via WebSocket
    background_tasks.add_task(ws_manager.broadcast_alert, alert_data)

    # Get all users and notify
    user_repo = UserRepository(db)
    users = user_repo.list_all(limit=1000)
    for user in users:
        background_tasks.add_task(
            email_service.send_alert_notification,
            user.email,
            data.title,
            data.message,
        )
        if user.phone:
            background_tasks.add_task(
                sms_service.send_emergency_alert,
                user.phone,
                data.region,
                data.message,
            )

    return alert


@router.get("", response_model=PaginatedResponse)
async def list_alerts(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    repo = AlertRepository(db)
    skip = (page - 1) * per_page
    items, total = repo.list_all(skip=skip, limit=per_page)
    pages = (total + per_page - 1) // per_page
    results = [
        {
            "id": str(a.id),
            "title": a.title,
            "message": a.message,
            "region": a.region,
            "severity": a.severity,
            "created_by": str(a.created_by),
            "created_at": a.created_at,
        }
        for a in items
    ]
    return PaginatedResponse(items=results, total=total, page=page, per_page=per_page, pages=pages)


@router.get("/{alert_id}", response_model=AlertResponse)
async def get_alert(alert_id: str, db: Session = Depends(get_db)):
    repo = AlertRepository(db)
    alert = repo.get_by_id(alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    return alert
