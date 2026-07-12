"""
JulAI Solutions — Automated Upwork Job Monitor & Proposal Generator
Runs every 30 minutes. Finds matching jobs. Generates ready-to-paste proposals.
Saves everything to upwork_proposals.md so you just open the file and paste.

Usage: python upwork_monitor.py
"""
import urllib.request
import xml.etree.ElementTree as ET
import json
import os
import time
import hashlib
from datetime import datetime

SEARCH_FEEDS = [
    ("n8n+automation", "https://www.upwork.com/ab/feed/jobs/rss?q=n8n+automation&sort=recency"),
    ("voice+AI+agent", "https://www.upwork.com/ab/feed/jobs/rss?q=voice+AI+agent&sort=recency"),
    ("AI+chatbot", "https://www.upwork.com/ab/feed/jobs/rss?q=AI+chatbot&sort=recency"),
    ("workflow+automation", "https://www.upwork.com/ab/feed/jobs/rss?q=workflow+automation&sort=recency"),
    ("AI+agent+development", "https://www.upwork.com/ab/feed/jobs/rss?q=AI+agent+development&sort=recency"),
    ("LLM+integration", "https://www.upwork.com/ab/feed/jobs/rss?q=LLM+integration&sort=recency"),
]

SEEN_FILE = "upwork_seen.json"
OUTPUT_FILE = "upwork_proposals.md"

PORTFOLIO = "https://m-alzayan.vercel.app"
AGENCY = "https://julai-agency-app.vercel.app"
VIRIDI = "https://viridi-demo.vercel.app"

PROPOSAL_TEMPLATES = {
    "n8n": """I build production n8n workflows that run without supervision.

For your project, I will build the complete automation from trigger to output. Every workflow includes error handling, retry logic, and a fallback path.

Why me:
- 200+ active n8n workflows in production right now
- Built a full AI sales pipeline (voice AI + CRM + RAG) for an EV manufacturer
- 11 IBM and Anthropic certifications

Live portfolio: {portfolio}
Talk to my AI agent: {agency}

Available to start today. I will scope your project within 24 hours.""",

    "voice": """I build voice AI agents that handle real phone calls.

Live demo you can try right now: {agency}
Click the mic. Talk in English or Arabic. The AI responds naturally.

Case study: VIRIDI — bilingual AI sales assistant for an EV charger manufacturer.
Live at {viridi}

For your project: voice agent customized to your business, connected to your tools, deployed within 2 weeks.

Available to start today.""",

    "chatbot": """I build AI chatbots that handle real conversations on any platform.

Live proof:
- Voice AI agent: {agency} (click the mic)
- Telegram bot demo: {agency}/demo

What you get:
- Working chatbot connected to your CRM, calendar, or database
- Multilingual (Arabic, English, French, Spanish)
- Loom walkthrough video for your team
- 30-day support included

Available to start immediately.""",

    "automation": """I automate business processes end to end using n8n, AI, and APIs.

Recent builds:
- AI lead gen: LinkedIn prospecting + email discovery + AI outreach + CRM logging
- Instagram customer service: multilingual DM automation (Arabic + English)
- Social media pipeline: trend monitoring + AI content + auto-posting

1,000+ integrations. If your tool has an API, I connect it.

Portfolio: {portfolio}
Available to start today.""",

    "agent": """I develop custom AI agents with multi-model orchestration and RAG memory.

My stack: Multi-AI orchestration, RAG with vector databases, n8n for workflows, FastAPI backend, Next.js frontend.

Live proof:
- Voice AI: {agency}
- Case study (bilingual EV sales AI): {viridi}
- 44+ agent types: {portfolio}

11 IBM and Anthropic certifications. Available to start today.""",

    "llm": """I integrate LLMs into production applications.

My stack: OpenAI, Claude, Gemini APIs. RAG pipelines. FastAPI backends. Next.js frontends.

Recent work: Built a multi-model AI engine with automatic fallback — if one provider fails, the system switches to another without downtime.

Live demo: {agency}
Full portfolio: {portfolio}

Available to start today."""
}

