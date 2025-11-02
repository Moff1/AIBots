import os
import shutil
from openai import OpenAI
from moviepy import (
    ImageClip, 
    TextClip, 
    CompositeVideoClip, 
    AudioFileClip,
    concatenate_videoclips,
    VideoFileClip
)
from pathlib import Path
from dotenv import load_dotenv

# Load API key from .env file
#load_dotenv()
#openai.api_key = os.getenv("OPENAI_API_KEY")

# --- Configuration ---
VIDEO_DIR = r"D:\TikTok\data\Favorites\videos"
AUDIO_DIR = "temp_audio/"
SORTED_DIR = "sorted/"

# --- Ensure folders exist ---
Path(AUDIO_DIR).mkdir(exist_ok=True)
Path(SORTED_DIR).mkdir(exist_ok=True)


client = OpenAI()

def extract_audio(video_path, audio_path):
    clip = VideoFileClip(video_path)
    
    if clip.audio is None:
        print(f"⚠️ No audio track found in: {video_path}")
        clip.close()
        return False  # Signal to skip this video

    clip.audio.write_audiofile(audio_path, logger=None)
    clip.close()
    return True

def transcribe_audio(audio_path):
    with open(audio_path, "rb") as audio_file:
        transcript = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file
        )
        return transcript.text

def classify_transcript(transcript):
    prompt = f"""You are a TikTok video content classifier. Given a transcript of a video, your job is to:

1. Choose the best matching category from this list:
   - Comedy
   - Motivation
   - Education
   - Fashion
   - Tech
   - Lifestyle

2. If none of the categories apply well, generate a **new concise category name** (one or two words max) that describes the video content.

Transcript:
\"\"\"{transcript}\"\"\"

Respond ONLY with the category name (existing or newly created). No explanations."""
    
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
    return response['choices'][0]['message']['content'].strip()


def sort_video(video_path, category):
    category_dir = os.path.join(SORTED_DIR, category)
    Path(category_dir).mkdir(parents=True, exist_ok=True)
    shutil.move(video_path, os.path.join(category_dir, os.path.basename(video_path)))

def main():
    video_files = [f for f in os.listdir(VIDEO_DIR) if f.endswith(('.mp4', '.mov'))]
    
    for video_file in video_files:
        video_path = os.path.join(VIDEO_DIR, video_file)
        audio_path = os.path.join(AUDIO_DIR, f"{Path(video_file).stem}.mp3")

        print(f"Processing {video_file}...")
        try:
            if not extract_audio(video_path, audio_path):
                continue  # Skip if no audio
            transcript = transcribe_audio(audio_path)
            category = classify_transcript(transcript)
            sort_video(video_path, category)
            print(f"Sorted '{video_file}' into '{category}'")
        except Exception as e:
            print(f"Failed to process {video_file}: {e}")

if __name__ == "__main__":
    main()