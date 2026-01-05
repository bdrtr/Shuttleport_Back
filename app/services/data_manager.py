import pandas as pd
import os
from typing import List, Dict, Optional

FILE_PATH = "static/istanbul_transfer.xlsx"

class DataManager:
    @staticmethod
    def ensure_file_exists():
        """Create file with headers if not exists"""
        if not os.path.exists(FILE_PATH):
            df = pd.DataFrame(columns=["Origin", "Destination", "Price_Sedan", "Price_Vito", "Price_VitoVIP", "Price_Sprinter"])
            # Ensure directory exists
            os.makedirs(os.path.dirname(FILE_PATH), exist_ok=True)
            df.to_excel(FILE_PATH, index=False)
            print(f"Created new data file at {FILE_PATH}")

    @staticmethod
    def load_routes() -> List[Dict]:
        """
        Load routes from Excel.
        Assumes standard format we enforce OR tries to parse the legacy format.
        """
        if not os.path.exists(FILE_PATH):
            return []

        try:
            df = pd.read_excel(FILE_PATH)
            
            routes = []
            
            # Check if it's our clean format
            if "Price_Vito" in df.columns:
                for _, row in df.iterrows():
                    if pd.notna(row["Origin"]) and pd.notna(row["Destination"]):
                        routes.append({
                            "origin": str(row["Origin"]).strip(),
                            "destination": str(row["Destination"]).strip(),
                            "price_vito": float(row["Price_Vito"]),
                            # Load others if needed, but we mostly use Vito as base for logic
                            "price_sedan": float(row["Price_Sedan"]) if "Price_Sedan" in df.columns and pd.notna(row["Price_Sedan"]) else None,
                            "price_sprinter": float(row["Price_Sprinter"]) if "Price_Sprinter" in df.columns and pd.notna(row["Price_Sprinter"]) else None
                        })
                return routes

            # Fallback to Legacy Parsing (Unstructured)
            df = pd.read_excel(FILE_PATH, header=None)
            for idx, row in df.iloc[4:].iterrows():
                if len(row) > 4 and pd.notna(row[2]) and pd.notna(row[3]) and pd.notna(row[4]):
                    try:
                        price = float(str(row[4]).replace("₺", "").replace(".", "").strip())
                        if price < 100: continue 
                        routes.append({
                            "origin": str(row[2]).strip(),
                            "destination": str(row[3]).strip(),
                            "price_vito": price
                        })
                    except ValueError:
                        continue
            return routes

        except Exception as e:
            print(f"Error loading routes from Excel: {e}")
            return []

    @staticmethod
    def save_route(origin: str, dest: str, price_vito: float, price_sprinter: Optional[float] = None):
        """Append or update a route and save to file with calculated fields"""
        DataManager.ensure_file_exists()
        
        current_routes = DataManager.load_routes()
        
        # Check duplicate/update
        found = False
        for r in current_routes:
            if r["origin"] == origin and r["destination"] == dest:
                r["price_vito"] = price_vito
                # We don't manually set others, we recalc them below
                found = True
                break
        
        if not found:
            current_routes.append({
                "origin": origin,
                "destination": dest,
                "price_vito": price_vito
            })
            
        # Convert back to DF with Formulas
        output_data = []
        for r in current_routes:
            base_price = r["price_vito"]
            
            # Pricing Formulas
            # Sedan (Standard): ~96% of Vito
            # Vito VIP: ~125% of Vito
            # Sprinter: ~195% of Vito
            
            output_data.append({
                "Origin": r["origin"],
                "Destination": r["destination"],
                "Price_Sedan": int(base_price * 0.96),
                "Price_Vito": base_price,
                "Price_VitoVIP": int(base_price * 1.25),
                "Price_Sprinter": int(base_price * 1.95)
            })
            
        df_out = pd.DataFrame(output_data)
        df_out.to_excel(FILE_PATH, index=False)
        print(f"Saved/Updated route {origin}->{dest} to {FILE_PATH} with calculated prices.")

    @staticmethod
    def refresh_calculations():
        """Force recalculation of all rows in the file"""
        routes = DataManager.load_routes()
        if not routes:
            return
            
        # Just saving the first one triggers the full rewrite with new headers/formulas
        # But we need to pass the list. save_route logic handles the list.
        # Calling save_route with an existing route updates it and rewrites file.
        r = routes[0]
        DataManager.save_route(r["origin"], r["destination"], r["price_vito"])