def load_seen():
    if os.path.exists(SEEN_FILE):
        with open(SEEN_FILE, "r") as f:
            return json.load(f)
    return []

def save_seen(seen):
    with open(SEEN_FILE, "w") as f:
        json.dump(seen, f)

def classify_job(title, desc):
    text = (title + " " + desc).lower()
    if "n8n" in text:
        return "n8n"
    if "voice" in text or "call" in text or "phone" in text or "receptionist" in text:
        return "voice"
    if "chatbot" in text or "chat bot" in text or "conversational" in text:
        return "chatbot"
    if "agent" in text and ("ai" in text or "llm" in text):
        return "agent"
    if "llm" in text or "gpt" in text or "claude" in text or "openai" in text:
        return "llm"
    return "automation"

def generate_proposal(category):
    template = PROPOSAL_TEMPLATES.get(category, PROPOSAL_TEMPLATES["automation"])
    return template.format(
        portfolio=PORTFOLIO,
        agency=AGENCY,
        viridi=VIRIDI
    )

def fetch_feed(url):
    try:
        req = urllib.request.Request(url, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        })
        with urllib.request.urlopen(req, timeout=15) as resp:
            return resp.read().decode("utf-8", errors="replace")
    except Exception as e:
        return None

def parse_jobs(xml_text):
    jobs = []
    try:
        root = ET.fromstring(xml_text)
        for item in root.findall(".//item"):
            title = item.find("title")
            link = item.find("link")
            desc = item.find("description")
            pub = item.find("pubDate")
            jobs.append({
                "title": title.text if title is not None else "No title",
                "link": link.text if link is not None else "",
                "description": desc.text[:500] if desc is not None and desc.text else "",
                "date": pub.text if pub is not None else ""
            })
    except ET.ParseError:
        pass
    return jobs

def run_scan():
    seen = load_seen()
    new_jobs = []

    for keyword, url in SEARCH_FEEDS:
        print(f"  Scanning: {keyword}...")
        xml = fetch_feed(url)
        if not xml:
            print(f"    Feed unavailable for {keyword}")
            continue
        
        jobs = parse_jobs(xml)
        for job in jobs:
            job_id = hashlib.md5(job["link"].encode()).hexdigest()
            if job_id not in seen:
                category = classify_job(job["title"], job["description"])
                job["category"] = category
                job["proposal"] = generate_proposal(category)
                job["keyword"] = keyword
                new_jobs.append(job)
                seen.append(job_id)

    save_seen(seen)
    return new_jobs

def write_proposals(jobs):
    with open(OUTPUT_FILE, "a", encoding="utf-8") as f:
        f.write(f"\n\n# New Jobs Found — {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n")
        if not jobs:
            f.write("No new matching jobs found this scan.\n")
            return
        
        for i, job in enumerate(jobs, 1):
            f.write(f"---\n\n")
            f.write(f"## Job {i}: {job['title']}\n\n")
            f.write(f"**Link:** {job['link']}\n")
            f.write(f"**Found via:** {job['keyword']}\n")
            f.write(f"**Category:** {job['category']}\n")
            f.write(f"**Date:** {job['date']}\n\n")
            f.write(f"**Description:**\n{job['description']}\n\n")
            f.write(f"### READY-TO-PASTE PROPOSAL:\n\n")
            f.write(f"```\n{job['proposal']}\n```\n\n")

def main():
    print("=" * 60)
    print("  JULAI UPWORK JOB MONITOR")
    print("  Scanning every 30 minutes...")
    print("=" * 60)
    
    cycle = 0
    while True:
        cycle += 1
        print(f"\n[Scan #{cycle}] {datetime.now().strftime('%Y-%m-%d %H:%M')}...")
        
        new_jobs = run_scan()
        write_proposals(new_jobs)
        
        if new_jobs:
            print(f"  FOUND {len(new_jobs)} NEW JOBS!")
            print(f"  Proposals saved to: {OUTPUT_FILE}")
        if "--cloud" in __import__("sys").argv:
            print("  [CLOUD MODE] Exiting after one scan.")
            break

        print(f"  Next scan in 30 minutes...")
        time.sleep(1800)

if __name__ == "__main__":
    main()
