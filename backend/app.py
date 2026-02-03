from fastapi import FastAPI
from pydantic import BaseModel
from model_utils import evaluate_text_pipeline, init_models
from db import init_db, SessionLocal, CheckLog
import os

app = FastAPI(title="SCSC API")

class EvalRequest(BaseModel):
    text: str

@app.on_event("startup")
async def startup_event():
    os.environ.setdefault('PYTHONHASHSEED', '0')
    init_db()
    init_models()


@app.post("/evaluate")
async def evaluate(req: EvalRequest):
    result = evaluate_text_pipeline(req.text)

    # Logging (optional)
    db = SessionLocal()
    log = CheckLog(
        text=req.text[:500],
        risk=result["risk"],
        categories=",".join([h["category"] for h in result["highlights"]]),
        highlights=str(result["highlights"]),
        rewrites="|".join(result["rewrites"])
    )
    db.add(log)
    db.commit()
    db.close()

    return result
