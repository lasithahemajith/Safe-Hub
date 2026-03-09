# SafeNZ – Disaster Incident Reporting Platform

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

> A production-ready, full-stack disaster reporting platform for New Zealand, built with FastAPI, Next.js, PostgreSQL/PostGIS, Redis, and AI-powered damage detection.

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Quick Start (Docker)](#quick-start-docker)
- [Local Development (Without Docker)](#local-development-without-docker)
- [Environment Variables](#environment-variables)
- [API Documentation](#api-documentation)
- [Seed Data](#seed-data)
- [Running Tests](#running-tests)
- [Deployment](#deployment)

---

## Overview

SafeNZ is a real-time disaster incident reporting and emergency management platform for New Zealand. It allows:

- **Citizens** to report disasters (earthquakes, floods, fires, etc.) with GPS location and photos
- **Emergency Responders** to manage incidents and coordinate resources
- **Government Admins** to broadcast emergency alerts and oversee the platform

---

## Features

| Feature | Description |
|---|---|
| 🗺️ **Live Disaster Map** | Interactive Leaflet map with severity-coloured incident markers |
| 📱 **Incident Reporting** | Report disasters with GPS location, photos, and AI damage analysis |
| ⚠️ **Real-Time Alerts** | WebSocket-based real-time notifications + Email/SMS broadcasting |
| 🏠 **Shelter Finder** | Find nearest emergency shelters with geospatial queries |
| 🚑 **Resource Tracking** | Track ambulances, fire units, and rescue teams |
| 🤖 **AI Damage Detection** | Automatic image analysis for damage severity scoring |
| 👥 **Community Crowdsourcing** | Confirm incidents with votes and comments |
| 🔐 **Role-Based Access** | Citizen, Responder, and Admin roles with JWT auth |
| 🌙 **Dark Mode** | Full dark mode support |
| 📍 **GPS Auto-Detection** | Browser geolocation for automatic location detection |

---

## Architecture

```
SafeNZ/
├── backend/                    # FastAPI backend (Clean Architecture)
│   ├── app/
│   │   ├── api/                # Routes, controllers, WebSocket manager
│   │   ├── core/               # Entities, use cases, services, config
│   │   ├── infrastructure/     # Database, repositories, external services
│   │   ├── models/             # SQLAlchemy ORM models
│   │   ├── schemas/            # Pydantic request/response schemas
│   │   └── main.py
│   ├── migrations/             # Alembic database migrations
│   ├── tests/                  # Pytest test suite
│   └── seed.py                 # Sample data seeder
│
├── frontend/                   # Next.js + TypeScript frontend
│   ├── components/             # Reusable UI components
│   ├── pages/                  # Next.js pages (routing)
│   ├── services/               # API client, WebSocket, data services
│   ├── store/                  # Zustand state management
│   └── styles/                 # TailwindCSS styles
│
├── ai-service/                 # Python AI damage detection microservice
│   ├── models/                 # Damage detector model
│   └── main.py
│
└── docker-compose.yml          # Full stack orchestration
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| **Backend** | Python 3.11, FastAPI, SQLAlchemy 2.0, Alembic |
| **Database** | PostgreSQL 16 + PostGIS (geospatial) |
| **Cache/Queue** | Redis 7 |
| **Frontend** | Next.js 14, React 18, TypeScript, TailwindCSS |
| **Maps** | Leaflet.js |
| **State** | Zustand, TanStack Query |
| **AI** | Python, NumPy, Pillow |
| **Auth** | JWT (python-jose + passlib/bcrypt) |
| **Notifications** | SendGrid (email), Twilio (SMS) |
| **Storage** | AWS S3 |
| **Real-Time** | WebSockets |
| **Container** | Docker, Docker Compose |

---

## Quick Start (Docker)

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/) ≥ 24
- [Docker Compose](https://docs.docker.com/compose/) ≥ 2.20

### Steps

```bash
# 1. Clone the repository
git clone https://github.com/lasithahemajith/Safe-Hub.git
cd Safe-Hub

# 2. Copy environment files
cp .env.example .env
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env.local

# 3. Build and start all services
docker compose up --build

# 4. In a separate terminal, run database migrations + seed data
docker compose exec backend alembic upgrade head
docker compose exec backend python seed.py
```

### Access the platform

| Service | URL |
|---|---|
| **Frontend** | http://localhost:3000 |
| **Backend API** | http://localhost:8000 |
| **API Docs (Swagger)** | http://localhost:8000/docs |
| **API Docs (ReDoc)** | http://localhost:8000/redoc |
| **AI Service** | http://localhost:8001 |

### Default Users (after seeding)

| Role | Email | Password |
|---|---|---|
| Admin | admin@safenz.co.nz | Admin123! |
| Responder | responder@safenz.co.nz | Resp123! |
| Citizen | citizen@safenz.co.nz | Citizen123! |

---

## Local Development (Without Docker)

### Backend

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy and configure environment
cp .env.example .env
# Edit .env with your PostgreSQL and Redis connection strings

# Run database migrations
alembic upgrade head

# Seed sample data
python seed.py

# Start the development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### AI Service

```bash
cd ai-service

pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8001
```

### Frontend

```bash
cd frontend

npm install

# Copy and configure environment
cp .env.example .env.local
# Edit .env.local if your backend is not at localhost:8000

npm run dev
```

---

## Environment Variables

### Backend (`backend/.env`)

| Variable | Description | Default |
|---|---|---|
| `SECRET_KEY` | JWT signing key (MUST change in production) | — |
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://safenz:safenz_password@localhost:5432/safenz_db` |
| `REDIS_URL` | Redis connection string | `redis://localhost:6379/0` |
| `AWS_ACCESS_KEY_ID` | AWS credentials for S3 | *(optional)* |
| `AWS_SECRET_ACCESS_KEY` | AWS secret key | *(optional)* |
| `AWS_S3_BUCKET` | S3 bucket name for images | `safenz-images` |
| `SENDGRID_API_KEY` | SendGrid API key for emails | *(optional, mocked if missing)* |
| `TWILIO_ACCOUNT_SID` | Twilio SID for SMS | *(optional, mocked if missing)* |
| `TWILIO_AUTH_TOKEN` | Twilio auth token | *(optional)* |
| `TWILIO_FROM_NUMBER` | Twilio sender number | *(optional)* |

### Frontend (`frontend/.env.local`)

| Variable | Description | Default |
|---|---|---|
| `NEXT_PUBLIC_API_URL` | Backend API base URL | `http://localhost:8000` |
| `NEXT_PUBLIC_WS_URL` | WebSocket server URL | `ws://localhost:8000` |

---

## API Documentation

The full interactive API documentation is available at:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Key Endpoints

#### Authentication
```
POST /api/v1/auth/register        Register a new user
POST /api/v1/auth/login           Login and get JWT tokens
POST /api/v1/auth/refresh         Refresh access token
POST /api/v1/auth/reset-password/request  Request password reset
GET  /api/v1/auth/me              Get current user profile
```

#### Incidents
```
GET  /api/v1/incidents            List incidents (paginated, filterable)
POST /api/v1/incidents            Create incident (auth required)
GET  /api/v1/incidents/nearby     Get incidents within radius
GET  /api/v1/incidents/{id}       Get incident details
PUT  /api/v1/incidents/{id}       Update incident
POST /api/v1/incidents/{id}/images  Upload incident photos
POST /api/v1/incidents/{id}/vote  Confirm/vote incident
POST /api/v1/incidents/{id}/comments  Add comment
GET  /api/v1/incidents/{id}/comments  List comments
```

#### Alerts
```
GET  /api/v1/alerts               List alerts (paginated)
POST /api/v1/alerts               Create alert (admin/responder only)
GET  /api/v1/alerts/{id}          Get alert details
```

#### Shelters
```
GET  /api/v1/shelters             List all shelters
GET  /api/v1/shelters/nearby      Find shelters within radius
GET  /api/v1/shelters/{id}        Get shelter details
PATCH /api/v1/shelters/{id}       Update shelter availability
```

#### Resources
```
GET  /api/v1/resources            List resources (auth required)
POST /api/v1/resources            Create resource (admin/responder)
GET  /api/v1/resources/{id}       Get resource
PATCH /api/v1/resources/{id}      Update resource
```

#### WebSocket
```
WS   /ws?token={jwt}              Real-time event stream
```

WebSocket message types:
```json
{ "type": "NEW_INCIDENT", "data": {...} }
{ "type": "INCIDENT_UPDATED", "data": {...} }
{ "type": "NEW_ALERT", "data": {...} }
{ "type": "CONNECTED", "data": { "client_id": "..." } }
```

---

## Seed Data

```bash
# Run seed data (after migrations)
cd backend
python seed.py

# Or with Docker
docker compose exec backend python seed.py
```

This creates:
- 3 users (admin, responder, citizen)
- 3 incidents (flood, earthquake, fire)
- 2 emergency alerts
- 3 shelters across NZ
- 3 resources (ambulance, fire unit, rescue team)

---

## Running Tests

### Backend

```bash
cd backend
pip install -r requirements.txt
pytest tests/ -v --tb=short
```

### Frontend

```bash
cd frontend
npm install
npm test
```

### With Docker

```bash
docker compose exec backend pytest tests/ -v
```

---

## Deployment

### AWS Deployment

1. **Database**: Use Amazon RDS for PostgreSQL with PostGIS extension
2. **Cache**: Use Amazon ElastiCache (Redis)
3. **Container Registry**: Push images to Amazon ECR
4. **Compute**: Deploy with Amazon ECS Fargate or EKS
5. **Load Balancer**: Use ALB with SSL termination
6. **Storage**: AWS S3 for images (already configured)
7. **Email**: AWS SES (or SendGrid)
8. **SMS**: AWS SNS (or Twilio)
9. **Monitoring**: CloudWatch + optional Prometheus/Grafana

### Production Checklist

- [ ] Set a strong `SECRET_KEY` (min 64 random characters)
- [ ] Set `ENVIRONMENT=production`
- [ ] Configure actual AWS credentials
- [ ] Set up SSL/TLS certificates
- [ ] Configure proper CORS origins
- [ ] Set up database backups
- [ ] Configure rate limiting
- [ ] Enable CloudWatch logging

---

## License

MIT – see [LICENSE](LICENSE)

---

*Built with ❤️ for New Zealand emergency preparedness*
