import os
import time
import random
import subprocess
import json
from youtube_transcript_api import YouTubeTranscriptApi


# ---------- GET VIDEO IDS ----------
# GET VIDEO IDS FROM PLAYLIST
def get_video_ids(playlist_url):
    result = subprocess.run(
        ["yt-dlp", "--flat-playlist", "-J", playlist_url],
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        print("Failed to fetch playlist")
        print(result.stderr)
        return []

    data = json.loads(result.stdout)
    return [entry["id"] for entry in data.get("entries", []) if entry]


# ---------- FETCH TRANSCRIPT (API) ----------

# FETCH TRANSCRIPT USING API (YT-TRANSCRIPT-API)
def fetch_transcript(video_id):
    try:
        api = YouTubeTranscriptApi()

        transcript = api.fetch(video_id)

        text = " ".join([t.text for t in transcript])

        return text

    except Exception as e:
        print(f"Transcript API failed for {video_id}: {e}")
        return None


# ---------- MAIN PIPELINE ----------
# PROCESSES SUBTITLES
def process_subtitles(video_ids):

    os.makedirs("data/transcripts", exist_ok=True)

    MAX_PER_RUN = 10                                 # safe limit to avoid long runs and API issues
    processed = 0

    start_time = time.time()

    for vid in video_ids:

        if processed >= MAX_PER_RUN:
            print("Batch limit reached. Resume later.")
            break

        transcript_path = f"data/transcripts/{vid}.txt"

        # Skip already done
        if os.path.exists(transcript_path):
            print(f"Skipping {vid}")
            continue

        print(f"\nProcessing {vid}")

        text = fetch_transcript(vid)

        if not text:
            print(f"Skipping {vid}")
            continue

        # Save transcript
        with open(transcript_path, "w", encoding="utf-8") as f:
            f.write(text)

        print(f"Saved {vid}")
        processed += 1

        # small delay (avoid API spam)
        sleep_time = random.uniform(1, 3)
        time.sleep(sleep_time)

        # safety stop (optional)
        if time.time() - start_time > 1800:
            print("Stopping to avoid long run. Resume later.")
            break

    print("\nExtraction complete")