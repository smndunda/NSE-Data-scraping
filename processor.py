import pdfplumber
import json
import os
import re
from datetime import datetime

def clean_val(text):
    if text is None: return 0.0
    # Extract only numbers and decimals (handles things like '12.50*', '1,200', or '12.50xd')
    cleaned = re.sub(r'[^\d.]', '', str(text).replace(',', '').strip())
    try:
        return float(cleaned) if cleaned else 0.0
    except:
        return 0.0

def parse_nse_pdf(pdf_path):
    extracted_data = []
    
    # Improved ticker map for the most traded stocks
    ticker_map = {
        "Safaricom": "SCOM", "Bamburi": "BAMB", "Equity": "EQTY", 
        "KCB": "KCB", "Absa": "ABSA", "E.A.Breweries": "EABL",
        "Centum": "CTUM", "Co-operative": "COOP", "KenGen": "KEGN",
        "BAT": "BAT", "Standard Chartered": "SCBK", "I&M": "IMH",
        "NCBA": "NCBA", "Stanbic": "SBIC", "Nation Media": "NMG"
    }

    try:
        with pdfplumber.open(pdf_path) as pdf:
            # Check the first 4 pages to be thorough
            for page in pdf.pages[:4]:
                # TRY STRATEGY 1: Text-based grid (Good for borderless)
                table = page.extract_table({
                    "vertical_strategy": "text", 
                    "horizontal_strategy": "text",
                    "snap_tolerance": 4
                })
                
                # TRY STRATEGY 2: If Strategy 1 failed, try a more aggressive split
                if not table or len(table) < 5:
                    table = page.extract_table()

                if not table: continue

                for row in table:
                    # Filter out header rows and empty rows
                    # A stock row usually has a Name in index 2 and numbers in index 0, 1, 7, 8
                    if row and len(row) >= 8:
                        name = str(row[2]).strip() if row[2] else ""
                        high_52w = clean_val(row[0])
                        low_52w = clean_val(row[1])
                        vwap = clean_val(row[7])
                        
                        # VALIDATION: If it has a 52-week range and a name, it's a stock
                        if high_52w > 0 and low_52w > 0 and len(name) > 3:
                            ticker = "OTHER"
                            for key, symbol in ticker_map.items():
                                if key.lower() in name.lower():
                                    ticker = symbol
                                    break
                            if ticker == "OTHER":
                                # Fallback: Take the first word of the name
                                ticker = re.sub(r'\W+', '', name.split()[0]).upper()[:4]

                            extracted_data.append({
                                "ticker": ticker,
                                "name": name,
                                "high_52w": high_52w,
                                "low_52w": low_52w,
                                "vwap": vwap,
                                "prev_price": clean_val(row[8]) if len(row) > 8 else 0,
                                "volume": clean_val(row[-1]) if len(row) > 9 else 0
                            })
        return extracted_data
    except Exception as e:
        print(f"   Error parsing {os.path.basename(pdf_path)}: {e}")
        return None

def run_backfill():
    pdf_folder = "NSE_Daily_Reports"
    json_folder = "NSE_Daily_JSON"
    if not os.path.exists(json_folder): os.makedirs(json_folder)

    # Get all PDFs and sort them
    pdf_files = sorted([f for f in os.listdir(pdf_folder) if f.endswith('.pdf')])
    print(f"Found {len(pdf_files)} PDFs. Starting backfill...")
    
    success_count = 0
    for pdf_file in pdf_files:
        date_str = pdf_file.replace("NSE_Price_List_", "").replace(".pdf", "")
        json_path = f"{json_folder}/{date_str}.json"
        
        # Skip if already exists
        if os.path.exists(json_path):
            continue

        data = parse_nse_pdf(os.path.join(pdf_folder, pdf_file))
        
        # Sanity Check: Most NSE reports have 50-65 stocks.
        # We accept anything > 15 to ensure we catch even partial reports.
        if data and len(data) >= 15:
            with open(json_path, 'w') as f:
                json.dump(data, f, indent=4)
            print(f"✅ Backfilled: {date_str} ({len(data)} stocks)")
            success_count += 1
        else:
            print(f"❌ Failed: {date_str} (Found {len(data) if data else 0} stocks)")

    print(f"\nBackfill complete. Successfully processed {success_count} new files.")

if __name__ == "__main__":
    run_backfill()
