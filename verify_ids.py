import pandas as pd
import os

file_path = "static/istanbul_transfer.xlsx"
try:
    if os.path.exists(file_path):
        df = pd.read_excel(file_path)
        print("Columns:", df.columns.tolist())
        # Check first 5 rows specifically for ID
        print(df[["ID", "Origin", "Destination"]].head().to_string())
        
        # Check if any ID is missing
        missing_ids = df["ID"].isnull().sum()
        print(f"Rows with missing IDs: {missing_ids}")
    else:
        print("File NOT found.")
except Exception as e:
    print(e)
