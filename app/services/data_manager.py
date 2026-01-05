import pandas as pd
import os
from typing import List, Dict

FILE_PATH = "static/istanbul_transfer.xlsx"

class DataManager:
    @staticmethod
    def ensure_file_exists():
        """Create file with headers if not exists"""
        if not os.path.exists(FILE_PATH):
            cols = ["ID", "Origin", "Destination", 
                    "Price_Sedan", "Price_Vito", "Price_VitoVIP", "Price_Sprinter",
                    "Active", "Discount", "Comp_Price", "Notes"]
            
            df = pd.DataFrame(columns=cols)
            # Ensure directory exists
            os.makedirs(os.path.dirname(FILE_PATH), exist_ok=True)
            df.to_excel(FILE_PATH, index=False)
            print(f"Created new data file at {FILE_PATH}")

    @staticmethod
    def load_routes() -> List[Dict]:
        """
        Load routes from Excel.
        """
        if not os.path.exists(FILE_PATH):
            return []

        try:
            df = pd.read_excel(FILE_PATH)
            routes = []
            
            if "Price_Vito" in df.columns:
                for _, row in df.iterrows():
                    if pd.notna(row["Origin"]) and pd.notna(row["Destination"]):
                        # Parse ID if exists
                        route_id = int(row["ID"]) if "ID" in df.columns and pd.notna(row["ID"]) else None

                        routes.append({
                            "id": route_id,
                            "origin": str(row["Origin"]).strip(),
                            "destination": str(row["Destination"]).strip(),
                            "price_vito": float(row["Price_Vito"]),
                            
                            # Prices
                            "price_sedan": float(row["Price_Sedan"]) if "Price_Sedan" in df.columns and pd.notna(row["Price_Sedan"]) else None,
                            "price_sprinter": float(row["Price_Sprinter"]) if "Price_Sprinter" in df.columns and pd.notna(row["Price_Sprinter"]) else None,
                            "price_vitovip": float(row["Price_VitoVIP"]) if "Price_VitoVIP" in df.columns and pd.notna(row["Price_VitoVIP"]) else None,
                            
                            # Extra Parameters
                            "active": bool(row["Active"]) if "Active" in df.columns and pd.notna(row["Active"]) else True,
                            "discount": float(row["Discount"]) if "Discount" in df.columns and pd.notna(row["Discount"]) else 0,
                            "comp_price": float(row["Comp_Price"]) if "Comp_Price" in df.columns and pd.notna(row["Comp_Price"]) else None,
                            "notes": str(row["Notes"]) if "Notes" in df.columns and pd.notna(row["Notes"]) else ""
                        })
                return routes
            
            return []

        except (FileNotFoundError, pd.errors.EmptyDataError, pd.errors.ParserError) as e:
            print(f"Error loading routes from Excel: {e}")
            return []
        except Exception as e:
            print(f"Unexpected error loading routes: {e}")
            return []
