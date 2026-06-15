"""
query.py — retrieval function.
Milestone 5 will add generate() and ask() to this same file.
"""

import chromadb
from sentence_transformers import SentenceTransformer

CHROMA_DIR      = "chroma_db"
COLLECTION_NAME = "professor_reviews"
MODEL_NAME      = "all-MiniLM-L6-v2"

# Lazy-loaded singletons so the model and DB connection are only created once
_model      = None
_collection = None


def _get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer(MODEL_NAME)
    return _model


def _get_collection():
    global _collection
    if _collection is None:
        client      = chromadb.PersistentClient(path=CHROMA_DIR)
        _collection = client.get_collection(COLLECTION_NAME)
    return _collection


def retrieve(query, k=5):
    """
    Embed the query and return the top-k most similar chunks.

    Returns a list of dicts:
        {
            "text":     the full chunk text,
            "metadata": {source, professor, department, course, ...},
            "distance": cosine distance (lower = more similar),
        }
    """
    model      = _get_model()
    collection = _get_collection()

    query_embedding = model.encode([query])[0].tolist()

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=k,
        include=["documents", "metadatas", "distances"],
    )

    chunks = []
    for doc, meta, dist in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0],
    ):
        chunks.append({"text": doc, "metadata": meta, "distance": dist})

    return chunks


# ── Manual retrieval test (Milestone 4 checkpoint) ────────────────────────────
if __name__ == "__main__":
    test_queries = [
        # ── Evaluation plan (all 5) ───────────────────────────────────────────
        "What do students say about Ashish Gulati's final exam in IFT300?",
        "How does Yan Shoshitaishvili's cybersecurity class work at ASU?",
        "What are the main complaints about Ruben Acuna's online lecture videos?",
        "Does Yan Shoshitaishvili offer extra credit?",
        "What do student reviews say about ASU biology professors?",

        # ── Nickname test ─────────────────────────────────────────────────────
        "What do students say about Zardus?",

        # ── Course-specific ───────────────────────────────────────────────────
        "What is SER222 like at ASU?",

        # ── Cross-cutting (multiple professors) ──────────────────────────────
        "Which CSE professor is the easiest at ASU?",

        # ── Attribute-based ───────────────────────────────────────────────────
        "Which professors require mandatory attendance?",
        "Which professor gives the most useful feedback to students?",

        # ── Department-level ──────────────────────────────────────────────────
        "What are ECE professors like at ASU?",

        # ── Avoidance query ───────────────────────────────────────────────────
        "Which professor should I avoid at ASU?",

        # ── Partial / informal name ───────────────────────────────────────────
        "What do students say about Professor Chen?",
    ]

    for query in test_queries:
        print(f"\n{'=' * 65}")
        print(f"QUERY: {query}")
        print(f"{'=' * 65}")

        chunks = retrieve(query, k=5)

        for i, chunk in enumerate(chunks, 1):
            print(f"\n[{i}] distance: {chunk['distance']:.3f}  |  source: {chunk['metadata']['source']}")
            print(chunk["text"])
            print("-" * 65)
