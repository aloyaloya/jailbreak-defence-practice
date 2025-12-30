import pickle
import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from app.scanner import HeuristicScanner
from app.vector_engine import VectorEngine
from app.vector_db import VectorDB
from app.preprocessor import TextPreprocessor
from app.config import DRY_RUN
from app.logger import AuditLogger

app = FastAPI()

scanner = HeuristicScanner()
vector_engine = VectorEngine()
vector_db = VectorDB()
preprocessor = TextPreprocessor()
audit_logger = AuditLogger()

classifier = None
classifier_path = "classifier.pkl"
if os.path.exists(classifier_path):
    with open(classifier_path, 'rb') as f:
        classifier = pickle.load(f)

class CheckRequest(BaseModel):
    text: str
    user_id: str | None = None

class CheckResponse(BaseModel):
    is_safe: bool
    block_reason: str | None = None
    score: float | None = None

@app.post("/v1/guard/check", response_model=CheckResponse)
async def check_prompt(request: CheckRequest):
    text = request.text
    
    is_blocked, reason = scanner.check(text)
    if is_blocked:
        audit_logger.log(text, "BLOCK", "heuristic", 1.0)
        if DRY_RUN:
            print(f"[ALARM] SHADOW BLOCK (heuristic): {text}")
            return CheckResponse(is_safe=True, block_reason=None, score=1.0)
        return CheckResponse(is_safe=False, block_reason=reason, score=1.0)
    
    processed_text = preprocessor.preprocess(text)
    vector = vector_engine.encode(processed_text)
    
    result = vector_db.search(vector, threshold=0.35, n_results=1)
    if result:
        threat_id, distance = result
        similarity_score = 1 - distance
        audit_logger.log(text, "BLOCK", "semantic_similarity", round(similarity_score, 2))
        if DRY_RUN:
            print(f"[ALARM] SHADOW BLOCK (semantic): {text} (distance: {distance:.2f})")
            return CheckResponse(is_safe=True, block_reason=None, score=round(similarity_score, 2))
        return CheckResponse(
            is_safe=False,
            block_reason="semantic_similarity",
            score=round(similarity_score, 2)
        )
    
    if classifier is not None:
        prob = classifier.predict_proba([vector])[0][1]
        if prob > 0.85:
            audit_logger.log(text, "BLOCK", "ai_classifier", round(prob, 2))
            if DRY_RUN:
                print(f"[ALARM] SHADOW BLOCK (ai_classifier): {text} (confidence: {prob:.2f})")
                return CheckResponse(is_safe=True, block_reason=None, score=round(prob, 2))
            return CheckResponse(
                is_safe=False,
                block_reason=f"ai_intent_detected_{prob:.2f}",
                score=round(prob, 2)
            )
        else:
            audit_logger.log(text, "SAFE", None, round(prob, 2))
            return CheckResponse(is_safe=True, block_reason=None, score=round(prob, 2))
    
    audit_logger.log(text, "SAFE", None, None)
    return CheckResponse(is_safe=True, block_reason=None, score=0.0)

@app.get("/health")
async def health():
    return {"status": "ok"}

from fastapi.staticfiles import StaticFiles
import os

static_dir = os.path.join(os.path.dirname(__file__), "..", "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")
    
@app.get("/")
async def root():
    static_file = os.path.join(static_dir, "index.html")
    if os.path.exists(static_file):
        from fastapi.responses import FileResponse
        return FileResponse(static_file)
    return {"message": "Эгида API", "docs": "/docs"}

