# Project 1 Planning: The Unofficial Guide

> Write this document before you write any pipeline code.
> Your spec and architecture diagram are what you'll use to direct AI tools (Claude, Copilot, etc.) to generate your implementation — the more specific they are, the more useful the generated code will be.
> Update the Retrieval Approach and Chunking Strategy sections if you change your approach during implementation.
> Update this file before starting any stretch features.

---

## Summary

This project is an unofficial guide to ASU professors in the CSE, ECE, and Data Science departments, built from real student reviews scraped from Rate My Professors. The goal is to let students ask plain questions like "Is this professor's exam fair?" or "Do I need to attend every class?" and get answers grounded in what other students actually experienced. This kind of knowledge is hard to find officially, course catalogs and department websites tell you what a professor teaches, but never whether their exams match the material, how they handle student questions, or whether their online lectures are worth watching.

---

## Domain

The domain is student professor reviews at Arizona State University (ASU), covering the CSE (Computer Science & Engineering), ECE (Electrical & Computer Engineering), and Data Science departments. All reviews were scraped from Rate My Professors.

This knowledge matters because students have to pick professors before they can see a syllabus or know anything real about the class. The official sources — course catalog, department page, university website — only tell you what topics a course covers, not whether the professor is fair, whether attendance matters, or whether the online videos are actually watchable. Rate My Professors is where students share that kind of honest, practical information. The problem is the site doesn't let you search across professors or ask broader questions. This system fixes that.

---

## Documents

I collected 24 `.txt` files, one per professor. Each file starts with the professor's overall stats (rating, would-take-again percentage, total reviews) and then lists individual student reviews separated by `---`.

| #   | Source                         | Description                                              | URL or location                                    |
| --- | ------------------------------ | -------------------------------------------------------- | -------------------------------------------------- |
| 1   | CSE_Ajay_Bansal.txt            | Reviews for CSE prof Ajay Bansal                         | https://www.ratemyprofessors.com/professor/2651122 |
| 2   | CSE_Yinong_Chen.txt            | Reviews for CSE prof Yinong Chen                         | https://www.ratemyprofessors.com/professor/18588   |
| 3   | CSE_Ruben_Acuna.txt            | Reviews for CSE prof Ruben Acuna (106 reviews)           | https://www.ratemyprofessors.com/professor/2075502 |
| 4   | CSE_Debra_Calliss.txt          | Reviews for CSE prof Debra Calliss                       | https://www.ratemyprofessors.com/professor/479387  |
| 5   | CSE_Phillip_Miller.txt         | Reviews for CSE prof Phillip Miller                      | https://www.ratemyprofessors.com/professor/1834878 |
| 6   | CSE_James_Gordon.txt           | Reviews for CSE prof James Gordon                        | https://www.ratemyprofessors.com/professor/2844149 |
| 7   | CSE_Yan_Shoshitaishvili.txt    | Reviews for CSE prof Yan Shoshitaishvili (cybersecurity) | https://www.ratemyprofessors.com/professor/2522770 |
| 8   | CSE_Mohamed_Sarwat.txt         | Reviews for CSE prof Mohamed Sarwat                      | https://www.ratemyprofessors.com/professor/1981360 |
| 9   | CSE_Steven_Osburn.txt          | Reviews for CSE prof Steven Osburn                       | https://www.ratemyprofessors.com/professor/2300900 |
| 10  | CSE_Adil_Ahmad.txt             | Reviews for CSE prof Adil Ahmad                          | https://www.ratemyprofessors.com/professor/2810322 |
| 11  | CSE_Chris_Bryan.txt            | Reviews for CSE prof Chris Bryan                         | https://www.ratemyprofessors.com/professor/2463568 |
| 12  | CSE_Connor_Nelson.txt          | Reviews for CSE prof Connor Nelson                       | https://www.ratemyprofessors.com/professor/2849863 |
| 13  | ECE_Bertan_Bakkaloglu.txt      | Reviews for ECE prof Bertan Bakkaloglu                   | https://www.ratemyprofessors.com/professor/812246  |
| 14  | ECE_Jennifer_Kitchen.txt       | Reviews for ECE prof Jennifer Kitchen                    | https://www.ratemyprofessors.com/professor/1805058 |
| 15  | ECE_Konstantinos_Tsakalis.txt  | Reviews for ECE prof Konstantinos Tsakalis               | https://www.ratemyprofessors.com/professor/1051277 |
| 16  | ECE_Alicia_Baumann.txt         | Reviews for ECE prof Alicia Baumann                      | https://www.ratemyprofessors.com/professor/1917991 |
| 17  | ECE_Trevor_Thornton.txt        | Reviews for ECE prof Trevor Thornton                     | https://www.ratemyprofessors.com/professor/1231640 |
| 18  | ECE_Keith_Holbert.txt          | Reviews for ECE prof Keith Holbert                       | https://www.ratemyprofessors.com/professor/911674  |
| 19  | ECE_Bassam_Matar.txt           | Reviews for ECE prof Bassam Matar                        | https://www.ratemyprofessors.com/professor/71723   |
| 20  | ECE_Sayfe_Kiaei.txt            | Reviews for ECE prof Sayfe Kiaei                         | https://www.ratemyprofessors.com/professor/781411  |
| 21  | ECE_Seth_Abraham.txt           | Reviews for ECE prof Seth Abraham                        | https://www.ratemyprofessors.com/professor/2268269 |
| 22  | Data_Science_Rick_Bird.txt     | Reviews for Data Science prof Rick Bird                  | https://www.ratemyprofessors.com/professor/2407726 |
| 23  | Data_Science_Ashish_Gulati.txt | Reviews for Data Science prof Ashish Gulati              | https://www.ratemyprofessors.com/professor/2523588 |
| 24  | Data_Science_Eric_Bishop.txt   | Reviews for Data Science prof Eric Bishop                | https://www.ratemyprofessors.com/professor/2714417 |

