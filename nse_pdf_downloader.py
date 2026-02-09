import requests
from bs4 import BeautifulSoup
from datetime import datetime
import os
from urllib.parse import urljoin # This fixes the URL issue

def download_daily_report():
    base_url = "https://www.nse.co.ke/dataservices/market-statistics/"
    headers = {"User-Agent": "Mozilla/5.0"}
    
    folder = "NSE_Daily_Reports"
    if not os.path.exists(folder):
        os.makedirs(folder)

    try:
        print("Checking NSE website...")
        response = requests.get(base_url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')

        download_link = None
        for a in soup.find_all('a', href=True):
            if "Daily Equity Price List" in a.text:
                # This line joins the base URL with the relative link
                download_link = urljoin(base_url, a['href'])
                break

        if download_link:
            today = datetime.now().strftime('%Y-%m-%d')
            filename = f"{folder}/NSE_Price_List_{today}.pdf"
            
            print(f"Found report at: {download_link}")
            print(f"Downloading to {filename}...")
            
            file_data = requests.get(download_link, headers=headers)
            
            with open(filename, 'wb') as f:
                f.write(file_data.content)
            print("Download successful.")
        else:
            print("Link not found. The site might not have updated yet.")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    download_daily_report()
