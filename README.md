# 📘 Building Large Language Models from Scratch — Book Generator

This project converts a YouTube lecture playlist into a structured, readable technical book using a reproducible LLM-powered pipeline.

---

## Objective

Given a lecture playlist, the pipeline:

1. Extracts transcripts
2. Breaks them into chunks
3. Extracts key topics
4. Organizes topics into chapters
5. Generates a full book
6. Exports to PDF

---

## Source Playlist

https://youtube.com/playlist?list=PLPTV0NXA_ZSgsLAr8YCgCwhPIJNNtexWu

---

## Pipeline Overview

```text
Extract → Chunk → Topics → Chapters → Book → PDF
```

Each step is modular and resumable.

---

## How to Run

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

---

### 2. Set environment variables

Create a `.env` file:

```env
GEMINI_API_KEY=your_api_key_here
```

---

### 3. Run the full pipeline

```bash
python run_pipeline.py all
```

---

## Running Individual Steps

```bash
python run_pipeline.py extract
python run_pipeline.py chunk
python run_pipeline.py topics
python run_pipeline.py chapters
python run_pipeline.py book
python run_pipeline.py pdf
```

---

## Notes on Rate Limits & Execution

### Transcript Extraction (YouTube)

* Transcript extraction may be rate-limited depending on your IP.
* The pipeline is designed to:

  * Skip already processed videos
  * Resume safely across runs

* The extraction has limit of 10, so rerun the following command until it shows "Extraction complete"

If extraction stops midway:

```bash
python run_pipeline.py extract
```

Run it again to continue from where it left off.

---

### LLM (Gemini API) Limits

* Free-tier Gemini API has strict limits (requests per minute/day).
* The pipeline handles this using:

  * batching
  * retries with delays
  * resumable processing

 If you hit limits:

* Wait and rerun the step, OR
* Use a higher quota API plan for smoother execution

---

## Reproducibility

* All intermediate outputs are saved:

  * transcripts
  * chunks
  * topics
  * chapters
* The pipeline is **fully resumable**
* Re-running commands will skip completed steps

---

## Output

Final outputs are stored in:

```text
output/book.md
output/book.pdf
```

---

## Design Principles

* No hallucination: Content is derived strictly from transcripts
* Structured generation: Multi-stage pipeline (not single prompt)
* Deterministic behavior: Low-temperature generation
* Resume-safe: Handles interruptions and rate limits

---

## Tech Stack

* Python
* youtube-transcript-api (transcript extraction)
* Gemini API (LLM)
* Markdown → PDF conversion

---

## Future Improvements
While the current pipeline successfully generates a structured book from the playlist, there are several areas for further enhancement:
### Content Quality
* Improve narrative flow across chapters (reduce repetition and increase cohesion)
* Add cross-chapter references to maintain continuity
* Enhance writing style to better resemble human-authored technical books

### Source Grounding
* Map chapters and sections directly to specific videos in the playlist
* Add timestamps or references for stronger traceability
* Optionally validate key concepts using external sources

### LLM Enhancements
* Experiment with higher-capability models for improved writing quality
* Introduce multi-pass refinement (draft → review → improve)
* Add consistency checks to reduce duplication and redundancy

### Pipeline Robustness
* Improve handling of API rate limits with smarter scheduling or queuing
* Add automatic retries with persistent state tracking
* Enable parallel processing for faster execution

---

## Summary

This project demonstrates how to build a reproducible system that transforms unstructured lecture content into a structured technical book using LLMs.
