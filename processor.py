import pdfplumber
import json
import os
import re
from datetime import datetime

def clean_val(text):
    if text is None: return 0.0
    # Remove commas and non-numeric characters except decimals
    cleaned = re.sub(r'[^\d.]', '', str(text).replace(',', '').strip())
    try:
        return float(cleaned) if cleaned else 0.0
    except:
        return 0.0

def parse_nse_pdf(pdf_path):
    extracted_data = []
    
    # We use a simple map to turn "Safaricom Plc..." into "SCOM" for your API
    ticker_map = {
        "Safaricom": "SCOM", "Bamburi": "BAMB", "Equity": "EQTY", 
        "KCB": "KCB", "Absa": "ABSA", "E.A.Breweries": "EABL",
        "Centum": "CTUM", "Co-operative": "COOP", "KenGen": "KEGN"
    }

    try:
        with pdfplumber.open(pdf_path) as pdf:
            # Loop through first 3 pages (where the equities live)
            for page in pdf.pages[:3]:
                # We use specific settings for NSE's borderless tables
                table = page.extract_table({
                    "vertical_strategy": "text", 
                    "horizontal_strategy": "text"
                })
                
                if not table: continue

                for row in table:
                    # Based on your screenshot, a valid row must have numbers 
                    # in the 52-Week High (Col 0) and 52-Week Low (Col 1)
                    if len(row) >= 10:
                        high_52w = clean_val(row[0])
                        low_52w = clean_val(row[1])
                        name = str(row[2]).strip()
                        status = str(row[4]).strip().lower() # cd, xd, etc.
                        vwap = clean_val(row[7]) # Column 8
                        prev = clean_val(row[8]) # Column 9
                        volume = clean_val(row[9]) # Column 10

                        # Validation: If it has a 52-week high and a name, it's a stock
                        if high_52w > 0 and len(name) > 3:
                            # Try to find a ticker, otherwise use the first word of name
                            ticker = "OTHER"
                            for key in ticker_map:
                                if key in name:
                                    ticker = ticker_map[key]
                                    break
                            if ticker == "OTHER":
                                ticker = name.split()[0].upper()[:4]

                            extracted_data.append({
                                "ticker": ticker,
                                "name": name,
                                "high_52w": high_52w,
                                "low_52w": low_52w,
                                "status": status if status in ['cd', 'xd', 's'] else "",
                                "vwap": vwap,
                                "prev_price": prev,
                                "volume": volume,
                                "change": round(vwap - prev, 2) if prev > 0 else 0
                            })
        return extracted_data
    except Exception as e:
        print(f"Error: {e}")
        return None

def run_bridge():
    pdf_folder = "NSE_Daily_Reports"
    json_folder = "NSE_Daily_JSON"
    if not os.path.exists(json_folder): os.makedirs(json_folder)

    pdf_files = sorted([f for f in os.listdir(pdf_folder) if f.endswith('.pdf')])
    
    for pdf_file in pdf_files:
        date_str = pdf_file.replace("NSE_Price_List_", "").replace(".pdf", "")
        json_path = f"{json_folder}/{date_str}.json"
        
        if os.path.exists(json_path): continue

        print(f"🌉 Bridge parsing: {date_str}")
        data = parse_nse_pdf(os.path.join(pdf_folder, pdf_file))
        
        if data and len(data) > 10:
            with open(json_path, 'w') as f:
                json.dump(data, f, indent=4)
            print(f"✅ Created {json_path} ({len(data)} stocks)")

if __name__ == "__main__":
    run_bridge()
