import os
import time
from datetime import datetime
from duckduckgo_search import DDGS

KEYWORDS = [
    "Best AI Tools for Small Business 2026",
    "Top 5 CRM Software for Real Estate Agents",
    "How to automate a dental clinic with AI",
    "Best automated trading bots for beginners",
    "Highest paying AI affiliate programs"
]

OUTPUT_DIR = "docs/_posts"

def generate_blog_post(keyword):
    print(f"[*] Generating SEO blog post for: {keyword}")
    
    prompt = f"""
    Write a highly engaging, SEO-optimized product review article for the keyword: "{keyword}".
    Include:
    - A catchy title
    - An introduction that hooks the reader
    - 3-5 product recommendations or strategies
    - Places where the user can insert their affiliate link (write [INSERT AFFILIATE LINK HERE])
    - A strong conclusion encouraging purchase
    Format it in beautiful Markdown. Do NOT wrap the entire response in a markdown code block, just output the raw markdown.
    """
    
    try:
        results = DDGS().chat(prompt, model='gpt-4o-mini')
        
        # Add Jekyll Frontmatter
        date_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        frontmatter = f"---\nlayout: post\ntitle:  \"{keyword}\"\ndate:   {date_str}\ncategories: ai review\n---\n\n"
        
        return frontmatter + results
    except Exception as e:
        print(f"[!] Error generating blog: {e}")
        return None

def main():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        
    print("="*50)
    print(" JULAI AFFILIATE BLOG AUTO-PUBLISHER")
    print("="*50)
    
    for kw in KEYWORDS:
        date_prefix = datetime.now().strftime('%Y-%m-%d')
        safe_kw = kw.replace(' ', '-').replace(',', '').lower()
        filename = f"{OUTPUT_DIR}/{date_prefix}-{safe_kw}.md"
        
        # Check if we already wrote a post for this keyword
        already_written = False
        for f in os.listdir(OUTPUT_DIR):
            if safe_kw in f:
                already_written = True
                break
                
        if already_written:
            continue # Skip if already written
            
        content = generate_blog_post(kw)
        if content:
            with open(filename, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"[+] Successfully wrote: {filename}")
            
        if "--cloud" in __import__("sys").argv:
            print("[*] Cloud mode enabled. Exiting after 1 article.")
            break
            
        time.sleep(10)

if __name__ == "__main__":
    main()
