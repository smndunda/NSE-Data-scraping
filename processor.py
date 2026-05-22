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
                # TRY
