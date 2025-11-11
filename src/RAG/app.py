import os
import requests
import gradio as gr
from typing import List, Dict, Any
from src.rag.prompt import SYSTEM_PROMPT
from src.rag.retriever import Retriever

OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "biomistral")

retriever = Retriever()


def call_ollama(system: str, user: str, context_blocks: List[Dict[str, Any]]) -> str:
    # Build context string
    ctx_lines = []
    for c in context_blocks:
        t = c.get("title") or ""
        d = c.get("date") or ""
        u = c.get("url") or ""
        ctx_lines.append(f"- {t} | {d} | {u}")
    context = "\n".join(ctx_lines)

    prompt = (
        f"SYSTEM:\n{system}\n\n"
        f"CONTEXT (top sources):\n{context}\n\n"
        f"USER QUESTION:\n{user}\n\n"
        f"RESPONSE FORMAT:\n"
        f"- Start with 3-6 concise bullets summarizing the answer.\n"
        f"- If applicable, include a table (drug | target | indication | phase | sponsor | last status/date | source).\n"
        f"- End with a Sources section (title — date — URL)."
    )

    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": 0.2}
    }
    r = requests.post(f"{OLLAMA_HOST}/api/generate", json=payload, timeout=600)
    r.raise_for_status()
    return r.json().get("response", "")


def chat_fn(message: str, history: List[List[str]]):
    hits = retriever.search(message)
    reply = call_ollama(SYSTEM_PROMPT, message, hits)
    # Append a collapsible sources panel in UI-friendly way
    src_lines = [f"• {h.get('title') or h.get('url')} — {h.get('date') or ''} — {h.get('url') or ''}" for h in hits]
    sources_block = "\n\n**Top Retrieved Sources**\n\n" + "\n".join(src_lines)
    return reply + sources_block


with gr.Blocks(title="TargetAI") as demo:
    gr.Markdown("# TargetAI – Drug Target & Trial RAG (MVP)")
    chat = gr.ChatInterface(chat_fn, type="messages")

if __name__ == "__main__":
    demo.launch()
