import requests
from bs4 import BeautifulSoup
from datetime import datetime
import os

def download_daily_report():
    url = "https://www.nse.co.ke/dataservices/market-statistics/"
    headers = {"User-Agent": "Mozilla/5.0"}
    
    # Folder to store PDFs
    folder = "NSE_Daily_Reports"
    if not os.path.exists(folder):
        os.makedirs(folder)

    try:
        print("Checking NSE website...")
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')

        download_link = None
        for a in soup.find_all('a', href=True):
            if "Daily Equity Price List" in a.text:
                download_link = a['href']
                break

        if download_link:
            today = datetime.now().strftime('%Y-%m-%d')
            filename = f"{folder}/NSE_Price_List_{today}.pdf"
            
            print(f"Found report! Downloading...")
            file_data = requests.get(download_link, headers=headers)
            
            with open(filename, 'wb') as f:
                f.write(file_data.content)
            print(f"Saved: {filename}")
        else:
            print("Link not found. The site might not have updated yet.")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    download_daily_report()
