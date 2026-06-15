import gradio as gr
from query import ask


def handle_query(question):
    if not question.strip():
        return "Please enter a question.", ""

    result  = ask(question)
    sources = "\n".join(f"• {s}" for s in result["sources"])
    return result["answer"], sources


with gr.Blocks(title="ASU Professor Unofficial Guide") as demo:
    gr.Markdown("# ASU Professor Unofficial Guide")
    gr.Markdown(
        "Ask questions about professors at Arizona State University "
        "based on real student reviews from Rate My Professors."
    )

    inp = gr.Textbox(
        label="Your question",
        placeholder='e.g. "What do students say about Ruben Acuna\'s lecture videos?"',
        lines=2,
    )
    btn = gr.Button("Ask", variant="primary")

    with gr.Row():
        answer  = gr.Textbox(label="Answer",         lines=10)
        sources = gr.Textbox(label="Retrieved from", lines=5)

    btn.click(handle_query, inputs=inp, outputs=[answer, sources])
    inp.submit(handle_query, inputs=inp, outputs=[answer, sources])


demo.launch()
