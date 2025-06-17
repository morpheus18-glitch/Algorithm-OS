from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import EventSourceResponse
from pydantic import BaseModel
import importlib
import pkgutil
import time
import json
import os
import asyncio
import sqlite3
import joblib
import faiss

app = FastAPI(title="Algorithm Dashboard API")

# -- Simple in-memory subscriber list for server-sent events
subscribers: list[asyncio.Queue] = []

# -- SQLite connection for persistent results
DB_PATH = os.path.join(os.path.dirname(__file__), "results.db")
conn = sqlite3.connect(DB_PATH, check_same_thread=False)
conn.execute(
    """CREATE TABLE IF NOT EXISTS results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            algorithm TEXT,
            data TEXT,
            result TEXT,
            created TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )"""
)
conn.commit()

# -- Load search index if available
INDEX_PATH = os.path.join(os.path.dirname(__file__), "ml", "index.faiss")
VECT_PATH = os.path.join(os.path.dirname(__file__), "ml", "vectorizer.joblib")
DOCS_PATH = os.path.join(os.path.dirname(__file__), "ml", "docs.json")
if os.path.exists(INDEX_PATH) and os.path.exists(VECT_PATH) and os.path.exists(DOCS_PATH):
    search_index = faiss.read_index(INDEX_PATH)
    vectorizer = joblib.load(VECT_PATH)
    with open(DOCS_PATH) as f:
        documents = json.load(f)
else:
    search_index = None
    vectorizer = None
    documents = []

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"] ,
    allow_headers=["*"],
)

class RunRequest(BaseModel):
    algorithm: str
    data: dict | None = None


class BenchmarkRequest(BaseModel):
    algorithms: list[str]
    data: dict | None = None


def list_algorithms() -> list[str]:
    """Return available algorithm module names."""
    pkg = importlib.import_module("backend.algorithms")
    names = []
    for _, modname, ispkg in pkgutil.iter_modules(pkg.__path__):
        if not ispkg:
            names.append(modname)
    return names


def publish(message: str) -> None:
    """Send a log message to all SSE subscribers."""
    for queue in list(subscribers):
        queue.put_nowait(message)


def execute_algorithm(name: str, data: dict) -> dict:
    try:
        module = importlib.import_module(f"backend.algorithms.{name}")
    except ModuleNotFoundError:
        raise HTTPException(status_code=404, detail=f"Algorithm {name} not found")

    if not hasattr(module, "run"):
        raise HTTPException(status_code=500, detail="Algorithm missing run()")

    publish(f"Running {name}")
    start = time.time()
    result = module.run(data)
    elapsed = time.time() - start
    publish(f"{name} done in {elapsed:.3f}s")
    if isinstance(result, dict):
        result.setdefault("elapsed", elapsed)
    else:
        result = {"result": result, "elapsed": elapsed}
    conn.execute(
        "INSERT INTO results (algorithm, data, result) VALUES (?, ?, ?)",
        (name, json.dumps(data), json.dumps(result)),
    )
    conn.commit()
    return result


@app.get("/api/algorithms")
async def get_algorithms():
    """Return a list of available algorithms."""
    return {"algorithms": list_algorithms()}

@app.post("/api/run")
async def run_algorithm(req: RunRequest):
    result = execute_algorithm(req.algorithm, req.data or {})
    return result


@app.post("/api/benchmark")
async def benchmark(req: BenchmarkRequest):
    results = {}
    for alg in req.algorithms:
        results[alg] = execute_algorithm(alg, req.data or {})
    return {"results": results}


@app.get("/api/logs")
async def log_stream():
    """Server-Sent Events endpoint for live logs."""

    async def event_generator(queue: asyncio.Queue):
        try:
            while True:
                data = await queue.get()
                yield {"data": data}
        except asyncio.CancelledError:
            pass

    queue: asyncio.Queue = asyncio.Queue()
    subscribers.append(queue)
    return EventSourceResponse(event_generator(queue))


@app.get("/api/search")
async def search(q: str, k: int = 5):
    """Return nearest documents for the query."""
    if not search_index or not vectorizer:
        raise HTTPException(status_code=503, detail="Search index not available")
    vec = vectorizer.transform([q]).toarray().astype("float32")
    D, I = search_index.search(vec, k)
    results = []
    for idx, dist in zip(I[0], D[0]):
        if idx < len(documents):
            results.append({"doc": documents[idx], "distance": float(dist)})
    return {"results": results}


@app.get("/api/results")
async def list_results():
    cur = conn.execute("SELECT id, algorithm, created FROM results ORDER BY id DESC LIMIT 100")
    rows = [dict(zip([c[0] for c in cur.description], row)) for row in cur.fetchall()]
    return {"results": rows}


@app.get("/api/results/{result_id}")
async def get_result(result_id: int):
    cur = conn.execute("SELECT id, algorithm, data, result, created FROM results WHERE id=?", (result_id,))
    row = cur.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Result not found")
    keys = [c[0] for c in cur.description]
    result = dict(zip(keys, row))
    result["data"] = json.loads(result["data"])
    result["result"] = json.loads(result["result"])
    return result
