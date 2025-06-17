from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import importlib
import time
import os
from datetime import datetime
from dotenv import load_dotenv
from sqlalchemy import (
    create_engine, Column, Integer, String, Float, DateTime, JSON
)
from sqlalchemy.orm import declarative_base, sessionmaker

app = FastAPI(title="Algorithm Dashboard API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"] ,
    allow_headers=["*"],
)

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://algouser:algopass@localhost:5432/algodb")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

class RunResult(Base):
    __tablename__ = "run_results"
    id = Column(Integer, primary_key=True)
    algorithm = Column(String, nullable=False)
    elapsed = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    data = Column(JSON)

Base.metadata.create_all(bind=engine)


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

    session = SessionLocal()
    session.add(
        RunResult(
            algorithm=req.algorithm,
            elapsed=elapsed,
            data=result,
        )
    )
    session.commit()
    session.close()

    return result
