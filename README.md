# Shuttleport Backend API

FastAPI-based backend service for Shuttleport transfer booking system with Excel-based route management.

## 🚀 Features

### Core Functionality
- **Real-time Pricing Calculation** - Dynamic pricing based on distance, duration, and vehicle type
- **Fixed Route Management** - Pre-configured routes with tiered pricing (Vito, Sedan, Sprinter, VIP)
- **Excel-Based Data Management** - Route data stored in Excel for easy editing
- **Two-Way Sync** - Admin panel changes automatically update Excel file

### Admin Panel (SQLAdmin)
- Vehicle management with image upload
- Route management with Excel import/export
- Pricing configuration
- Real-time Excel synchronization

### API Endpoints
- `/api/pricing/calculate` - Calculate transfer price
- `/api/pricing/exchange-rates` - Get currency exchange rates
- `/api/admin/import-excel` - Upload Excel file to update routes
- `/admin` - Admin dashboard

## 📋 Tech Stack

- **Framework**: FastAPI 0.109.0
- **Database**: PostgreSQL with SQLAlchemy 2.0
- **Admin Panel**: SQLAdmin 0.22.0
- **Excel Processing**: Pandas + OpenPyxl
- **Authentication**: JWT with passlib/bcrypt
- **Rate Limiting**: SlowAPI

## 🛠️ Installation

### Prerequisites
- Python 3.11+
- PostgreSQL
- Virtual environment (recommended)

### Setup

1. **Clone & Install**
```bash
git clone <repository-url>
cd Shuttleport_Back
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

2. **Environment Variables**
Create `.env` file:
```env
DATABASE_URL=postgresql://user:password@localhost/shuttleport
GOOGLE_MAPS_API_KEY=your_api_key_here
SECRET_KEY=your_secret_key
```

3. **Database Setup**
```bash
# Run migrations
alembic upgrade head

# Start server
uvicorn main:app --reload --port 8000
```

4. **Access Admin Panel**
Navigate to `http://localhost:8000/admin`

## 📊 Excel Route Management

### File Structure
Routes are stored in `static/istanbul_transfer.xlsx` with columns:
- **ID** - Unique route identifier
- **Origin** - Starting location
- **Destination** - End location
- **Price_Sedan** - Sedan price (auto-calculated: Vito × 0.96)
- **Price_Vito** - Base Vito price
- **Price_VitoVIP** - VIP price (auto-calculated: Vito × 1.25)
- **Price_Sprinter** - Sprinter price (auto-calculated: Vito × 1.95)
- **Active** - Route status (True/False)
- **Discount** - Discount percentage
- **Comp_Price** - Competitor price (for reference)
- **Notes** - Additional notes

### How It Works

1. **Startup**: System loads routes from Excel into database
2. **Admin Changes**: Adding/editing routes in admin panel updates both DB and Excel
3. **Excel Upload**: Import button in Fixed Routes page replaces all routes with uploaded file
4. **No Excel File**: If file doesn't exist, system starts with empty routes

### Excel Import

1. Go to Admin Panel → Fixed Routes
2. Click "Import Excel" button
3. Select `.xlsx` file
4. System automatically syncs database

## 🗂️ Project Structure

```
Shuttleport_Back/
├── app/
│   ├── admin/          # Admin panel configuration
│   ├── api/            # API endpoints
│   ├── core/           # Constants and config
│   ├── models/         # SQLAlchemy models
│   ├── services/       # Business logic & data management
│   └── templates/      # Admin templates
├── static/             # Static files & Excel data
├── alembic/            # Database migrations
├── main.py             # Application entry point
└── requirements.txt    # Dependencies
```

## 🔧 Configuration

### Pricing Logic
- Minimum fare enforced (configured in pricing_config table)
- Tiered pricing by vehicle type
- Distance-based calculation with per-km rates
- Excel file serves as single source of truth for fixed routes

### Vehicle Types
- `vito` - Standard Mercedes Vito (base price)
- `sedan` - Luxury Sedan (96% of Vito price)
- `vito_vip` - VIP Vito (125% of Vito price)
- `sprinter` - Mercedes Sprinter (195% of Vito price)

## 📝 Development

### Running in Development
```bash
uvicorn main:app --reload --port 8000
```

### Database Migrations
```bash
# Create new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head
```

## 🚢 Deployment

### Production Checklist
- [ ] Set `DATABASE_URL` to production PostgreSQL
- [ ] Configure `SECRET_KEY` securely
- [ ] Set up CORS allowed origins
- [ ] Enable HTTPS
- [ ] Configure rate limiting
- [ ] Set up backup for Excel file

## 📄 License

Proprietary - All rights reserved

---

**Last Updated**: January 2026
