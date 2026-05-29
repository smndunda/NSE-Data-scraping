import pdfplumber
import pandas as pd
import json
import os

# Your exact function
def extract_nse_sector(pdf_path, target_sector):
    target_sector = target_sector.upper()
    extracted_rows = []
    columns = [0, 45, 90, 270, 360, 400, 450, 490, 540, 600, 700]
    col_names = ["52wk_High", "52wk_Low", "Security", "ISIN", "Status", "High", "Low", "VWAP", "Prev_Price", "Volume"]
    found_sector = False

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            table = page.extract_table({
                "vertical_strategy": "explicit", 
                "explicit_vertical_lines": columns,
                "horizontal_strategy": "text"
            })
            if not table: continue
            for row in table:
                clean_row = [cell.strip() if cell else "" for cell in row]
                row_text = " ".join(clean_row).upper()
                if target_sector in row_text:
                    found_sector = True
                    continue 
                if found_sector:
                    if clean_row[3] == "" and clean_row[2] == "": 
                        found_sector = False
                        break
                    if "KE" in clean_row[3] or "UA" in clean_row[3] or "ZA" in clean_row[3]:
                        extracted_rows.append(clean_row)
                    elif len(extracted_rows) > 0 and clean_row[2] != "":
                        found_sector = False
                        break
    df = pd.DataFrame(extracted_rows, columns=col_names)
    return df

# --- THE BATCH LOGIC ---
PDF_FOLDER = "NSE_Daily_Reports"
JSON_FOLDER = "NSE_Daily_JSON"
# List of sectors you want to extract
SECTORS = ["AGRICULTURAL", "BANKING", "INSURANCE", "MANUFACTURING & ALLIED", "ENERGY & PETROLEUM"]

if not os.path.exists(JSON_FOLDER):
    os.makedirs(JSON_FOLDER)

for filename in os.listdir(PDF_FOLDER):
    if filename.endswith(".pdf"):
        print(f"Processing {filename}...")
        all_sector_data = []
        
        for sector in SECTORS:
            df = extract_nse_sector(os.path.join(PDF_FOLDER, filename), sector)
            # Add a 'Sector' column so you know which is which
            df['Sector'] = sector
            # Convert this sector to a list of dictionaries
            all_sector_data.extend(df.to_dict(orient="records"))
            
        # Save the combined sectors to one JSON file per PDF
        json_filename = filename.replace(".pdf", ".json")
        with open(os.path.join(JSON_FOLDER, json_filename), 'w') as f:
            json.dump(all_sector_data, f, indent=4)

print("Finished processing all PDFs!")
