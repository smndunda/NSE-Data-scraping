import tabula
import pandas as pd
import json
import os
from datetime import datetime

def process_pdfs_to_json():
    pdf_folder = "NSE_Daily_Reports"
    json_folder = "NSE_Daily_JSON"
    if not os.path.exists(json_folder): os.makedirs(json_folder)

    pdf_files = sorted([f for f in os.listdir(pdf_folder) if f.endswith('.pdf')])
    
    for pdf_file in pdf_files:
        date_str = pdf_file.replace("NSE_Price_List_", "").replace(".pdf", "")
        json_path = f"{json_folder}/{date_str}.json"
        
        if os.path.exists(json_path): continue

        print(f"⚙️ Tabula is extracting: {date_str}")
        pdf_path = os.path.join(pdf_folder, pdf_file)
        
        try:
            # Tabula reads the PDF and looks specifically for tables
            # 'pages="all"' ensures we check every page
            tables = tabula.read_pdf(pdf_path, pages='all', multiple_tables=True)
            
            all_stocks = []
            for df in tables:
                # We only want tables that have at least 3 columns (Ticker, Name, Price)
                if len(df.columns) >= 3:
                    # Rename columns to be safe
                    df.columns = [str(i) for i in range(len(df.columns))]
                    
                    for index, row in df.iterrows():
                        ticker = str(row['0']).strip()
                        # Check if it looks like a Ticker (Uppercase, 2-5 chars)
                        if ticker.isupper() and 2 <= len(ticker) <= 5:
                            all_stocks.append({
                                "ticker": ticker,
                                "price": row.iloc[5] if len(row) > 5 else 0, # Usually 6th col
                                "volume": row.iloc[-1] # Usually last col
                            })

            if len(all_stocks) > 10:
                with open(json_path, 'w') as
