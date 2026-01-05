from app.services.data_manager import DataManager

print("Refreshing calculations to trigger ID backfill...")
DataManager.refresh_calculations()
print("Done. Check Excel file for IDs.")
