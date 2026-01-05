import pandas as pd
import os

file_path = "static/istanbul_transfer.xlsx"
try:
    if os.path.exists(file_path):
        df = pd.read_excel(file_path)
        print(f"Total Rows: {len(df)}")
        print(df.to_string())
    else:
        print("File NOT found.")
except Exception as e:
    print(e)
