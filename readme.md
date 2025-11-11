# TargetAI (MVP)


A free, local RAG chatbot for drug-target and clinical-trial insights.


**Data sources (MVP):** OpenTargets, PubMed, ClinicalTrials.gov, EU CTIS (public).


**Stack:**
- Embeddings: BioMedBERT-style (Sentence-Transformers)
- Reranker: BAAI/bge-reranker-base
- Vector DB: FAISS (local)
- LLM: BioMistral-7B-Instruct via Ollama
- UI: Gradio


## Quickstart


### 1) System deps
- Python 3.10+
- **Ollama** installed and running (https://ollama.com)
- Pull the model: `ollama pull biomistral`


### 2) Setup project
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```



### 3) Ingest + index
```bash
python -m scripts.rebuild_index
```
This will fetch small sample slices from OpenTargets, ClinicalTrials.gov, PubMed (and stub from EU CTIS), normalize, chunk, embed, and build a FAISS index under `data/index/`.


### 4) Run the app
```bash
python -m src.RAG.app
```
Open the local Gradio link and start chatting.


## Notes
- This MVP uses **public endpoints** (respect rate limits). For EU CTIS the public search is used; API access is limited — the module currently stubs a minimal fetch with TODOs.
- Everything runs free on CPU; performance depends on your machine. 
