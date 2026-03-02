# Techculture.ai — Service Information Assistant

An AI assistant that answers questions about Techculture.ai's services, pricing, and past projects. Built using a RAG (Retrieval-Augmented Generation) pipeline with agentic tool use — every answer is grounded in actual company documents with source citations.

Built as part of the AI Transformation Specialist technical assignment.

---

## What It Does

- Indexes 9 company documents (services, FAQs, pricing guide, case studies) into a local vector store
- For each user query, retrieves the most relevant document chunks using semantic search
- Generates a grounded answer using **Groq (Llama 3.1 8B)** — the model only sees retrieved context, not its general training data
- Every response includes source citations showing which document and section was used
- Agentic behaviour: autonomously calls a **Pricing Estimator** tool when pricing intent is detected, and runs **Sentiment Analysis** on every query
- Two interfaces: a FastAPI REST API and a Streamlit chat UI

---

## Project Structure

```
techculture-ai-assistant/
├── docs/                          # Knowledge base — 9 company documents
│   ├── services_overview.md
│   ├── ai_consulting_services.md
│   ├── digital_marketing_services.md
│   ├── web_app_development.md
│   ├── data_engineering_services.md
│   ├── faq.md
│   ├── pricing_guide.md
│   ├── case_study_fintech.md
│   └── case_study_ecommerce.md
│
├── ingestion.py        # Document loading and chunking (~600 char chunks, 80 char overlap)
├── embeddings.py       # Local embeddings via ChromaDB (all-MiniLM-L6-v2) + semantic search
├── rag_pipeline.py     # Retrieval + Groq Llama 3.1 answer generation
├── tools.py            # Pricing Estimator + Sentiment Analyzer tools
├── agent.py            # Orchestration — decides when to invoke which tools
├── api.py              # FastAPI REST API (POST /ask, GET /health, GET /rebuild)
├── app.py              # Streamlit chat interface
├── config.py           # All config loaded from .env — no secrets in code
├── requirements.txt
├── .env.example        # Copy to .env and fill in your GROQ_API_KEY
└── .gitignore
```

---

## Architecture

### Data Flow

```
Documents (docs/)
    └─► ingestion.py    — read .md/.txt files, split into ~600 char chunks with metadata
    └─► embeddings.py   — generate embeddings with all-MiniLM-L6-v2 (runs locally, no API)
    └─► ChromaDB        — persist vectors to disk in chroma_db/

User Query
    └─► agent.py        — sentiment analysis + pricing intent check
    └─► embeddings.py   — embed query, cosine similarity search, return top-5 chunks
    └─► rag_pipeline.py — build grounded prompt + call Groq Llama 3.1
    └─► Response        — answer + source citations + tool outputs
```

### Agent Decision Flow

```
Incoming Query
    ├── SentimentAnalyzer        (always runs — keyword-based classifier)
    │       → Positive / Negative / Neutral
    │
    ├── Pricing Intent Check     ("cost", "price", "how much", "budget"...)
    │       → YES: call PricingEstimator(service_type, duration_months)
    │       → NO: skip
    │
    └── RAG Pipeline             (always runs)
            → semantic search → top-5 chunks
            → build grounded prompt
            → Groq Llama 3.1 generates answer
            → return answer + source citations
```

### Technology Stack

| Component | Technology | Why |
|---|---|---|
| LLM (generation) | Groq — `llama-3.1-8b-instant` | Fast inference, generous free tier, no billing required |
| Embeddings | `all-MiniLM-L6-v2` via ChromaDB | Runs entirely on the server, no API cost, good semantic quality |
| Vector DB | ChromaDB (local, persistent) | No infrastructure setup needed, cosine similarity built-in |
| API | FastAPI | Async, auto-generates Swagger docs, Pydantic validation |
| UI | Streamlit | Rapid interactive chat interface |
| Config | python-dotenv | Keeps API keys out of source code |

---

## Setup Instructions

### 1. Clone the repository

```bash
git clone https://github.com/Amanroy666/techculture-ai-assistant.git
cd techculture-ai-assistant
```

### 2. Create a virtual environment

