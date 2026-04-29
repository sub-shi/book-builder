import os
import time
import math
import re
import google.generativeai as genai
from src.utils import cached_generate
from dotenv import load_dotenv
import os

load_dotenv()

# ---------- CONFIG ----------
API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=API_KEY)

model = genai.GenerativeModel("gemini-2.5-flash-lite")

MAX_DAILY_REQUESTS = 20
SAFE_REQUESTS = 18


# ---------- TOPIC EXTRACTION ----------
# EXTRACT TOPICS FROM CHUNK
def extract_topics_from_chunk(chunk_text):

    prompt = f"""
You are analyzing lecture transcripts.

Extract ALL unique key concepts.

Rules:
- Only use information from text
- No hallucination
- Merge duplicates
- Keep concise bullet points

Text:
{chunk_text}

Output:
- topic 1
- topic 2
"""

    return cached_generate(model, prompt)


# ---------- EXTRACT ALL TOPICS ----------
# PROCESSES ALL CHUNKS IN BATCHES TO EXTRACT TOPICS
def extract_all_topics():

    os.makedirs("data/topics", exist_ok=True)

    files = sorted(os.listdir("data/chunks"))
    total_chunks = len(files)

    batch_size = max(1, math.ceil(total_chunks / MAX_DAILY_REQUESTS))

    print(f"Total chunks: {total_chunks}")
    print(f"Batch size: {batch_size}")

    for i in range(0, total_chunks, batch_size):

        output_file = f"data/topics/batch_{i}.txt"

        # SKIP LOGIC
        if os.path.exists(output_file):
            print(f"Skipping batch {i}")
            continue

        batch_files = files[i:i+batch_size]

        combined_text = ""
        for file in batch_files:
            with open(f"data/chunks/{file}", "r", encoding="utf-8") as f:
                combined_text += f.read() + "\n\n"

        print(f"Processing batch {i}")

        retry = 0

        while retry < 3:
            try:
                topics = extract_topics_from_chunk(combined_text)

                with open(output_file, "w", encoding="utf-8") as out:
                    out.write(topics)

                print(f"Batch {i} done")
                break

            except Exception as e:
                retry += 1
                wait = 60 * retry
                print(f"Retry {retry} in {wait}s")
                time.sleep(wait)

        time.sleep(15)


