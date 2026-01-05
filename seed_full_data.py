from app.services.data_manager import DataManager
from app.core.constants import ISTANBUL_LOCATIONS

print("Seeding full dataset to Excel...")

# Standard Location References
loc_ist = ISTANBUL_LOCATIONS[0][0]
loc_saw = ISTANBUL_LOCATIONS[1][0]
loc_sultanahmet = ISTANBUL_LOCATIONS[2][0]
loc_taksim = ISTANBUL_LOCATIONS[3][0]
loc_besiktas = ISTANBUL_LOCATIONS[4][0]
loc_kadikoy = ISTANBUL_LOCATIONS[5][0]

routes = [
    # IST
    {"origin": loc_ist, "destination": loc_sultanahmet, "price": 1764},
    {"origin": loc_ist, "destination": loc_taksim, "price": 1619},
    {"origin": loc_ist, "destination": loc_besiktas, "price": 1690},
    {"origin": loc_ist, "destination": loc_kadikoy, "price": 2050},
    
    # SAW
    {"origin": loc_saw, "destination": loc_sultanahmet, "price": 1900},
    {"origin": loc_saw, "destination": loc_taksim, "price": 1830},
]

for r in routes:
    print(f"Adding/Updating: {r['origin']} -> {r['destination']}")
    DataManager.save_route(r["origin"], r["destination"], r["price"])

print("Done. Please check the Excel file.")
