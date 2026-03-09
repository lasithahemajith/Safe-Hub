import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, Float, Integer, Text, Enum, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from geoalchemy2 import Geography
from app.infrastructure.database.base import Base
from app.core.entities.models import (
    UserRole, DisasterType, SeverityLevel,
    IncidentStatus, ResourceType, ResourceStatus
)


def gen_uuid():
    return str(uuid.uuid4())


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    name = Column(String(200), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    phone = Column(String(20), nullable=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), nullable=False, default=UserRole.CITIZEN)
    verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    incidents = relationship("Incident", back_populates="reporter", foreign_keys="Incident.reported_by")
    alerts = relationship("Alert", back_populates="creator")
    votes = relationship("IncidentVote", back_populates="user")
    comments = relationship("IncidentComment", back_populates="user")


class Incident(Base):
    __tablename__ = "incidents"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=False)
    disaster_type = Column(Enum(DisasterType), nullable=False)
    severity = Column(Enum(SeverityLevel), nullable=False, default=SeverityLevel.MEDIUM)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    location = Column(Geography(geometry_type="POINT", srid=4326), nullable=True)
    status = Column(Enum(IncidentStatus), nullable=False, default=IncidentStatus.REPORTED)
    reported_by = Column(UUID(as_uuid=False), ForeignKey("users.id"), nullable=False)
    image_urls = Column(JSON, default=list)
    ai_damage_level = Column(String(50), nullable=True)
    ai_confidence = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    reporter = relationship("User", back_populates="incidents", foreign_keys=[reported_by])
    votes = relationship("IncidentVote", back_populates="incident")
    comments = relationship("IncidentComment", back_populates="incident")
    resources = relationship("Resource", back_populates="assigned_incident_obj")


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    title = Column(String(500), nullable=False)
    message = Column(Text, nullable=False)
    region = Column(String(200), nullable=False)
    severity = Column(Enum(SeverityLevel), nullable=False)
    created_by = Column(UUID(as_uuid=False), ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    creator = relationship("User", back_populates="alerts")


class Shelter(Base):
    __tablename__ = "shelters"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    name = Column(String(300), nullable=False)
    capacity = Column(Integer, nullable=False)
    available_space = Column(Integer, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    location = Column(Geography(geometry_type="POINT", srid=4326), nullable=True)
    contact_number = Column(String(20), nullable=False)
    address = Column(String(500), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Resource(Base):
    __tablename__ = "resources"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    resource_type = Column(Enum(ResourceType), nullable=False)
    status = Column(Enum(ResourceStatus), nullable=False, default=ResourceStatus.AVAILABLE)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    location = Column(Geography(geometry_type="POINT", srid=4326), nullable=True)
    assigned_incident = Column(UUID(as_uuid=False), ForeignKey("incidents.id"), nullable=True)
    description = Column(String(500), nullable=False)
    contact = Column(String(200), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    assigned_incident_obj = relationship("Incident", back_populates="resources")


class IncidentVote(Base):
    __tablename__ = "incident_votes"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    incident_id = Column(UUID(as_uuid=False), ForeignKey("incidents.id"), nullable=False)
    user_id = Column(UUID(as_uuid=False), ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    incident = relationship("Incident", back_populates="votes")
    user = relationship("User", back_populates="votes")


class IncidentComment(Base):
    __tablename__ = "incident_comments"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    incident_id = Column(UUID(as_uuid=False), ForeignKey("incidents.id"), nullable=False)
    user_id = Column(UUID(as_uuid=False), ForeignKey("users.id"), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    incident = relationship("Incident", back_populates="comments")
    user = relationship("User", back_populates="comments")
