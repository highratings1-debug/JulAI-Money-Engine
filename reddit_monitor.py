"""
JulAI Solutions — Reddit Lead Finder
Monitors Reddit for posts where people need AI automation, voice AI, or chatbots.
Generates ready-to-post helpful replies that position JulAI without hard-selling.
Saves everything to reddit_leads.md.

Runs every 45 minutes. Uses Reddit's public JSON API (no auth needed).

Usage: python reddit_monitor.py
"""
import urllib.request
import json
import os
import time
import hashlib
from datetime import datetime

SUBREDDITS = [
    "smallbusiness",
    "Entrepreneur",
    "artificial",
    "n8n",
    "SaaS",
    "automation",
]

KEYWORDS = [
    "ai agent", "ai chatbot", "voice ai", "ai receptionist",
    "n8n", "workflow automation", "ai automation",
    "chatbot for business", "automate customer",
    "automate calls", "automate email", "lead generation ai",
    "need a bot", "looking for automation", "crm automation",
    "appointment booking", "missed calls",
]

SEEN_FILE = "reddit_seen.json"
OUTPUT_FILE = "reddit_leads.md"

REPLY_TEMPLATE = """Great question. I work in this space and here are some practical thoughts:

{helpful_advice}

I built something similar for an EV manufacturer in Egypt — a bilingual AI agent that handles calls, qualifies leads, and logs everything to a CRM automatically.

If you want to see a working example, there is a live demo at julai-agency-app.vercel.app (click the mic to talk to it).

Happy to answer any technical questions about implementation."""

ADVICE_MAP = {
    "chatbot": "For a business chatbot, the key decisions are: (1) which platform (website widget, WhatsApp, Telegram), (2) whether you need it to take actions (book appointments, update CRM) or just answer questions, and (3) your budget. The action-taking bots cost more but generate real ROI. A simple FAQ bot rarely justifies the investment.",
    "voice": "Voice AI has gotten reliable in the last year. The main platforms are Vapi, Retell AI, and Bland AI. The critical factor is latency — your AI needs to respond in under 800ms or the caller notices the delay. Also, human handoff logic is essential. The AI should know when to transfer to a real person.",
    "automation": "For workflow automation, n8n is the most flexible option if you want control. Make.com is easier for simple flows. The real value is in connecting your existing tools — CRM, email, calendar, payment system — into one automated pipeline. Start with your highest-volume manual task and automate that first.",
    "lead_gen": "AI lead generation works best when you combine scraping (finding prospects) with AI personalization (writing custom outreach) and CRM tracking (knowing who responded). The biggest mistake is automating outreach without personalizing it. Generic automated emails get flagged as spam.",
    "receptionist": "AI receptionists work well for high-call-volume businesses like dental clinics, law firms, and real estate. The AI answers 24/7, qualifies the caller, books appointments to your calendar, and sends you a summary. Most businesses miss 30-40% of calls outside hours. The AI eliminates that.",
    "general": "The fastest way to see ROI from AI automation is to identify your most repetitive task — usually it is answering the same questions, following up with leads, or data entry between tools. Automate that one thing first. The compound effect builds from there.",
}

def load_seen():
    if os.path.exists(SEEN_FILE):
        with open(SEEN_FILE, "r") as f:
            return json.load(f)
    return []

def save_seen(seen):
    with open(SEEN_FILE, "w") as f:
        json.dump(seen, f)

def classify_post(title, text):
    combined = (title + " " + text).lower()
    if any(w in combined for w in ["chatbot", "chat bot", "conversational"]):
        return "chatbot"
    if any(w in combined for w in ["voice", "call", "phone", "receptionist"]):
        return "voice"
    if any(w in combined for w in ["lead gen", "lead generation", "prospecting", "outreach"]):
        return "lead_gen"
    if any(w in combined for w in ["receptionist", "front desk", "answer calls"]):
        return "receptionist"
    if any(w in combined for w in ["automat", "workflow", "n8n", "zapier", "make.com"]):
        return "automation"
    return "general"

def fetch_subreddit(subreddit):
    url = f"https://www.reddit.com/r/{subreddit}/new.json?limit=25"
    try:
        req = urllib.request.Request(url, headers={
            "User-Agent": "JulAI-LeadFinder/1.0"
        })
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        return None

def matches_keywords(title, selftext):
    combined = (title + " " + selftext).lower()
    for kw in KEYWORDS:
        if kw.lower() in combined:
            return True
    return False

def run_scan():
    seen = load_seen()
    new_leads = []

    for sub in SUBREDDITS:
        print(f"  Scanning r/{sub}...")
        data = fetch_subreddit(sub)
        if not data or "data" not in data:
            print(f"    Could not fetch r/{sub}")
            continue

        posts = data["data"].get("children", [])
        for post in posts:
            p = post.get("data", {})
            post_id = p.get("id", "")
            title = p.get("title", "")
            selftext = p.get("selftext", "")
            url = f"https://www.reddit.com{p.get('permalink', '')}"
            score = p.get("score", 0)
            num_comments = p.get("num_comments", 0)

            if post_id in seen:
                continue

            if matches_keywords(title, selftext):
                category = classify_post(title, selftext)
                advice = ADVICE_MAP.get(category, ADVICE_MAP["general"])
                reply = REPLY_TEMPLATE.format(helpful_advice=advice)

                new_leads.append({
                    "subreddit": sub,
                    "title": title,
                    "url": url,
                    "score": score,
                    "comments": num_comments,
                    "category": category,
                    "reply": reply,
                    "snippet": selftext[:300]
                })
                seen.append(post_id)

    save_seen(seen)
    return new_leads

def write_leads(leads):
    with open(OUTPUT_FILE, "a", encoding="utf-8") as f:
        f.write(f"\n\n# Reddit Leads Found - {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n")
        if not leads:
            f.write("No new matching posts this scan.\n")
            return

        for i, lead in enumerate(leads, 1):
            f.write(f"---\n\n")
            f.write(f"## Lead {i}: r/{lead['subreddit']} ({lead['score']} upvotes, {lead['comments']} comments)\n\n")
            f.write(f"**Title:** {lead['title']}\n\n")
            f.write(f"**Link:** {lead['url']}\n\n")
            f.write(f"**Category:** {lead['category']}\n\n")
            if lead['snippet']:
                f.write(f"**Post snippet:** {lead['snippet']}...\n\n")
            f.write(f"### READY-TO-POST REPLY:\n\n")
            f.write(f"```\n{lead['reply']}\n```\n\n")

def main():
    print("=" * 60)
    print("  JULAI REDDIT LEAD FINDER")
    print("  Scanning every 45 minutes...")
    print("=" * 60)

    cycle = 0
    while True:
        cycle += 1
        print(f"\n[Scan #{cycle}] {datetime.now().strftime('%Y-%m-%d %H:%M')}...")

        new_leads = run_scan()
        write_leads(new_leads)

        if new_leads:
            print(f"  FOUND {len(new_leads)} NEW LEADS!")
            print(f"  Replies saved to: {OUTPUT_FILE}")
        if "--cloud" in __import__("sys").argv:
            print("  [CLOUD MODE] Exiting after one scan.")
            break

        print(f"  Next scan in 45 minutes...")
        time.sleep(2700)

if __name__ == "__main__":
    main()
