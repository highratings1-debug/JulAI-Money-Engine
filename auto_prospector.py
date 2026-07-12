import time
import re
import csv
import os
import random
from itertools import cycle
try:
    from ddgs import DDGS
except ImportError:
    print("Please run: pip install ddgs")
    exit(1)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROSPECTS_FILE = os.path.join(BASE_DIR, "prospects.csv")

INDUSTRIES = ["dental clinic", "real estate agency", "gym", "restaurant", "car dealership", "law firm", "medical center", "cleaning company", "plumbing company", "roofing company"]
CITIES = ["Dubai", "Abu Dhabi", "Riyadh", "Jeddah", "Cairo", "London", "New York", "Chicago", "Toronto", "Sydney", "Miami", "Los Angeles", "Houston", "Dallas", "Atlanta"]
LANGUAGES = {"Dubai": "en", "Abu Dhabi": "en", "Riyadh": "ar", "Jeddah": "ar", "Cairo": "ar", "London": "en", "New York": "en", "Chicago": "en", "Toronto": "en", "Sydney": "en", "Miami": "en", "Los Angeles": "en", "Houston": "en", "Dallas": "en", "Atlanta": "en"}

EMAIL_REGEX = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"

def get_existing_emails():
    existing = set()
    if os.path.exists(PROSPECTS_FILE):
        with open(PROSPECTS_FILE, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                existing.add(row.get("email", "").strip().lower())
    return existing

def save_prospect(name, email, company, industry, language):
    file_exists = os.path.exists(PROSPECTS_FILE)
    with open(PROSPECTS_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["name", "email", "company", "industry", "language"])
        writer.writerow([name, email, company, industry, language])
    print(f"  [NEW LEAD ADDED] {company} | {email}")

def scrape_leads():
    print("=" * 60)
    print("  JULAI AUTO-PROSPECTOR - UNLIMITED LEADS ENGINE")
    print("=" * 60)
    
    # Generate all combinations and shuffle them
    combinations = [(ind, city) for ind in INDUSTRIES for city in CITIES]
    random.shuffle(combinations)
    query_cycle = cycle(combinations)
    
    ddgs = DDGS()
    
    for industry, city in query_cycle:
        language = LANGUAGES.get(city, "en")
        query = f'"{industry}" "{city}" email contact "info@"'
        print(f"\n[*] Scraping Web for: {query}")
        
        try:
            results = ddgs.text(query, max_results=20)
            existing_emails = get_existing_emails()
            new_leads_found = 0
            
            for result in results:
                text_content = result.get('body', '') + " " + result.get('title', '')
                emails_found = re.findall(EMAIL_REGEX, text_content)
                
                for email in emails_found:
                    email = email.lower().strip()
                    # Filter out useless emails
                    if any(x in email for x in ['example', 'domain', 'sentry', 'wix', 'wordpress']):
                        continue
                        
                    if email not in existing_emails:
                        # Extract a potential company name from the URL or title
                        company_name = result.get('title', '').split('|')[0].split('-')[0].strip()
                        if len(company_name) > 30 or len(company_name) < 3:
                            company_name = f"{city} {industry.title()}"
                            
                        save_prospect("There", email, company_name, industry, language)
                        existing_emails.add(email)
                        new_leads_found += 1
                        
            print(f"  -> Found {new_leads_found} new leads.")
            
        except Exception as e:
            print(f"  [ERROR] Scraping failed: {e}")
            
        if "--cloud" in sys.argv:
            print("[*] CLOUD MODE: Exiting after one search.")
            break
            
        print("[*] Waiting 15 minutes before next search run...")
        time.sleep(900)

if __name__ == "__main__":
    import sys
    scrape_leads()
