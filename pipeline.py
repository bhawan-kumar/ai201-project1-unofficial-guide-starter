import re
import random
from pathlib import Path

DATA_DIR = Path("data")


def parse_professor_file(filepath):
    """
    Parse one professor .txt file into a list of chunk dicts.
    Each chunk = one student review with professor metadata prepended.
    """
    text = filepath.read_text(encoding="utf-8")

    # Split header from reviews on the === separator line
    if "========================================" not in text:
        print(f"  WARNING: no separator found in {filepath.name}, skipping")
        return []

    header_raw, reviews_raw = text.split("========================================", 1)

    # Parse header fields
    header = {}
    for line in header_raw.strip().splitlines():
        if ": " in line:
            key, val = line.split(": ", 1)
            header[key.strip()] = val.strip()

    professor      = header.get("Professor", "Unknown")
    department     = header.get("Department", "Unknown")
    overall_rating = header.get("Overall Rating", "N/A")
    would_take     = header.get("Would Take Again", "N/A")

    # Split into individual review blocks on the --- delimiter
    review_blocks = re.split(r"\n---\n", reviews_raw)

    chunks = []
    for block in review_blocks:
        block = block.strip()
        if not block:
            continue

        # Parse review fields line by line
        fields  = {}
        comment = ""
        for line in block.splitlines():
            line = line.strip()
            if line.startswith("Comment: "):
                comment = line[len("Comment: "):].strip()
            elif ": " in line:
                key, val = line.split(": ", 1)
                fields[key.strip()] = val.strip()

        # Skip review blocks that have no written comment
        if not comment:
            continue

        # Build chunk text: professor context header + review fields + comment
        course_val = fields.get("Course", "N/A")
        course_str = f" | Course: {course_val}" if course_val != "N/A" else ""
        meta_line = (
            f"Professor: {professor} | Department: {department}{course_str} | "
            f"Overall Rating: {overall_rating} | Would Take Again: {would_take}"
        )
        detail_line = (
            f"Course: {fields.get('Course', 'N/A')} | "
            f"Date: {fields.get('Date', 'N/A')} | "
            f"Quality: {fields.get('Quality', 'N/A')} | "
            f"Difficulty: {fields.get('Difficulty', 'N/A')} | "
            f"Grade: {fields.get('Grade', 'N/A')} | "
            f"Attendance: {fields.get('Attendance', 'N/A')}"
        )

        lines = [meta_line, detail_line]

        tags = fields.get("Tags", "")
        if tags and tags != "N/A":
            lines.append(f"Tags: {tags}")

        lines.append(f"Student Review: {comment}")

        chunk_text = "\n".join(lines)

        chunks.append({
            "text":           chunk_text,
            "source":         filepath.name,
            "professor":      professor,
            "department":     department,
            "overall_rating": overall_rating,
            "course":         fields.get("Course", "N/A"),
            "quality":        fields.get("Quality", "N/A"),
            "difficulty":     fields.get("Difficulty", "N/A"),
        })

    return chunks


def load_all_chunks():
    """Load all .txt files from data/ and return a flat list of chunks."""
    all_chunks = []

    for filepath in sorted(DATA_DIR.glob("*.txt")):
        chunks = parse_professor_file(filepath)
        print(f"  {filepath.name}: {len(chunks)} chunks")
        all_chunks.extend(chunks)

    return all_chunks


def inspect_chunks(chunks, n=5):
    """Print n randomly sampled chunks for manual inspection."""
    samples = random.sample(chunks, min(n, len(chunks)))

    print(f"\n{'=' * 65}")
    print(f"SAMPLE CHUNKS  ({n} of {len(chunks)} total)")
    print(f"{'=' * 65}")

    for i, chunk in enumerate(samples, 1):
        print(f"\n[Chunk {i}]  source: {chunk['source']}  |  {len(chunk['text'])} chars")
        print(chunk["text"])
        print("-" * 65)


def run_checks(chunks):
    """Basic sanity checks on the chunk list."""
    print(f"\n{'=' * 65}")
    print("CHECKS")
    print(f"{'=' * 65}")

    # Empty chunks
    empty = [c for c in chunks if not c["text"].strip()]
    if empty:
        print(f"  FAIL  {len(empty)} empty chunks found — check parser")
    else:
        print(f"  PASS  No empty chunks")

    # Count range
    total = len(chunks)
    if total < 50:
        print(f"  WARN  Only {total} chunks — may be too large (aim for 50+)")
    elif total > 2000:
        print(f"  WARN  {total} chunks — may be too small (aim for under 2000)")
    else:
        print(f"  PASS  {total} chunks — within expected range (50–2000)")

    # Chunks missing professor name in text
    missing_meta = [c for c in chunks if "Professor:" not in c["text"]]
    if missing_meta:
        print(f"  FAIL  {len(missing_meta)} chunks missing professor metadata")
    else:
        print(f"  PASS  All chunks contain professor metadata")


if __name__ == "__main__":
    print(f"Loading documents from {DATA_DIR}/\n")
    all_chunks = load_all_chunks()

    print(f"\nTotal: {len(all_chunks)} chunks from {len(list(DATA_DIR.glob('*.txt')))} files")

    run_checks(all_chunks)
    inspect_chunks(all_chunks, n=5)
