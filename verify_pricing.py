import pandas as pd
import os

file_path = "static/istanbul_transfer.xlsx"
try:
    if os.path.exists(file_path):
        df = pd.read_excel(file_path)
        print("Columns:", df.columns.tolist())
        print(df.head().to_string())
    else:
        print("File NOT found.")
except Exception as e:
    print(e)
