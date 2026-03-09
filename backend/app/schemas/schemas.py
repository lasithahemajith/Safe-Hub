from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, field_validator, model_validator
from app.core.entities.models import UserRole, DisasterType, SeverityLevel, IncidentStatus, ResourceType, ResourceStatus


# ─────────────────────────── Auth ───────────────────────────

class UserRegister(BaseModel):
    name: str
    email: EmailStr
    phone: Optional[str] = None
    password: str
    role: UserRole = UserRole.CITIZEN

    @field_validator("password")
    @classmethod
    def password_strength(cls, v):
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        return v


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: str
    name: str
    email: str
    phone: Optional[str]
    role: UserRole
    verified: bool
    created_at: datetime

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserResponse


class PasswordResetRequest(BaseModel):
    email: EmailStr


class PasswordReset(BaseModel):
    token: str
    new_password: str

    @field_validator("new_password")
    @classmethod
    def password_strength(cls, v):
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        return v


# ─────────────────────────── Incidents ───────────────────────────

class IncidentCreate(BaseModel):
    title: str
    description: str
    disaster_type: DisasterType
    severity: SeverityLevel = SeverityLevel.MEDIUM
    latitude: float
    longitude: float

    @field_validator("latitude")
    @classmethod
    def validate_lat(cls, v):
        if not (-90 <= v <= 90):
            raise ValueError("Latitude must be between -90 and 90")
        return v

    @field_validator("longitude")
    @classmethod
    def validate_lon(cls, v):
        if not (-180 <= v <= 180):
            raise ValueError("Longitude must be between -180 and 180")
        return v


class IncidentUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    severity: Optional[SeverityLevel] = None
    status: Optional[IncidentStatus] = None


class IncidentResponse(BaseModel):
    id: str
    title: str
    description: str
    disaster_type: DisasterType
    severity: SeverityLevel
    latitude: float
    longitude: float
    status: IncidentStatus
    reported_by: str
    image_urls: List[str] = []
    ai_damage_level: Optional[str] = None
    ai_confidence: Optional[float] = None
    vote_count: int = 0
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ─────────────────────────── Alerts ───────────────────────────

class AlertCreate(BaseModel):
    title: str
    message: str
    region: str
    severity: SeverityLevel


class AlertResponse(BaseModel):
    id: str
    title: str
    message: str
    region: str
    severity: SeverityLevel
    created_by: str
    created_at: datetime

    class Config:
        from_attributes = True


# ─────────────────────────── Shelters ───────────────────────────

class ShelterCreate(BaseModel):
    name: str
    capacity: int
    available_space: int
    latitude: float
    longitude: float
    contact_number: str
    address: str


class ShelterResponse(BaseModel):
    id: str
    name: str
    capacity: int
    available_space: int
    latitude: float
    longitude: float
    contact_number: str
    address: str
    is_active: bool
    distance_km: Optional[float] = None

    class Config:
        from_attributes = True


class ShelterUpdate(BaseModel):
    available_space: Optional[int] = None
    is_active: Optional[bool] = None


# ─────────────────────────── Resources ───────────────────────────

class ResourceCreate(BaseModel):
    resource_type: ResourceType
    latitude: float
    longitude: float
    description: str
    contact: str


class ResourceResponse(BaseModel):
    id: str
    resource_type: ResourceType
    status: ResourceStatus
    latitude: float
    longitude: float
    assigned_incident: Optional[str]
    description: str
    contact: str

    class Config:
        from_attributes = True


class ResourceUpdate(BaseModel):
    status: Optional[ResourceStatus] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    assigned_incident: Optional[str] = None


# ─────────────────────────── Community ───────────────────────────

class CommentCreate(BaseModel):
    content: str


class CommentResponse(BaseModel):
    id: str
    incident_id: str
    user_id: str
    content: str
    created_at: datetime

    class Config:
        from_attributes = True


# ─────────────────────────── WebSocket ───────────────────────────

class WSMessage(BaseModel):
    type: str
    data: dict


# ─────────────────────────── Pagination ───────────────────────────

class PaginatedResponse(BaseModel):
    items: list
    total: int
    page: int
    per_page: int
    pages: int
