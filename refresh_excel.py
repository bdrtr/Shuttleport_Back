from app.services.data_manager import DataManager

print("Refreshing Excel calculations...")
try:
    DataManager.refresh_calculations()
    print("Done.")
except Exception as e:
    print(f"Error: {e}")
