from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import tempfile
import os

from ocr_engine import extract_text
from entity_extractor import extract_entities
from llm_processor import analyze_document
from database import init_db, save_document, get_all_documents, check_duplicate_invoice

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

init_db()


@app.get("/api/debug-env")
async def debug_env():
    key = os.getenv("GEMINI_API_KEY")
    return {
        "key_exists": key is not None,
        "key_length": len(key) if key else 0,
        "key_preview": (key[:6] + "...") if key else "MISSING"
    }


@app.post("/api/process-document")
async def process_document(file: UploadFile = File(...)):
    suffix = os.path.splitext(file.filename)[1]
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name

    raw_text = extract_text(tmp_path)
    entities = extract_entities(raw_text)
    analysis = analyze_document(raw_text, entities)

    is_duplicate = False
    if entities.get("invoice_number"):
        is_duplicate = check_duplicate_invoice(entities["invoice_number"])

    os.unlink(tmp_path)

    return {
        "filename": file.filename,
        "raw_text": raw_text,
        "entities": entities,
        "analysis": analysis,
        "is_duplicate": is_duplicate,
    }


@app.post("/api/save-document")
async def save_doc(data: dict):
    save_document(
        data["filename"], data["document_type"], data["raw_text"],
        data["entities"], data["summary"], data["anomalies"]
    )
    return {"status": "saved"}


@app.get("/api/documents")
async def get_documents():
    docs = get_all_documents()
    result = []
    for doc in docs:
        result.append({
            "id": doc[0], "filename": doc[1], "document_type": doc[2],
            "summary": doc[5], "anomalies": doc[6], "processed_at": doc[7],
        })
    return result