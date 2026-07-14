import os
import time
import random
from duckduckgo_search import DDGS
from datetime import datetime

OUTPUT_DIR = "youtube_shorts"

# Infinite topic generator prompts
PROMPTS = [
    "Give me one catchy, viral title for a 60-second YouTube Short about dark psychology. Just the title, nothing else.",
    "Give me one catchy, viral title for a 60-second YouTube Short about a scary true story. Just the title, nothing else.",
    "Give me one catchy, viral title for a 60-second YouTube Short about building extreme wealth. Just the title, nothing else.",
    "Give me one catchy, viral title for a 60-second YouTube Short about a crazy historical fact. Just the title, nothing else."
]

def generate_topic():
    try:
        results = DDGS().chat(random.choice(PROMPTS), model='gpt-4o-mini')
        return results.strip().replace('"', '')
    except Exception as e:
        print(f"[!] Topic generation error: {e}")
        return None

def generate_script(topic):
    print(f"[*] Generating script for: {topic}")
    prompt = f"Write a 60-word viral YouTube Shorts script about: '{topic}'. Do not include any stage directions or visual cues, ONLY the spoken words."
    try:
        results = DDGS().chat(prompt, model='gpt-4o-mini')
        return results
    except Exception as e:
        print(f"[!] DDGS Error: {e}")
        return None

def main():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        
    print("="*50)
    print(" JULAI INFINITE YOUTUBE SHORTS ENGINE")
    print("="*50)
    
    # Generate 3 shorts per run (Optimal for YouTube algorithm without getting flagged for spam)
    for i in range(3):
        topic = generate_topic()
        if not topic:
            continue
            
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        safe_name = "".join([c for c in topic if c.isalpha() or c.isdigit() or c==' ']).rstrip()[:30].replace(' ', '_')
        video_file = f"{OUTPUT_DIR}/short_{timestamp}_{safe_name}.mp4"
            
        script_text = generate_script(topic)
        if not script_text:
            continue
            
        print(f"[+] Script generated:\n{script_text}")
        
        with open("temp_script.txt", "w", encoding="utf-8") as f:
            f.write(script_text)
            
        audio_file = f"temp_audio.mp3"
        print("[*] Generating AI Voiceover...")
        os.system(f'edge-tts --text "{script_text}" --write-media "{audio_file}" --voice "en-US-ChristopherNeural"')
        
        # Generate random background color
        colors = ["black", "darkblue", "darkred", "darkgreen", "purple"]
        bg_color = random.choice(colors)
        bg_image = "temp_bg.png"
        os.system(f'ffmpeg -f lavfi -i color=c={bg_color}:s=1080x1920 -frames:v 1 {bg_image} -y')
            
        print("[*] Stitching final video...")
        safe_topic = topic.replace("'", "")
        # Add word wrap to the text so it fits on screen
        ffmpeg_cmd = (
            f'ffmpeg -loop 1 -i {bg_image} -i "{audio_file}" '
            f'-vf "drawtext=text=\'{safe_topic}\':fontcolor=white:fontsize=80:x=(w-text_w)/2:y=(h-text_h)/2:autofit=1:box=1:boxcolor=black@0.5:boxborderw=20" '
            f'-c:v libx264 -c:a aac -shortest "{video_file}" -y'
        )
        os.system(ffmpeg_cmd)
        
        print(f"[+] Successfully created viral short: {video_file}")
        
        if "--cloud" in __import__("sys").argv:
            print("[*] Cloud mode enabled. Finished 1 video in loop.")

if __name__ == "__main__":
    main()
