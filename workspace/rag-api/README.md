# RAG API

REST API for Retrieval-Augmented Generation with continuous learning.

## Quick Start

```bash
cp .env.example .env
# Add your OPENAI_API_KEY to .env

pip install -r requirements.txt
python main.py
```

Or with Docker:

```bash
docker compose up -d
```

## API Endpoints

### POST /ask
Ask a question against your knowledge base.

```bash
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "How do I reset a password?", "top_k": 5}'
```

Response:
```json
{
  "answer": "To reset a password, go to Settings > Security...",
  "sources": [{"content": "...", "source": "docs/guide.md"}],
  "confidence": 0.9,
  "query_id": "a1b2c3d4"
}
```

### POST /ingest
Upload a document (.txt, .md) to the knowledge base.

```bash
curl -X POST http://localhost:8000/ingest \
  -F "file=@./my-doc.md"
```

### POST /feedback
Submit feedback for continuous learning ( thumbs up/down on answers ).

```bash
curl -X POST http://localhost:8000/feedback \
  -H "Content-Type: application/json" \
  -d '{"query_id": "a1b2c3d4", "rating": 5, "comment": "Very helpful!"}'
```

### GET /sources
List indexed documents.

```bash
curl http://localhost:8000/sources
```

### GET /health
Health check.

```bash
curl http://localhost:8000/health
```

## Cloud Deployment

### Railway (recommended)
1. Push to GitHub
2. Connect repo to [Railway](https://railway.app)
3. Add `OPENAI_API_KEY` env var
4. Deploy

### Render
1. Create `render.yaml` or connect directly via Render dashboard
2. Set env vars and deploy

### AWS / GCP
```bash
docker build -t rag-api .
docker push <your-registry>/rag-api
# Then deploy via ECS / Cloud Run with your cloud provider
```

## Continuous Learning

Feedback is logged to `data/feedback.jsonl`. To improve the system:

1. **Review low ratings** — find gaps in your docs
2. **Re-ingest improved docs** — the vector store updates automatically
3. **Add FAQ documents** — for common weak areas
4. **Tune the prompt** — edit `DEFAULT_PROMPT` in `main.py`
