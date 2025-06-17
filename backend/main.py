from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import importlib
import time

app = FastAPI(title="Algorithm Dashboard API")

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

@app.post("/api/run")
async def run_algorithm(req: RunRequest):
    try:
        module = importlib.import_module(f"backend.algorithms.{req.algorithm}")
    except ModuleNotFoundError:
        raise HTTPException(status_code=404, detail="Algorithm not found")

    if not hasattr(module, "run"):
        raise HTTPException(status_code=500, detail="Algorithm missing run()")

    start = time.time()
    result = module.run(req.data or {})
    elapsed = time.time() - start
    if isinstance(result, dict):
        result.setdefault("elapsed", elapsed)
    else:
        result = {"result": result, "elapsed": elapsed}
    return result
