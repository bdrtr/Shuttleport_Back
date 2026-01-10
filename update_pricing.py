#!/usr/bin/env python3
"""
Script to update Excel pricing file with competitor-based pricing (50 TL cheaper)
"""
import pandas as pd
import os

# Competitor prices from istanbulshuttleport.com (Istanbul Airport → Sultanahmet)
competitor_prices = {
    "Sedan Private": 2042,
    "Mercedes Vito & VW Private": 2127,
    "VIP V CLASS LUXURY VANS BLACK PRIVATE": 2340,
    "VIP Mercedes Maybach Private": 2808,
    "Sprinter & VW Private": 2935,
    "Mercedes Vito Black": 3616,
    "VIP Mercedes Sprinter Black Private": 3914,
    "Private Mercedes EQE": 6380,
    "Wheelchair Accessible Vans": 7784,
    "Private Mercedes EQS or BMW 7 Series": 11484,
    "Private Mercedes S Series": 12761
}

# Our pricing (50 TL cheaper)
DISCOUNT = 50

# Map competitor vehicles to our vehicle types
our_prices = {
    "sedan": competitor_prices["Sedan Private"] - DISCOUNT,  # 1992
    "vito": competitor_prices["Mercedes Vito & VW Private"] - DISCOUNT,  # 2077
    "vito_vip": competitor_prices["VIP V CLASS LUXURY VANS BLACK PRIVATE"] - DISCOUNT,  # 2290
    "sprinter": competitor_prices["Sprinter & VW Private"] - DISCOUNT,  # 2885
}

excel_path = "static/istanbul_transfer.xlsx"

# Read existing data
if os.path.exists(excel_path):
    df = pd.read_excel(excel_path)
else:
    df = pd.DataFrame()

# Check if Istanbul Airport → Sultanahmet route exists
route_exists = False
if not df.empty:
    route_exists = (
        (df['Origin'].str.contains('İstanbul Havalimanı', case=False, na=False)) & 
        (df['Destination'].str.contains('Sultanahmet', case=False, na=False))
    ).any()

if route_exists:
    # Update existing route
    mask = (
        (df['Origin'].str.contains('İstanbul Havalimanı', case=False, na=False)) & 
        (df['Destination'].str.contains('Sultanahmet', case=False, na=False))
    )
    df.loc[mask, 'Price_Sedan'] = our_prices['sedan']
    df.loc[mask, 'Price_Vito'] = our_prices['vito']
    df.loc[mask, 'Price_VitoVIP'] = our_prices['vito_vip']
    df.loc[mask, 'Price_Sprinter'] = our_prices['sprinter']
    df.loc[mask, 'Comp_Price'] = competitor_prices["Mercedes Vito & VW Private"]
    df.loc[mask, 'Notes'] = "Rakipten 50 TL ucuz (istanbulshuttleport.com)"
    print("✅ Updated existing Istanbul Airport → Sultanahmet route")
else:
    # Add new route
    new_route = {
        'ID': len(df) + 1 if not df.empty else 1,
        'Origin': 'İstanbul Havalimanı (IST)',
        'Destination': 'Sultanahmet, Fatih',
        'Price_Sedan': our_prices['sedan'],
        'Price_Vito': our_prices['vito'],
        'Price_VitoVIP': our_prices['vito_vip'],
        'Price_Sprinter': our_prices['sprinter'],
        'Active': True,
        'Discount': 0,
        'Comp_Price': competitor_prices["Mercedes Vito & VW Private"],
        'Notes': "Rakipten 50 TL ucuz (istanbulshuttleport.com)"
    }
    df = pd.concat([df, pd.DataFrame([new_route])], ignore_index=True)
    print("✅ Added new Istanbul Airport → Sultanahmet route")

# Save updated Excel file
df.to_excel(excel_path, index=False)
print(f"✅ Saved updated pricing to {excel_path}")
print("\nUpdated pricing:")
print(df.to_string())
