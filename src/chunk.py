import re
import os


# ---------- CLEAN TEXT ----------

# CLEANING TEXT
def clean_text(text):
    text = re.sub(r"\[.*?\]", "", text)                        # remove [Music]
    text = re.sub(r"\s+", " ", text)                           # normalize spaces
    text = text.replace(" ,", ",").replace(" .", ".")
    return text.strip()


# ---------- BETTER SENTENCE SPLIT ----------
# SENTENCE SPLIT
def split_sentences(text):                                                          
    sentences = re.split(r'(?<=[.!?]) +', text)               # handles ., ?, !
    return [s.strip() for s in sentences if s.strip()]


# ---------- CHUNKING ----------
# CHUNKING
def chunk_text(text, chunk_size=800):
    sentences = split_sentences(text)

    chunks = []
    current_chunk = ""

    for sentence in sentences:
        if len(current_chunk) + len(sentence) < chunk_size:
            current_chunk += sentence + " "
        else:
            chunks.append(current_chunk.strip())
            current_chunk = sentence + " "

    if current_chunk:
        chunks.append(current_chunk.strip())

    return chunks


# ---------- MAIN PIPELINE ----------
# PROCESSES ALL TRANSCRIPTS AND SAVES CHUNKS
def process_all_transcripts():

    os.makedirs("data/chunks", exist_ok=True)

    files = sorted(os.listdir("data/transcripts"))                       # deterministic approach

    print(f"Found {len(files)} transcript files")

    for file in files:

        transcript_path = f"data/transcripts/{file}"

        # skip if already chunked
        existing_chunks = [
            f for f in os.listdir("data/chunks")
            if f.startswith(file + "_")
        ]

        if existing_chunks:
            print(f"Skipping {file} (already chunked)")
            continue

        print(f"\nProcessing: {file}")

        with open(transcript_path, "r", encoding="utf-8") as f:
            raw_text = f.read()

        if not raw_text.strip():
            print("Empty transcript, skipping")
            continue

        clean = clean_text(raw_text)
        chunks = chunk_text(clean)

        print(f"Generated {len(chunks)} chunks")

        for i, chunk in enumerate(chunks):
            out_path = f"data/chunks/{file}_{i}.txt"
            with open(out_path, "w", encoding="utf-8") as out:
                out.write(chunk)

        print(f"Saved chunks for {file}")

    print("\nChunking complete")