import pandas as pd
import os

file_path = "static/istanbul_transfer.xlsx"
try:
    if os.path.exists(file_path):
        df = pd.read_excel(file_path)
        print("Columns:", df.columns.tolist())
        # Print first 2 rows with new columns
        cols = ["ID", "Origin", "Active", "Discount", "Notes"]
        print(df[cols].head().to_string())
    else:
        print("File NOT found.")
except Exception as e:
    print(e)
