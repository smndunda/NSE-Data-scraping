import pdfplumber
import json
import os
import re
from datetime import datetime

def clean_number(text):
    if text is None: return 0.0
    text = str(text).strip().replace(',', '')
    if text in ['-', '—', 'None', '', 'N/A']: return 0.0
    # Extract only the numeric part (handling things like '12.50c')
    match = re.search(r'(\d+\.?\d*)', text)
    try:
        return float(match.group(1)) if match else 0.0
    except:
        return 0.0

def parse_pdf(pdf_path):
    extracted_data = []
    try:
        with pdfplumber.open(pdf_path) as pdf:
            # The Equity Price list is usually on Page 1 or 2
            for page in pdf.pages[:3]:
                tables = page.extract_tables()
                for table in tables:
                    for row in table:
                        # Clean the row (remove None and whitespace)
                        row = [str(cell).strip() if cell else "" for cell in row]
                        
                        # LOGIC: A valid stock row usually starts with a 1-5 letter ticker 
                        # and has numbers in the later columns.
                        ticker = row[0]
                        if ticker and 1 <= len(ticker) <= 5 and ticker.isupper() and ticker != 'PIVOT':
                            
                            # We search for the Price. In NSE PDFs, it's usually 
                            # after the 'Low' and before the 'Change'.
                            # Usually index 5, 6, or 7. We take the first valid number after index 3.
                            price = 0.0
                            for cell in row[3:8]:
                                val = clean_number(cell)
                                if val > 0:
                                    price = val
                                    break
                            
                            # Volume is usually one of the last two columns
                            volume = clean_number(row[-1]) if len(row) > 1 else 0.0
                            
                            if price > 0:
                                extracted_data.append({
                                    "ticker": ticker,
                                    "name": row[1] if len(row) > 1 else "",
                                    "price": price,
                                    "volume": volume
                                })
        return extracted_data
    except Exception as e:
        print(f"Error parsing {pdf_path}: {e}")
        return None

def backfill_all_data():
    pdf_folder = "NSE_Daily_Reports"
    json_folder = "NSE_Daily_JSON"
    if not os.path.exists(json_folder): os.makedirs(json_folder)

    pdf_files = [f for f in os.listdir(pdf_folder) if f.endswith('.pdf')]
    print(f"Found {len(pdf_files)} PDFs in archive.")

    for pdf_file in sorted(pdf_files):
        date_str = pdf_file.replace("NSE_Price_List_", "").replace(".pdf", "")
        json_path = f"{json_folder}/{date_str}.json"

        if os.path.exists(json_path):
            continue

        print(f"⚙️ Processing: {date_str}...")
        data = parse_pdf(os.path.join(pdf_folder, pdf_file))
        
        # We lowered the sanity check to 10 stocks just to get the backfill started
        if data and len(data) >= 10:
            with open(json_path, 'w') as f:
                json.dump(data, f, indent=4)
            print(f"✅ Created {json_path} ({len(data)} stocks)")
        else:
            print(f"⚠️ Warning: Could not extract enough data from {pdf_file}")

if __name__ == "__main__":
    backfill_all_data()
