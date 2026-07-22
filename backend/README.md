# Yojana Autopilot Backend

Production-quality FastAPI backend for an AI-powered Government Services and Welfare Assistant for Andhra Pradesh.

## Features

- Deterministic eligibility engine from `app/data/schemes.json`
- ChromaDB vector index over schemes, services, offices, and portals
- SentenceTransformers embeddings
- Groq-powered grounded chat with DuckDuckGo fallback
- District office lookup
- Portal lookup
- Service and scheme search
- Scheme document checklist
- Typed Pydantic v2 request and response models
- Swagger/OpenAPI documentation

## Folder Structure

```text
backend/
  app/
    main.py
    config.py
    dependencies.py
    prompts.py
    routers/
    services/
    utils/
    models/
    data/
      schemes.json
      services.json
      offices.json
      portals.json
    vector_db/
  requirements.txt
  .env.example
  README.md
```

## Installation

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

Set `GROQ_API_KEY` in `.env` for full chatbot generation. Without it, `/chat` returns retrieval-only grounded snippets.

## Run Server

```powershell
uvicorn app.main:app --reload
```

Open Swagger:

```text
http://127.0.0.1:8000/docs
```

The first startup may take longer because SentenceTransformers downloads the embedding model and ChromaDB builds the local index.

## Environment Variables

| Variable | Purpose |
| --- | --- |
| `GROQ_API_KEY` | Groq API key for chat completions |
| `GROQ_MODEL` | Groq model name |
| `EMBEDDING_MODEL` | SentenceTransformers model |
| `RAG_TOP_K` | Default retrieval count |
| `RAG_MIN_CONFIDENCE` | Threshold before web fallback |
| `API_PREFIX` | Optional API prefix, for example `/api/v1` |

## API Examples

### Health

```bash
curl http://127.0.0.1:8000/health
```

### Eligibility

```bash
curl -X POST http://127.0.0.1:8000/eligibility ^
  -H "Content-Type: application/json" ^
  -d "{\"district\":\"Visakhapatnam\",\"income\":9000,\"location\":\"rural\",\"has_rice_card\":true,\"farmer\":true,\"disabled\":false,\"widow\":false,\"student\":true,\"electricity_units\":120,\"land\":2,\"four_wheeler\":false}"
```

### Chat

```bash
curl -X POST http://127.0.0.1:8000/chat ^
  -H "Content-Type: application/json" ^
  -d "{\"question\":\"How do I apply for a PAN card in Andhra Pradesh?\",\"top_k\":5}"
```

### Offices

```bash
curl http://127.0.0.1:8000/offices/Visakhapatnam
curl "http://127.0.0.1:8000/offices/Guntur?office_type=meeseva"
```

### Portal

```bash
curl http://127.0.0.1:8000/portal/uidai
```

### Service Search

```bash
curl -X POST http://127.0.0.1:8000/services/search ^
  -H "Content-Type: application/json" ^
  -d "{\"keywords\":[\"aadhaar\",\"mobile\"],\"category\":\"identity\",\"top_k\":5}"
```

### Scheme Search

```bash
curl -X POST http://127.0.0.1:8000/schemes/search ^
  -H "Content-Type: application/json" ^
  -d "{\"benefits\":[\"scholarship\",\"education\"],\"category\":\"Education\",\"top_k\":5}"
```

### Document Checklist

```bash
curl http://127.0.0.1:8000/schemes/pm_kisan/documents
```

## Deployment

Use a production ASGI server such as Uvicorn behind a reverse proxy:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Persist `app/vector_db/` between deployments to avoid rebuilding embeddings on every boot. Keep the JSON files in `app/data/` as the source of truth; do not hardcode scheme or service records in code.

