import pandas as pd
import os
from typing import List, Dict, Optional

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

        except Exception as e:
            print(f"Error loading routes from Excel: {e}")
            return []

    @staticmethod
    def save_route(origin: str, dest: str, price_vito: float, 
                   active: bool = True, discount: float = 0, comp_price: Optional[float] = None, notes: str = ""):
        """Append or update a route and save to file with calculated fields"""
        DataManager.ensure_file_exists()
        
        current_routes = DataManager.load_routes()
        
        # Determine Max ID
        existing_ids = [r["id"] for r in current_routes if r.get("id") is not None]
        next_id = max(existing_ids) + 1 if existing_ids else 1
        
        # Check duplicate/update
        found = False
        target_route = None
        for r in current_routes:
            if r["origin"] == origin and r["destination"] == dest:
                r["price_vito"] = price_vito
                # Update other fields if explicitly passed? 
                # For now, we overwrite if we are calling save_route programmatically.
                # If reading from Excel, we use load_routes.
                r["active"] = active
                r["discount"] = discount
                r["comp_price"] = comp_price
                r["notes"] = notes
                
                target_route = r
                found = True
                break
        
        if found:
            if target_route.get("id") is None:
                target_route["id"] = next_id
        else:
            current_routes.append({
                "id": next_id,
                "origin": origin,
                "destination": dest,
                "price_vito": price_vito,
                "active": active,
                "discount": discount,
                "comp_price": comp_price,
                "notes": notes
            })
            
        # Convert back to DF
        output_data = []
        
        # ID Logic
        used_ids = set(existing_ids)
        if found and target_route["id"] not in existing_ids:
             used_ids.add(target_route["id"])
             
        running_id = max(used_ids) + 1 if used_ids else 1
        
        for r in current_routes:
            if r.get("id") is None:
                r["id"] = running_id
                running_id += 1
            
            base_price = r["price_vito"]
            
            output_data.append({
                "ID": r["id"],
                "Origin": r["origin"],
                "Destination": r["destination"],
                "Price_Sedan": int(base_price * 0.96),
                "Price_Vito": base_price,
                "Price_VitoVIP": int(base_price * 1.25),
                "Price_Sprinter": int(base_price * 1.95),
                "Active": r.get("active", True),
                "Discount": r.get("discount", 0),
                "Comp_Price": r.get("comp_price", None),
                "Notes": r.get("notes", "")
            })
            
        df_out = pd.DataFrame(output_data)
        
        cols = ["ID", "Origin", "Destination", 
                "Price_Sedan", "Price_Vito", "Price_VitoVIP", "Price_Sprinter",
                "Active", "Discount", "Comp_Price", "Notes"]
        
        # Enforce columns
        for c in cols:
            if c not in df_out.columns:
                df_out[c] = None
                
        df_out = df_out[cols]
        
        df_out.to_excel(FILE_PATH, index=False)
        print(f"Saved/Updated route {origin}->{dest}")

    @staticmethod
    def refresh_calculations():
        """Force recalculation of all rows in the file"""
        routes = DataManager.load_routes()
        if not routes:
            return
        # Load all, save all (to ensure columns are added)
        # We can just iterate and save, but efficient way is to just write the loaded dict back via DataFrame logic
        # But save_route has the logic. 
        # Let's just create a dummy "update" call that touches the first route, 
        # BUT we must ensure we preserve all other routes' data.
        # save_route loads from disk. 
        
        # To strictly refresh columns without changing data:
        # We should just call save_route on the first item with its EXISTING data.
        r = routes[0]
        DataManager.save_route(
            r["origin"], r["destination"], r["price_vito"],
            active=r.get("active", True),
            discount=r.get("discount", 0),
            comp_price=r.get("comp_price", None),
            notes=r.get("notes", "")
        )


