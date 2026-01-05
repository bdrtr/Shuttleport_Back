import asyncio
import httpx
from app.database import SessionLocal
from app.models.db_models import Vehicle, PricingConfig

async def verify_system():
    print("🔬 Starting System Verification...\n")
    
    # 1. Database Data Verification
    print("1️⃣  Verifying Database Content...")
    db = SessionLocal()
    try:
        vehicles = db.query(Vehicle).all()
        print(f"   - Vehicles Found: {len(vehicles)}")
        for v in vehicles:
            print(f"     * {v.name_en} ({v.vehicle_type})")
            
        configs = db.query(PricingConfig).all()
        print(f"   - Pricing Configs Found: {len(configs)}")
        min_fare = db.query(PricingConfig).filter(PricingConfig.config_key == "minimum_fare").first()
        if min_fare and float(min_fare.config_value) == 1200.0:
            print("     ✅ Minimum Fare is set to 1200.00 TL")
        else:
            print(f"     ❌ Minimum Fare check failed! Value: {min_fare.config_value if min_fare else 'None'}")
            
    finally:
        db.close()

    # 2. Endpoint Verification (Admin & API)
    print("\n2️⃣  Verifying API Endpoints...")
    async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
        # Check Admin Panel
        try:
            resp = await client.get("/admin/vehicle/list")
            if resp.status_code == 200:
                print("   ✅ Admin Panel (/admin/vehicle/list) is accessible (200 OK)")
            else:
                print(f"   ❌ Admin Panel Failed: {resp.status_code}")
        except Exception as e:
            print(f"   ❌ Could not connect to Admin Panel: {e}")

        # Check Price Calculation (Minimum Fare Logic)
        # 1 KM distance should be cheap, but floor should be 1200
        payload = {
            "origin_lat": 41.0, "origin_lng": 28.9, "origin_name": "Test A",
            "destination_lat": 41.01, "destination_lng": 28.91, "destination_name": "Test B",
            "distance_km": 1.0,
            "duration_minutes": 5,
            "passenger_count": 1
        }
        try:
            resp = await client.post("/api/pricing/calculate", json=payload)
            if resp.status_code == 200:
                data = resp.json()
                vito_price = next((v['final_price'] for v in data['vehicles'] if v['vehicle_type'] == 'vito'), 0)
                
                print(f"   - API Calculation Test (1 KM):")
                if vito_price >= 1200:
                    print(f"     ✅ Minimum Fare Applied! Price: {vito_price} TL (>= 1200)")
                else:
                    print(f"     ❌ Minimum Fare Failed! Price: {vito_price} TL")
            else:
                 # If 500/400, print detail
                print(f"   ❌ Pricing API Error: {resp.status_code} - {resp.text}")
        except Exception as e:
            print(f"   ❌ Could not connect to Pricing API: {e}")

if __name__ == "__main__":
    asyncio.run(verify_system())
