"""
JulAI Solutions - ALL-IN-ONE MONEY DAEMON
==========================================
Single script. Runs forever. Does everything automatically:
  1. Sends cold emails to prospects every 3 minutes
  2. Auto-generates personalized emails per industry
  3. Logs every action
  4. Reports status every cycle

REQUIRES: JULAI_EMAIL and JULAI_EMAIL_PASSWORD environment variables.
"""
import smtplib
import csv
import os
import sys
import time
import json
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

# Force UTF-8
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROSPECTS_FILE = os.path.join(BASE_DIR, "prospects.csv")
SENT_LOG = os.path.join(BASE_DIR, "email_sent_log.csv")
STATUS_FILE = os.path.join(BASE_DIR, "daemon_status.json")

DEMO = "https://julai-agency-app.vercel.app"
VIRIDI = "https://viridi-demo.vercel.app"
PORTFOLIO = "https://m-alzayan.vercel.app"

PAIN_MAP = {
    "dental": "missed calls and appointment booking",
    "real estate": "lead follow-up and showing bookings",
    "restaurant": "order taking and reservations",
    "law": "client intake and scheduling",
    "e-commerce": "customer support inquiries",
    "insurance": "lead qualification and policy questions",
    "car dealership": "inbound sales calls and test drive bookings",
    "gym": "membership inquiries and class bookings",
    "hotel": "reservations and guest inquiries",
    "medical": "appointment scheduling and patient inquiries",
}

def get_email_body(name, company, industry, language):
    first = name.split()[0] if name else "there"
    pain = PAIN_MAP.get(industry.lower().strip(), "manual repetitive tasks")

    if language.strip().lower() == "ar":
        return f"""مرحبا {first},

معاك محمد الزيان من JulAI Solutions.

بنبني أنظمة ذكاء اصطناعي بترد على المكالمات وبتتابع العملاء تلقائياً 24 ساعة بالعربي والإنجليزي.

عندنا عميل كان بيفقد 40% من المكالمات بعد ساعات العمل. دلوقتي صفر مكالمات فايتة.

جرّب النسخة الحية دلوقتي: {DEMO}
اضغط على أيقونة الميكروفون واتكلم بالعربي.

يبدأ من $500 تأسيس + $100 شهرياً. مفيش التزام طويل.

يستحق 15 دقيقة نتكلم فيها؟

تحياتي،
محمد الزيان
شريك مؤسس، JulAI Solutions
{PORTFOLIO}"""
    
    if "dental" in industry.lower():
        return f"""Hi {first},

I build AI receptionists specifically for dental clinics.

The AI answers every call 24/7, books appointments to your calendar, handles insurance and pricing FAQs, and texts patients appointment reminders.

One of my clients went from missing 40% of after-hours calls to zero missed calls.

You can try the AI live right now: {DEMO}
Click the mic icon and talk to it.

Starting at $500 setup + $100/month. No long-term commitment.

Worth a 15-minute call this week to see if it fits {company}?

Best,
Mohamed Al Zayan
Co-Founder, JulAI Solutions
{PORTFOLIO}"""

    if "real estate" in industry.lower():
        return f"""Hi {first},

I build AI systems that follow up with every real estate lead in under 60 seconds.

The AI calls or texts new leads immediately, qualifies them with your custom questions, books showings on your calendar, and logs everything to your CRM.

Most agencies lose 60% of leads because follow-up takes too long. This eliminates that.

Live demo you can try right now: {DEMO}

We also built a bilingual AI sales assistant for an EV manufacturer that handles every inbound inquiry automatically: {VIRIDI}

Worth a quick call this week?

Best,
Mohamed Al Zayan
Co-Founder, JulAI Solutions
{PORTFOLIO}"""

    return f"""Hi {first},

I build AI voice agents and automation systems that handle {pain} for {industry} businesses.

The AI works 24/7 in Arabic and English. It answers calls, qualifies leads, books appointments, and logs everything to your CRM automatically.

You can try a live version right now: {DEMO}
Click the mic icon and talk to it.

Case study: We built a bilingual AI sales assistant for an EV manufacturer that handles every inbound inquiry automatically: {VIRIDI}

If this is relevant to {company}, I am happy to show you a 15-minute demo this week.

Best,
Mohamed Al Zayan
Co-Founder, JulAI Solutions
{PORTFOLIO}"""

