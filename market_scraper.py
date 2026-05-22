import requests
import pandas as pd
import json
import os
from datetime import datetime

def scrape_nse_data():
    # We use a clean HTML source for Kenyan stocks
    url = "https://www.mystocks.co.ke/prices"
    headers = {"User-Agent": "Mozilla/5.0"}
    
    json_folder = "NSE_Daily_JSON"
    if not os.path.exists(json_folder):
        os.makedirs(json_folder)

    try:
        print("Fetching market data from HTML source...")
        # pandas.read_html is very powerful for clean tables
        tables = pd.read_html(url)
        
        # Usually, the first table is the main price list
        df = tables[0]
        
        # Data Cleaning: Keep only Ticker, Name, Price, and Volume
        # MyStocks columns are usually: Ticker, Name, Volume, Price, etc.
        # We rename them to match your desired JSON schema
        df = df.iloc[:, [0, 1, 3, 2]] # Select Ticker, Name, Price, Volume
        df.columns = ['ticker', 'name', 'price', 'volume']
        
        # Clean numeric data (remove commas and ensure they are floats/ints)
        df['price'] = pd.to_numeric(df['price'].astype(str).str.replace(',', ''), errors='coerce')
        df['volume'] = pd.to_numeric(df['volume'].astype(str).str.replace(',', ''), errors='coerce')
        df = df.dropna(subset=['price']) # Remove rows without a price

        # Convert to list of dictionaries
        data_list = df.to_dict(orient='records')
        
        # Save JSON
        today = datetime.now().strftime('%Y-%m-%d')
        filename = f"{json_folder}/{today}.json"
        
        with open(filename, 'w') as f:
            json.dump(data_list, f, indent=4)
            
        print(f"✅ Success! Saved {len(data_list)} stocks to {filename}")

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    scrape_nse_data()
