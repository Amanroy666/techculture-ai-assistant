# Techculture.ai — Service Information Assistant

A production-grade AI assistant built with **RAG (Retrieval-Augmented Generation)** and **agentic AI** concepts. It answers questions about Techculture.ai's services, pricing, and past projects — grounded in real company documents with source citations.

Built as part of the AI Transformation Specialist technical assignment.

---

## What This Does

- Ingests and indexes company service documents using semantic embeddings
- Answers user questions using RAG — retrieves relevant document chunks before generating answers
- Includes source citations in every response (which document + section was used)
- Has agentic behavior: autonomously calls a **Pricing Estimator tool** for pricing questions and a **Sentiment Analyzer** on every query
- Exposes a REST API (FastAPI) and an interactive Streamlit UI

---

## Project Structure

```
techculture-ai-assistant/
├── docs/                         # Knowledge base documents
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
├── ingestion.py                  # Document loading and chunking
├── embeddings.py                 # Embedding generation + ChromaDB management
├── rag_pipeline.py               # Retrieval + Gemini generation logic
├── tools.py                      # Pricing Estimator + Sentiment Analyzer tools
├── agent.py                      # Tool orchestration and autonomous decision logic
├── api.py                        # FastAPI REST API
├── app.py                        # Streamlit interactive UI
├── config.py                     # Configuration (reads from .env)
│
├── requirements.txt
├── .env.example                  # Template — copy to .env and fill in your key
├── .gitignore
└── README.md
```

---

## Architecture Overview

### Data Flow

```
Documents (docs/)
    ↓ ingestion.py — Load & chunk into ~600 char segments with metadata
    ↓ embeddings.py — Generate embeddings via Gemini embedding-001
    ↓ ChromaDB — Store vectors locally with persistent storage

User Query
    ↓ agent.py — Sentiment analysis (always) + pricing intent detection
    ↓ embeddings.py — Embed query, semantic search top-5 chunks
    ↓ rag_pipeline.py — Build grounded prompt + call Groq Llama 3.1 (llama-3.1-8b-instant)
    ↓ Response — Answer + source citations + tool outputs
```

### Agent Decision Flow

```
User Query
    │
    ├── SentimentAnalyzer (always runs)
    │       → Classify as Positive / Negative / Neutral
    │
    ├── Pricing Intent Check
    │       → Keyword scan for: "cost", "price", "how much", "budget", etc.
    │       → If YES: call PricingEstimator(service_type, duration_months)
    │       → If NO: skip
    │
    └── RAG Pipeline (always runs)
            → Semantic search → retrieve top-5 chunks
            → Build grounded prompt
            → Gemini generates answer
            → Return answer + citations
```

### Technology Choices

| Component | Technology | Why |
|-----------|-----------|-----|
| LLM | Google Groq Llama 3.1 (llama-3.1-8b-instant) | Fast, free tier, strong reasoning |
| Embeddings | Gemini `embedding-001` | Same API, good multilingual quality |
| Vector DB | ChromaDB | Local, persistent, no infra needed |
| API | FastAPI | Modern Python, async, auto-docs |
| UI | Streamlit | Fast to build, clean for demos |
| Config | python-dotenv | Simple, keeps secrets out of code |

---

## Setup Instructions

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/techculture-ai-assistant.git
cd techculture-ai-assistant
```

### 2. Create a virtual environment

```bash
python -m venv venv
source venv/bin/activate       # Linux / Mac
# OR
venv\Scripts\activate          # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure your API key

Copy the example env file and add your Gemini API key:

```bash
cp .env.example .env
```

Edit `.env`:
```
GEMINI_API_KEY=your_actual_gemini_api_key_here
```

Get a free Gemini API key at: https://aistudio.google.com/app/apikey

### 5. Build the vector store (index documents)

```bash
python embeddings.py --build
```

This reads all files in `docs/`, chunks them, generates embeddings, and saves them to `chroma_db/` (local). Takes ~2-3 minutes due to API rate limits on the free tier.

