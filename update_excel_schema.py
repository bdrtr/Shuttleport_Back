from app.services.data_manager import DataManager

print("Adding new columns (Active, Discount, etc.) to Excel...")
try:
    # Trigger refresh which loads and overwrites with new schema
    DataManager.refresh_calculations()
    print("Done. Headers updated.")
except Exception as e:
    print(f"Error: {e}")