# ---------- COMBINE TOPICS ----------
# COMBINE AND DEDUPLICATE TOPICS INTO ONE FILE
def combine_all_topics():
    import os
    import re

    topic_files = sorted(os.listdir("data/topics"))

    raw_topics = []

    # -------------------- LOAD --------------------
    for file in topic_files:
        with open(f"data/topics/{file}", "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()

                if not line.startswith("-"):
                    continue

                # remove leading "-"
                topic = line.lstrip("-").strip()

                # normalize spacing
                topic = re.sub(r"\s+", " ", topic)

                # normalize casing (important)
                topic = topic.strip().capitalize()

                if topic:
                    raw_topics.append(topic)

    if not raw_topics:
        print("No topics found")
        return

    # -------------------- DEDUP --------------------
    unique_topics = []
    seen = set()

    for topic in raw_topics:
        key = topic.lower()

        # simple semantic dedup (very effective)
        if key in seen:
            continue

        # avoid near duplicates like:
        # "Vector embedding" vs "Vector embeddings"
        if any(key in s or s in key for s in seen):
            continue

        seen.add(key)
        unique_topics.append(topic)

    # -------------------- SORT (LOGICAL ORDER IMPROVEMENT) --------------------
    # Keep original order but slightly group similar concepts
    unique_topics = sorted(unique_topics)

    # -------------------- SAVE --------------------
    with open("data/all_topics.txt", "w", encoding="utf-8") as out:
        for topic in unique_topics:
            out.write(f"- {topic}\n")

    print(f"Topics combined ({len(unique_topics)} unique)")



# ---------- GENERATE CHAPTERS ----------
# GENERATE CHAPTERS FROM TOPICS
def generate_chapters():

    output_path = "data/chapters.txt"

    # Skip only if VALID file exists
    if os.path.exists(output_path):
        with open(output_path, "r", encoding="utf-8") as f:
            existing = f.read().strip()

        if existing:
            print("⏭ Chapters already exist")
            return
        else:
            print("Empty chapters file found. Regenerating...")

    # Load topics
    with open("data/all_topics.txt", "r", encoding="utf-8") as f:
        topics = f.read()

    if not topics.strip():
        print("❌ No topics found. Cannot generate chapters.")
        return

    # Stronger prompt
    prompt = f"""
You are organizing a technical book.

Given the following topics:

{topics}

Your task:
- Remove duplicates
- Group related topics into chapters
- Ensure each topic appears ONLY ONCE
- Maintain logical learning progression

STRICT RULES:
- No repetition anywhere
- Each topic must appear in exactly one chapter
- Avoid redundant or similar entries

Output format:

Chapter 1: Title
- topic
- topic

Chapter 2: Title
- topic
- topic
"""

    text = cached_generate(model, prompt)

    # ADD THIS HERE
    lines = text.splitlines()
    seen = set()
    cleaned = []

    for line in lines:
        if line.strip().startswith("-"):
            if line not in seen:
                seen.add(line)
                cleaned.append(line)
        else:
            cleaned.append(line)

    text = "\n".join(cleaned)
    # END

    # then save
    with open("data/chapters.txt", "w", encoding="utf-8") as out:
        out.write(text)
    print("Chapters generated")



# ---------- GENERATE BOOK ----------
# GENERATE BOOK FROM CHAPTERS
def generate_book():

    if os.path.exists("output/book.md"):
        print("Book already exists")
        return

    with open("data/chapters.txt", "r", encoding="utf-8") as f:
        chapters = f.read()

    chapter_blocks = chapters.split("Chapter ")[1:]

    os.makedirs("output", exist_ok=True)

    PLAYLIST_URL = "https://youtube.com/playlist?list=PLPTV0NXA_ZSgsLAr8YCgCwhPIJNNtexWu"

    full_book = f"""# Building Large Language Models from Scratch

> Derived from lecture series: {PLAYLIST_URL}

"""

    # TOC
    full_book += "## Table of Contents\n\n"

    titles = []
    for ch in chapter_blocks:
        title = ch.splitlines()[0].replace("**", "").strip()
        titles.append(title)
        full_book += f"- {title}\n"

    full_book += "\n---\n\n"

    # chapters
    for ch in chapter_blocks:

        ch = "Chapter " + ch.strip()
        title = ch.splitlines()[0].replace("**", "").strip()

        print(f"{title}")

        prompt = f"""
Write chapter.

Rules:
- No hallucination
- Use only provided content
- Build on previous chapters progressively
- Avoid repetitive phrasing
- Use varied sentence structures
- Do not repeat concepts explained earlier
- Write like a human instructor, not a template

Format:
## {title}
### Overview
### Key Concepts
### Technical Explanation
### Practical Intuition
### Insight
### Summary

Content:
{ch}
"""

        text = cached_generate(model, prompt)

        if not text:
            continue

        text = text.encode("utf-8", "ignore").decode("utf-8")

        # fix formatting
        text = re.sub(r'([a-z])([A-Z])', r'\1 \2', text)

        if not text.startswith("##"):
            text = f"## {title}\n\n" + text

        full_book += f"{text}\n\n---\n\n"

        time.sleep(10)

    with open("output/book.md", "w", encoding="utf-8") as f:
        f.write(full_book)

    print("Book generated")


# ---------- PDF ----------
# CONVERT MARKDOWN BOOK TO PDF
def convert_to_pdf():

    import markdown
    import pdfkit

    if not os.path.exists("output/book.md"):
        print("book.md missing")
        return

    with open("output/book.md", "r", encoding="utf-8") as f:
        html = markdown.markdown(f.read(), extensions=['extra'])

    styled = f"""
    <html><body style="font-family:Georgia;margin:60px;line-height:1.8;">
    {html}
    </body></html>
    """

    config = pdfkit.configuration(
        wkhtmltopdf=r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe"
    )

    pdfkit.from_string(styled, "output/book.pdf", configuration=config)

    print("PDF generated")