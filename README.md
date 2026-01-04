# Shuttleport Backend API

Modern transfer booking platform - FastAPI backend with PostgreSQL database

## 🚀 Features

- **Multi-image uploads** per vehicle with primary selection
- **Template route system** for 60+ popular destinations  
- **Dynamic pricing** with minimum fare enforcement (1200₺)
- **Admin panel** with SQLAdmin (thumbnails, formatted tables)
- **Database migrations** with Alembic
- **RESTful API** with automatic documentation

## 📁 Project Structure

```
shuttleport_backend/
├── app/
│   ├── admin/              # Admin panel (SQLAdmin)
│   │   ├── admin_panel.py  # Admin views
│   │   └── utils.py        # Custom fields
│   ├── api/                # API endpoints
│   │   ├── pricing.py      # Pricing calculations
│   │   └── exchange_rates.py
│   ├── models/             # Database models
│   │   ├── db_models.py    # SQLAlchemy models
│   │   └── pricing.py      # Pricing logic
│   └── database.py         # Database config
├── alembic/                # Database migrations
│   └── versions/           # Migration files
├── scripts/                # Utility scripts
│   └── create_template_routes.py
├── static/
│   └── images/             # Uploaded vehicle images
└── main.py                 # FastAPI app
```

## 🗄️ Database Schema

4 main tables:
- **vehicles** - Vehicle types (Vito, Sprinter, Luxury Sedan)
- **vehicle_images** - Multi-image support with primary flag
- **fixed_routes** - Pre-priced popular routes
- **pricing_config** - Global pricing settings

View `database_schema.drawio` for full ER diagram.

## 🛠️ Setup

### Prerequisites
- Python 3.9+
- PostgreSQL
- Node.js (for frontend)

### Installation

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup environment
cp .env.example .env
# Edit .env with your DATABASE_URL
```

### Database Setup

```bash
# Run migrations
alembic upgrade head

# (Optional) Create template routes
python scripts/create_template_routes.py --all
```

### Run Development Server

```bash
# Backend
uvicorn main:app --reload --port 8000

# Admin panel: http://localhost:8000/admin
# API docs: http://localhost:8000/docs
```

## 🎨 Admin Panel

Access at `/admin` with features:
- **Vehicle management** with image gallery
- **Multi-image upload** (Ctrl+Click)
- **Fixed routes** with formatted tables
- **Pricing configuration**

## 🚗 Template Routes

Generate routes for all vehicles:

```bash
# Preview
python scripts/create_template_routes.py --all --dry-run

# Create
python scripts/create_template_routes.py --all

# Single vehicle
python scripts/create_template_routes.py --vehicle vito
```

Creates 60+ routes:
- Istanbul Airport → 10 destinations
- Sabiha Gökçen Airport → 10 destinations
- For all 3 vehicle types

## 💰 Pricing

### Minimum Fare
All trips: **1200₺ minimum**

### Dynamic Pricing Formula
```
price = max(
    base_fare + (distance_km × per_km_rate) + airport_fee,
    minimum_fare
)
```

### Fixed Routes
Pre-priced routes override dynamic calculation.

## 📊 API Endpoints

### Pricing
- `POST /api/pricing/calculate` - Calculate trip price
- `GET /api/pricing/vehicles` - List vehicles
- `GET /api/pricing/fixed-routes` - Get fixed routes

### Example Request
```bash
curl -X POST http://localhost:8000/api/pricing/calculate \
  -H "Content-Type: application/json" \
  -d '{
    "origin_lat": 41.0082,
    "origin_lng": 28.8784,
    "origin_name": "Avcılar",
    "destination_lat": 40.9925,
    "destination_lng": 28.8853,
    "destination_name": "Küçükçekmece",
    "distance_km": 7,
    "passenger_count": 1
  }'
```

## 🔧 Database Migrations

```bash
# Create new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

## 📝 Recent Updates

- ✅ Multi-image upload with primary selection
- ✅ Template route generation system
- ✅ 1200₺ minimum fare enforcement
- ✅ Admin UI improvements (thumbnails, tables)
- ✅ Database schema diagram

## 🤝 Contributing

1. Create feature branch
2. Make changes
3. Test thoroughly
4. Submit PR

## 📄 License

MIT
