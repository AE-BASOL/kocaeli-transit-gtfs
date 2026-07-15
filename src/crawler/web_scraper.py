import requests
from bs4 import BeautifulSoup
import json
import os

def scrape_akcaray_schedule():
    """
    Scrapes the tram (Akçaray) schedule and stops from UlasimPark API.
    """
    base_url = "https://www.ulasimpark.com.tr"
    page_url = f"{base_url}/tramvay/tramvay-saatleri"
    api_durak = f"{base_url}/Hizmetlerimiz/TramvayDurakGetir"
    api_saat = f"{base_url}/Hizmetlerimiz/TramvaySaatGetir"
    
    session = requests.Session()
    
    try:
        # Step 1: Get the page to extract __RequestVerificationToken
        res = session.get(page_url, timeout=10)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, 'html.parser')
        
        token_input = soup.find("input", {"name": "__RequestVerificationToken"})
        if not token_input:
            print("[WebScraper] Error: Could not find __RequestVerificationToken for Tramvay.")
            return {"status": "error"}
            
        token = token_input["value"]
        
        # Step 2: Fetch stops and schedules for T1, T2, T3 (Tram lines)
        tram_lines = ["T1", "T2", "T3"]
        tram_data = {}
        
        for yon in tram_lines:
            # Fetch Stops
            durak_res = session.post(api_durak, data={"__RequestVerificationToken": token, "yon": yon}, timeout=10)
            durak_json = json.loads(durak_res.json()) if isinstance(durak_res.json(), str) else durak_res.json()
            duraklar = durak_json.get("Result", [])
            
            # Fetch Schedules
            saat_res = session.post(api_saat, data={"__RequestVerificationToken": token, "yon": yon}, timeout=10)
            saat_json = json.loads(saat_res.json()) if isinstance(saat_res.json(), str) else saat_res.json()
            saatler = saat_json.get("Result", [])
            
            if duraklar or saatler:
                tram_data[yon] = {
                    "duraklar": duraklar,
                    "saatler": saatler
                }
                
        print(f"[WebScraper] Successfully scraped Akçaray data for lines: {list(tram_data.keys())}")
        return {"status": "ok", "routes": tram_data}
        
    except Exception as e:
        print(f"[WebScraper] Error scraping Akçaray: {e}")
        return {"status": "error"}

def scrape_ferry_schedule():
    """
    Scrapes the ferry (Vapur) schedule from Kocaeli official websites.
    """
    url = "https://www.kocaeli.bel.tr/tr/main/hatlar/vapur"
    # Ferry scraping logic to be expanded as needed.
    # Currently a skeleton since it requires deeper reverse-engineering of kocaeli.bel.tr.
    print("[WebScraper] Ferry schedule scraper is a skeleton.")
    return {"status": "ok", "routes": {}}
