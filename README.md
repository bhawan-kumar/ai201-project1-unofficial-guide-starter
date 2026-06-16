# The Unofficial Guide — Project 1

> **How to use this template:**
> Complete each section *after* you've built and tested the corresponding part of your system.
> Do not write placeholder text — if a section isn't done yet, leave it blank and come back.
> Every section below is required for submission. One-liners will not receive full credit.

---

## Demo Video

[Watch the demo on Loom](https://www.loom.com/share/078f3b786be843568b5c7d15daf670ea)

---

## Domain

This system covers student reviews of professors in the CSE (Computer Science & Engineering), ECE (Electrical & Computer Engineering), and Data Science departments at Arizona State University. All reviews were scraped from Rate My Professors.

The knowledge here is hard to find through official channels because ASU's course catalog and department pages only tell you what a class covers — they say nothing about whether the professor's exams match the material, whether lecture videos are actually watchable, or whether attendance matters. Students rely on Rate My Professors for that kind of honest, practical information, but the site doesn't let you ask questions across multiple professors at once. This system fixes that: you can ask "which professor is the easiest in CSE?" or "does this professor's final match what was taught?" and get answers grounded in what real students said.

---

## Document Sources

I collected 24 `.txt` files, one per professor. Each file was manually scraped from Rate My Professors and cleaned into a structured format: a header section with the professor's overall stats, followed by individual reviews separated by `---`.

| # | Source | Type | URL or file path |
|---|--------|------|-----------------|
| 1 | CSE_Ajay_Bansal.txt | Scraped RMP reviews | https://www.ratemyprofessors.com/professor/2651122 |
| 2 | CSE_Yinong_Chen.txt | Scraped RMP reviews | https://www.ratemyprofessors.com/professor/18588 |
| 3 | CSE_Ruben_Acuna.txt | Scraped RMP reviews | https://www.ratemyprofessors.com/professor/2075502 |
| 4 | CSE_Debra_Calliss.txt | Scraped RMP reviews | https://www.ratemyprofessors.com/professor/479387 |
| 5 | CSE_Phillip_Miller.txt | Scraped RMP reviews | https://www.ratemyprofessors.com/professor/1834878 |
| 6 | CSE_James_Gordon.txt | Scraped RMP reviews | https://www.ratemyprofessors.com/professor/2844149 |
| 7 | CSE_Yan_Shoshitaishvili.txt | Scraped RMP reviews | https://www.ratemyprofessors.com/professor/2522770 |
| 8 | CSE_Mohamed_Sarwat.txt | Scraped RMP reviews | https://www.ratemyprofessors.com/professor/1981360 |
| 9 | CSE_Steven_Osburn.txt | Scraped RMP reviews | https://www.ratemyprofessors.com/professor/2300900 |
| 10 | CSE_Adil_Ahmad.txt | Scraped RMP reviews | https://www.ratemyprofessors.com/professor/2810322 |
| 11 | CSE_Chris_Bryan.txt | Scraped RMP reviews | https://www.ratemyprofessors.com/professor/2463568 |
| 12 | CSE_Connor_Nelson.txt | Scraped RMP reviews | https://www.ratemyprofessors.com/professor/2849863 |
| 13 | ECE_Bertan_Bakkaloglu.txt | Scraped RMP reviews | https://www.ratemyprofessors.com/professor/812246 |
| 14 | ECE_Jennifer_Kitchen.txt | Scraped RMP reviews | https://www.ratemyprofessors.com/professor/1805058 |
| 15 | ECE_Konstantinos_Tsakalis.txt | Scraped RMP reviews | https://www.ratemyprofessors.com/professor/1051277 |
| 16 | ECE_Alicia_Baumann.txt | Scraped RMP reviews | https://www.ratemyprofessors.com/professor/1917991 |
| 17 | ECE_Trevor_Thornton.txt | Scraped RMP reviews | https://www.ratemyprofessors.com/professor/1231640 |
| 18 | ECE_Keith_Holbert.txt | Scraped RMP reviews | https://www.ratemyprofessors.com/professor/911674 |
| 19 | ECE_Bassam_Matar.txt | Scraped RMP reviews | https://www.ratemyprofessors.com/professor/71723 |
| 20 | ECE_Sayfe_Kiaei.txt | Scraped RMP reviews | https://www.ratemyprofessors.com/professor/781411 |
| 21 | ECE_Seth_Abraham.txt | Scraped RMP reviews | https://www.ratemyprofessors.com/professor/2268269 |
| 22 | Data_Science_Rick_Bird.txt | Scraped RMP reviews | https://www.ratemyprofessors.com/professor/2407726 |
| 23 | Data_Science_Ashish_Gulati.txt | Scraped RMP reviews | https://www.ratemyprofessors.com/professor/2523588 |
| 24 | Data_Science_Eric_Bishop.txt | Scraped RMP reviews | https://www.ratemyprofessors.com/professor/2714417 |

---

## Chunking Strategy

**Chunk size:** One complete review entry per chunk. There is no fixed character limit — each chunk ends wherever the natural `---` delimiter appears in the file. In practice, chunks range from about 200 to 600 characters.

**Overlap:** None. Instead of overlapping windows, every chunk gets the professor's name, department, course name, and overall rating prepended at the top. This means every chunk is fully self-contained — retrieval works even without overlap, because the metadata is embedded directly in the chunk text.

**Why these choices fit your documents:** The reviews in this dataset are short, complete opinions. Each one is 2–5 sentences by a single student about a specific course experience. Splitting on `---` matches the natural document boundary exactly — there's never a case where a single meaningful thought is split across two chunks. Using fixed-size character splits would actually make this worse, because a 500-character window might cut a review mid-sentence and pair the beginning of one student's opinion with the end of another's. That kind of hybrid chunk would embed strangely and retrieve poorly. The reason I added professor name, course, and rating to every chunk header is that without it, a chunk containing just "exams were brutal and completely off-topic" gives the embedding model nothing to connect to a query about a specific professor — you'd need the professor's name in the chunk to retrieve it for the right person.

**Final chunk count:** 1,735 chunks across 24 files.

---

## Embedding Model

**Model used:** `all-MiniLM-L6-v2` from the `sentence-transformers` library. It runs fully locally with no API key or rate limits, produces 384-dimensional vectors, and handles short opinion text well.

**Production tradeoff reflection:** If I were deploying this for real ASU students, there are a few things I'd weigh differently. First, course codes like SER222 and CSE466 are rare in general training data, so MiniLM may not embed them precisely — a model like OpenAI's `text-embedding-3-large` or `bge-large-en-v1.5` (which was fine-tuned more specifically on English text retrieval) would likely handle domain-specific terms better. Second, MiniLM caps at 256 tokens, which is fine for the short reviews in this dataset but would truncate longer documents in other domains. Third, latency: MiniLM runs in about 10ms locally, while an API-based model adds 100–300ms of network round-trip per query — for a high-traffic student tool, that adds up. Finally, there's a privacy consideration: running locally means review text never leaves the machine. Sending every chunk to an API means a third party processes all the student opinion data.

---

## Grounded Generation

**System prompt grounding instruction:** The system prompt is explicit about scope and includes a required fallback phrase:

```
You are a helpful academic advisor for Arizona State University students.
Answer questions about ASU professors using ONLY the student reviews provided
in the context below. Follow these rules strictly:
1. Use ONLY information from the provided student reviews. Do not use your own
   knowledge about professors, universities, or courses.
2. If the reviews do not contain enough information to answer the question,
   respond with exactly: "I don't have enough information in the student reviews
   to answer that question."
3. Always mention the professor's name when relevant.
4. Be concise and stick to what the reviews actually say.
```

The key design choice was making rule 2 a required exact phrase. This makes grounding testable — when I ask about biology professors (who are not in the dataset), the system always returns that exact string, which is easy to verify automatically. A freeform refusal like "I'm not sure about this one" would be harder to check and easier for the model to slip out of.

**How source attribution is surfaced in the response:** Sources are never generated by the LLM — they are attached programmatically in `query.py`. After the LLM returns its answer, the code runs `sorted(set(c["metadata"]["source"] for c in chunks))` over the retrieved chunks and appends that list to the response. The Gradio UI displays these filenames in a separate "Retrieved from" box. This means sources cannot hallucinate — if a chunk wasn't retrieved, its file will never appear in the sources list.

---

## Evaluation Report

| # | Question | Expected answer | System response (summarized) | Retrieval quality | Response accuracy |
|---|----------|-----------------|------------------------------|-------------------|-------------------|
| 1 | What do students say about Ashish Gulati's final exam in IFT300? | Class avg 33, material never taught, deviated from syllabus, professor refused to curve | Class avg 33, "completely deviated from material taught," "NEVER covered" material, "nothing provided for it and its broad" | Relevant | Accurate |
| 2 | How does Yan Shoshitaishvili's cybersecurity class work at ASU? | Coding challenges = grade, no traditional exams, late extensions available, pwn.college tip | Solve coding challenges → submit code → get grade; graded on completion; generous late policy; clear lectures | Relevant | Accurate |
| 3 | What are the main complaints about Ruben Acuna's online lecture videos? | Mumbles, subtitles can't keep up, factual mistakes in lectures, students go to YouTube instead | Mumbles and stutters, subtitles don't keep up, crutch words, outdated (6+ year old) videos, fast talking | Relevant | Partially accurate |
| 4 | Does Yan Shoshitaishvili offer extra credit? | Yes — multiple reviews mention it, EXTRA CREDIT tag appears | Yes — "Extra credit pays dividends," "Lots of extra credit opportunities," EXTRA CREDIT tag confirmed | Relevant | Accurate |
| 5 | What do student reviews say about ASU biology professors? | System should decline — no biology professors in dataset | "I don't have enough information in the student reviews to answer that question." | N/A | Accurate |

**Retrieval quality:** Relevant / Partially relevant / Off-target
**Response accuracy:** Accurate / Partially accurate / Inaccurate

**Notes on Q3:** The system caught the mumbling and subtitle issues correctly but missed the two most specific complaints in the planning.md expected answer — that Acuna makes factual mistakes in his lectures and that students recommend going to YouTube instead. Those details exist in the data but were not in the top-5 retrieved chunks for this query. The chunks that were retrieved focused on delivery style (mumbling, speed, crutch words) rather than content accuracy. This is a retrieval coverage gap, not a hallucination.

---

## Failure Case Analysis

**Question that failed:** "How hard is CSE466?" (tested outside the 5 evaluation questions)

**What the system returned:** "I don't have enough information in the student reviews to answer that question." — even though CSE466 is Yan Shoshitaishvili's well-reviewed cybersecurity class with 47 chunks describing it as extremely time-intensive (20–30 hours per week).

**Root cause (tied to a specific pipeline stage):** This is a retrieval failure. The query "How hard is CSE466?" gets embedded as a vector, and the system searches for the most semantically similar chunks. The problem is that the word "CSE466" by itself is a course code — it has almost no semantic meaning in the vector space. The embedding model (all-MiniLM-L6-v2) was trained on general English text where "CSE466" does not appear as a meaningful word, so it gets embedded as a near-zero-signal token. The chunks that describe the class as hard say things like "requires 20-30 hours a week" and "solve coding challenges" — those phrases are semantically close to general difficulty queries, but not to the query "How hard is CSE466?" which anchors strongly on the course code. The result is that the retrieval stage returns zero Yan chunks — the top-5 results come from completely different professors whose reviews happened to use similar phrasing about difficulty in unrelated contexts.

**What you would change to fix it:** The most direct fix is a hybrid retrieval approach: run both semantic search (current) and keyword search in parallel, then merge the results. A keyword search for "CSE466" would immediately find all 47 Yan chunks, and combining that with semantic search would give the LLM the right context. ChromaDB supports metadata filtering, so one option is to detect when a query contains a course code pattern (e.g., `[A-Z]{2,4}\d{3}`) and filter results by matching course in the metadata before running semantic search. A second option is to add a course-code index alongside ChromaDB — a simple Python dict mapping course codes to professor names — so that if a query contains a known course code, the system routes directly to that professor's chunks.

---

## Spec Reflection

**One way the spec helped you during implementation:** The chunking strategy section in planning.md gave a clear written reason for why one-review-per-chunk was the right choice: "each review is already a complete thought." When I was implementing `pipeline.py` and was tempted to try fixed 500-character splits (which is a common default approach), I referred back to the spec and stuck with the natural `---` delimiter. The spec's reasoning — that splitting mid-review would pair one student's rating with another's comment and create an incoherent embedding — gave me something concrete to check against. If my chunks ever merged two reviews or cut one off mid-sentence, I could see immediately that it violated the spec. That written rationale turned a vague instinct into a verifiable property.

**One way your implementation diverged from the spec, and why:** The original spec described the chunk header as containing only professor name, department, and overall rating. During implementation I discovered that the course name was essential and had to be added. Two different reviews of the same professor in different courses are almost opposite in quality — Ashish Gulati's IFT300 reviews are very negative about the final exam, while reviews in other courses are more neutral. Without the course name in the chunk header, a query asking specifically about IFT300 would retrieve whichever Gulati chunks happened to score highest semantically, with no way to filter by course. After adding the course name to the header and rerunning retrieval tests, the IFT300 query started pulling the right chunks consistently. The spec was updated to reflect this change.

---

## AI Usage

**Instance 1 — Chunk header format**

- *What I gave the AI:* The Documents section from planning.md (describing the 24 `.txt` files and their `---` delimiter structure) and the Chunking Strategy section (one review per chunk, professor metadata prepended).
- *What it produced:* `pipeline.py` with a `parse_professor_file()` function that prepended professor name, department, and overall rating to each chunk. The chunk header looked like: `Professor: Ashish Gulati | Dept: Data_Science | Overall: 2.6`.
- *What I changed or overrode:* I directed the AI to also add the course name to the header line after noticing during testing that reviews for the same professor in different courses told completely different stories. The query "What do students say about Gulati's final exam in IFT300?" was returning chunks from other Gulati courses where the final was unremarkable. Adding `Course: IFT300` to the chunk header fixed the retrieval for course-specific queries without changing the rest of the pipeline.

**Instance 2 — Grounding system prompt and source attribution**

- *What I gave the AI:* The grounded generation requirement from planning.md — "answers must come only from the retrieved chunks, and the system must explicitly decline if the answer isn't in the context" — plus the expected output format (answer + source filenames).
- *What it produced:* A system prompt with a general instruction to use only the provided reviews, and a `generate()` function that returned the LLM's answer and extracted source filenames from chunk metadata.
- *What I changed or overrode:* I directed the AI to make the decline response a fixed, exact phrase rather than a freeform refusal. The original version said something like "tell the user you don't know." I changed it to require the model to output exactly: *"I don't have enough information in the student reviews to answer that question."* This made the out-of-scope test (Q5 — biology professors) deterministic and easy to verify — I could confirm grounding was working by checking for that exact string rather than interpreting whether a freeform response counted as a refusal. I also directed the AI to attach sources programmatically from metadata after the LLM call, rather than asking the LLM to cite sources in its response text, which would have introduced a hallucination risk.

**Instance 3 — Retrieval stress testing**

- *What I gave the AI:* The 5 evaluation questions from planning.md and a request to test the retrieval pipeline.
- *What it produced:* A test script that ran only those 5 queries through `retrieve()` and printed the top-5 chunks and distances.
- *What I changed or overrode:* I directed the AI to expand the test to 13 different query types — adding cross-professor comparisons ("which CSE professor is the easiest?"), nickname queries ("what do students say about Zardus?"), avoidance queries ("which professor should I avoid?"), partial name queries ("Professor Chen"), and out-of-scope queries. The original 5-question test would have only validated the happy path. The expanded test revealed two real limitations: the nickname miss (Zardus → Yan has low retrieval accuracy) and the avoidance query behavior (returns positive reviews because "avoid" has no semantic opposite in the embedding space). Both were documented in planning.md as anticipated challenges and confirmed by the expanded test.
