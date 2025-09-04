import os, json, typing as t
from fastapi import FastAPI, Request, HTTPException
import httpx

TEI_BASE = os.getenv("TEI_BASE_URL", "http://tei:80")
MODEL    = os.getenv("MODEL_NAME",  "onnx-community/bge-reranker-v2-m3-ONNX")

app = FastAPI()

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/v1/models")
@app.get("/models")
def models():
    # RAGFlow uses this to validate the base URL
    return {"object": "list", "data": [{"id": MODEL, "object": "model"}]}

@app.post("/v1/rerank")
@app.get("/rerank")
async def rerank(req: Request):
    p = await req.json()
    model   = p.get("model", MODEL)
    query   = p.get("query") or p.get("input")
    docs    = p.get("documents") or p.get("texts") or []
    top_n   = int(p.get("top_n") or len(docs) or 1)
    if not query or not isinstance(docs, list) or len(docs) == 0:
        # OpenAI-style error object
        raise HTTPException(status_code=400, detail="query/documents required")

    tei_payload = {"query": query, "texts": docs, "top_n": top_n, "raw_scores": False}
    async with httpx.AsyncClient(timeout=30.0) as client:
        r = await client.post(f"{TEI_BASE}/rerank", json=tei_payload)
        r.raise_for_status()
        scores = r.json()  # [{"index":..., "score":...}, ...]

    data = [{"index": s["index"], "relevance_score": s["score"]} for s in scores]
    # Return both common shapes just to be safe
    return {"object": "rerank", "model": model, "data": data, "results": data}
