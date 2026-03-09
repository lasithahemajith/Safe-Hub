"""Initial SafeNZ schema

Revision ID: 0001_initial
Revises: 
Create Date: 2024-01-01 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '0001_initial'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Enable PostGIS
    op.execute("CREATE EXTENSION IF NOT EXISTS postgis")

    # Users table
    op.create_table(
        'users',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('email', sa.String(255), unique=True, nullable=False),
        sa.Column('phone', sa.String(20), nullable=True),
        sa.Column('password_hash', sa.String(255), nullable=False),
        sa.Column('role', sa.String(20), nullable=False, server_default='citizen'),
        sa.Column('verified', sa.Boolean, server_default='false'),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now()),
    )
    op.create_index('ix_users_email', 'users', ['email'])

    # Incidents table
    op.create_table(
        'incidents',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('title', sa.String(500), nullable=False),
        sa.Column('description', sa.Text, nullable=False),
        sa.Column('disaster_type', sa.String(20), nullable=False),
        sa.Column('severity', sa.String(20), nullable=False),
        sa.Column('latitude', sa.Float, nullable=False),
        sa.Column('longitude', sa.Float, nullable=False),
        sa.Column('location', sa.Text, nullable=True),
        sa.Column('status', sa.String(20), nullable=False, server_default='reported'),
        sa.Column('reported_by', sa.String(36), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('image_urls', postgresql.JSON, nullable=True),
        sa.Column('ai_damage_level', sa.String(50), nullable=True),
        sa.Column('ai_confidence', sa.Float, nullable=True),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now()),
    )
    op.create_index('ix_incidents_created_at', 'incidents', ['created_at'])

    # Alerts table
    op.create_table(
        'alerts',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('title', sa.String(500), nullable=False),
        sa.Column('message', sa.Text, nullable=False),
        sa.Column('region', sa.String(200), nullable=False),
        sa.Column('severity', sa.String(20), nullable=False),
        sa.Column('created_by', sa.String(36), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
    )

    # Shelters table
    op.create_table(
        'shelters',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('name', sa.String(300), nullable=False),
        sa.Column('capacity', sa.Integer, nullable=False),
        sa.Column('available_space', sa.Integer, nullable=False),
        sa.Column('latitude', sa.Float, nullable=False),
        sa.Column('longitude', sa.Float, nullable=False),
        sa.Column('location', sa.Text, nullable=True),
        sa.Column('contact_number', sa.String(20), nullable=False),
        sa.Column('address', sa.String(500), nullable=False),
        sa.Column('is_active', sa.Boolean, server_default='true'),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now()),
    )

    # Resources table
    op.create_table(
        'resources',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('resource_type', sa.String(30), nullable=False),
        sa.Column('status', sa.String(20), nullable=False, server_default='available'),
        sa.Column('latitude', sa.Float, nullable=False),
        sa.Column('longitude', sa.Float, nullable=False),
        sa.Column('location', sa.Text, nullable=True),
        sa.Column('assigned_incident', sa.String(36), sa.ForeignKey('incidents.id'), nullable=True),
        sa.Column('description', sa.String(500), nullable=False),
        sa.Column('contact', sa.String(200), nullable=False),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now()),
    )

    # Incident votes
    op.create_table(
        'incident_votes',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('incident_id', sa.String(36), sa.ForeignKey('incidents.id'), nullable=False),
        sa.Column('user_id', sa.String(36), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
    )

    # Incident comments
    op.create_table(
        'incident_comments',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('incident_id', sa.String(36), sa.ForeignKey('incidents.id'), nullable=False),
        sa.Column('user_id', sa.String(36), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('content', sa.Text, nullable=False),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now()),
    )


def downgrade():
    op.drop_table('incident_comments')
    op.drop_table('incident_votes')
    op.drop_table('resources')
    op.drop_table('shelters')
    op.drop_table('alerts')
    op.drop_table('incidents')
    op.drop_table('users')
