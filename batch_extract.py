import pdfplumber
import pandas as pd
import os
import json

# Define your paths
PDF_FOLDER = "NSE_Daily_Reports"
JSON_FOLDER = "NSE_Daily_JSON"

# Create the JSON folder if it doesn't exist
if not os.path.exists(JSON_FOLDER):
    os.makedirs(JSON_FOLDER)

def extract_all_sectors(pdf_path):
    """Extracts all sectors and their stocks into a single list of dictionaries."""
    data_points = []
    current_sector = "UNKNOWN"
    
    # Standard NSE columns (x-coordinates)
    columns = [0, 45, 90, 270, 360, 400, 450, 490, 540, 600, 700]
    
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            # Extract table using the vertical column markers
            table = page.extract_table({
                "vertical_strategy": "explicit", 
                "explicit_vertical_lines": columns,
                "horizontal_strategy": "text"
            })
            
            if not table: continue

            for row in table:
                clean_row = [cell.strip() if cell else "" for cell in row]
                
                # 1. Detect Sector Headers (e.g., BANKING, AGRICULTURAL)
                # Usually these rows have data in the first column but nothing in ISIN
                if clean_row[2] != "" and clean_row[3] == "" and clean_row[5] == "":
                    current_sector = clean_row[2].upper()
                    continue

                # 2. Detect Stock Rows (Must have an ISIN code)
                isin = clean_row[3]
                if isin and (isin.startswith("KE") or isin.startswith("ZA") or isin.startswith("UA")):
                    stock_entry = {
                        "sector": current_sector,
                        "security": clean_row[2],
                        "isin": isin,
                        "status": clean_row[4],
                        "high": clean_row[5],
                        "low": clean_row[6],
                        "vwap": clean_row[7],
                        "prev_price": clean_row[8],
                        "volume": clean_row[9].replace(',', '') if clean_row[9] else "0"
                    }
                    data_points.append(stock_entry)
                    
    return data_points

# --- MAIN LOOP ---
print("Starting batch extraction...")

for filename in os.listdir(PDF_FOLDER):
    if filename.endswith(".pdf"):
        pdf_path = os.path.join(PDF_FOLDER, filename)
        
        # Create a filename for the JSON (e.g., NSE_Price_List_2026-02-12.json)
        json_filename = filename.replace(".pdf", ".json")
        json_path = os.path.join(JSON_FOLDER, json_filename)
        
        # Check if we already processed this file to save time
        if os.path.exists(json_path):
            print(f"Skipping {filename} (Already exists)")
            continue
            
        print(f"Processing: {filename}...")
        try:
            extracted_data = extract_all_sectors(pdf_path)
            
            # Save to JSON folder
            with open(json_path, 'w') as f:
                json.dump(extracted_data, f, indent=4)
                
        except Exception as e:
            print(f"Error processing {filename}: {e}")

print("Done! Check your NSE_Daily_JSON folder.")
