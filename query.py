"""
query.py — retrieval + grounded generation.
"""

import os
import chromadb
from groq import Groq
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer

load_dotenv()

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


# ── Generation ────────────────────────────────────────────────────────────────

_groq_client = None

def _get_groq():
    global _groq_client
    if _groq_client is None:
        _groq_client = Groq(api_key=os.environ["GROQ_API_KEY"])
    return _groq_client


def generate(query, chunks):
    """
    Generate a grounded answer from retrieved chunks.
    Sources are attached programmatically from metadata — never left to the LLM.
    """
    context = "\n\n---\n\n".join(c["text"] for c in chunks)

    system_prompt = (
        "You are a helpful academic advisor for Arizona State University students.\n\n"
        "Answer questions about ASU professors using ONLY the student reviews provided "
        "in the context below. Follow these rules strictly:\n"
        "1. Use ONLY information from the provided student reviews. "
        "Do not use your own knowledge about professors, universities, or courses.\n"
        "2. If the reviews do not contain enough information to answer the question, "
        "respond with exactly: "
        "\"I don't have enough information in the student reviews to answer that question.\"\n"
        "3. Always mention the professor's name when relevant.\n"
        "4. Be concise and stick to what the reviews actually say."
    )

    user_prompt = (
        f"Student reviews from Rate My Professors:\n\n{context}\n\n"
        f"Question: {query}\n\n"
        "Answer using only the student reviews above. Do not use outside knowledge."
    )

    client = _get_groq()
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user",   "content": user_prompt},
        ],
        temperature=0.1,
        max_tokens=512,
    )

    answer  = response.choices[0].message.content.strip()
    sources = sorted(set(c["metadata"]["source"] for c in chunks))

    return {"answer": answer, "sources": sources, "chunks": chunks}


def ask(question):
    """End-to-end: retrieve then generate."""
    chunks = retrieve(question)
    return generate(question, chunks)


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