---

## Chunking Strategy

**Chunk size:** One complete review entry per chunk. Each chunk is roughly 200–600 characters. There is no fixed character limit — the natural `---` delimiter in the file marks where each review ends, and that is where each chunk ends.

**Overlap:** No sliding-window overlap. Instead, every chunk has the professor's name, department, and overall rating prepended at the top so every chunk stands on its own.

**Reasoning:**

The reviews in this dataset are short — most comments are 2–5 sentences, which is already a self-contained opinion. That directly answers the first guiding question: because the documents are short reviews (not long guides), a small chunk size that matches one review is exactly right. There's no need to go larger.

If a key fact spans two adjacent chunks, it would be a problem — but here it doesn't, because each review is already a complete thought. The rating, the tags, and the comment all belong to the same student's experience and they're all inside one `---` block. As long as I don't split mid-block, nothing important gets cut in half.

If chunks were too small (e.g., just the one-sentence comment, no rating or professor name), retrieval would fail because there's not enough context in the embedding to match a query like "which professor has unfair exams" to a chunk that just says "exams were brutal." Too small = not enough signal. If chunks were too large (e.g., merging 5 reviews into one block), the embedding would average out multiple opinions and lose the specific detail that makes individual reviews useful. A query about one professor's attendance policy would retrieve a blended chunk that also talks about a different professor's grading — noisy and off-target.

---

## Retrieval Approach

**Embedding model:** `all-MiniLM-L6-v2` from the `sentence-transformers` library. It runs locally with no API key and no rate limits, and produces 384-dimensional vectors that work well for short opinion text.

**Top-k:** 5. Five chunks gives the LLM enough evidence to spot patterns — like three different students all mentioning the same issue with a final exam — without flooding the context with loosely related reviews. Too few (k=1 or 2) means if the top result is slightly off, there's nothing else to fall back on. Too many (k=10+) floods the prompt with weakly related chunks and the LLM starts pulling from the wrong ones.

Semantic search works even when the query doesn't share exact words with the document because the embedding model maps meaning into a vector space — "unfair test" and "exam had nothing to do with what we learned" end up close together because the model was trained on enough text to associate those ideas, not just match keywords.

**Production tradeoff reflection:**
- **Accuracy on domain text:** Course codes like SER222 and nicknames like "Zardus" are rare in general training data. A model like `text-embedding-3-large` (OpenAI) or `bge-large` would likely handle these better than MiniLM.
- **Context length:** MiniLM caps at 256 tokens — fine for short reviews, but would truncate longer documents. `text-embedding-3-large` supports up to 8,191 tokens.
- **Latency vs. cost:** MiniLM runs in ~10ms locally with no cost. API-based models add 100–300ms of network time per query and charge per token — matters for a live student-facing tool.
- **Privacy:** Running locally means review text never leaves the machine. An API-based model sends every chunk to a third-party server.
- **Multilingual:** Only relevant if reviews aren't all English. Not a concern here, but worth flagging for a real deployment.

---

## Evaluation Plan

| #   | Question                                                                | Expected answer                                                                                                                                                                                                                                                |
| --- | ----------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1   | What do students say about Ashish Gulati's final exam in IFT300?        | The final covered advanced SQL that was never taught in class. The course only covered basic and intermediate SQL. The class average on the final was 33. The professor refused to curve or meet with students about grades.                                   |
| 2   | How does Yan Shoshitaishvili's cybersecurity class work at ASU?         | Students watch video lectures and complete coding challenges. Submitting the correct challenge code earns the grade — there are no traditional exams. Late extensions are available. Several reviews suggest getting ahead on pwn.college before the semester. |
| 3   | What are the main complaints about Ruben Acuna's online lecture videos? | He mumbles often to the point that subtitles cannot keep up, he makes factual mistakes in his lectures, and students say they had to go to YouTube to actually learn the material.                                                                             |
| 4   | Does Yan Shoshitaishvili offer extra credit?                            | Yes. Multiple reviews mention extra credit and the tag EXTRA CREDIT appears across several of his reviews.                                                                                                                                                     |
| 5   | What do student reviews say about ASU biology professors?               | The system should say it does not have enough information — no biology professors are in the dataset.                                                                                                                                                          |

