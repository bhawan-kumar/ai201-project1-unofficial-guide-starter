from query import ask

eval_questions = [
    "What do students say about Ashish Gulati's final exam in IFT300?",
    "How does Yan Shoshitaishvili's cybersecurity class work at ASU?",
    "What are the main complaints about Ruben Acuna's online lecture videos?",
    "Does Yan Shoshitaishvili offer extra credit?",
    "What do student reviews say about ASU biology professors?",
]

for i, q in enumerate(eval_questions, 1):
    sep = "=" * 70
    print(f"\n{sep}")
    print(f"Q{i}: {q}")
    print(sep)
    r = ask(q)
    print("ANSWER:", r["answer"])
    print("SOURCES:", r["sources"])
