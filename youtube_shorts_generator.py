import os
import time
from duckduckgo_search import DDGS

OUTPUT_DIR = "youtube_shorts"

TOPICS = [
    "3 psychological tricks that make people instantly like you",
    "The secret to building extreme wealth in your 20s",
    "Why you should never tell people your goals",
    "The dark history of how diamonds became valuable"
]

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
        
    for i, topic in enumerate(TOPICS):
        video_file = f"{OUTPUT_DIR}/short_{i}.mp4"
        if os.path.exists(video_file):
            continue
            
        # 1. Generate Script
        script_text = generate_script(topic)
        if not script_text:
            continue
            
        print(f"[+] Script generated:\n{script_text}")
        
        # 2. Generate Audio (Edge TTS)
        # We save the text to a temporary file
        with open("temp_script.txt", "w", encoding="utf-8") as f:
            f.write(script_text)
            
        audio_file = f"{OUTPUT_DIR}/audio_{i}.mp3"
        print("[*] Generating AI Voiceover...")
        os.system(f'edge-tts --text "{script_text}" --write-media "{audio_file}" --voice "en-US-ChristopherNeural"')
        
        # 3. Generate a blank background
        bg_image = "black_bg.png"
        if not os.path.exists(bg_image):
            os.system('ffmpeg -f lavfi -i color=c=black:s=1080x1920 -frames:v 1 black_bg.png -y')
            
        # 4. Stitch together with FFmpeg
        print("[*] Stitching final video...")
        # A simple ffmpeg command that takes the black background, loops it, adds the audio, and overlays the title text
        safe_topic = topic.replace("'", "")
        ffmpeg_cmd = (
            f'ffmpeg -loop 1 -i {bg_image} -i "{audio_file}" '
            f'-vf "drawtext=text=\'{safe_topic}\':fontcolor=white:fontsize=60:x=(w-text_w)/2:y=(h-text_h)/2" '
            f'-c:v libx264 -c:a aac -shortest "{video_file}" -y'
        )
        os.system(ffmpeg_cmd)
        
        print(f"[+] Successfully created viral short: {video_file}")
        
        if "--cloud" in __import__("sys").argv:
            print("[*] Cloud mode enabled. Exiting after 1 video.")
            break

if __name__ == "__main__":
    main()