---

## Anticipated Challenges

1. **Nickname mismatches:** Yan Shoshitaishvili goes by "Zardus" in many reviews. A query using his full name might not retrieve chunks that only mention the nickname, because the embedding model has no way of knowing the two names refer to the same person. This means some relevant reviews could be missed even when the query is perfectly reasonable.

2. **N/A fields making chunks less useful:** A lot of reviews have `N/A` for fields like Course, Attendance, or Textbook. Those chunks have less structured context. For example, a query like "which professors require mandatory attendance?" would miss reviews where the attendance field wasn't filled in, even if the professor does actually require it. The only way to catch it is if the student mentioned attendance in their written comment.

---

## Architecture

```
┌──────────────────────────────────────────────────────────┐
│  1. DOCUMENT INGESTION                                   │
│     Load 24 .txt files from data/ folder                 │
│     Tool: Python (pathlib, open)                         │
└───────────────────────┬──────────────────────────────────┘
                        │
                        ▼
┌──────────────────────────────────────────────────────────┐
│  2. CHUNKING                                             │
│     Split each file on "---" → one chunk per review      │
│     Prepend professor name + dept + overall rating       │
│     to every chunk                                       │
│     Tool: Python (re, string parsing)                    │
└───────────────────────┬──────────────────────────────────┘
                        │
                        ▼
┌──────────────────────────────────────────────────────────┐
│  3. EMBEDDING + VECTOR STORE                             │
│     Embed each chunk and store with source metadata      │
│     Embedding: sentence-transformers all-MiniLM-L6-v2   │
│     Vector store: ChromaDB (cosine similarity,           │
│                   persistent on disk)                    │
└───────────────────────┬──────────────────────────────────┘
                        │
                        ▼
┌──────────────────────────────────────────────────────────┐
│  4. RETRIEVAL                                            │
│     Embed query → cosine similarity search → top-5      │
│     Return chunks + source filenames + distances         │
│     Tool: ChromaDB .query(), sentence-transformers       │
└───────────────────────┬──────────────────────────────────┘
                        │
                        ▼
┌──────────────────────────────────────────────────────────┐
│  5. GENERATION                                           │
│     Top-5 chunks injected as context into the prompt    │
│     System prompt: answer from context only, decline    │
│     if the answer isn't in the retrieved chunks         │
│     LLM: Groq llama-3.3-70b-versatile                   │
│     Sources appended from chunk metadata                │
└───────────────────────┬──────────────────────────────────┘
                        │
                        ▼
┌──────────────────────────────────────────────────────────┐
│  6. QUERY INTERFACE                                      │
│     Gradio web UI: text input → answer + source list    │
│     Run with: python app.py → localhost:7860             │
└──────────────────────────────────────────────────────────┘
```

---

## AI Tool Plan

**Milestone 3 — Ingestion and chunking:**
I'll use Claude (this tool) to help implement the ingestion and chunking pipeline. I'll share the Documents section (describing the 24 `.txt` files and their `---` delimiter structure) and the Chunking Strategy section (one review per chunk, professor metadata prepended). I'll ask Claude to generate `pipeline.py` with a `parse_professor_file()` function and a `build_pipeline()` function. After getting the code, I'll read through it myself to make sure it matches the spec, run it, print 5 chunks, and verify each one is self-contained and clean before moving on.

**Milestone 4 — Embedding and retrieval:**
I'll use Claude to implement the retrieval side. I'll share the Retrieval Approach section (all-MiniLM-L6-v2, top-k=5, ChromaDB with cosine similarity) and the chunk schema from Milestone 3. I'll ask Claude to write a `retrieve(query, k=5)` function in `query.py`. I'll test it manually by running all 5 evaluation questions and checking that the returned chunks are obviously relevant and that distance scores on the top results are below 0.5.

**Milestone 5 — Generation and interface:**
I'll use Claude to wire up generation and the Gradio interface. I'll share the grounding requirement (answers must come only from the retrieved chunks, and the system must explicitly decline if the answer isn't in the context) and the expected output format (answer + source filenames). I'll ask Claude to write `generate()` in `query.py` using the Groq API and `app.py` as the Gradio UI. I'll test grounding by checking whether any response includes information that wasn't in the retrieved chunks, and I'll run Question 5 (biology professors) to confirm the system declines instead of making something up.
