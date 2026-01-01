# Shuttleport Backend

FastAPI backend for the Shuttleport transfer booking platform.

## Project Structure

```
app/
├── __init__.py
├── main.py                 # FastAPI app initialization
├── api/                    # API layer
│   ├── v1/                # API version 1
│   │   ├── router.py      # Main API router
│   │   └── endpoints/     # Endpoint modules
│   │       ├── health.py
│   │       └── maps.py
├── core/                   # Core configurations
│   ├── config.py          # Settings (Pydantic)
│   ├── security.py        # Auth & security
│   └── exceptions.py      # Custom exceptions
├── models/                 # Database models (future)
├── schemas/                # Request/Response schemas
│   └── maps.py
├── services/               # Business logic
│   └── maps_service.py
├── repositories/           # Data access (future)
├── middleware/             # Custom middleware
│   └── logging.py
└── utils/                  # Utilities
    └── google_maps.py
```

## Architecture

### Layered Architecture

The backend follows a clean layered architecture:

1. **API Layer** (`app/api/`): HTTP endpoints and request handling
2. **Service Layer** (`app/services/`): Business logic and orchestration
3. **Utils Layer** (`app/utils/`): External API clients and helpers
4. **Repository Layer** (`app/repositories/`): Data access (future DB integration)

### Request Flow

```
Request → Endpoint → Service → Utils/Repository → Response
         (API)      (Business) (Data/External)
```

## Getting Started

### Prerequisites

- Python 3.9+
- pip

### Installation

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Environment Setup

Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

Update the environment variables:

```env
GOOGLE_MAPS_API_KEY=your_api_key_here
CORS_ORIGINS=http://localhost:3000
```

### Development

```bash
# Run development server
uvicorn app.main:app --reload --port 8000
```

API documentation available at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Testing

```bash
# Install dev dependencies
pip install -r requirements-dev.txt

# Run tests
pytest tests/ -v
```

## Adding New Features

### 1. Create Schema

Define request/response models in `app/schemas/`:

```python
# app/schemas/booking.py
from pydantic import BaseModel

class BookingRequest(BaseModel):
    customer_name: str
    # ... other fields
```

### 2. Create Service

Implement business logic in `app/services/`:

```python
# app/services/booking_service.py
class BookingService:
    async def create_booking(self, request: BookingRequest):
        # Business logic here
        pass
```

### 3. Create Endpoint

Add API endpoint in `app/api/v1/endpoints/`:

```python
# app/api/v1/endpoints/booking.py
from fastapi import APIRouter
from app.services.booking_service import booking_service

router = APIRouter()

@router.post("/bookings")
async def create_booking(request: BookingRequest):
    return await booking_service.create_booking(request)
```

### 4. Register Router

Add to main API router in `app/api/v1/router.py`:

```python
from app.api.v1.endpoints import booking

api_router.include_router(booking.router, tags=["booking"])
```

## Configuration

All configuration is managed through `app/core/config.py` using Pydantic Settings:

```python
from app.core.config import settings

# Access configuration
api_key = settings.GOOGLE_MAPS_API_KEY
debug_mode = settings.DEBUG
```

## Error Handling

Custom exceptions are defined in `app/core/exceptions.py`:

```python
from app.core.exceptions import GoogleMapsAPIError

raise GoogleMapsAPIError("API call failed", details={"code": 500})
```

## API Versioning

The API is versioned with the `/api/v1` prefix. Future versions can be added by creating new version modules under `app/api/`.

## Available Scripts

- Development: `uvicorn app.main:app --reload`
- Production: `uvicorn app.main:app --host 0.0.0.0 --port 8000`
- Tests: `pytest tests/ -v`
