"""Seed data for SafeNZ – run this to populate the database with sample data."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.infrastructure.database.base import SessionLocal
from app.models.db_models import User, Incident, Alert, Shelter, Resource
from app.core.entities.models import (
    UserRole, DisasterType, SeverityLevel, IncidentStatus, ResourceType, ResourceStatus
)
from app.core.services.auth_service import hash_password
from geoalchemy2.elements import WKTElement
import uuid


def seed():
    db = SessionLocal()
    try:
        # ─── Users ───
        admin = User(
            id=str(uuid.uuid4()),
            name="Admin User",
            email="admin@safenz.co.nz",
            phone="+6421000001",
            password_hash=hash_password("Admin123!"),
            role=UserRole.ADMIN,
            verified=True,
        )
        responder = User(
            id=str(uuid.uuid4()),
            name="Emergency Responder",
            email="responder@safenz.co.nz",
            phone="+6421000002",
            password_hash=hash_password("Resp123!"),
            role=UserRole.RESPONDER,
            verified=True,
        )
        citizen = User(
            id=str(uuid.uuid4()),
            name="Jane Citizen",
            email="citizen@safenz.co.nz",
            phone="+6421000003",
            password_hash=hash_password("Citizen123!"),
            role=UserRole.CITIZEN,
            verified=True,
        )
        db.add_all([admin, responder, citizen])
        db.flush()

        # ─── Incidents ───
        incident1 = Incident(
            id=str(uuid.uuid4()),
            title="Flooding in Lower Hutt",
            description="Heavy rainfall causing flooding on main roads. Multiple cars stranded.",
            disaster_type=DisasterType.FLOOD,
            severity=SeverityLevel.HIGH,
            latitude=-41.2100,
            longitude=174.9100,
            location=WKTElement("POINT(174.9100 -41.2100)", srid=4326),
            status=IncidentStatus.CONFIRMED,
            reported_by=citizen.id,
            image_urls=[],
        )
        incident2 = Incident(
            id=str(uuid.uuid4()),
            title="Earthquake M5.8 – Christchurch",
            description="Significant earthquake felt across Canterbury. Some building damage reported.",
            disaster_type=DisasterType.EARTHQUAKE,
            severity=SeverityLevel.CRITICAL,
            latitude=-43.5320,
            longitude=172.6360,
            location=WKTElement("POINT(172.6360 -43.5320)", srid=4326),
            status=IncidentStatus.IN_PROGRESS,
            reported_by=citizen.id,
            image_urls=[],
            ai_damage_level="severe",
            ai_confidence=0.87,
        )
        incident3 = Incident(
            id=str(uuid.uuid4()),
            title="Bush Fire – Nelson",
            description="Wildfire spreading near residential area. Evacuation orders issued.",
            disaster_type=DisasterType.FIRE,
            severity=SeverityLevel.CRITICAL,
            latitude=-41.2706,
            longitude=173.2840,
            location=WKTElement("POINT(173.2840 -41.2706)", srid=4326),
            status=IncidentStatus.IN_PROGRESS,
            reported_by=responder.id,
            image_urls=[],
        )
        db.add_all([incident1, incident2, incident3])

        # ─── Alerts ───
        alert1 = Alert(
            id=str(uuid.uuid4()),
            title="Flood Warning – Wellington Region",
            message="Severe flooding expected in low-lying areas. Move to higher ground immediately.",
            region="Wellington",
            severity=SeverityLevel.HIGH,
            created_by=admin.id,
        )
        alert2 = Alert(
            id=str(uuid.uuid4()),
            title="Tsunami Advisory – East Coast",
            message="Tsunami advisory issued. Coastal residents should move inland.",
            region="East Coast",
            severity=SeverityLevel.CRITICAL,
            created_by=admin.id,
        )
        db.add_all([alert1, alert2])

        # ─── Shelters ───
        shelters = [
            Shelter(
                id=str(uuid.uuid4()),
                name="Wellington Community Centre",
                capacity=500,
                available_space=350,
                latitude=-41.2865,
                longitude=174.7762,
                location=WKTElement("POINT(174.7762 -41.2865)", srid=4326),
                contact_number="+6444000001",
                address="100 Willis St, Wellington",
                is_active=True,
            ),
            Shelter(
                id=str(uuid.uuid4()),
                name="Christchurch Arena Evacuation Centre",
                capacity=2000,
                available_space=1200,
                latitude=-43.5309,
                longitude=172.6305,
                location=WKTElement("POINT(172.6305 -43.5309)", srid=4326),
                contact_number="+6433000001",
                address="55 Jack Hinton Dr, Christchurch",
                is_active=True,
            ),
            Shelter(
                id=str(uuid.uuid4()),
                name="Auckland War Memorial Museum Shelter",
                capacity=800,
                available_space=600,
                latitude=-36.8600,
                longitude=174.7762,
                location=WKTElement("POINT(174.7762 -36.8600)", srid=4326),
                contact_number="+6499000001",
                address="The Domain, Auckland",
                is_active=True,
            ),
        ]
        db.add_all(shelters)

        # ─── Resources ───
        resources = [
            Resource(
                id=str(uuid.uuid4()),
                resource_type=ResourceType.AMBULANCE,
                status=ResourceStatus.AVAILABLE,
                latitude=-41.2865,
                longitude=174.7762,
                location=WKTElement("POINT(174.7762 -41.2865)", srid=4326),
                description="Wellington Ambulance Unit 1",
                contact="+6444111001",
            ),
            Resource(
                id=str(uuid.uuid4()),
                resource_type=ResourceType.FIRE_UNIT,
                status=ResourceStatus.ASSIGNED,
                latitude=-41.2706,
                longitude=173.2840,
                location=WKTElement("POINT(173.2840 -41.2706)", srid=4326),
                assigned_incident=str(incident3.id),
                description="Nelson Fire Brigade Unit 3",
                contact="+6435444001",
            ),
            Resource(
                id=str(uuid.uuid4()),
                resource_type=ResourceType.RESCUE_TEAM,
                status=ResourceStatus.AVAILABLE,
                latitude=-43.5320,
                longitude=172.6360,
                location=WKTElement("POINT(172.6360 -43.5320)", srid=4326),
                description="Canterbury Search & Rescue",
                contact="+6433911001",
            ),
        ]
        db.add_all(resources)

        db.commit()
        print("✅ Seed data inserted successfully!")
        print(f"  Users: admin@safenz.co.nz / Admin123!")
        print(f"         responder@safenz.co.nz / Resp123!")
        print(f"         citizen@safenz.co.nz / Citizen123!")

    except Exception as e:
        db.rollback()
        print(f"❌ Seed failed: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()
