import pdfplumber
import json
import os
import re
from datetime import datetime

def clean_number(text):
    if not text or text in ['-', '—', 'None']: return 0.0
    cleaned = re.sub(r'[^\d.]', '', str(text).strip())
    try:
        return float(cleaned) if cleaned else 0.0
    except ValueError:
        return 0.0

def parse_pdf(pdf_path):
    """The core logic to extract data from a single PDF"""
    extracted_data = []
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages[:3]:
                table = page.extract_table()
                if not table: continue
                for row in table:
                    # Logic: Ticker is usually Col 0, Price is Col 5 or 6
                    if row and row[0] and len(row[0]) <= 5 and row[0].isupper():
                        extracted_data.append({
                            "ticker": row[0],
                            "name": row[1],
                            "price": clean_number(row[5]),
                            "volume": clean_number(row[-1]),
                        })
        return extracted_data
    except Exception as e:
        print(f"Failed to parse {pdf_path}: {e}")
        return None

def backfill_all_data():
    pdf_folder = "NSE_Daily_Reports"
    json_folder = "NSE_Daily_JSON"
    
    if not os.path.exists(json_folder): os.makedirs(json_folder)

    # Get list of all PDFs
    pdf_files = [f for f in os.listdir(pdf_folder) if f.endswith('.pdf')]
    print(f"Found {len(pdf_files)} PDFs in archive.")

    for pdf_file in pdf_files:
        # Extract date from filename (e.g., 'NSE_Price_List_2024-02-09.pdf')
        # We assume the date is the last 10 characters before .pdf
        date_str = pdf_file.replace("NSE_Price_List_", "").replace(".pdf", "")
        json_path = f"{json_folder}/{date_str}.json"

        # SMART CHECK: Only process if we haven't done this one yet
        if os.path.exists(json_path):
            print(f"⏩ Skipping {date_str}, JSON already exists.")
            continue

        print(f"⚙️ Processing historical data for: {date_str}...")
        data = parse_pdf(os.path.join(pdf_folder, pdf_file))
        
        if data and len(data) > 10:
            with open(json_path, 'w') as f:
                json.dump(data, f, indent=4)
            print(f"✅ Created {json_path}")
        else:
            print(f"⚠️ Warning: Could not extract valid data from {pdf_file}")

if __name__ == "__main__":
    backfill_all_data()
  
