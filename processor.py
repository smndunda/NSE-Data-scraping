import pdfplumber
import json
import os
import re
from datetime import datetime

def clean_val(text):
    if text is None: return 0.0
    # Removes commas and any letters/symbols attached to numbers (like 12.50* or 1,200xd)
    cleaned = re.sub(r'[^\d.]', '', str(text).replace(',', '').strip())
    try:
        return float(cleaned) if cleaned else 0.0
    except:
        return 0.0

def parse_nse_line_by_line(pdf_path):
    extracted_data = []
    
    ticker_map = {
        "Safaricom": "SCOM", "Bamburi": "BAMB", "Equity": "EQTY", 
        "KCB": "KCB", "Absa": "ABSA", "E.A.Breweries": "EABL",
        "Co-operative": "COOP", "KenGen": "KEGN", "BAT": "BAT", 
        "Centum": "CTUM", "I&M": "IMH", "NCBA": "NCBA"
    }

    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages[:4]:
                text = page.extract_text()
                if not text: continue
                
                for line in text.split('\n'):
                    # The Magic Pattern: Look for lines that start with 
                    # 52W High (number) + 52W Low (number) + Name (Text)
                    # Pattern matches: "12.50 10.00 Company Name..."
                    match = re.search(r'^(\d[\d,.]*)\s+(\d[\d,.]*)\s+([A-Za-z\s.\-&]+)', line)
                    
                    if match:
                        high_52w = clean_val(match.group(1))
                        low_52w = clean_val(match.group(2))
                        name = match.group(3).strip()
                        
                        # Only proceed if we have valid 52-week numbers and a name
                        if high_52w > 0 and len(name) > 5:
                            # Extract all numbers from the line to find VWAP and Volume
                            # Numbers are usually at the end of the line
                            line_numbers = re.findall(r'[\d,.]+', line)
                            
                            # Based on your map: 
                            # High/Low are indices 0,1. 
                            # VWAP is usually index -3, Prev is -2, Volume is -1
                            if len(line_numbers) >= 5:
                                vwap = clean_val(line_numbers[-3])
                                prev = clean_val(line_numbers[-2])
                                volume = clean_val(line_numbers[-1])
                                
                                ticker = "OTHER"
                                for key, symbol in ticker_map.items():
                                    if key.lower() in name.lower():
                                        ticker = symbol
                                        break
                                if ticker == "OTHER":
                                    ticker = re.sub(r'\W+', '', name.split()[0]).upper()[:4]

                                extracted_data.append({
                                    "ticker": ticker,
                                    "name": name,
                                    "high_52w": high_52w,
                                    "low_52w": low_52w,
                                    "vwap": vwap,
                                    "prev_price": prev,
                                    "volume": volume,
                                    "date": datetime.now().strftime('%Y-%m-%d')
                                })
        return extracted_data
    except Exception as e:
        print(f"   Error: {e}")
        return None

def run_backfill():
    pdf_folder = "NSE_Daily_Reports"
    json_folder = "NSE_Daily_JSON"
    if not os.path.exists(json_folder): os.makedirs(json_folder)

    pdf_files = sorted([f for f in os.listdir(pdf_folder) if f.endswith('.pdf')])
    print(f"Found {len(pdf_files)} PDFs. Starting aggressive line-by-line backfill...")
    
    count = 0
    for pdf_file in pdf_files:
        date_str = pdf_file.replace("NSE_Price_List_", "").replace(".pdf", "")
        json_path = f"{json_folder}/{date_str}.json"
        
        # We process even if it exists to fix previously empty/failed files
        data = parse_nse_line_by_line(os.path.join(pdf_folder, pdf_file))
        
        if data and len(data) > 10:
            with open(json_path, 'w') as f:
                json.dump(data, f, indent=4)
            print(f"✅ Recovered: {date_str} ({len(data)} stocks)")
            count += 1
        else:
            print(f"❌ Still failing: {date_str}")

    print(f"\nProcessing complete. Recovered {count} dates.")

if __name__ == "__main__":
    run_backfill()
