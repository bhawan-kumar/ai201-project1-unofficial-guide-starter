"""
One-time script: embeds all chunks from pipeline.py and stores them in ChromaDB.
Run this once (or re-run to rebuild the index from scratch).
"""

import chromadb
from sentence_transformers import SentenceTransformer
from pipeline import load_all_chunks

CHROMA_DIR      = "chroma_db"
COLLECTION_NAME = "professor_reviews"
MODEL_NAME      = "all-MiniLM-L6-v2"


def build_index():
    # ── 1. Load chunks ────────────────────────────────────────────
    print("Loading chunks from pipeline...\n")
    chunks = load_all_chunks()
    print(f"\n  {len(chunks)} chunks loaded")

    # ── 2. Embed ──────────────────────────────────────────────────
    print(f"\nLoading embedding model ({MODEL_NAME})...")
    model = SentenceTransformer(MODEL_NAME)

    print("Embedding chunks (this takes ~30 seconds)...")
    texts      = [c["text"] for c in chunks]
    embeddings = model.encode(texts, show_progress_bar=True, batch_size=64)
    print(f"  Done — embeddings shape: {embeddings.shape}")

    # ── 3. Store in ChromaDB ──────────────────────────────────────
    print(f"\nConnecting to ChromaDB at {CHROMA_DIR}/...")
    client = chromadb.PersistentClient(path=CHROMA_DIR)

    # Drop and recreate so re-runs start clean
    try:
        client.delete_collection(COLLECTION_NAME)
        print("  Dropped existing collection")
    except Exception:
        pass

    collection = client.create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )

    ids       = [f"chunk_{i}" for i in range(len(chunks))]
    metadatas = [
        {
            "source":         c["source"],
            "professor":      c["professor"],
            "department":     c["department"],
            "overall_rating": c["overall_rating"],
            "course":         c["course"],
            "quality":        c["quality"],
            "difficulty":     c["difficulty"],
        }
        for c in chunks
    ]

    # Insert in batches of 500 to stay well under ChromaDB's limit
    batch_size = 500
    total      = len(chunks)
    for start in range(0, total, batch_size):
        end = min(start + batch_size, total)
        collection.add(
            ids        = ids[start:end],
            documents  = texts[start:end],
            embeddings = embeddings[start:end].tolist(),
            metadatas  = metadatas[start:end],
        )
        print(f"  Stored {end}/{total} chunks")

    print(f"\nIndex built — {total} chunks in ChromaDB.")
    return collection


if __name__ == "__main__":
    build_index()