def get_subject(name, company, industry, language):
    first = name.split()[0] if name else "there"
    pain = PAIN_MAP.get(industry.lower().strip(), "manual tasks")
    
    if language.strip().lower() == "ar":
        return f"AI يتولى {pain} تلقائياً لـ {company}"
    if "dental" in industry.lower():
        return f"AI receptionist for {company} - handles every call 24/7"
    if "real estate" in industry.lower():
        return f"AI that follows up with every lead in 60 seconds - for {company}"
    return f"AI that handles {pain} for {company} - live demo inside"

def load_sent_emails():
    sent = set()
    if os.path.exists(SENT_LOG):
        with open(SENT_LOG, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            next(reader, None)
            for row in reader:
                if len(row) >= 2 and not row[5].startswith("failed"):
                    sent.add(row[1].strip().lower())
    return sent

def log_sent(name, email, company, industry, status):
    exists = os.path.exists(SENT_LOG)
    with open(SENT_LOG, "a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        if not exists:
            w.writerow(["date", "email", "name", "company", "industry", "status"])
        w.writerow([datetime.now().strftime("%Y-%m-%d %H:%M"), email, name, company, industry, status])

def update_status(total_sent, total_failed, last_action, running=True):
    with open(STATUS_FILE, "w") as f:
        json.dump({
            "running": running,
            "total_sent": total_sent,
            "total_failed": total_failed,
            "last_action": last_action,
            "last_update": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "email": os.environ.get("JULAI_EMAIL", "not set"),
        }, f, indent=2)

def send_email_with_reconnect(email, password, target_email, msg):
    # Connect fresh every time to avoid connection timeouts
    server = smtplib.SMTP("smtp.gmail.com", 587, timeout=30)
    server.ehlo()
    server.starttls()
    server.ehlo()
    server.login(email, password)
    server.sendmail(email, target_email, msg.as_string())
    server.quit()

def main():
    print("=" * 60)
    print("  JULAI MONEY DAEMON - FULLY AUTOMATIC (ANTI-TIMEOUT)")
    print("=" * 60)

    email = os.environ.get("JULAI_EMAIL", "").strip()
    password = os.environ.get("JULAI_EMAIL_PASSWORD", "").strip()

    if not email or not password:
        print("\n  [ERROR] Gmail credentials not set in environment.")
        update_status(0, 0, "ERROR: No credentials", running=False)
        return

    print(f"  Email: {email}")
    print(f"  Password: {'*' * len(password)}")

    while True:
        # Load prospects
        if not os.path.exists(PROSPECTS_FILE):
            time.sleep(60)
            continue

        all_prospects = []
        with open(PROSPECTS_FILE, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get("email", "").strip() and not row["email"].startswith("example@"):
                    all_prospects.append(row)

        sent_emails = load_sent_emails()
        unsent = [p for p in all_prospects if p["email"].strip().lower() not in sent_emails]

        if not unsent:
            print(f"\n  [{datetime.now().strftime('%H:%M')}] All prospects emailed. Monitoring for new ones...")
            update_status(len(sent_emails), 0, "Monitoring for new prospects", running=True)
            time.sleep(1800)
            continue

        if "--cloud" in sys.argv:
            unsent = unsent[:10]

        print(f"\n  Found {len(unsent)} unsent prospects. Sending...")
        
        total_sent = len(sent_emails)
        total_failed = 0

        for i, prospect in enumerate(unsent, 1):
            name = prospect.get("name", "").strip()
            target_email = prospect.get("email", "").strip()
            company = prospect.get("company", "your business").strip()
            industry = prospect.get("industry", "service").strip()
            language = prospect.get("language", "en").strip()

            subject = get_subject(name, company, industry, language)
            body = get_email_body(name, company, industry, language)

            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = f"Mohamed Al Zayan <{email}>"
            msg["To"] = target_email
            msg.attach(MIMEText(body, "plain", "utf-8"))

            try:
                send_email_with_reconnect(email, password, target_email, msg)
                total_sent += 1
                log_sent(name, target_email, company, industry, "sent")
                status_msg = f"SENT #{total_sent}: {name} at {company} ({target_email})"
                print(f"  [{i}/{len(unsent)}] {status_msg}")
                update_status(total_sent, total_failed, status_msg)
            except Exception as e:
                total_failed += 1
                log_sent(name, target_email, company, industry, f"failed: {e}")
                status_msg = f"FAILED: {name} ({target_email}) - {e}"
                print(f"  [{i}/{len(unsent)}] {status_msg}")
                update_status(total_sent, total_failed, status_msg)

            if i < len(unsent) and "--cloud" not in sys.argv:
                time.sleep(180)

        if "--cloud" in sys.argv:
            print("  [CLOUD MODE] Finished batch. Exiting.")
            break

if __name__ == "__main__":
    main()
