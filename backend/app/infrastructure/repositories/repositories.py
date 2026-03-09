from typing import Optional, List, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func, text
from app.models.db_models import User, Incident, Alert, Shelter, Resource, IncidentVote, IncidentComment
from app.core.entities.models import IncidentStatus, SeverityLevel


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, user: User) -> User:
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def get_by_id(self, user_id: str) -> Optional[User]:
        return self.db.query(User).filter(User.id == user_id).first()

    def get_by_email(self, email: str) -> Optional[User]:
        return self.db.query(User).filter(User.email == email).first()

    def update(self, user: User) -> User:
        self.db.commit()
        self.db.refresh(user)
        return user

    def list_all(self, skip: int = 0, limit: int = 50) -> List[User]:
        return self.db.query(User).offset(skip).limit(limit).all()


class IncidentRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, incident: Incident) -> Incident:
        self.db.add(incident)
        self.db.commit()
        self.db.refresh(incident)
        return incident

    def get_by_id(self, incident_id: str) -> Optional[Incident]:
        return self.db.query(Incident).filter(Incident.id == incident_id).first()

    def list_all(
        self,
        skip: int = 0,
        limit: int = 50,
        disaster_type=None,
        severity=None,
        status=None,
    ) -> Tuple[List[Incident], int]:
        query = self.db.query(Incident)
        if disaster_type:
            query = query.filter(Incident.disaster_type == disaster_type)
        if severity:
            query = query.filter(Incident.severity == severity)
        if status:
            query = query.filter(Incident.status == status)
        total = query.count()
        items = query.order_by(Incident.created_at.desc()).offset(skip).limit(limit).all()
        return items, total

    def find_nearby(self, lat: float, lon: float, radius_km: float = 10) -> List[Incident]:
        """Find incidents within radius_km using PostGIS ST_DWithin."""
        radius_m = radius_km * 1000
        query = text(
            """
            SELECT i.* FROM incidents i
            WHERE ST_DWithin(
                i.location::geography,
                ST_SetSRID(ST_MakePoint(:lon, :lat), 4326)::geography,
                :radius
            )
            AND i.status != 'closed'
            ORDER BY ST_Distance(
                i.location::geography,
                ST_SetSRID(ST_MakePoint(:lon, :lat), 4326)::geography
            )
            """
        )
        result = self.db.execute(query, {"lat": lat, "lon": lon, "radius": radius_m})
        ids = [row[0] for row in result]
        if not ids:
            return []
        return self.db.query(Incident).filter(Incident.id.in_(ids)).all()

    def update(self, incident: Incident) -> Incident:
        self.db.commit()
        self.db.refresh(incident)
        return incident

    def get_vote_count(self, incident_id: str) -> int:
        return self.db.query(func.count(IncidentVote.id)).filter(
            IncidentVote.incident_id == incident_id
        ).scalar() or 0

    def add_vote(self, vote: IncidentVote) -> IncidentVote:
        self.db.add(vote)
        self.db.commit()
        self.db.refresh(vote)
        return vote

    def get_vote(self, incident_id: str, user_id: str) -> Optional[IncidentVote]:
        return self.db.query(IncidentVote).filter(
            IncidentVote.incident_id == incident_id,
            IncidentVote.user_id == user_id,
        ).first()

    def add_comment(self, comment: IncidentComment) -> IncidentComment:
        self.db.add(comment)
        self.db.commit()
        self.db.refresh(comment)
        return comment

    def list_comments(self, incident_id: str) -> List[IncidentComment]:
        return self.db.query(IncidentComment).filter(
            IncidentComment.incident_id == incident_id
        ).order_by(IncidentComment.created_at.asc()).all()


class AlertRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, alert: Alert) -> Alert:
        self.db.add(alert)
        self.db.commit()
        self.db.refresh(alert)
        return alert

    def list_all(self, skip: int = 0, limit: int = 50) -> Tuple[List[Alert], int]:
        query = self.db.query(Alert)
        total = query.count()
        items = query.order_by(Alert.created_at.desc()).offset(skip).limit(limit).all()
        return items, total

    def get_by_id(self, alert_id: str) -> Optional[Alert]:
        return self.db.query(Alert).filter(Alert.id == alert_id).first()


class ShelterRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, shelter: Shelter) -> Shelter:
        self.db.add(shelter)
        self.db.commit()
        self.db.refresh(shelter)
        return shelter

    def list_all(self, skip: int = 0, limit: int = 100) -> List[Shelter]:
        return self.db.query(Shelter).filter(Shelter.is_active == True).offset(skip).limit(limit).all()

    def find_nearby(self, lat: float, lon: float, radius_km: float = 20) -> List[dict]:
        """Find shelters within radius_km with distance."""
        radius_m = radius_km * 1000
        query = text(
            """
            SELECT s.id, s.name, s.capacity, s.available_space,
                   s.latitude, s.longitude, s.contact_number, s.address, s.is_active,
                   ST_Distance(
                       s.location::geography,
                       ST_SetSRID(ST_MakePoint(:lon, :lat), 4326)::geography
                   ) / 1000 AS distance_km
            FROM shelters s
            WHERE ST_DWithin(
                s.location::geography,
                ST_SetSRID(ST_MakePoint(:lon, :lat), 4326)::geography,
                :radius
            )
            AND s.is_active = true
            ORDER BY distance_km
            """
        )
        result = self.db.execute(query, {"lat": lat, "lon": lon, "radius": radius_m})
        return [dict(row._mapping) for row in result]

    def get_by_id(self, shelter_id: str) -> Optional[Shelter]:
        return self.db.query(Shelter).filter(Shelter.id == shelter_id).first()

    def update(self, shelter: Shelter) -> Shelter:
        self.db.commit()
        self.db.refresh(shelter)
        return shelter


class ResourceRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, resource: Resource) -> Resource:
        self.db.add(resource)
        self.db.commit()
        self.db.refresh(resource)
        return resource

    def list_all(self, skip: int = 0, limit: int = 100) -> List[Resource]:
        return self.db.query(Resource).offset(skip).limit(limit).all()

    def get_by_id(self, resource_id: str) -> Optional[Resource]:
        return self.db.query(Resource).filter(Resource.id == resource_id).first()

    def update(self, resource: Resource) -> Resource:
        self.db.commit()
        self.db.refresh(resource)
        return resource
