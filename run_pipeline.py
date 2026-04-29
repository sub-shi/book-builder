import sys
import json
import os

from src.extract import get_video_ids, process_subtitles
from src.chunk import process_all_transcripts
from src.structure import (
    extract_all_topics,
    combine_all_topics,
    generate_chapters,
    generate_book,
    convert_to_pdf
)

PLAYLIST_URL = "https://youtube.com/playlist?list=PLPTV0NXA_ZSgsLAr8YCgCwhPIJNNtexWu"

PROGRESS_FILE = "progress.json"


# -------------------- PROGRESS HELPERS --------------------
def load_progress():
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, "r") as f:
            return json.load(f)
    return {}


def save_progress(progress):
    with open(PROGRESS_FILE, "w") as f:
        json.dump(progress, f, indent=2)


# -------------------- MAIN --------------------
if __name__ == "__main__":
    step = sys.argv[1] if len(sys.argv) > 1 else "all"
    force = "--force" in sys.argv

    print(f"Running step: {step} | force={force}")

    progress = load_progress()

    # -------------------- SINGLE STEPS --------------------
    if step == "extract":
        vids = get_video_ids(PLAYLIST_URL)
        process_subtitles(vids)

    elif step == "chunk":
        process_all_transcripts()

    elif step == "topics":
        extract_all_topics()

    elif step == "chapters":
        combine_all_topics()
        generate_chapters()

    elif step == "book":
        if force:
            progress["book_done"] = False

        generate_book()
        progress["book_done"] = True
        save_progress(progress)

    elif step == "pdf":
        convert_to_pdf()

    # -------------------- FULL PIPELINE --------------------
    elif step == "all":


        vids = get_video_ids(PLAYLIST_URL)
        print(f"Found {len(vids)} videos")

        # -------- EXTRACT --------
        transcript_dir = "data/transcripts"
        transcript_files = os.listdir(transcript_dir) if os.path.exists(transcript_dir) else []

        if force or (not progress.get("extract_done") and len(transcript_files) == 0):
            print("\n Extracting transcripts...")

            try:
                process_subtitles(vids)
            except Exception as e:
                print("Extraction failed, continuing:", e)

            progress["extract_done"] = True
            save_progress(progress)

        else:
            print("Skipping extract (transcripts already exist)")

        # -------- CHUNK --------
        if force or not progress.get("chunk_done"):
            print("\nProcessing chunks...")
            process_all_transcripts()
            progress["chunk_done"] = True
            save_progress(progress)
        else:
            print("Skipping chunk")

        # -------- TOPICS --------
        if force or not progress.get("topics_done"):
            print("\nExtracting topics...")
            extract_all_topics()
            progress["topics_done"] = True
            save_progress(progress)
        else:
            print("Skipping topics")

        # -------- CHAPTERS --------
        if force or not progress.get("chapters_done"):
            print("\n Combining topics...")
            combine_all_topics()
            print("\n Generating chapters...")
            generate_chapters()

            progress["chapters_done"] = True
            save_progress(progress)
        else:
            print("Skipping chapters")

        # -------- BOOK --------
        book_exists = os.path.exists("output/book.md")

        if force or not progress.get("book_done") or not book_exists:
            print("\n Generating book...")
            generate_book()
            progress["book_done"] = True
            save_progress(progress)
        else:
            print("Skipping book")

        # -------- PDF --------
        pdf_exists = os.path.exists("output/book.pdf")

        if force or not progress.get("pdf_done") or not pdf_exists:
            print("\n Generating PDF...")
            convert_to_pdf()
            progress["pdf_done"] = True
            save_progress(progress)
        else:
            print("Skipping PDF")

    # -------------------- RESET --------------------
    elif step == "reset":
        if os.path.exists(PROGRESS_FILE):
            os.remove(PROGRESS_FILE)
            print(" Deleted progress.json")
        else:
            print("progress.json not found")

        # Optional cleanup
        if os.path.exists("output/book.md"):
            os.remove("output/book.md")
            print("Deleted book.md")

        if os.path.exists("output/book.pdf"):
            os.remove("output/book.pdf")
            print("Deleted book.pdf")

        print("Reset complete")


    # -------------------- INVALID --------------------
    else:
        print("Invalid step. Use: extract | chunk | topics | chapters | book | pdf | all | reset")