### 6. Run the application

**Option A — Streamlit UI (recommended for demo)**
```bash
streamlit run app.py
```
Then open http://localhost:8501 in your browser.

**Option B — FastAPI REST API**
```bash
uvicorn api:app --host 0.0.0.0 --port 8000 --reload
```
Then open http://localhost:8000/docs for interactive Swagger UI.

---

## API Usage

### POST /ask

```bash
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "What AI services do you offer?"}'
```

**Response:**
```json
{
  "question": "What AI services do you offer?",
  "answer": "Techculture.ai offers a comprehensive range of AI services...",
  "sources": [
    {"file": "ai_consulting_services.md", "section": "What We Offer"},
    {"file": "services_overview.md", "section": "Core Service Areas"}
  ],
  "tools_used": ["SentimentAnalyzer"],
  "tool_outputs": {
    "SentimentAnalyzer": "🎭 Query Sentiment: Neutral (confidence: High)"
  },
  "sentiment": {"label": "Neutral", "confidence": "High", "signals": []},
  "pricing_estimate": {"triggered": false}
}
```

### GET /health

```bash
curl http://localhost:8000/health
```

### GET /rebuild

Re-indexes documents after adding new files to `docs/`:
```bash
curl http://localhost:8000/rebuild
```

---

## Adding New Documents

1. Add `.md` or `.txt` files to the `docs/` folder
2. Rebuild the index:
   ```bash
   python embeddings.py --rebuild
   ```
   Or hit `GET /rebuild` if the API is running.

---

## Assumptions & Limitations

**Assumptions made:**
- Company documents are in English
- Dummy documents were created to simulate realistic service information since real documents weren't provided
- Pricing is shown in INR with USD approximate equivalents
- Gemini free tier is used — there are rate limits that require batching embeddings with small delays

**Known limitations:**
- The pricing estimator uses a static pricing database, not real-time quotes
- Sentiment analysis is rule-based (keyword matching) — not a trained model
- ChromaDB is local-only — not suitable for multi-instance deployment without switching to a hosted vector DB
- Context window is limited — very long queries with many required sources may lose some context
- No conversation memory — each question is treated independently (no multi-turn context)

---

## Future Improvements

Given more time, I would add:

1. **Conversation memory**: Maintain multi-turn context so follow-up questions work naturally
2. **Hybrid search**: Combine semantic search with BM25 keyword search for better recall on exact-match queries
3. **Hosted vector DB**: Replace local ChromaDB with Pinecone or Weaviate for production scalability
4. **Re-ranker**: Add a cross-encoder re-ranker after initial retrieval to improve answer quality
5. **Evaluation pipeline**: Automated RAG evaluation using RAGAS framework — measuring faithfulness, answer relevancy, and context precision
6. **Auth on API**: Add API key authentication for the REST API
7. **Admin panel**: UI for uploading new documents and triggering re-indexing without CLI
8. **Streaming responses**: Stream Gemini output token-by-token for faster perceived response time

### Production Scaling Plan

| Concern | Current | Production Approach |
|---------|---------|---------------------|
| Vector DB | Local ChromaDB | Pinecone or Weaviate (managed) |
| LLM | Gemini Flash (shared) | Dedicated API quota or self-hosted open-source |
| API | Single uvicorn instance | Docker + Kubernetes with horizontal scaling |
| Document ingestion | Manual CLI | Background job queue (Celery + Redis) |
| Monitoring | Logs only | Prometheus + Grafana + LLM-specific metrics |

---

## Running Tests

```bash
# Test ingestion
python ingestion.py

# Test embeddings and search
python embeddings.py --build
python embeddings.py --search "What AI services do you offer?"

# Test agent end-to-end
python agent.py

# Test tools in isolation
python tools.py
```

---

## Contact

Built by: [Your Name]
For: Techculture.ai AI Transformation Specialist Assignment

Questions? Reach out at hello@techculture.ai
