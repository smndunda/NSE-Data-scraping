import pdfplumber
import json
import os
import re
from datetime import datetime

def clean_number(text):
    """Turns '1,234.50' into 1234.5 and '-' into 0"""
    if not text or text == '-' or text == '—': return 0.0
    # Remove commas and other non-numeric characters except the decimal point
    cleaned = re.sub(r'[^\d.]', '', text.strip())
    try:
        return float(cleaned) if cleaned else 0.0
    except ValueError:
        return 0.0

def process_latest_pdf():
    pdf_folder = "NSE_Daily_Reports"
    json_folder = "NSE_Daily_JSON"
    
    if not os.path.exists(json_folder): 
        os.makedirs(json_folder)

    # 1. Find the latest PDF
    if not os.path.exists(pdf_folder):
        print("PDF folder not found.")
        return
        
    files = [f for f in os.listdir(pdf_folder) if f.endswith('.pdf')]
    if not files:
        print("No PDFs found to process.")
        return
    
    # Sort by filename (which has the date) to get the newest
    latest_pdf = os.path.join(pdf_folder, sorted(files)[-1])
    print(f"Bridge is processing: {latest_pdf}")
    
    extracted_data = []

    with pdfplumber.open(latest_pdf) as pdf:
        # We check the first 3 pages where the Equity Price List usually sits
        for page in pdf.pages[:3]:
            table = page.extract_table()
            if not table: continue
            
            for row in table:
                # Basic check: Ticker symbols are usually 1-5 uppercase letters
                # And the row must have enough columns (usually 8-10)
                if row and row[0] and len(row[0]) <= 5 and row[0].isupper() and len(row) >= 6:
                    try:
                        ticker = row[0]
                        name = row[1]
                        # In the NSE PDF, the 'Current Price' is usually the 6th or 7th column
                        # We try to find a valid price in common column positions
                        price = clean_number(row[5])
                        volume = clean_number(row[-1]) # Volume is usually near the end
                        
                        extracted_data.append({
                            "ticker": ticker,
                            "name": name,
                            "price": price,
                            "volume": volume,
                            "date_processed": datetime.now().strftime('%Y-%m-%d')
                        })
                    except Exception as e:
                        continue

    # --- SANITY CHECKS ---
    print(f"Extracted {len(extracted_data)} companies.")
    
    if len(extracted_data) < 10: # Minimum check
        print("❌ ERROR: Too few stocks found. PDF parsing might be misaligned.")
        return

    # Check for Safaricom as a benchmark
    scom = next((item for item in extracted_data if item["ticker"] == "SCOM"), None)
    if scom and scom["price"] <= 0:
        print("❌ ERROR: Data integrity check failed (SCOM price is 0).")
        return

    # 2. Save as JSON
    date_str = datetime.now().strftime('%Y-%m-%d')
    json_path = f"{json_folder}/{date_str}.json"
    
    with open(json_path, 'w') as f:
        json.dump(extracted_data, f, indent=4)
    
    print(f"✅ Bridge Success: Created {json_path}")

if __name__ == "__main__":
    process_latest_pdf()
