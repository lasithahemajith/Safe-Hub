from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional, List
import uuid


class UserRole(str, Enum):
    CITIZEN = "citizen"
    RESPONDER = "responder"
    ADMIN = "admin"


class DisasterType(str, Enum):
    EARTHQUAKE = "earthquake"
    FLOOD = "flood"
    LANDSLIDE = "landslide"
    STORM = "storm"
    FIRE = "fire"
    OTHER = "other"


class SeverityLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class IncidentStatus(str, Enum):
    REPORTED = "reported"
    CONFIRMED = "confirmed"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"


class ResourceType(str, Enum):
    AMBULANCE = "ambulance"
    RESCUE_TEAM = "rescue_team"
    FIRE_UNIT = "fire_unit"
    POLICE = "police"
    MEDICAL = "medical"
    OTHER = "other"


class ResourceStatus(str, Enum):
    AVAILABLE = "available"
    ASSIGNED = "assigned"
    UNAVAILABLE = "unavailable"


@dataclass
class UserEntity:
    id: str
    name: str
    email: str
    phone: Optional[str]
    password_hash: str
    role: UserRole
    verified: bool
    created_at: datetime
    updated_at: datetime


@dataclass
class IncidentEntity:
    id: str
    title: str
    description: str
    disaster_type: DisasterType
    severity: SeverityLevel
    latitude: float
    longitude: float
    status: IncidentStatus
    reported_by: str
    created_at: datetime
    updated_at: datetime
    image_urls: List[str] = field(default_factory=list)
    ai_damage_level: Optional[str] = None
    ai_confidence: Optional[float] = None
    vote_count: int = 0


@dataclass
class AlertEntity:
    id: str
    title: str
    message: str
    region: str
    severity: SeverityLevel
    created_by: str
    created_at: datetime


@dataclass
class ShelterEntity:
    id: str
    name: str
    capacity: int
    available_space: int
    latitude: float
    longitude: float
    contact_number: str
    address: str
    is_active: bool


@dataclass
class ResourceEntity:
    id: str
    resource_type: ResourceType
    status: ResourceStatus
    latitude: float
    longitude: float
    assigned_incident: Optional[str]
    description: str
    contact: str
