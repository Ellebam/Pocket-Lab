import os, json, re, html, typing as t
from fastapi import FastAPI, Request, HTTPException
import httpx

TEI_BASE = os.getenv("TEI_BASE_URL", "http://tei:80").rstrip("/")
MODEL    = os.getenv("MODEL_NAME", "onnx-community/bge-reranker-v2-m3-ONNX")

TEI_CLIENT_BATCH_MAX     = int(os.getenv("TEI_CLIENT_BATCH_MAX", os.getenv("MAX_CLIENT_BATCH_SIZE", "64")))
RERANK_MAX_DOCS_PER_CALL = int(os.getenv("RERANK_MAX_DOCS_PER_CALL", "256"))
TEI_PAYLOAD_SOFT_LIMIT   = int(os.getenv("TEI_PAYLOAD_SOFT_LIMIT", "10000000"))  # bytes; 0 = unlimited
DOC_CLIP_CHARS           = int(os.getenv("DOC_CLIP_CHARS", "50000"))             # per-doc safeguard

MAX_DOCS_PER_SLICE = min(TEI_CLIENT_BATCH_MAX, RERANK_MAX_DOCS_PER_CALL)

TAG_RE = re.compile(r"<[^>]+>")

def prep_doc(s: str) -> str:
    # light sanitization; avoids ballooning payloads
    s = html.unescape(s)
    s = TAG_RE.sub(" ", s)
    s = " ".join(s.split())
    if len(s) > DOC_CLIP_CHARS:
        s = s[:DOC_CLIP_CHARS]
    return s

app = FastAPI()

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/v1/models")
@app.get("/models")
def models():
    return {"object": "list", "data": [{"id": MODEL, "object": "model"}]}

@app.post("/v1/rerank")
@app.post("/rerank")
async def rerank(req: Request):
    try:
        p = await req.json()
    except Exception:
        raise HTTPException(status_code=400, detail="invalid JSON")

    model = p.get("model") or MODEL
    query = p.get("query") or p.get("input")
    docs  = p.get("documents") or p.get("texts") or []
    top_n = int(p.get("top_n") or len(docs) or 1)
    if not query or not isinstance(docs, list) or not docs:
        raise HTTPException(status_code=400, detail="query/documents required")

    # sanitize & clip each document
    proc_docs = [prep_doc(d if isinstance(d, str) else json.dumps(d)) for d in docs]

    def slices():
        start = 0
        while start < len(proc_docs):
            end = min(start + MAX_DOCS_PER_SLICE, len(proc_docs))
            while end > start:
                payload = {"query": query, "texts": proc_docs[start:end],
                           "top_n": end - start, "raw_scores": False}
                size = len(json.dumps(payload, ensure_ascii=False).encode("utf-8"))
                if TEI_PAYLOAD_SOFT_LIMIT == 0 or size <= TEI_PAYLOAD_SOFT_LIMIT:
                    yield start, payload
                    start = end
                    break
                # too big -> shrink slice
                end = start + max(1, (end - start) // 2)
            if end == start:
                # even a single clipped doc is over limit
                raise HTTPException(status_code=413, detail="single document exceeds payload limit")

    results: list[dict] = []
    timeout = httpx.Timeout(60.0, connect=10.0, read=60.0, write=60.0)
    async with httpx.AsyncClient(timeout=timeout) as client:
        for offset, payload in slices():
            r = await client.post(f"{TEI_BASE}/rerank", json=payload)
            r.raise_for_status()
            for item in r.json():  # [{"index": i, "score": s}, ...]
                results.append({
                    "index": offset + int(item["index"]),
                    "relevance_score": float(item["score"])
                })

    results.sort(key=lambda x: x["relevance_score"], reverse=True)
    results = results[:top_n]
    return {"object": "rerank", "model": model, "data": results, "results": results}