```bash
python -m venv venv
source venv/bin/activate        # Linux / Mac
# venv\Scripts\activate         # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure your API key

```bash
cp .env.example .env
```

Edit `.env` and add your Groq API key:

```
GROQ_API_KEY=your_groq_api_key_here
```

Get a **free** Groq API key (no credit card required) at: **https://console.groq.com**

### 5. Build the vector store

```bash
python embeddings.py --build
```

Reads all 9 documents, chunks them, generates local embeddings using `all-MiniLM-L6-v2`, and saves everything to `chroma_db/`. Takes about 30–60 seconds. No API calls needed for this step.

### 6. Start the application

**Streamlit UI (recommended for demo):**
```bash
streamlit run app.py
```
Open http://localhost:8501

**FastAPI REST API:**
```bash
uvicorn api:app --host 0.0.0.0 --port 8000 --reload
```
Open http://localhost:8000/docs for interactive Swagger UI.

---

## API Reference

### POST /ask

```bash
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the cost of a 3-month digital marketing campaign?"}'
```

**Response:**
```json
{
  "question": "What is the cost of a 3-month digital marketing campaign?",
  "answer": "For a 3-month digital marketing campaign, pricing ranges from ₹2,25,000 to ₹6,00,000...",
  "sources": [
    {"file": "pricing_guide.md", "section": "Campaign Packages"},
    {"file": "digital_marketing_services.md", "section": "Packages and Pricing"}
  ],
  "tools_used": ["SentimentAnalyzer", "PricingEstimator"],
  "sentiment": {"label": "Neutral", "confidence": "High", "signals": []},
  "pricing_estimate": {
    "triggered": true,
    "service_type": "Digital Marketing",
    "duration_months": 3,
    "min_inr": 225000,
    "max_inr": 600000,
    "min_usd": 2711,
    "max_usd": 7229
  }
}
```

### GET /health
```bash
curl http://localhost:8000/health
```

### GET /rebuild
Rebuild the index after adding new documents to `docs/`:
```bash
curl http://localhost:8000/rebuild
```

---

## Adding New Documents

1. Add `.md` or `.txt` files to `docs/`
2. Rebuild the index:
```bash
python embeddings.py --rebuild
```

---

## Assumptions & Limitations

**Assumptions:**
- Documents are in English
- Company documents are realistic dummy data — real internal documents were not provided
- Pricing is shown in INR with USD equivalents at approximately ₹83/USD

**Known limitations:**
- Sentiment analysis is rule-based keyword matching, not a trained model
- Pricing estimator uses a static lookup table, not live data
- ChromaDB is local-only — multi-server deployment needs Pinecone or Weaviate
- No multi-turn memory — each question is answered independently
- Context window limits how many retrieved chunks fit per query

---

## Future Improvements

1. **Conversation memory** — maintain context across follow-up questions
2. **Hybrid search** — combine semantic search with BM25 for better keyword recall
3. **Hosted vector DB** — Pinecone or Weaviate for production scalability
4. **Re-ranker** — cross-encoder to improve chunk ranking before generation
5. **RAG evaluation** — automated scoring with RAGAS (faithfulness, relevancy, precision)
6. **Streaming responses** — stream tokens for lower perceived latency
7. **API authentication** — protect the REST endpoints with key-based auth
8. **Admin UI** — document upload and re-indexing through a browser interface

### Production Scaling Plan

| Concern | Current | Production Approach |
|---|---|---|
| Vector DB | Local ChromaDB | Pinecone or Weaviate (managed) |
| LLM | Groq free tier | Dedicated Groq quota or self-hosted Llama |
| API | Single uvicorn | Docker + Kubernetes, horizontal scaling |
| Ingestion | Manual CLI | Background job queue (Celery + Redis) |
| Monitoring | Application logs | Prometheus + Grafana + LLM latency dashboards |

---

## Running Tests

```bash
# Verify document ingestion and chunking
python ingestion.py

# Build vector store and test semantic search
python embeddings.py --build
python embeddings.py --search "What AI services do you offer?"

# Test full agent pipeline end-to-end
python agent.py

# Test tools in isolation
python tools.py
```

---

## Contact

Built by: Aman Roy
For: Techculture.ai — AI Transformation Specialist Technical Assignment
